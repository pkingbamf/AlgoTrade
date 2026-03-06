# Project Status

## Current Phase
Phase 3 — Backtesting & Validation (Complete)

---

# Completed

## Phase 1 — Foundation
Completed:
- repo scaffold
- Docker configuration
- PostgreSQL setup
- environment handling
- logging
- base architecture
- startup lifecycle hardening (`FastAPI` lifespan)
- sqlite thread-safety config for local dev/test

## Phase 2 — Research Engine
Completed:
- market data ingestion (`DataService.ingest_csv`)
- parquet storage + metadata persistence to DB (`DataAsset`)
- data validation utilities (required columns, null checks, negative volume checks)
- YAML strategy specification schema validation (`StrategySpecSchema`)
- strategy generator and variant materialization
- feature calculation utilities
- factor library utilities
- parameter sweep engine (`ParameterSweepEngine`)
- experiment runner (`ExperimentService`)
- experiment results persistence (`ExperimentRun`, `ExperimentResult`)

## Phase 3 — Backtesting & Validation
Completed:
- vectorized backtesting engine with fees and slippage
- portfolio-level metrics (CAGR, Sharpe, Sortino, Calmar, drawdown, PF, turnover, exposure, expectancy)
- train/validation/test split logic
- walk-forward evaluation windows
- trade-sequence Monte Carlo resampling
- parameter sensitivity scoring (`parameter_stability`)
- promotion scoring integration
- complete report payload builder (`build_backtest_report`)

---

# Current Work

Phase 3 closeout and readiness for paper-trading system implementation.

---

# Decisions

- promotion-score ranking is used as primary experiment ranking signal in Phase 3
- OOS metrics and stability are persisted per variant
- report payload includes IS/OOS metrics + Monte Carlo + sensitivity for auditability

---

# Known Issues

- Environment dependency availability may impact local `pytest` execution if packages are not installed.

---

# Next Phase

Phase 4 — Paper Trading System
