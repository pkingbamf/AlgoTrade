from risk.policies import RiskEngine, RiskLimits


def test_risk_limit_enforcement():
    engine = RiskEngine(RiskLimits(max_position_pct=0.1))
    ok, reason = engine.check_order(order_notional=15000, equity=100000, strategy_id="s1", rolling_vol=0.1)
    assert not ok
    assert reason == "max_position_limit"


def test_kill_switch_behavior():
    engine = RiskEngine(RiskLimits())
    engine.kill_switch = True
    ok, reason = engine.check_order(order_notional=1000, equity=100000, strategy_id="s1", rolling_vol=0.1)
    assert not ok and reason == "global_kill_switch"
