# Quant Hedge Fund in a Box (MVP)

Research-first quantitative research and paper-trading platform.

## Architecture decisions
- **FastAPI + SQLAlchemy + Pydantic** for typed API and service boundaries.
- **Parquet + Pandas** for fast research loops and data handling.
- **PostgreSQL/SQLite support** for metadata, run history, promotion decisions.
- **Vectorized MVP backtester** (`SimpleBacktestEngine`) for robust v1 simplicity.
- **Central RiskEngine** to enforce hard controls before paper order acceptance.
- **PaperBroker only** (no live money execution in v1 by design).

## Project layout

```text
quant-box/
  app/{api,services,models,schemas,db,core}
  data/{raw,processed}
  research/{strategy_specs,generated_strategies,factors,features,experiments,ranking}
  backtests/{engines,reports,validation}
  execution/{paper,brokers,deployment}
  risk/
  monitoring/
  frontend/
  tests/
  scripts/
  configs/
  docker/
```

## Quick start

```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
python scripts/generate_sample_data.py
python scripts/load_strategy_specs.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:
- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8000/`

## Docker

```bash
docker compose up --build
```

## Phase 2 research workflow

```bash
python scripts/generate_sample_data.py
python scripts/ingest_and_register_data.py
python scripts/load_strategy_specs.py
python scripts/run_experiment.py
```

This produces parquet research data, registers metadata in `data_assets`, and persists sweep runs to `experiment_runs` and `experiment_results`.


## API endpoints included
- `/health`, `/metrics`
- `/strategies`, `/strategies/{id}`
- `/strategy-specs`
- `/backtests/run`, `/backtests/{id}`, `/backtests/{id}/report`
- `/rankings`, `/promotions`
- `/paper/deployments` (GET/POST), `/paper/orders` (GET/POST), `/paper/positions`, `/paper/pnl`, `/paper/portfolio-monitor`, `/paper/reconcile/{strategy_id}`
- `/risk/state`, `/risk/limits`, `/risk/kill-switch/{active}`, `/risk/disable/{strategy_id}`, `/risk/enable/{strategy_id}`
- `/system/logs`, `/system/jobs`, `/system/data-freshness`

## Strategy spec format
YAML keys:
- `strategy_id`
- `family`
- `asset_universe`
- `timeframe`
- `indicators`
- `entry_rules`
- `exit_rules`
- `risk_rules`
- `parameter_ranges`
- `notes`

8 sample specs are provided across trend, mean reversion, breakout, and pairs families.

## Validation pipeline
1. In-sample backtest
2. Out-of-sample backtest
3. Walk-forward windows
4. Parameter sweep via spec variants
5. Monte Carlo trade-sequence bootstrap
6. Parameter sensitivity analysis
7. Threshold gates (trades, Sharpe, drawdown, profit factor, turnover, stability)
8. Promotion score + decision reason

## Testing

```bash
pytest -q
```

## Remaining work
- richer multi-asset pairs engine and portfolio construction
- async job queue for long experiments
- persistent metrics exporter and alert integrations
- full frontend UX beyond lightweight dashboard page
- Alembic migration generation automation


## Risk controls include
- max position sizing
- strategy family allocation caps
- asset exposure caps
- daily loss and drawdown kill-switch triggers
- strategy disable/enable controls
- volatility-based size reduction


## Monitoring
- health details include heartbeat, data freshness, running jobs, and alert counts
- metrics endpoint includes system counters and service status map
- stale-data detection emits alert-hook events visible in system logs


## Dashboard pages
- `/dashboard/overview`
- `/dashboard/strategy-library`
- `/dashboard/backtest-runs`
- `/dashboard/rankings`
- `/dashboard/paper-trading`
- `/dashboard/risk-monitor`
- `/dashboard/system-health`
