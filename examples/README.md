# Examples

Reports generated with `nvidia/nemotron-3-ultra-550b-a55b:free` on OpenRouter:

| Report | Question | Date |
|--------|----------|------|
| [torch-masked.md](torch-masked.md), [torch-masked.json](torch-masked.json) | Is reviving `torch.masked` worth an upstream contribution? | 10 October 2026 |
| [numpy-ma.md](numpy-ma.md) | Is improving `numpy.ma` worth an upstream contribution, given `__array_function__`? | 8 October 2026 |

GitHub changes daily, so a new run will differ. The rest of this page follows the
`torch.masked` run through each stage.

## 1. The request

```bash
consta assess \
  -q "Is reviving torch.masked worth an upstream contribution?" \
  -r pytorch/pytorch -p torch/masked -e pytorch -t 2 \
  -o torch-masked.md
```

`-p` scopes activity and issue counts to `torch/masked`. `-e pytorch` loads
[profiles/pytorch.yaml](../profiles/pytorch.yaml). `-t 2` adds merged PRs and forum threads.

## 2. Planning

The planner turns the question and profile into searches. Some of them:

```text
github_issues      repo:pytorch/pytorch is:issue 89734                      pinned in the profile
                   repo:pytorch/pytorch is:issue label:"module: masked operators"
                   repo:pytorch/pytorch is:issue MaskedTensor in:title      profile synonym
github_prs         repo:pytorch/pytorch is:pr is:merged path:torch/masked
adjacent_projects  https://pytorch.org/docs/stable/nested.html              from the profile
                   https://pytorch.org/blog/flexattention/
vital_signs        commits and issue counts for torch/masked
```

The profile supplies what a plain search would miss: the class is called `MaskedTensor`,
the label is `module: masked operators`, and NestedTensor and FlexAttention are the
alternatives to check.

## 3. Retrieval

The searches run in parallel. Each result becomes an evidence item with an id, a link,
a title and a snippet of source text:

```text
[1]  issue-89734            Masked Tensor documentation is missing
[3]  vitals-torch-masked    commits 3/6/12mo = 0/7/23 (falling); open_issues_total=100 ...
[9]  adjacent-nestedtensor  Nested tensors are not currently under active development. ...
```

Vital signs are counted from the GitHub API: commits on the path in the last 3, 6 and
12 months, committers, open and closed issues, and whether CODEOWNERS covers the path.

## 4. Validation

Searching for "masked" also returns sparse-tensor tracking issues and compiler bugs.
Issues and PRs that match no specific term from the question or profile are dropped.
This run kept 52 items and dropped 42; the dropped ones are listed at the end of the
report with the reason.

Up to this point no LLM is involved. With `--no-synthesis` the report ends here.

## 5. Summary

The LLM receives the question and the first 25 items. It must use only those items and
end every claim with a quote of at most 15 words from the cited item, followed by `[n]`.

## 6. Citation check

The code then checks the summary:

| Check | Catches |
|-------|---------|
| `[n]` points to an item in the report | `[31]` when only 25 items were sent |
| Every paragraph cites something | A closing paragraph of opinion |
| The quote is in the cited item's title or snippet | Paraphrases and invented wording |
| The quote is more than the item's name | `"pandas" [5]` |

A failed check gets one retry. If that fails too, the report shows the evidence and the
errors, without a summary.

From the numpy report:

> The numpy/ma module shows declining commit activity … "commits 3/6/12mo = 30/57/197 (falling)" [3]

Item [3] in that report contains that text.

The check cannot tell whether a sentence draws the right conclusion from its quote. In
another run, a smaller model quoted "commits 3/6/12mo = 0/7/23" and then wrote that the
module had no commits in six months; the figure for six months is 7.

## 7. The report

| Section | Content | Source |
|---------|---------|--------|
| Summary | Cited paragraphs, or why there is none | LLM, then the citation check |
| Topic trajectory | Experimental forecast; usually declines to give a number | Code |
| Evidence | Kept items by kind, with links | Code |
| Open questions | What the evidence does not settle | Code and LLM |
| Retrieved but excluded | Dropped items and why | Code |
| Diagnostics | Failed fetches, truncated samples | Code |

In the `torch.masked` report the evidence alone shows the situation: many open bugs, no
commits in three months, and the nearest alternative, NestedTensor, is itself marked as
not under active development.

## Checking a report yourself

`consta check` re-runs the citation check on a saved JSON report. It needs no network
and no keys:

```bash
consta check examples/torch-masked.json
# OK: 18 citations, every quote found in its source.
```

Change one quote in the summary and run it again:

```bash
python -c "
import json
d = json.load(open('examples/torch-masked.json'))
d['summary'] = d['summary'].replace('0/7/23 (falling)', '9/17/43 (rising)', 1)
json.dump(d, open('forged.json', 'w'))
"
consta check forged.json -o forged.md
# FAILED: 1 citation error(s). Summary withheld; evidence kept.
#   - Citation [3] quote 'commits 3/6/12mo = 9/17/43 (rising)' not found in cited item 'vitals-torch-masked'
```

`forged.md` has the evidence and the error, and no summary.

## Running it

```bash
pip install -e ".[dev,web]"
cp .env.example .env    # set CONSTA_GITHUB_TOKEN; an LLM key is optional
consta ping
consta assess -q "..." -r owner/repo -p path/in/repo --no-synthesis
consta assess -q "..." -r owner/repo -p path/in/repo -o report.json   # with a summary, saved as JSON
consta check report.json
```

More questions are in [eval/sample_cases.yaml](../eval/sample_cases.yaml).
`./scripts/run_sample_assessments.sh` writes a set of reports to `reports/`.
