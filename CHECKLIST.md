# Before you open that issue: a checklist

You found a gap in a library you use. Before you open an issue, write an RFC or spend a
month on a pull request, collect the evidence. This takes 30–60 minutes with `gh`,
`git`, `rg` (ripgrep) and the template at the end. You do not need Consta for it; Consta
automates the same steps.

The examples use `torch.masked` in `pytorch/pytorch`. Replace the repository, path and
terms with yours.

## 0. Write the question as a decision

Bad: "Tell me about torch.masked."
Good: "Is reviving `torch.masked` worth a multi-month upstream contribution, or is a
smaller change enough?"

A decision question tells you what evidence would change your mind.

## 1. Find out what was already said

Search closed issues first. They hold the duplicates, the "won't fix" answers and the
design discussions.

```bash
gh search issues --repo pytorch/pytorch --state closed --match title "MaskedTensor"
gh search issues --repo pytorch/pytorch --state open --label "module: masked operators" --limit 50
gh issue view 89734 --repo pytorch/pytorch --comments
```

- Search with the class name and the label, not a generic word. "masked" alone returns
  unrelated MPS and TorchScript issues.
- Read the closed issues closed as "not planned" in full; the reason is usually in the
  last maintainer comment.
- Note every issue number you rely on. You will cite them.

## 2. Find what was merged

```bash
gh search prs --repo pytorch/pytorch --merged "MaskedTensor"
```

A merged PR titled "Add prototype warning to MaskedTensor constructor" (#87380, October 2022)
says more about the module's
status than any open issue.

## 3. Measure activity on the path, not the repository

`pytorch/pytorch` gets hundreds of commits a week. That says nothing about one module.

```bash
git clone --filter=blob:none https://github.com/pytorch/pytorch && cd pytorch
git log --since="3 months ago"  --oneline -- torch/masked | wc -l
git log --since="6 months ago"  --oneline -- torch/masked | wc -l
git log --since="12 months ago" --oneline -- torch/masked | wc -l
git shortlog -sn --since="12 months ago" -- torch/masked
git log -5 --format="%h %ad %an %s" --date=short -- torch/masked
rg -n "torch/masked" .github/CODEOWNERS
```

- Compare the last 6 months with the 6 months before. A falling count matters more than
  a low one.
- Look at who committed. Bots, mass refactors and lint sweeps touch dormant code too.
- No CODEOWNERS entry means no one is obliged to review your PR.

## 4. Check the alternatives

```bash
rg -n -i "prototype|not .*under active development|deprecated" torch/masked docs/source/masked*
curl -sL https://docs.pytorch.org/docs/main/nested.html | rg -o "not currently under active development"
```

- An alternative counts only with a live URL and a sentence from that page. Fetch the
  page itself: `docs/stable/` URLs on pytorch.org are redirect stubs that contain no text. "Library X
  already does this" without both is a guess.
- Check the alternative's own status. For `torch.masked`, the closest alternative,
  NestedTensor, is itself "not currently under active development".

## 5. Check the process

```bash
gh api repos/pytorch/pytorch/contents/CONTRIBUTING.md --jq .content | base64 -d | rg -n -i "rfc|design"
gh repo view pytorch/rfcs
```

Large changes in many projects need an RFC or design document first. Find out before
writing code.

## 6. Write the brief

One page. Every claim gets a link and a short quote from the source, so a teammate can
check it in ten minutes. Copy this template:

```markdown
# Should we <decision>?

Date: <YYYY-MM-DD>   Repository: <owner/name>   Path: <path>

## Answer in three lines
<what the evidence says, conditional, no verdict without sources>

## Evidence
| Claim | Quote from the source | Link |
|-------|-----------------------|------|
| Docs are missing | "Masked Tensor documentation is missing" | https://github.com/pytorch/pytorch/issues/89734 |
| Activity is falling | <commit counts 3/6/12 months> | <git log command or commits URL> |
| The alternative is not maintained either | "not currently under active development" | <docs URL> |

## Activity on <path>
Commits 3 / 6 / 12 months: <n> / <n> / <n>. Committers (12 months): <n>. CODEOWNERS: <yes/no>.

## Alternatives
| Project | URL | What it covers | Its own status |
|---------|-----|----------------|----------------|

## Open questions
- <what the evidence does not settle; ask the maintainers>

## Decision
<who decided, what, and which evidence moved it>
```

## What not to trust

- A verdict from a chat with an LLM that cites nothing. It names projects and facts it
  never checked.
- "Library X already does this" without a URL and a quote from X's docs.
- Repository-level health (stars, total commits, release cadence) for a module-level
  question.
- Issue counts from a broad keyword search. Check what the results actually are.
- Labels as a status signal without checking the label still exists and is still used.
- Your own summary, until a teammate has opened the links.

## Automating it

[Consta](README.md) runs steps 1–5 and writes the brief with a link for every item. If
you use its LLM summary, every claim must carry a quote that is found verbatim in the
cited source, or the summary is withheld.

```bash
pip install consta
consta assess -q "Is reviving torch.masked worth an upstream contribution?" \
  -r pytorch/pytorch -p torch/masked -e pytorch --no-synthesis
```
