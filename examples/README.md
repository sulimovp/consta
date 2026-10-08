# Examples: how a Consta report is made

Two real reports, generated on 8 October 2026 with the free OpenRouter model
`nvidia/nemotron-3-ultra-550b-a55b:free`:

| Report | Question |
|--------|----------|
| [torch-masked.md](torch-masked.md) | Is reviving `torch.masked` worth an upstream contribution? |
| [numpy-ma.md](numpy-ma.md) | Is improving `numpy.ma` worth an upstream contribution, given `__array_function__`? |

They are snapshots. GitHub changes every day, so your own run will differ in the details.

The rest of this page follows the `torch.masked` run from question to report.

---

## Step 0: you ask a question

```bash
consta assess \
  -q "Is reviving torch.masked worth an upstream contribution?" \
  -r pytorch/pytorch -p torch/masked -e pytorch -t 2 \
  -o torch-masked.md
```

| Flag | Meaning |
|------|---------|
| `-q` | Your question, in plain language |
| `-r` | The repository |
| `-p` | The folder (module) you care about. Activity and issue counts are scoped to it |
| `-e` | An ecosystem profile with hand-written hints ([profiles/pytorch.yaml](../profiles/pytorch.yaml)). Optional |
| `-t 2` | Tier 2 adds merged PRs and forum threads to issues, files and commits |

Nothing is trained, and the model doesn't need to know PyTorch. Steps 1–3 are ordinary
Python calling the GitHub API and fetching web pages. The LLM appears only in step 4.

## Step 1: plan the searches (no AI)

The planner combines your question with the profile and writes a list of concrete searches.
For this run:

```text
github_issues     repo:pytorch/pytorch is:issue 89734            ← pinned tracking issues
                  repo:pytorch/pytorch is:issue label:"module: masked operators"
                  repo:pytorch/pytorch is:issue MaskedTensor in:title   ← profile synonym
                  repo:pytorch/pytorch is:issue torch.masked
github_prs        repo:pytorch/pytorch is:pr is:merged path:torch/masked
adjacent_projects https://pytorch.org/docs/stable/nested.html    ← alternatives to check
                  https://pytorch.org/blog/flexattention/
discourse         dev-discuss.pytorch.org threads (pinned + site search)
vital_signs       commits and issue counts for torch/masked
```

The profile adds knowledge a search engine lacks: `MaskedTensor` is the class name for
`torch.masked`, the label is `module: masked operators`, and NestedTensor and FlexAttention
are the alternatives worth checking. Without `-e`, the planner works from the question
and path alone.

## Step 2: retrieve (no AI)

All the searches run in parallel. Each result becomes an **evidence item**: an id, a link,
a title and a short snippet of real text. For example:

```text
[1]  issue-89734           Masked Tensor documentation is missing
[3]  vitals-torch-masked   commits 3/6/12mo = 0/7/23 (falling); open_issues_total=100 ...
[9]  adjacent-nestedtensor "Nested tensors are not currently under active development. ..."
```

**Vital signs** are counted, not written by a model: commits in the last 3, 6 and 12 months
on the folder, distinct committers, open and closed issues and the closure rate, and
whether CODEOWNERS mentions the path.

## Step 3: validate (no AI)

Every item is checked before it can count as evidence:

- **Dead links are dropped.** Pages are fetched, not trusted.
- **Off-topic results are dropped, with a reason.** GitHub search for "masked" also returns
  sparse-tensor tracking issues and Inductor bugs. In this run **52 items were kept and
  42 excluded**. All 42 are listed at the bottom of the report under
  *Retrieved but excluded*, so you can check that nothing was hidden.
- **Each kind gets a seat.** Issues outnumber everything else, so the top items of every
  kind (activity, alternatives, PRs, forums) move to the front, where the model will see them.

If you stop here (`--no-synthesis`), you already have a complete, cited report with no AI.

## Step 4: synthesize (the only AI step)

The model receives the question and the first 25 evidence items, numbered, and
these rules:

- Use only the evidence. Name nothing that isn't in the list.
- Every claim ends with a **verbatim quote** (at most 15 words) from the cited item, then `[n]`.
- Every paragraph cites something.
- Be conditional. Contributing may be unwise if an alternative already covers the need.

It is a general-purpose model (Claude, GPT, Nemotron and so on), used as is. It learns
nothing from the repository, and every run starts fresh.

## Step 5: the citation gate (no AI)

Code, not the model, checks the model's answer:

| Check | Example it catches |
|-------|-------------------|
| Every `[n]` points to a real evidence item | `[31]` when only 25 items were given |
| Every paragraph has a citation | A closing paragraph of pure opinion |
| The quote really appears in that item's title or snippet | A paraphrase or invented wording |
| The quote is more than the item's name | `"pandas" [5]` used as "evidence" |

If a check fails, the model gets one repair attempt with the errors listed. If the repair
also fails, **the summary is withheld** and the report says why. The evidence is still shown.

In the numpy run, every sentence passed:

> The numpy/ma module shows declining commit activity … "commits 3/6/12mo = 30/57/197 (falling)" [3]

Open [3] and the quote is there.

**What the gate cannot do:** it proves the quote exists, not that the sentence built on
it is right. In another run, a smaller model quoted "commits 3/6/12mo = 0/7/23" correctly,
then wrote "0 commits in the last 6 months" (the quote says 7). Checking the quotes is
your job, and the report makes that quick.

## Step 6: the report

| Section | What it is | Made by |
|---------|------------|---------|
| Summary | 2–3 cited paragraphs, or the reason it was withheld | LLM, checked by the gate |
| Topic trajectory | Experimental forecast. Usually refuses (not enough measured data) | Code |
| Evidence | Every kept item, grouped by kind, with its link | Code |
| Open questions | What the evidence doesn't settle, e.g. pinned issues not found | Code + LLM |
| Retrieved but excluded | Everything dropped in step 3, with the reason | Code |
| Diagnostics | Failed fetches, truncated samples | Code |

**How to read it:** start with *Module vital signs* and *Adjacent projects*, then the
summary, then click 2–3 citations to check them. In the torch.masked report, the evidence
tells the story without the model: dozens of open bugs, 0 commits in 3 months, and the
team's nearest alternative (NestedTensor) is itself "not currently under active development".
**The verdict is yours.**

---

## Run it yourself

```bash
pip install -e ".[dev,web]"
cp .env.example .env        # add CONSTA_GITHUB_TOKEN; an LLM key is optional
consta ping                 # checks GitHub and the LLM
consta assess -q "..." -r owner/repo -p path/in/repo --no-synthesis   # no AI needed
consta-web                  # http://127.0.0.1:5050, six preset scenarios
```

More scenarios: [eval/sample_cases.yaml](../eval/sample_cases.yaml). Regenerate a full set
into the git-ignored `reports/` with `./scripts/run_sample_assessments.sh`.
