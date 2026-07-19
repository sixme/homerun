"""Paper desk equity/ROI must include open inventory mark, not free cash only."""

from services.simulation import compute_paper_equity_and_roi


def test_equity_roi_flat_deployed_book_is_near_zero_not_deeply_negative():
    # $2000 bankroll, $250 free cash, $1750 open inventory marked at cost.
    equity, roi = compute_paper_equity_and_roi(
        initial_capital=2000.0,
        current_capital=250.0,
        market_value=1750.0,
    )
    assert equity == 2000.0
    assert abs(roi) < 1e-9


def test_equity_roi_reflects_unrealized_gain_on_inventory():
    equity, roi = compute_paper_equity_and_roi(
        initial_capital=1000.0,
        current_capital=400.0,
        market_value=700.0,  # cost was 600 → +100 unrealized
    )
    assert equity == 1100.0
    assert abs(roi - 10.0) < 1e-9


def test_equity_roi_cash_only_when_flat():
    equity, roi = compute_paper_equity_and_roi(
        initial_capital=1000.0,
        current_capital=1050.0,
        market_value=0.0,
    )
    assert equity == 1050.0
    assert abs(roi - 5.0) < 1e-9


def test_equity_roi_zero_initial_is_safe():
    equity, roi = compute_paper_equity_and_roi(
        initial_capital=0.0,
        current_capital=100.0,
        market_value=50.0,
    )
    assert equity == 150.0
    assert roi == 0.0
