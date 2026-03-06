from execution.paper.broker import PaperBroker


def test_portfolio_monitor_shape():
    broker = PaperBroker()
    broker.place_order(symbol="ETHUSDT", side="buy", quantity=1.5, price=2000.0)
    monitor = broker.portfolio_monitor({"ETHUSDT": 2100.0})
    assert "positions" in monitor
    assert "unrealized_pnl" in monitor
    assert monitor["orders"] == 1
