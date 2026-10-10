# Contributor notes

Code layout: `ARCHITECTURE.md`. Status: `docs/STATUS.md`.

```bash
pip install -e ".[dev,web]"
./scripts/verify.sh
consta ping
consta-web
```

- `./scripts/verify.sh` must exit 0 before work is reported as done.
- UI or report layout changes: follow `docs/VERIFICATION.md`.
- Keys live in `.env`, which is not committed.
- Every claim in a summary needs a citation with a quote from the cited item.
- Ecosystem-specific knowledge goes in `profiles/*.yaml`, not in engine code.
