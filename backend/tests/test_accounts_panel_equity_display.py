"""Structural checks: Accounts metrics helpers must use equity not free cash."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CORE = REPO / "frontend" / "src" / "services" / "apiCore.ts"
ACCOUNTS = REPO / "frontend" / "src" / "components" / "AccountsPanel.tsx"


def test_simulation_account_helpers_exported():
    text = CORE.read_text(encoding="utf-8")
    assert "export function simulationAccountEquity" in text
    assert "export function simulationAccountTotalPnl" in text
    assert "export function simulationAccountRoiPercent" in text
    assert "equity?: number" in text or "equity:" in text


def test_accounts_panel_uses_equity_helpers_not_free_cash_as_equity():
    text = ACCOUNTS.read_text(encoding="utf-8")
    assert "simulationAccountEquity" in text
    assert "simulationAccountTotalPnl" in text
    assert "sandboxMetrics.totalEquity" in text
    # Bug we fixed: simEquity was bound to deployableCapital (free cash).
    assert "value={formatUsd(sandboxMetrics.deployableCapital)}" not in text
    assert "value={formatUsd(sandboxMetrics.totalEquity)}" in text
    # Account capital column must not be free cash only.
    assert (
        "formatUsd(account.current_capital || 0)" not in text.split("colCapital")[1].split("colPnl")[0]
        if "colCapital" in text
        else True
    )
