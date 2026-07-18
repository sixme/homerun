# Homerun + Grok CLI

When working in this repo from a Grok CLI session:

## Prefer MCP for live app state

If the backend is up, use the **homerun** MCP server (`http://127.0.0.1:8000/mcp`) for markets, strategies, traders, wallets, and ops tools — same surface as the in-app AI Agents tab.

Do **not** reimplement those handlers by scraping the UI.

## Local stack

| Piece | Default |
|-------|---------|
| UI | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| MCP | http://127.0.0.1:8000/mcp |
| Postgres | `postgresql+asyncpg://homerun:homerun@127.0.0.1:5432/homerun` |
| Python venv | `backend/venv/bin/python` |

Launcher: `./scripts/infra/run.sh` (Postgres + GUI + worker planes).  
API-only after crash: `cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000`.

## Architecture reminders

- **One bot = one strategy** (`source_configs` length must be 1).
- **Account is global** (header Select Account → orchestrator `shadow_account_id`), not per-bot.
- **Discovery plane is OFF by default** — Traders/Discovery UI empty until enabled.
- **Shadow** does not need Polymarket API keys; **live** does.
- macOS: set `KMP_DUPLICATE_LIB_OK=TRUE` before loading torch/sklearn/faiss.

## Skills in this repo

Use project skills under `.grok/skills/` for shadow bots, discovery, and MCP troubleshooting rather than reinventing procedures.
