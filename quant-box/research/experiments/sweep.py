from app.services.strategy_service import StrategyService


class ParameterSweepEngine:
    """Materializes strategy variants from a structured strategy spec."""

    def __init__(self):
        self.strategy_service = StrategyService()

    def sweep(self, spec: dict) -> list[dict]:
        return self.strategy_service.generate_variants(spec)
