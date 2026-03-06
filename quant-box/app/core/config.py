from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "quant-box"
    env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite:///./quant_box.db"
    local_database_url: str = "sqlite:///./quant_box.db"
    data_dir: str = "./data"

    promotion_min_trades: int = 30
    promotion_min_oos_sharpe: float = 0.8
    promotion_max_drawdown: float = 0.2

    risk_max_position_pct: float = 0.10
    risk_max_family_allocation_pct: float = 0.25
    risk_max_daily_loss_pct: float = 0.02
    risk_max_portfolio_dd_pct: float = 0.10
    vol_reduction_threshold: float = 0.35

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
