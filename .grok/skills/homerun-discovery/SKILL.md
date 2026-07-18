---
name: homerun-discovery
description: >
  Enable and diagnose Homerun wallet/trader discovery. Use when the Traders
  or Discovery UI is empty, copy-trade bots have no activity, or the user
  asks how trader scanning works.
when-to-use: |
  discovery empty, no traders, wallet scan, tracked wallets, copy trade,
  discovery plane, traders confluence
compatibility: Requires API and preferably full launcher with discovery plane.
---

# Homerun trader / wallet discovery

## Important distinction

| System | What it fills | Default |
|--------|---------------|---------|
| **Market scanner** (detection plane) | Opportunities / arb signals | ON |
| **Wallet discovery** (discovery plane) | People/wallets in Traders UI | **OFF** |

Empty Traders list with markets/signals working is **normal** until discovery is enabled.

## How it works

```text
Enable discovery subsystem
  → workers.host discovery plane
      • discovery_worker      (scan/rank wallets)
      • tracked_traders_worker (follow tracked set)
  → discovered_wallets / tracked_wallets tables
  → UI Traders / Discovery
  → optional bots: traders_copy_trade, traders_confluence
```

Code: `backend/workers/discovery_worker.py`, `backend/workers/host.py` plane `"discovery"`.  
Launcher default in `gui.py`: `"discovery": False`.

## Enable discovery

### Preferred: desktop GUI

In the Homerun control window / subsystem toggles, turn **Discovery** ON so the launcher starts the discovery plane.

### Manual process (dev)

```bash
cd backend && source venv/bin/activate
export KMP_DUPLICATE_LIB_OK=TRUE
export HOMERUN_PROCESS_ROLE=worker
export HOMERUN_WORKER_PLANE=discovery
# Ensure DATABASE_URL points at local Postgres
python -m workers.host discovery
```

## Verify

```bash
# Running planes should include discovery
ps -ax -o command= | awk '/workers\.host/ {print}'

# Counts (from backend venv)
python - <<'PY'
import asyncio
from sqlalchemy import text
from models.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as s:
        for t in ("discovered_wallets", "tracked_wallets", "wallet_trades"):
            try:
                n = (await s.execute(text(f"select count(*) from {t}"))).scalar()
                print(t, n)
            except Exception as e:
                print(t, e)

asyncio.run(main())
PY
```

Worker snapshots may show `discovery` with activity like `Scanning trader wallets...`.

## Related bots

| Bot source_key | Needs |
|----------------|--------|
| `traders_copy_trade` | Tracked wallets + discovery/tracked workers |
| `traders_confluence` | Same plane; pure-CPU confluence strategy |

These stay quiet if discovery never populates wallets.

## Do not confuse with

- **Bots** tab empty of *people* — bots are strategies, not wallets  
- **Market scanner** “no catalog” — different subsystem (market_universe)  
