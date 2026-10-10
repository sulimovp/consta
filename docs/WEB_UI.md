# Web UI

A Flask app that runs the same engine as the CLI.

```bash
pip install -e ".[web]"
consta-web    # http://127.0.0.1:5050
```

Python changes need a server restart.

## Pages

| Path | Method | Purpose |
|------|--------|---------|
| `/` | GET | Form and preset cards; `?preset=<id>` fills the form |
| `/assess` | POST | Start a background job and redirect to its status page |
| `/assess/status/<id>` | GET | Refreshes every 3 seconds until the report is ready |
| `/health` | GET | GitHub and LLM connectivity |

A run takes 30–90 seconds. The report page shows the summary, open questions, the
evidence by kind, and a Markdown download.

## Presets

The home page cards come from [eval/sample_cases.yaml](../eval/sample_cases.yaml), read
on each request. To add or change a preset, edit that file.

| Preset | Repository | Notes |
|--------|------------|-------|
| PyTorch — torch.masked | `pytorch/pytorch` | Tier 2, summary on |
| PyTorch — torch.nested | `pytorch/pytorch` | Compare with `torch.masked` |
| NumPy — numpy.ma | `numpy/numpy` | Summary off |
| NumPy — numpy.ma (strategy) | `numpy/numpy` | Tier 1, fastest |
| scikit-learn — metadata routing | `scikit-learn/scikit-learn` | SLEP006 |
| scikit-learn — generic feature | `scikit-learn/scikit-learn` | Template question |

## Settings

| Variable | Default | Purpose |
|----------|---------|---------|
| `CONSTA_WEB_HOST` | `127.0.0.1` | Bind address |
| `CONSTA_WEB_PORT` | `5050` | Port |
| `CONSTA_FLASK_SECRET` | development value | Session secret; set it in production |
| `CONSTA_WEB_DEBUG` | off | Flask debug mode; never on a public host |

Deployment: [DEPLOY.md](DEPLOY.md).

## Not built

- Comparing two reports side by side
- Editing profiles in the browser
- Shareable report links
- A job store shared between workers
