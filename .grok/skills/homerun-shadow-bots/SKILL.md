---
name: homerun-shadow-bots
description: >
  Create, start, stop, and diagnose Homerun shadow trading bots and the
  trader orchestrator. Use for paper trading setup, Engine Stopped /
  MANAGE-ONLY / Bot Stopped status, sandbox accounts, and per-strategy bots.
when-to-use: |
  shadow bot, paper trading, create bots, orchestrator, engine stopped,
  manage-only, sandbox account, start bots
compatibility: Requires API on :8000 and Postgres; sandbox account recommended.
---

# Homerun shadow bots

## Mental model

```text
Select Account (global sandbox)  →  orchestrator start (mode=shadow)
One bot = one strategy           →  trader start/unpause
Kill switch OPEN                 →  entries allowed
```

- Account is **not** configured on each bot.
- `MANAGE-ONLY` = engine running, **no entry-eligible bots** (all paused/blocked).
- `Bot Stopped` = that trader is paused; click Start / API start.
- `Engine Stopped` = orchestrator not started.

## Sandbox account

List:

```bash
curl -fsS http://127.0.0.1:8000/api/simulation/accounts
```

Create:

```bash
curl -fsS -X POST http://127.0.0.1:8000/api/simulation/accounts \
  -H 'Content-Type: application/json' \
  -d '{"name":"Paper Trading","initial_capital":10000,"max_position_pct":10,"max_positions":10}'
```

Or use UI: **Accounts → New Sandbox**.

## Orchestrator (engine)

Kill switch off + start shadow:

```bash
ACCOUNT_ID='<sandbox-uuid>'

curl -fsS -X POST http://127.0.0.1:8000/api/trader-orchestrator/kill-switch \
  -H 'Content-Type: application/json' \
  -d '{"enabled":false,"requested_by":"grok"}'

curl -fsS -X POST http://127.0.0.1:8000/api/trader-orchestrator/start \
  -H 'Content-Type: application/json' \
  -d "{\"mode\":\"shadow\",\"selected_account_id\":\"$ACCOUNT_ID\",\"requested_by\":\"grok\"}"
```

Overview:

```bash
curl -fsS http://127.0.0.1:8000/api/trader-orchestrator/overview | python3 -m json.tool | head -80
```

## Create one bot per strategy

API enforces **exactly one** `source_configs` entry.

Naming convention used in this repo: `Shadow · {Strategy Name}`.

```bash
curl -fsS -X POST http://127.0.0.1:8000/api/traders \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Shadow · Basic Arbitrage",
    "mode": "shadow",
    "latency_class": "normal",
    "interval_seconds": 5,
    "is_enabled": true,
    "is_paused": false,
    "source_configs": [{
      "source_key": "scanner",
      "strategy_key": "basic",
      "strategy_params": {}
    }],
    "risk_limits": {
      "max_trade_notional_usd": 2,
      "max_position_notional_usd": 5,
      "max_gross_exposure_usd": 25,
      "max_open_positions": 3,
      "max_open_orders": 4,
      "max_daily_loss_usd": 15,
      "max_spread_bps": 75
    },
    "requested_by": "grok"
  }'
```

Start bot:

```bash
curl -fsS -X POST "http://127.0.0.1:8000/api/traders/<trader_id>/start" \
  -H 'Content-Type: application/json' \
  -d '{"requested_by":"grok"}'
```

Delete bot:

```bash
curl -fsS -X DELETE "http://127.0.0.1:8000/api/traders/<trader_id>?action=force_delete"
```

## Latency classes

| Source | Typical latency_class | interval_seconds |
|--------|----------------------|------------------|
| crypto | fast | 2 |
| scanner | normal | 5 |
| traders | normal | 10 |
| news | slow | 15 |
| weather | slow | 30 |

Crypto fast path lives in `workers/fast_trader_runtime.py`.

## Interpreting decisions

| Message | Meaning |
|---------|---------|
| SKIPPED + gate reason (spread, edge, …) | Healthy filter |
| FAILED + DetachedInstanceError | Bug (payload materialize); restart trading plane |
| FAST_SUBMIT_NO_ORDER after SKIPPED | Expected — no order written |
| Missing Polymarket credentials | Live only; shadow OK without keys |

## Prefer MCP when available

If `homerun` MCP is connected, use trader/orchestrator tools instead of raw curl when they exist.
