# Consta

Consta collects evidence for a question about contributing to an open-source project:
issues, merged PRs, commit activity on a module, docs, and alternative projects. It
writes a report with a link for every item and, optionally, a short LLM summary in which
every claim quotes its source.

The name is Spanish and Italian for "it is on record".

```bash
pip install consta
consta assess -q "Is reviving torch.masked worth an upstream contribution?" \
  -r pytorch/pytorch -p torch/masked -e pytorch --no-synthesis
```

[examples/](examples/README.md) has two real reports and explains how a report is built.
[ARCHITECTURE.md](ARCHITECTURE.md) describes the code.

## Install

```bash
pip install consta              # CLI
pip install "consta[web]"       # CLI and web UI
pip install -e ".[dev,web]"     # from a checkout, with test dependencies
```

## Configure

```bash
cp .env.example .env
```

Consta reads `./.env` and `~/.config/consta/.env`.

| Variable | Required | Purpose |
|----------|----------|---------|
| `CONSTA_GITHUB_TOKEN` | Yes | GitHub token (fine-grained, or classic with `public_repo`) |
| `CONSTA_LLM_PROVIDER` | No | `anthropic` (default), `openai`, `openrouter` or `huggingface` |
| `CONSTA_ANTHROPIC_API_KEY` | No | Key for `anthropic` |
| `CONSTA_OPENAI_API_KEY` | No | Key for `openai` |
| `CONSTA_OPENROUTER_API_KEY` | No | Key for `openrouter` |
| `CONSTA_HF_TOKEN` | No | Key for `huggingface`; also used to read gated Hugging Face Hub discussions |
| `CONSTA_LLM_MODEL` | No | Model id, if not the provider's default |

Without an LLM key the report has no summary; everything else works.

## Usage

```bash
consta ping            # check GitHub and LLM access
consta list-profiles

consta assess \
  --question "Is reviving torch.masked worth an upstream contribution?" \
  --repo pytorch/pytorch \
  --path torch/masked \
  --ecosystem pytorch \
  --tier 2 \
  --output report.md
```

| Option | Effect |
|--------|--------|
| `--path` | Scope commit activity and issue counts to one directory |
| `--ecosystem` | Use a profile from `profiles/` (synonyms, labels, alternative projects) |
| `--tier 2` | Add merged PRs and forum threads |
| `--no-synthesis` | Skip the LLM summary |
| `--json` | Print the report as JSON |
| `--allow-stale-profile` | Use a profile older than its `max_age_days` |

### Web UI

```bash
consta-web    # http://127.0.0.1:5050
```

The home page offers six preset questions from [eval/sample_cases.yaml](eval/sample_cases.yaml).
See [docs/WEB_UI.md](docs/WEB_UI.md).

## Profiles

A profile is a YAML file with hints for one ecosystem. Without one, Consta works from
the question and path alone.

| Profile | Source | Covers |
|---------|--------|--------|
| `pytorch` | `pytorch/pytorch` | `torch.masked`, `torch.nested` |
| `numpy` | `numpy/numpy` | `numpy.ma`, NEPs, missing data |
| `sklearn` | `scikit-learn/scikit-learn` | SLEPs, metadata routing |
| `apertus` | `swiss-ai/apertus-format`, Hugging Face Hub | Model repo discussions |

To add one, copy [profiles/_template.yaml](profiles/_template.yaml).

## GitHub Action

[action/action.yml](action/action.yml) runs Consta on new issues and posts the report as
a comment. It skips the LLM summary unless you set `synthesize: "true"`.

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

## Development

```bash
./scripts/verify.sh                           # tests; must pass before merging
CONSTA_RUN_LIVE=1 pytest tests/test_live.py   # against the real GitHub API
./scripts/run_sample_assessments.sh           # regenerate reports/ (needs .env)
```

See [docs/VERIFICATION.md](docs/VERIFICATION.md) and [docs/STATUS.md](docs/STATUS.md).

## License

Apache-2.0. No CLA.
