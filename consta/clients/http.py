import html as html_lib
import re
from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx

_DEFAULT_HEADERS = {"User-Agent": "consta/0.1 (evidence retrieval)"}
_REFRESH_URL_RE = re.compile(r"url\s*=\s*['\"]?([^'\";]+)", re.IGNORECASE)
# Page chrome, not content: dropping it keeps CSS, nav menus and cookie banners
# out of snippets (and out of the quote gate's haystack).
_SKIP_TAGS = frozenset(
    {"head", "script", "style", "noscript", "svg", "template", "nav", "header", "footer"}
)
_VOID_TAGS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
     "source", "track", "wbr"}
)


class _PageText(HTMLParser):
    """Title, meta description, meta-refresh target and visible body text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.refresh_url: str | None = None
        self._chunks: list[str] = []
        self._main_chunks: list[str] = []
        self._main_depth = 0
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "meta":
            a = {k.lower(): (v or "") for k, v in attrs}
            name = (a.get("name") or a.get("property") or "").lower()
            if name in ("description", "og:description") and not self.description:
                self.description = a.get("content", "").strip()
            if a.get("http-equiv", "").lower() == "refresh":
                match = _REFRESH_URL_RE.search(a.get("content", ""))
                if match:
                    self.refresh_url = match.group(1).strip()
            return
        if tag == "title":
            self._in_title = True
        if tag in ("main", "article"):
            self._main_depth += 1
        if tag in _SKIP_TAGS and tag not in _VOID_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag in ("main", "article") and self._main_depth:
            self._main_depth -= 1
        if tag in _SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        elif not self._skip_depth:
            self._chunks.append(data)
            if self._main_depth:
                self._main_chunks.append(data)

    @property
    def body(self) -> str:
        # <main>/<article> when the page marks its content; whole body otherwise.
        chunks = self._main_chunks if self._main_chunks else self._chunks
        return re.sub(r"\s+", " ", " ".join(chunks)).strip()


def extract_page_text(html: str) -> tuple[str, str, str | None]:
    """Return (title, snippet, meta-refresh URL) for an HTML document."""
    parser = _PageText()
    try:
        parser.feed(html)
        parser.close()
    except Exception:  # noqa: BLE001 — malformed HTML yields whatever was parsed
        pass
    title = re.sub(r"\s+", " ", parser.title).strip()
    description = re.sub(r"\s+", " ", html_lib.unescape(parser.description)).strip()
    body = parser.body
    if description and not body.startswith(description):
        snippet = f"{description} — {body}" if body else description
    else:
        snippet = body or description
    return title, snippet, parser.refresh_url


class HttpClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def fetch_page_summary(self, url: str, *, max_len: int = 400) -> tuple[str, str]:
        """Return (title, plain-text snippet) for a public HTML page."""
        html = await self.fetch_html(url)
        if html is None:
            return url, "Page could not be fetched."
        title, snippet, refresh = extract_page_text(html)
        if refresh:
            # Docs hosts often redirect "stable" URLs with a meta refresh.
            target = await self.fetch_html(urljoin(url, refresh))
            if target is not None:
                title, snippet, _ = extract_page_text(target)
        if not snippet:
            snippet = "Curated discussion thread (pinned in ecosystem profile)."
        return (title or url)[:200], snippet[:max_len]

    async def fetch_html(self, url: str) -> str | None:
        try:
            response = await self._client.get(
                url, follow_redirects=True, headers=_DEFAULT_HEADERS
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPError:
            return None

    async def url_exists(self, url: str) -> bool:
        try:
            head = await self._client.head(url, follow_redirects=True)
            if head.status_code < 400:
                return True
            if head.status_code == 405:
                get = await self._client.get(url, follow_redirects=True)
                return get.status_code < 400
            return False
        except httpx.HTTPError:
            return False
