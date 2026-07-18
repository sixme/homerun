#!/usr/bin/env bash
# List shadow traders via API.
set -euo pipefail
API="${HOMERUN_API:-http://127.0.0.1:8000}"

curl -fsS "$API/api/traders?mode=shadow" | python3 -c '
import json, sys
d = json.load(sys.stdin)
traders = d.get("traders") if isinstance(d, dict) else d
if isinstance(d, dict) and "data" in d and "traders" not in d:
    traders = (d.get("data") or {}).get("traders")
traders = traders or []
print(f"{len(traders)} shadow bot(s)")
print(f"{'name':40s} {'mode':6s} {'en':3s} {'paused':6s} strategy")
for t in sorted(traders, key=lambda x: str(x.get('name') or '')):
    cfgs = t.get("source_configs") or []
    sk = ""
    if cfgs:
        sk = f"{cfgs[0].get('source_key')}/{cfgs[0].get('strategy_key')}"
    print(f"{str(t.get('name'))[:40]:40s} {str(t.get('mode')):6s} {str(bool(t.get('is_enabled'))):3s} {str(bool(t.get('is_paused'))):6s} {sk}")
'
