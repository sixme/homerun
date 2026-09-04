"""Simulation package.

Provides simulation service and execution simulator components.
"""

from __future__ import annotations

from .execution_simulator import ExecutionSimulator, execution_simulator
from .fill_models import FillConfig, FillModel
from .historical_data_provider import HistoricalDataProvider
from .service import (
    AsyncSessionLocal,
    SimulationService,
    SlippageModel,
    compute_paper_desk_metrics,
    compute_paper_equity_and_roi,
    expected_free_cash_from_trades,
    position_mark_price,
    positions_market_value,
    simulation_service,
)

__all__ = [
    "AsyncSessionLocal",
    "ExecutionSimulator",
    "FillConfig",
    "FillModel",
    "HistoricalDataProvider",
    "SimulationService",
    "SlippageModel",
    "compute_paper_desk_metrics",
    "compute_paper_equity_and_roi",
    "execution_simulator",
    "expected_free_cash_from_trades",
    "position_mark_price",
    "positions_market_value",
    "simulation_service",
]
