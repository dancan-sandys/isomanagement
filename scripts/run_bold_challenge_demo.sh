#!/usr/bin/env bash
set -euo pipefail

if [ -z "${PYTHONPATH:-}" ]; then
  export PYTHONPATH="$(cd "$(dirname "$0")"/.. && pwd)/backend"
fi

python3 backend/seed_htst_bold_demo.py | tee /tmp/demo_run.log

PROC_ID=$(grep -oE '\{"batch_id".*\}' /tmp/demo_run.log | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("process_id"))' || true)
if [ -z "$PROC_ID" ]; then
  echo "Could not detect process_id from output. Check /tmp/demo_run.log" >&2
  exit 0
fi

BASE=${BASE_URL:-http://localhost:8000/api/v1}

echo
echo "Verify transitions:" 
echo "curl -s $BASE/production/processes/$PROC_ID/transitions | jq . | head -200"

echo "Verify simple audit (diverts):"
echo "curl -s $BASE/production/processes/$PROC_ID/audit-simple | jq . | head -200"