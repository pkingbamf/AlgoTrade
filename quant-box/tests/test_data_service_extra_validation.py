import pandas as pd
import pytest

from app.services.data_service import DataService


def test_data_validation_rejects_negative_volume():
    df = pd.DataFrame(
        {
            "timestamp": ["2024-01-01"],
            "open": [1],
            "high": [1],
            "low": [1],
            "close": [1],
            "volume": [-1],
        }
    )
    with pytest.raises(ValueError):
        DataService().validate_ohlcv(df)
