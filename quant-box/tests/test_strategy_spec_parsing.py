from app.services.strategy_service import StrategyService


def test_strategy_spec_parsing():
    service = StrategyService()
    spec = service.load_spec("research/strategy_specs/trend_ma_cross_1.yaml")
    assert spec["family"] == "trend_following"
    variants = service.generate_variants(spec)
    assert len(variants) == 9
