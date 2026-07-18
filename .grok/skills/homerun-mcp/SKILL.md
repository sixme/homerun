---
name: homerun-mcp
description: >
  Connect Grok CLI to Homerun's MCP tool surface (same tools as the AI Agents tab).
  Use when the user wants to call Homerun tools from CLI, configure MCP, debug
  /mcp connectivity, or operate live app state without the browser UI.
when-to-use: |
  homerun mcp, mcp tools, AI agents from CLI, call homerun tools, /mcp
compatibility: Requires Homerun backend on localhost:8000 (or configured URL).
---

# Homerun MCP for Grok CLI

## What this is

Homerun exposes its agent tool registry over MCP:

- **Code:** `backend/services/mcp/http_app.py` (mounted at `/mcp`)
- **Tools:** `backend/services/ai/tools/*.py` (~88 tools)
- **Project config:** `.grok/config.toml` → `[mcp_servers.homerun]`

This is **not** the same as copying Python into `.grok/`. MCP is the live bridge.

## Prerequisites

1. Backend running and healthy:

```bash
curl -fsS http://127.0.0.1:8000/health/live
```

2. MCP server enabled in project config (`.grok/config.toml`).

3. **Reload Grok** or open a new session in this repo so project MCP is picked up.
   Check with `/mcps` or `grok mcp list` (if available in your Grok build).

## Using tools in a session

1. Prefer **search_tool** / MCP discovery for `homerun__*` tools.
2. Call tools via the MCP `use_tool` path with the qualified name  
   `homerun__<tool_name>` (exact naming depends on Grok’s MCP namespace rules).
3. If tools are missing:
   - Confirm backend is up
   - Confirm URL is `http://127.0.0.1:8000/mcp` (not `/api/mcp`)
   - Restart Grok after editing `.grok/config.toml`
   - Check backend logs for `MCP HTTP transport mounted at /mcp`

## Optional category filters

When starting the backend:

```bash
export HOMERUN_MCP_ALLOWED_CATEGORIES=market,strategy,trading,system
# or
export HOMERUN_MCP_DENIED_CATEGORIES=web
```

## Local-only auth model

Homerun MCP has **no auth** by design (single-user local app). Keep the API on loopback.

## Do not

- Expect MCP to work with only the frontend (`:3000`) up
- Paste consumer SuperGrok / Gemini Pro sessions as “API keys” for Homerun AI UI  
  (MCP tools that need LLM still use Settings API keys inside Homerun)
