#!/usr/bin/env bash
# Mandatory verification gate for consta changes.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== consta verify: pytest ==="
pytest -v "$@"

echo "=== consta verify: report contracts (if reports present) ==="
if compgen -G "reports/*.md" > /dev/null; then
  python scripts/validate_reports.py
else
  echo "SKIP validate_reports.py (no reports/*.md — run run_sample_assessments.sh for live samples)"
fi

echo "=== consta verify: OK ==="
