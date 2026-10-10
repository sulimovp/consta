# Architecture

Consta answers one request: a question, a repository, and optionally a path and an
ecosystem profile. It runs a fixed pipeline and writes a Markdown or JSON report.

```text
question, repo, path, profile
  → planner        build search queries and URLs              consta/engine/planner.py
  → retrievers     fetch evidence in parallel                 consta/retrievers/
  → validator      drop off-topic items, dedupe, rank         consta/engine/validator.py
  → synthesizer    optional LLM summary                       consta/engine/synthesizer.py
  → citation check verify every citation and quote            consta/engine/citation_checker.py
  → renderer       Markdown report                            consta/render/markdown.py
```

Only the synthesizer calls an LLM. Every other stage is deterministic and tested
without network access.

## Layout

```text
consta/
  cli.py              typer commands: assess, ping, list-profiles
  config.py           settings from CONSTA_* env vars and .env files
  models/             pydantic models: request, evidence, report, profile
  engine/             planner, orchestrator, validator, synthesizer, citation checker
  retrievers/         one module per evidence source
  clients/            GitHub, HTTP, Hugging Face Hub and LLM clients
  cache/              on-disk cache for GitHub search results (1 hour)
  render/markdown.py  report layout
  predict/            experimental topic forecast (see docs/PREDICT.md)
  web/                Flask UI
profiles/             ecosystem profiles (YAML)
eval/                 sample cases and labelled data for the forecast
```

## Data model

`AssessmentRequest` holds the question, `repo`, `path`, `ecosystem`, `tier` (1 or 2),
`synthesize` and `max_evidence`.

`EvidenceItem` is one piece of evidence:

| Field | Notes |
|-------|-------|
| `id` | Stable slug, e.g. `issue-89734`, `vitals-torch-masked` |
| `kind` | `issue`, `pull_request`, `commit`, `file`, `process_doc`, `discourse_thread`, `hf_discussion`, `adjacent_project`, `vital_signs`, … |
| `title`, `url` | Shown in the report |
| `snippet` | Up to 500 characters of source text. Quotes in the summary are checked against title and snippet |
| `relevance_score` | 0–1, set by the retriever |
| `metadata` | Kind-specific: labels, state, curator note, exclusion reason |

`EvidenceBundle` holds the kept items, the excluded items with reasons, open questions
and diagnostics. `AssessmentReport` adds the summary, the citation map and any citation
errors.

## Retrievers

Each retriever has a `plan()` step, which builds its queries without network access,
and an async `fetch()`. The orchestrator runs every retriever whose tier is at most the
requested tier. One failing retriever adds a diagnostic and does not stop the run.

| Retriever | Tier | Produces |
|-----------|------|----------|
| `github_issues` | 1 | Issues from search queries, pinned issue numbers and profile labels |
| `repo_files` | 1 | `README.md`, `CONTRIBUTING.md`, `.github/CODEOWNERS` and the profile's `scope_files` |
| `git_activity` | 1 | Recent commits on the path |
| `vital_signs` | 1 | Commit counts for 3, 6 and 12 months, committers, open and closed issue counts, CODEOWNERS |
| `adjacent_projects` | 1 | Alternative projects from the profile; each URL is fetched and kept only if it responds |
| `github_prs` | 2 | Merged PRs on the path or topic |
| `process_docs` | 2 | RFC and design-process pages from the profile |
| `discourse` | 2 | Forum threads: pinned in the profile, plus site search |
| `huggingface_discussions` | 2 | Discussions on Hugging Face Hub repos listed in the profile |

## Planner

`build_plan()` turns the request and profile into one `RetrievalSpec` per retriever:
GitHub search strings, file paths and URLs. It expands the question with the profile's
synonyms and adds pinned issues, label searches and the profile's alternative projects.
If `--path` is not given, a profile's `path_hints` can set it from words in the question.
No LLM is involved.

## Validator

`validate_evidence()` runs on every retrieved item:

- Issues and PRs must match at least one specific term from the question, path or
  profile. Matching only the project name is not enough. Pinned issues and label search
  hits are always kept.
- Items with an empty snippet are excluded.
- Duplicates by URL are merged, keeping the higher score.

Excluded items are kept with their reason and listed in the report.

The orchestrator then orders the kept items: the top two of each kind come first, then
the rest by score. The synthesizer only reads the first 25 items, and without this step
they would all be issues.

## Synthesizer and citation check

The synthesizer sends the question and the first 25 items (id, kind, title, URL,
snippet) to the configured LLM and asks for JSON: paragraphs, a map from `[n]` to
evidence id, and open questions. Each claim must end with a quote of at most 15 words
from the cited item, followed by `[n]`.

`check_citations()` then requires that:

- the summary has citations, and every paragraph has at least one;
- every `[n]` maps to an evidence id in the bundle, and to the id at that position;
- every quote appears in the cited item's title or snippet (case, whitespace, backticks
  and quote marks are ignored; `...` may join fragments that appear in order);
- the quote is more than the item's name, for kinds whose title is only a name
  (alternative projects, vital signs, files).

If the model numbers its citations in a different order but names valid ids, the
citations are renumbered to those ids before the check. If the check fails, the model
gets one retry with the errors listed. If the retry also fails, the report shows the
evidence without a summary and lists the errors.

The check confirms that each quote exists in its source. It does not confirm that the
sentence around the quote is correct.

## Profiles

A profile is a YAML file in `profiles/`, loaded by name. Engine code has no
ecosystem-specific logic. A profile can set:

- `synonyms` for query expansion and on-topic matching;
- `label_boosts` and `pinned_issue_numbers`;
- `adjacent_projects` with a URL and a curator note (shown, never quoted);
- `scope_files`, `path_hints`, `rfc`, `discourse`, `huggingface`;
- `last_verified` and `max_age_days`. A profile older than that is refused unless
  `--allow-stale-profile` is passed.

## LLM providers

`consta/clients/llm.py` supports Anthropic, OpenAI, OpenRouter and the Hugging Face
router. The provider is chosen by `CONSTA_LLM_PROVIDER` and the model by
`CONSTA_LLM_MODEL`.

## Topic forecast

`consta/predict/` adds a "Topic trajectory" section: inflow of new issues and the share
resolved, recent against baseline. It refuses to print a result when its inputs are not
measured well enough, which is the usual case. Design and status:
[docs/PREDICT.md](docs/PREDICT.md) and [docs/PREDICT_QUADRANT.md](docs/PREDICT_QUADRANT.md).

## Not built

- A local index of issues and PRs (`consta/index/` is a placeholder). Every run uses
  the GitHub API, with the search cache above.
- Embedding-based ranking.
- A GitHub App. The [GitHub Action](action/action.yml) covers the comment-on-new-issue case.
- A check that a sentence is supported by its quote, beyond the quote's existence.

## Tests

| Layer | How |
|-------|-----|
| Planner, validator, citation check, renderer | Unit tests |
| Retrievers and engine | `pytest-httpx` with mocked GitHub and HTTP responses |
| Sample cases | Plan checks against `eval/sample_cases.yaml` |
| Live | `CONSTA_RUN_LIVE=1 pytest tests/test_live.py` |

`./scripts/verify.sh` runs everything except the live test. CI runs it on every push.
