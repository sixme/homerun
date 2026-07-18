#!/usr/bin/env bash
# Quick Homerun health for Grok CLI sessions.
set -euo pipefail
API="${HOMERUN_API:-http://127.0.0.1:8000}"

echo "== API health =="
if curl -fsS "$API/health/live"; then
  echo
else
  echo "API not reachable at $API"
  exit 1
fi

echo
echo "== MCP mount (expect non-404) =="
code=$(curl -sS -o /dev/null -w '%{http_code}' "$API/mcp" || true)
echo "GET $API/mcp -> HTTP $code"

echo
echo "== Worker host processes =="
ps -ax -o command= | awk '/workers\.host/ && $0 !~ /awk/ {print}' || true

echo
echo "== Sandbox accounts =="
curl -fsS "$API/api/simulation/accounts" | python3 -m json.tool 2>/dev/null | head -40 || true

echo
echo "== Orchestrator (summary) =="
curl -fsS "$API/api/trader-orchestrator/overview" | python3 -c '
import json,sys
d=json.load(sys.stdin)
if "control" not in d and isinstance(d.get("data"), dict):
    d=d["data"]
c=d.get("control") or {}
r=d.get("runtime_state") or {}
print("mode", c.get("mode"), "enabled", c.get("is_enabled"), "paused", c.get("is_paused"), "kill", c.get("kill_switch"))
print("label", r.get("label"), "state", r.get("state"))
s=c.get("settings") or {}
print("account", s.get("selected_account_id") or s.get("shadow_account_id"))
' 2>/dev/null || true
