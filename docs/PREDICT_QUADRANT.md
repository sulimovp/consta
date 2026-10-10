# Topic rollup: implementation notes

The "Topic trajectory" section of a report places a path-scoped topic on two axes:
demand (are new issues arriving faster or slower) and supply (are they being resolved
by merged changes more or less often). It is computed from past outcomes only; no model
is trained. The design is in [PREDICT.md](PREDICT.md) §§2.3, 3 and 7. This page records
how it is built.

| | Supply rising | Supply falling |
|---|---|---|
| **Demand rising** | Thriving | Gap: a contribution target |
| **Demand falling** | Maturing | Dying |

The resolution-time score next to it is always refused, because no trained model ships.

## Windows

Both axes use the same two windows, which do not overlap:

| Window | Range | Months |
|--------|-------|--------|
| Recent | last 180 days | 6 |
| Baseline | 730 to 180 days ago | 18 |

An earlier version compared 3 months with 12 months. The 12-month window contained the
3-month one, which pulled any surge towards a ratio of 1.

Trends are classified from Poisson intervals on inflow counts and Wilson intervals on
resolution rates, with at least 5 issues in the recent window and 8 in the baseline.
Callers that pass bare rates use thresholds of 1.25 and 0.8.

## Inputs (`consta/predict/topic_history.py`)

### Inflow

Two issue searches on the quoted path (`"torch/masked"`, so that it is not
split into separate words), one per window, reading `total_count`. GitHub caps
`total_count` at 1000. If either window reaches the cap, inflow is left unknown and the
rollup refuses, because a rate from a capped count would be wrong.

### Resolution rate

For each window, up to 50 closed issues on the path, sorted by
creation date rather than relevance. Each issue's timeline is read and its outcome
labelled:

- R1: closed with a linked merged PR that touched the topic's paths;
- R2: closed without one.

The rate is R1 / (R1 + R2).

To know whether a linked PR touched the path, its file list is fetched (at most 3 PRs per
issue). If that fetch failed and the issue were counted anyway, it would count as R2 and
look like falling maintainer capacity. Such issues are excluded from both numerator and
denominator instead. If more than 25% of a window's sample is excluded, the rate is left
unknown and the rollup refuses.

### Topic age

The date of the first commit on the path, read from the last page of the
commit list.

A failed fetch leaves its field unknown and adds a diagnostic. No input defaults to zero.

## Assignment precision

Counting issues "on a topic" depends on how accurately issues are assigned to it. Each
profile can record a hand-checked measurement, for example in `profiles/pytorch.yaml`:

```yaml
assignment_precision:
  measured_at: 2026-08-28
  n: 95
  precision: 0.91
```

The rollup refuses when there is no measurement, when it is older than the profile's
`max_age_days`, when precision is below 0.80, or when recall is recorded and below 0.80.
The refusal reason includes the measured numbers. Gold labels are in
`eval/topic_assignment/`; the scorer is `scripts/score_topic_assignment.py`.

## Output

Under the quadrant, the report prints the inputs so the result can be checked:

```text
Inflow 3.7/mo recent vs 1.9/mo baseline · R1 rate 0.31 (n=44, 6 excluded) vs 0.68 (n=50)
· assignment precision 0.91 (n=95, measured 2026-08-28)
```

## Cost

Per report with a path: 2 inflow searches, 2 closed-issue searches, up to 100 timelines,
up to 300 PR file lists and 2 commit-list calls. The PR file lists dominate. One report
fits in the 5,000 requests per hour of a GitHub token.
