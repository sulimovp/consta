# Topic forecast: design

Written 2026-08-24, updated since. Design for predicting whether issues on a topic get
resolved, and for summarising a topic's trajectory. The parts that are built are
described in [PREDICT_QUADRANT.md](PREDICT_QUADRANT.md); status is in [STATUS.md](STATUS.md).

The starting point was `vitals-logistic-v0`: nine hand-set constants over eight
vital-signs features, three of them broken. It is not a model and is no longer printed.

## 1. Constraints from the Apertus case

The Apertus run (Hugging Face Hub discussions on `swiss-ai` models) used retrieval,
rule-based ranking and an LLM summary. No forecast ran: the profile has no path, so vital
signs never fired. Three properties of that evidence shape the design:

- Small. Seven threads on `Apertus-v1.5-8B`, 33 on `Apertus-8B-Instruct-2509`. A
  per-topic statistic over seven items has a standard error larger than the effect.
- Young. The 1.5 weights were a month old, so there is no history to reconstruct and
  no elapsed outcome window to label.
- Decided by one item. The answer depended on draft PR
  [#5](https://huggingface.co/swiss-ai/Apertus-v1.5-8B/discussions/5) and a `transformers`
  doc page that still said "Coming soon". No average over the threads would have shown
  that. Better ranking surfaced it.

So for young or thin ecosystems, ranking and showing items beats scoring and
aggregating. The model below is for corpora like PyTorch with years of resolved history.
For Apertus it refuses.

## 2. Design decisions

### 2.1 An LLM extracts features; a tabular model predicts

The LLM turns issue text into a few schema-constrained fields. A tabular model, which can
be calibrated, backtested and inspected, makes the prediction. The LLM never produces the
result, in the same way the citation check keeps the summary tied to quotes.

- Stance over sentiment. Sentiment on issue text mostly tracks issue type (bug reports
  read negative, feature requests positive). The useful fields describe the request and
  the response: what is asked, whether there is a reproducer, whether a maintainer
  replied and what they committed to. `maintainer_stance ∈ {none, acknowledged, planned,
  deferred, declined, needs_info}` is expected to be the strongest extracted field. One
  `affect` field (0–2) is kept and expected to rank low.
- A pinned extractor. If the extraction model or prompt changes between training rows
  and test rows, a temporal split measures extractor drift and reports it as signal.
  Every extracted row stores `extractor_version` (model id, prompt hash, schema version),
  and any change forces full re-extraction. A router alias such as
  `gpt-oss-120b:fastest` can move and is not a pin. Current pin, captured 2026-08-30
  ([docs/hf_snapshot/](hf_snapshot/README.md)):
  - Hub revision of `openai/gpt-oss-120b`: `b5c939de8f754692c1647ca79fbf85e8c1e70f8a`
  - Router id: `openai/gpt-oss-120b:groq` (the router does not accept a revision)
  - `extractor_version` model id:
    `openai/gpt-oss-120b:groq@b5c939de8f754692c1647ca79fbf85e8c1e70f8a`
    (`PINNED_EXTRACTOR_MODEL_ID` in `predict/extractor.py`)

  `CONSTA_LLM_MODEL` must be the router id; rows extracted with `:fastest` are unusable.
  The runner is `python -m consta.predict.extract_run`.
- Reactions from the list endpoint. `GET /repos/{o}/{r}/issues/{n}/reactions` returns
  each reaction with its own `created_at` (checked against the REST docs on 2026-08-24),
  so counts at time *T* can be reconstructed. The `reactions` summary on the issue
  object is current state and leaks the future.

### 2.2 Target: competing risks, not "closed"

An issue closes either because it was resolved (a merged change, an answer, a design
decision) or because it was closed administratively (stale bot, duplicate, wontfix, no
response). The two mean opposite things for a topic, and declining modules produce many
administrative closures: backlogs get swept and stale bots get enabled when nobody
triages. A model trained on "closed" would rate a declining module as healthy.

Outcomes:

- R1, resolved. Closed with a linked merged PR or commit touching the topic's paths;
  closed by a maintainer comment that the extractor labels as an answer; or, on the Hub,
  a merged PR on the repo.
- R2, closed administratively. Stale, duplicate, wontfix or invalid label at close,
  closed by a bot, or closed with no linked code and no maintainer answer. Repositories
  that do not use `fixes #N` will have real fixes counted as R2. This is controlled by
  `unlabeled_closed_as_r2` (on by default), and the false-R2 rate is measured by hand.
- R3, censored. Still open at the end of the window.

The model predicts the hazard of R1. R2 is a competing event. Dropping R2 rows would
inflate the R1 estimate on exactly the declining topics.

### 2.3 Rollup: two axes, not one score

For items whose window has passed, the outcome is known. Averaging model predictions over
them replaces data with a smoothed function of the features. A survival estimator uses
known outcomes where they exist and the model only for items still open.

A single "alive or dying" score also loses the distinction that matters to a
contributor. The rollup uses two axes:

- Demand: inflow of substantive issues on the topic (support questions excluded via
  the extracted `intent`), last 6 months against the 18 months before. Compared with
  Poisson rate intervals; refused when a window has too few issues.
- Supply: the R1 rate, and later the restricted mean time to R1 at 180 days (defined
  under censoring), with its trend.

| | Supply rising | Supply falling |
|---|---|---|
| **Demand rising** | Thriving | Gap: a contribution target |
| **Demand falling** | Maturing | Dying |

`torch/masked` is expected in the top-right cell: demand persists, resolution fell after
2022, and NestedTensor took the attention. A "dying topic" detector would say to avoid
the module; the two-axis view says it is where a contribution is most needed.

## 3. Unit of prediction

- Item: an issue or Hub discussion, observed weekly from creation until R1, R2 or
  censoring, for at most 26 weeks. The model works at this level.
- Topic: a `(repo, topic, T)` triple. Topics come from the profile: path prefixes on
  GitHub (`torch/masked`), synonym clusters on the Hub. The report speaks at this level.

Issues are assigned to topics by path mentions in title and body, paths touched by linked
PRs, and profile synonyms. Assignment errors propagate into everything downstream, so
precision and recall are measured on hand-labelled issues and printed with the rollup.
Below about 0.8 precision, the rollup refuses.

## 4. Model

Discrete-time competing-risks hazard with weekly periods. Each item becomes one row
per week at risk, with `exposure_days` (at most 7; the last week of a censored item is
clipped at `observation_end`). Two hazard models are trained on the same table, `h1_j`
for R1 and `h2_j` for R2 in week *j*, or one multinomial head with three outcomes.
Composing with `1 − Π(1 − h1_j)` alone would treat R2 as censoring.

Cumulative incidence of R1 by week *k*:

`CIF₁(k) = Σ_{j≤k} h1_j · Π_{i<j}(1 − h1_i − h2_i)`

This is what "probability resolved by week *k*" means in a report. Restricted mean time
and trend summaries derive from this curve, not from a Kaplan–Meier complement that
ignores R2.

`exposure_days` must reach the model as a log-exposure offset (`log(exposure_days / 7)`
via LightGBM `init_score`) or as a row weight of `exposure_days / 7`. Treating a clipped
week as a full one biases the hazard down, most of all on the newest items.
`to_training_row()` in `predict/person_period.py` produces training rows.

Reasons for this shape:

- One model answers "resolved within X days" for any X.
- It handles censoring, and the newest, most relevant items are always censored.
- It is a binary classifier on an expanded table: LightGBM works directly, there is no
  `lifelines` dependency, and trees can be exported to a pure-Python scorer.

Size: about 40,000 issues × 8 weeks mean survival ≈ 320,000 rows.

Baselines, on the same folds:

1. Base rate per repository.
2. The vital-signs decision rule with an explicit threshold.
3. Discrete-time logistic regression on blocks 1–4 only, without LLM features.

Baseline 3 decides whether LLM extraction is worth its cost. A null result there is a
valid outcome.

Metrics. Time-dependent and integrated Brier score, calibration slope at 30, 90 and
180 days, and a reliability diagram per fold. C-index only measures ranking and does not
decide anything. A number printed next to citations has to be calibrated.

## 5. Features and leakage

Each feature is listed with how it is reconstructed as of time *T* and what could leak
into it. For item-level features the GitHub REST API is already point-in-time: the
timeline endpoint (`/issues/{n}/timeline`) and the reactions list both give a
`created_at` per event (checked 2026-08-24), so filtering by `created_at <= T`
reconstructs a thread at *T* without GH Archive. GH Archive would still be needed for
repository history and author priors, and is out of scope for v1.

### Block 1: item, at creation

| Feature | Reconstruction at *T* | Leakage risk |
|---|---|---|
| `age_days` | `T - created_at` | none |
| `body_len`, `title_len` | body at creation | edits are not versioned in the API; accepted |
| `has_code_block`, `has_traceback`, `has_version_info` | regex on body | same |
| `is_pull_request` | issue object | none |
| `n_linked_refs` | timeline `cross-referenced` events ≤ *T* | current references leak; use the timeline |

### Block 2: author, as of *T*

| Feature | Reconstruction at *T* | Leakage risk |
|---|---|---|
| `author_prior_issues` | search `author:X created:<T` | rate limits; cache per author and quarter |
| `author_prior_merged_prs` | same, `is:pr is:merged` | same |
| `author_is_maintainer_at_T` | CODEOWNERS at the commit that was HEAD at *T* | CODEOWNERS from today's `main` leaks |
| `author_is_bot` | login suffix and a curated list | pin the list version |
| `author_account_age` | user `created_at` | none |

### Block 3: engagement up to *T*

| Feature | Reconstruction at *T* | Leakage risk |
|---|---|---|
| `n_comments_le_T` | timeline `commented` events ≤ *T* | the issue's `comments` count is current state |
| `n_participants_le_T` | distinct actors in the timeline ≤ *T* | same |
| `maintainer_replied_le_T` | participants ∩ `MaintainerSet(logins, as_of)` with `as_of <= T` | leaks if either side is read as of now; code does not accept a bare `set[str]` |
| `hours_to_first_maintainer_reply` | first such event | missing if none, not 0 |
| `reactions_{+1,heart,eyes,-1}_le_T` | reactions list, `created_at <= T` | the `reactions` summary is current state |
| `label_set_at_T` | replay `labeled` and `unlabeled` events | current labels are the easiest leak to make |

### Block 4: topic at *T*

| Feature | Reconstruction at *T* | Leakage risk |
|---|---|---|
| `commits_topic_3m/6m/12m` | `git log --before=T -- <paths>` on a local clone | use `log1p`; raw counts saturated v0 |
| `distinct_committers_12m` | same | none |
| `top_committer_active_6m` | same | none |
| `open_backlog_size_at_T` | replay open and close events | today's open count leaks |
| `median_backlog_age_at_T` | same | same |
| `inflow_recent / inflow_baseline` | issue `created_at` before *T*, 6 and 18 months | none; this is the demand axis |
| `realized_R1_rate_prior` | outcomes of items closed before *T* | the window must not cross *T* |
| `has_codeowners_at_T` | blob at HEAD as of *T* | as in block 2 |
| `topic_in_release_notes_6m` | releases with `published_at < T` | none |

The old `closure_rate` is removed. It divided two result sets each capped at 30 items, so
it was 0.5 on any repository with more than 30 of each. `realized_R1_rate_prior`
replaces it.

### Block 5: displacement

The part of this design not covered by repository-level prior work.

| Feature | Reconstruction at *T* | Leakage risk |
|---|---|---|
| `adjacent_commit_trend` | same git log on adjacent paths from the profile | pin the profile's `adjacent_projects` per snapshot |
| `displacement_score` | adjacent rising × own falling | none |
| `inflow_ratio_self_vs_adjacent` | issue histograms | none |
| `names_alternative_rate` | block 6 field, aggregated over the topic | depends on the extractor |

### Block 6: LLM-extracted, from the thread up to *T*

Schema-constrained, temperature 0, one JSON object per item. Every field is ordinal or
categorical; no free text reaches the model.

| Field | Type | Note |
|---|---|---|
| `intent` | bug / feature_request / support / docs / design_proposal / integration_report / other | Excludes support questions from inflow |
| `specificity` | 0–3 | From vague to a reproducer with expected and actual output |
| `proposed_solution_present` | bool | |
| `patch_offered` | bool | Usually a strong positive |
| `blocking_severity` | 0–3 | From curiosity to blocking production |
| `affect` | 0–2 | Expected to rank low |
| `maintainer_stance` | none / acknowledged / planned / deferred / declined / needs_info | From maintainer comments ≤ *T* only |
| `scope` | one_line_fix / contained / cross_cutting / requires_design | |
| `names_alternative` | bool and string | Feeds block 5 |
| `evidence_span` | quote of at most 15 words | Quotable fields only |
| `evidence_anchor` | cell from a closed rubric | Judged fields: `specificity`, `blocking_severity`, `affect`, `scope` |

Rules:

- Input is the thread as of *T*: body plus comments with `created_at <= T`. Feeding
  today's thread leaks the outcome; a comment saying "fixed in #4471" predicts R1
  perfectly. The pilots so far used title and body from the gold files, which have no
  comments, so `maintainer_stance` is nearly always empty until comments are
  reconstructed.
- `extractor_version` is stored on every row (§2.1). Current schema: `block6-v3`
  (2026-08-31). Do not resume a v2 file with the v3 runner and treat it as one study.
- Issues and Hub questions only. A PR already carries a patch, so `patch_offered` and
  `proposed_solution_present` are true by construction, and `blocking_severity` rates
  the defect being fixed (#137890 is an example). PRs in the gold files stay for the
  assignment evaluation and do not enter block 6. `extract_run --kinds` defaults to
  `issue,hub`, and `--stratify` samples across source and kind.
- Extract once per item and quarter, not per weekly row. Threads change little
  between comments, and weekly extraction would cost eight times as much.
- Quotes only for presence. A positive value on a quotable field (`intent`,
  `proposed_solution_present=true`, `patch_offered=true`, a `maintainer_stance` other
  than none, `names_alternative=true`) needs a quote of at most 15 words. Absence needs
  none. Judged fields need a rubric cell from the list in `predict/extractor.py`. v2
  required a quote for every non-null field, which emptied the ordinals; requiring quotes
  for `false` (fixed 2026-09-02) did the same to booleans.
- Measure extractor agreement before using the fields. Re-run extraction with a
  second model and report Krippendorff's α for ordinals and Cohen's κ for categoricals.
  Fields below α ≈ 0.6 are dropped. Planned at n = 200; measured so far on 19 pairs
  (gpt-oss against Gemma, `agreement_2026-09-01_gpt_oss_x_gemma_v3.json`): `intent`
  κ 0.77 (n=17), `specificity` α 0.81 (n=19), `blocking_severity` α 0.95 (n=18), `scope`
  κ 0.19 (n=17). `affect` agrees on 18 of 19 rows but α is 0 because it is nearly always
  0. `maintainer_stance` has n=1.

Extraction was frozen on 2026-09-03 at the 112-row pilot: `affect` is constant and the
ordinals are nearly binary. The 200-item agreement run and comment reconstruction are
on hold until `scope` is kept or dropped. Details: [eval/extraction/](../eval/extraction/README.md).

Cost: about 40,000 items × 1,500 tokens in and 300 out, extracted once. On a small
hosted model that is tens of dollars.

## 6. Evaluation

- Walk-forward with an expanding window, 4–6 folds. A single split gives one number
  and no variance, and drift matters more than the pooled score.
- Purge one horizon. Test snapshots start at least 180 days after the last training
  snapshot, so training labels have resolved before test features are drawn.
- Two headline numbers. Temporal split only (scoring a module seen in training, the
  usual use) and temporal plus grouped by repository (a module never seen). They answer
  different questions; report both.
- Metrics against R1. Brier score and calibration are computed against the
  cumulative incidence of R1, not against closed or open. Scoring against "closed" would
  reward the confusion §2.2 removes.
- Extractor swap. Repeat the block-6 ablation with the second extractor's features. A
  gain that appears with one extractor only is not a result.

## 7. Refusal rules

The rollup is descriptive: realized inflow and R1 rates. The score is predictive:
cumulative incidence over about 180 days. The score inherits every rollup refusal.

### Rollup

| Condition | Action |
|---|---|
| Any retrieval error in its inputs | Refuse; a failed fetch is not absence of evidence |
| No path (`--path` missing) | Refuse |
| Assignment precision not measured for the profile | Refuse |
| Number of resolved items unknown | Refuse |
| Fewer than 12 resolved items on the topic | Refuse |
| Topic first appeared less than 12 months before *T* | Refuse; `torch/masked` did not exist before November 2022 |
| Hub items present and no issues | Refuse; Hub items are inference-only in v1 |
| Inflow rates unknown | Refuse; no demand axis |
| R1 rates unknown | Refuse; no supply axis |
| Demand and supply both flat | Refuse; no trajectory to report |

### Score

| Condition | Action |
|---|---|
| Any rollup refusal | Refuse |
| No trained model shipped | Refuse (current state) |
| `extractor_version` differs from the trained model's | Refuse block 6 and the score |
| Observation window shorter than twice the horizon (360 days for 180), or unknown | Refuse |

Apertus is refused on several of these: seven threads on 1.5, no path, no elapsed
window. The report prints both reasons. The refusal follows from the rules rather than
from a judgement call.

## 8. Packaging

Tree models are dumped to text and evaluated in about 60 lines of pure Python. The core
install does not depend on `lightgbm`, `onnxruntime` or NumPy. Training code lives in a
separate repository that is not part of the wheel. Model files ship as release assets,
cached under `~/.cache/consta/models/`, with the version pinned in the profile YAML so
that a stale model is as visible as a stale profile.

LLM extraction at report time would cost a call per item and require a key. Blocks 1–4
are therefore the default model, and block 6 is opt-in behind `--extract`. A run
without any key matters more than a few points of Brier score.

## 9. Scope for v1

v1 is `topic-hazard-v1`. Building it meant deferring the GitHub Action.

In scope:

- One corpus of 30–50 large Python repositories with real module structure.
- Point-in-time reconstruction from the REST API only (timeline and reactions
  endpoints). No GH Archive, which is the largest saving.
- Blocks 1–4 in full; block 5 reduced to git-log trends (no LLM-derived alternative
  mentions); block 6 on a subsample, for the ablation.
- Discrete-time weekly hazard, 26-week cap, R1, R2 and censored.
- Walk-forward, 4 purged folds, both headline numbers.
- The refusal rules, including the Apertus case.

Out of scope:

- GH Archive.
- Full author priors. Block 2 is best effort because of rate limits.
- Hub items in training. Hub discussions are scored at inference only, and the report
  must say the model was not trained on them.
- Models of 70B parameters or more, and neural sequence models.

Kill criterion, set in advance. If the model does not beat the vital-signs baseline
on Brier score at 90 days with folds grouped by repository, ship the deterministic
scorecard and state that the model did not beat it.

Claims Consta must not make:

- That it predicts whether a feature will survive. It is a resolution-hazard forecast for
  a topic, over 180 days, with an interval.
- That prediction itself is new. Repository-level abandonment prediction is published
  and has production tools. What is new is module and topic level, competing risks and
  displacement; see [MSR_ISSUE_RESOLUTION.md](MSR_ISSUE_RESOLUTION.md).
- That it ran on Apertus. It refuses on Apertus and says why.
- Any number without its interval and refusal rule next to it.

## 10. Open questions

- Does issue-to-topic assignment reach usable precision on `torch/masked`? Measured: 0.91
  on 95 items, recall not yet measured. If recall is low, v1 stays a per-issue tool and
  the rollup waits.
- Issue body edits cannot be retrieved per version through the API. How much does that
  affect block 1, and is it worth measuring on a sample?
- Keep `affect` for the ablation although it is expected to rank low, or drop it and
  simplify the schema?
- Prior work on issue resolution time is summarised in
  [MSR_ISSUE_RESOLUTION.md](MSR_ISSUE_RESOLUTION.md); a fuller survey is still to do.
