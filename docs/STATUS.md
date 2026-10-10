# Status (October 2026)

## Working

| Area | State |
|------|-------|
| CLI | `assess`, `ping`, `list-profiles`; options `--path`, `--ecosystem`, `--tier`, `--no-synthesis`, `--json` |
| Retrieval | GitHub issues, merged PRs, commits, files; vital signs per path; alternative projects (each URL fetched); Discourse threads (pinned and search); Hugging Face Hub discussions |
| Validation | Off-topic issues and PRs excluded with a reason; every evidence kind represented in the first 25 items |
| Summary | Anthropic, OpenAI, OpenRouter or Hugging Face router. Citation check on every `[n]`, every paragraph and every quote; one retry; otherwise the summary is withheld |
| Profiles | `pytorch`, `numpy`, `sklearn`, `apertus`. Last checked 2026-08-30; they expire after 90 days |
| Web UI | Flask on port 5050, background jobs, six presets |
| GitHub Action | [action/action.yml](../action/action.yml): comment on new issues, no summary by default |
| Tests | `./scripts/verify.sh` locally and in CI; live test with `CONSTA_RUN_LIVE=1` |

## Experimental

### Topic forecast

Code in `consta/predict/`. The report's "Topic trajectory" section compares
recent and baseline issue inflow and resolution for the topic. It refuses unless its
inputs are measured well enough, and in current runs it usually refuses (for
`torch/masked`: resolution rates unknown). Issue-to-topic assignment has been measured
for two profiles:

| Profile | Sample | Precision | Recall |
|---------|--------|-----------|--------|
| `pytorch` | 95 | 0.91 | not measured |
| `apertus` | 81 | 0.88 | 0.64 (below 0.80, so the rollup is refused) |

The resolution-time score is always refused: no trained model is shipped. Design:
[PREDICT.md](PREDICT.md), [PREDICT_QUADRANT.md](PREDICT_QUADRANT.md).

### LLM feature extraction

Used by the forecast. Frozen at version 3 on 112 labelled rows.
About three fields are usable (`intent`, and `specificity` and `blocking_severity` as
yes/no); `affect` is constant and `scope` unreliable (κ 0.19). See
[eval/extraction/README.md](../eval/extraction/README.md).

## Open

- No interviews with maintainers yet to check that the reports help them.
- Evaluation is three held-out sample cases, not a measured set of questions.
- Linking issues to the PRs that fixed them is minimal.
- No local index; every run calls the GitHub API (search results are cached for an hour).
- The citation check confirms quotes, not the claims built on them.

## Sample cases

| Id | Repository | Purpose |
|----|------------|---------|
| `pytorch-masked` | `pytorch/pytorch` | Reference case with expected issue numbers |
| `pytorch-nested` | `pytorch/pytorch` | Compare with `torch.masked` |
| `numpy-ma` | `numpy/numpy` | `__array_function__` question |
| `numpy-ma-strategy` | `numpy/numpy` | Short question, tier 1 |
| `sklearn-routing` | `scikit-learn/scikit-learn` | SLEP006 metadata routing |
| `sklearn-generic` | `scikit-learn/scikit-learn` | Template question |

`./scripts/run_sample_assessments.sh` writes reports for four of them to `reports/`.
