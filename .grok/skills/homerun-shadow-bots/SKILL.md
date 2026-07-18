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
      "max_orders_per_cycle": 6,
      "max_open_orders": 20,
      "max_open_positions": 12,
      "max_trade_notional_usd": 10,
      "max_position_notional_usd": 50,
      "max_gross_exposure_usd": 500,
      "max_daily_loss_usd": 150,
      "max_daily_spend_usd": 500,
      "max_spread_bps": 150,
      "slippage_bps": 50,
      "max_entry_drift_pct": 15,
      "max_consecutive_losses": 5,
      "order_ttl_seconds": 1200
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

## Risk limits (paper defaults)

Sizing uses `base_size = max(1, 0.4 × max_trade_notional_usd)`.  
With `max_trade=2`, base is **$1** → often blocked by **min-exit-notional** (needs ~$1.06 with a 6% stop, ~$2 with the 0.5 exit-price floor).

Default shadow profile (apply to all paper bots unless the user wants tighter):

| Field | Paper default | Why |
|-------|---------------|-----|
| `max_trade_notional_usd` | **10** | base size ~$4 clears min-exit |
| `max_position_notional_usd` | **50** | multi-clip room |
| `max_gross_exposure_usd` | **500** | concurrent positions |
| `max_open_positions` | **12** | platform default |
| `max_open_orders` | **20** | platform default |
| `max_orders_per_cycle` | **6** | platform default |
| `max_daily_loss_usd` | **150** | not trip on noise |
| `max_daily_spend_usd` | **500** | explore without daily hard-stop |
| `max_spread_bps` | **150** | weather / illiquid markets |
| `slippage_bps` | **50** | slightly looser than live |
| `max_entry_drift_pct` | **15** | more fill opportunity |
| `max_consecutive_losses` | **5** | fewer false halts |

Do **not** reintroduce the old ultra-tight skill template (`trade=2 / gross=25 / positions=3`).

## Interpreting decisions

| Message | Meaning |
|---------|---------|
| SKIPPED + gate reason (spread, edge, …) | Healthy filter |
| BLOCKED + Min-exit-notional | Size too small vs $1 exit floor — raise `max_trade_notional_usd` |
| FAILED + DetachedInstanceError | Bug (payload materialize); restart trading plane |
| FAST_SUBMIT_NO_ORDER after SKIPPED | Expected — no order written |
| Missing Polymarket credentials | Live only; shadow OK without keys |

## Prefer MCP when available

If `homerun` MCP is connected, use trader/orchestrator tools instead of raw curl when they exist.
