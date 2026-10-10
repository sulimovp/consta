# Extraction pilots

Runs of `python -m consta.predict.extract_run`, which asks an LLM to fill a fixed set of
fields (`intent`, `specificity`, `blocking_severity`, `affect`, `scope`,
`maintainer_stance`) for each issue, PR or Hub discussion in the topic-assignment gold
files. No new items were fetched for these runs.

## Current state

Frozen on 2026-09-03 at schema `block6-v3`, run
`pilot_2026-09-02_block6_v3_demand_gpt_oss.jsonl` (112 rows: 50 PyTorch issues, 17 other
issues, 45 Hub discussions; no PRs).

Fill rates are high, but the distributions show that only about three columns carry
information:

| Field | Filled (of 109) | Distribution | Usable |
|-------|-----------------|--------------|--------|
| `intent` | not recorded | not recorded | Yes (κ 0.77 between models) |
| `specificity` | 96% | Nearly binary | Yes, as yes/no |
| `blocking_severity` | 94% | Nearly binary | Yes, as yes/no |
| `affect` | 96% | 0 on 102 of 105 non-null rows | No |
| `scope` | 92% | 66% `one_line_fix`; κ 0.19 between models | No |
| `maintainer_stance` | 7% | n/a | No: gold files hold only title and body |

3 of the 112 rows failed with router `json_validate_failed` errors after one retry.
6 rows have span failures (a quote that is not in the thread).

## Runs

| File | Schema | Model | Rows | Parse errors | Span failures |
|------|--------|-------|------|--------------|---------------|
| `pilot_2026-08-30.jsonl` | v1 | `openai/gpt-oss-120b:groq` | 176 | 0 | 90 (51%) |
| `pilot_2026-08-31_block6_v2_gpt_oss.jsonl` | v2 | `openai/gpt-oss-120b:groq` | 176 | 0 | 7 (4.0%) |
| `smoke_block6_v2_gpt_oss.jsonl` | v2 | `openai/gpt-oss-120b:groq` | 10 | 0 | 0 |
| `smoke_block6_v2_gemma.jsonl` | v2 | `google/gemma-4-31B-it:cerebras` | 20 | 0 | 2 |
| `smoke_block6_v2_qwen.jsonl` | v2 | `Qwen/Qwen3-14B:nscale` | 20 | 3 | 1 |
| `smoke_block6_v3_gpt_oss.jsonl` | v3 | `openai/gpt-oss-120b:groq` | 10 | 0 | 1 |
| `smoke_block6_v3_demand_gpt_oss.jsonl` | v3 | `openai/gpt-oss-120b:groq` | 20 | 0 | 1 |
| `secondary_block6_v3_gemma.jsonl` | v3 | `google/gemma-4-31B-it:cerebras` | 20 | 0 | 0 |
| `pilot_2026-09-02_block6_v3_demand_gpt_oss.jsonl` | v3 | `openai/gpt-oss-120b:groq` | 112 | 3 | 6 |

Notes on individual runs:

- v2's low span-failure rate is misleading. On the 176-row v2 file,
  `blocking_severity` is filled on 6.2% of rows and `affect` on 3.4%. v3 fills them.
- `smoke_block6_v3_gpt_oss.jsonl` is `--limit 10` over `pytorch_holdout.yaml`, whose
  first 45 entries are PRs. It shows that the rubric fills on PRs, not that it
  discriminates. `affect` is 0 on all nine filled rows.
- `smoke_block6_v3_demand_gpt_oss.jsonl` is `--stratify 20 --seed 0 --kinds issue,hub`:
  6 PyTorch issues, 7 other issues, 7 Hub discussions. `maintainer_stance` is filled on
  1 of 20. One row still fails its span check (`pytorch#39639`: the `intent` quote is
  not in the thread).
- Agreement, gpt-oss against Gemma on that draw
  (`agreement_2026-09-01_gpt_oss_x_gemma_v3.json`, 19 valid pairs): `intent` κ 0.77
  (n=17), `specificity` α 0.81 (n=19), `blocking_severity` α 0.95 (n=18), `scope` κ 0.19
  (n=17). `affect` agrees on 18 of 19 rows, but α is 0 because the value is almost always 0.
  `n` is the number of pairs where both runs filled the field; read it first.
- `agreement_2026-08-31_gpt_oss_x_gemma.json` and `..._x_qwen.json` are the same
  comparison on the 20-item v2 overlaps.

Rows of different schema versions do not match each other's `extractor_version`. Do not
resume a v2 file with the v3 runner and treat the result as one study.

The gpt-oss runs use
`openai/gpt-oss-120b:groq@b5c939de8f754692c1647ca79fbf85e8c1e70f8a`
([docs/hf_snapshot/](../../docs/hf_snapshot/README.md)).

## Runner behaviour

- `--kinds` defaults to `issue,hub`. The demand-side fields are not defined for PRs.
- `--limit N` over the PyTorch holdout returns only PRs for N ≤ 45; use `--stratify`.
- `--stratify K --seed S` draws evenly from each source×kind cell.
- A batch stops on HTTP 401 or 402 (checked by status code). A run that hit 402 is not a
  valid sample; start a new output file rather than resuming it.
- On resume, rows without `repair_attempts` count as incomplete, parse and transport
  failures are retried, and rows that failed only the span check are kept. New rows are
  appended and the file is compacted: current draw first, then other existing rows.
- `--revalidate` recomputes span errors from stored fields without calling the LLM.

## Commands

Calls to the extractor cost inference credit; the agreement step does not.

```bash
set -a; . ./.env; set +a

# Demand-side smoke (20 items)
python -m consta.predict.extract_run \
  -i eval/topic_assignment/pytorch_holdout.yaml eval/topic_assignment/apertus.yaml \
  -o eval/extraction/smoke_block6_v3_demand_gpt_oss.jsonl \
  --stratify 20 --seed 0 --kinds issue,hub

# All 112 issue and Hub rows (seed from the smoke file to skip repeated calls)
python -m consta.predict.extract_run \
  -i eval/topic_assignment/pytorch_holdout.yaml eval/topic_assignment/apertus.yaml \
  -o eval/extraction/pilot_2026-09-02_block6_v3_demand_gpt_oss.jsonl \
  --kinds issue,hub

# Second model, for agreement
python -m consta.predict.extract_run \
  -i eval/topic_assignment/pytorch_holdout.yaml eval/topic_assignment/apertus.yaml \
  -o eval/extraction/secondary_block6_v3_gemma.jsonl \
  --router-model google/gemma-4-31B-it:cerebras \
  --extractor-model google/gemma-4-31B-it:cerebras@842da3794eaa0b77d5f08bae87a17459d91ff475 \
  --stratify 20 --seed 0 --kinds issue,hub

# Agreement (no network)
python -m consta.predict.agreement \
  --primary eval/extraction/smoke_block6_v3_demand_gpt_oss.jsonl \
  --secondary eval/extraction/secondary_block6_v3_gemma.jsonl \
  --output eval/extraction/agreement_2026-09-01_gpt_oss_x_gemma_v3.json
```
