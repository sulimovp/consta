# Verification

## Before merging

```bash
./scripts/verify.sh
```

It runs `pytest` and, if `reports/*.md` exist, `scripts/validate_reports.py`, which checks
report format and expected content. CI runs the same script on every push and pull
request, then builds the wheel and checks that profiles and sample cases are inside it.

The live test is skipped unless enabled:

```bash
CONSTA_RUN_LIVE=1 pytest tests/test_live.py -v
./scripts/run_sample_assessments.sh   # writes reports/, needs .env
python scripts/validate_reports.py
```

## UI and report layout changes

For changes to `consta/web/`, its templates or `consta/render/markdown.py`, also check
the UI by hand:

1. Start `consta-web`; restart it after code changes.
2. Open http://127.0.0.1:5050. The home page shows the presets, the form and the
   connection status in the footer.
3. Open `/health`.
4. Run the "NumPy — numpy.ma (strategy)" preset (tier 1, no summary). The status page
   should lead to a report with the evidence sections.
5. Download the Markdown file.

## Checklist

- [ ] `./scripts/verify.sh` exits 0
- [ ] UI or report change: steps above done
- [ ] Change affects live retrieval: live test run, or the reason it was skipped noted
- [ ] No secrets committed
