# Consta

Evidence-first briefs for OSS contribution decisions. Given a question and a target repository, Consta retrieves cited evidence (issues, commits, docs, adjacent projects) and optionally synthesizes a short summary. Humans keep the final call.

```bash
pip install consta
uvx consta assess -q "…" -r pytorch/pytorch -p torch/masked --no-synthesis
```

*Consta* is Latin, Italian and Spanish for "it is on record, it stands as fact". The tool reports what the evidence establishes and leaves the verdict to you.

**Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)

Product backlog and delivery dates live in the private Arraxis planning workspace, not in this tree.

## Install (dev)

```bash
pip install -e ".[dev]"      # CLI + tests
pip install -e ".[dev,web]"  # + Flask UI (consta-web)
```

## Configure

Copy the template and fill in secrets (never commit `.env`):

```bash
cp .env.example .env
```

| Variable | Required | Purpose |
|----------|----------|---------|
| `CONSTA_GITHUB_TOKEN` | Yes (live runs) | Fine-grained PAT or classic `public_repo` |
| `CONSTA_LLM_PROVIDER` | Optional | `huggingface`, `openai` or `anthropic` (code default: `anthropic`; `.env.example` sets `huggingface`) |
| `CONSTA_HF_TOKEN` | Optional | Synthesis via the Hugging Face router; also used for gated Hub discussions |
| `CONSTA_OPENAI_API_KEY` | Optional | Synthesis via OpenAI |
| `CONSTA_ANTHROPIC_API_KEY` | Optional | Synthesis via Anthropic |
| `CONSTA_LLM_MODEL` | Optional | Override the provider's default model |

## Web UI

```bash
pip install -e ".[web]"
consta-web
# http://127.0.0.1:5050 — form, sample cases, cited report (Bootstrap)
```

**Not sure what to try?** Pick a card on the home page — six scenarios across `pytorch`, `numpy`, and `sklearn` ([`eval/sample_cases.yaml`](eval/sample_cases.yaml)).

See [docs/WEB_UI.md](docs/WEB_UI.md) and [docs/STATUS.md](docs/STATUS.md).

## Commands

```bash
consta ping
consta list-profiles

consta assess \
  --question "Is reviving torch.masked worth an upstream contribution?" \
  --repo pytorch/pytorch \
  --path torch/masked \
  --ecosystem pytorch \
  --tier 2 \
  --output report.md
```

Flags: `--no-synthesis`, `--json`, `--allow-stale-profile`.

## Test (mandatory before claiming done)

```bash
./scripts/verify.sh
```

See [docs/VERIFICATION.md](docs/VERIFICATION.md).

```bash
pytest -v
CONSTA_RUN_LIVE=1 pytest tests/test_live.py -v
consta ping
```

## Ecosystem profiles

| Profile | Repo | Use case |
|---------|------|----------|
| `pytorch` | `pytorch/pytorch` | `torch.masked`, `torch.nested`, … |
| `numpy` | `numpy/numpy` | `numpy.ma`, NEPs, missing-data semantics |
| `sklearn` | `scikit-learn/scikit-learn` | SLEPs, metadata routing, estimator API |

```bash
consta list-profiles
./scripts/run_sample_assessments.sh   # needs .env
python scripts/validate_reports.py
```

## GitHub Action

[`action/action.yml`](action/action.yml) posts a sticky evidence comment on issues:

```yaml
on:
  issues:
    types: [opened]
permissions:
  issues: write
jobs:
  brief:
    runs-on: ubuntu-latest
    steps:
      - uses: sulimovp/consta/action@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          ecosystem: pytorch
```

## License

Apache-2.0. No CLA.

