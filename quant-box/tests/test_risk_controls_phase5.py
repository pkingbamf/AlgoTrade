from risk.policies import RiskEngine, RiskLimits


def test_strategy_family_and_asset_caps_enforced():
    engine = RiskEngine(RiskLimits(max_strategy_family_pct=0.25, max_asset_exposure_pct=0.3))

    ok, reason, _ = engine.check_order(
        order_notional=1000,
        equity=100000,
        strategy_id="s1",
        rolling_vol=0.1,
        context={"strategy_family_allocation_pct": 0.4, "asset_exposure_pct": 0.1},
    )
    assert not ok and reason == "max_strategy_family_allocation"

    ok, reason, _ = engine.check_order(
        order_notional=1000,
        equity=100000,
        strategy_id="s1",
        rolling_vol=0.1,
        context={"strategy_family_allocation_pct": 0.2, "asset_exposure_pct": 0.35},
    )
    assert not ok and reason == "max_asset_exposure"
