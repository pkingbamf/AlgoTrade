from risk.policies import RiskEngine, RiskLimits


def test_risk_limit_enforcement():
    engine = RiskEngine(RiskLimits(max_position_pct=0.1))
    ok, reason, _ = engine.check_order(
        order_notional=15000,
        equity=100000,
        strategy_id="s1",
        rolling_vol=0.1,
        context={},
    )
    assert not ok
    assert reason == "max_position_limit"


def test_kill_switch_behavior():
    engine = RiskEngine(RiskLimits())
    engine.set_kill_switch(True)
    ok, reason, _ = engine.check_order(order_notional=1000, equity=100000, strategy_id="s1", rolling_vol=0.1, context={})
    assert not ok and reason == "global_kill_switch"


def test_daily_loss_trigger_sets_kill_switch():
    engine = RiskEngine(RiskLimits(max_daily_loss_pct=0.02))
    ok, reason, _ = engine.check_order(
        order_notional=1000,
        equity=100000,
        strategy_id="s1",
        rolling_vol=0.1,
        context={"daily_loss_pct": 0.03},
    )
    assert not ok and reason == "max_daily_loss_breached"
    assert engine.kill_switch


def test_volatility_size_reduction():
    engine = RiskEngine(RiskLimits(vol_reduction_threshold=0.2))
    ok, reason, mult = engine.check_order(
        order_notional=1000,
        equity=100000,
        strategy_id="s1",
        rolling_vol=0.4,
        context={},
    )
    assert ok and reason == "ok"
    assert 0.25 <= mult < 1.0
