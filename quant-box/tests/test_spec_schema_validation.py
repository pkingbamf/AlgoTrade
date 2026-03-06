import pytest
from pydantic import ValidationError

from app.schemas.research import StrategySpecSchema


def test_spec_schema_rejects_invalid_family():
    with pytest.raises(ValidationError):
        StrategySpecSchema(
            strategy_id="x1",
            family="bad_family",
            asset_universe=["BTCUSDT"],
            timeframe="1h",
            indicators={},
            entry_rules=["a"],
            exit_rules=["b"],
            risk_rules={},
            parameter_ranges={"k": [1, 2]},
        )
