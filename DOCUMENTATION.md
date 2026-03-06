# Project Status

## Current Phase
Phase 5 — Risk Management (Complete)

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
- portfolio-level metrics and report payload builder
- walk-forward + train/test + Monte Carlo + parameter sensitivity

## Phase 4 — Paper Trading System
Completed:
- paper broker interface + execution simulator
- deployment registry + audit logs
- portfolio monitor + reconciliation

## Phase 5 — Risk Management
Completed:
- max position size enforcement
- strategy-family allocation limit checks
- asset exposure cap checks
- max daily loss and max drawdown triggers
- global kill switch controls
- strategy-level disable/enable controls
- volatility reduction sizing multiplier
- risk endpoints integrated into API order flow

---

# Current Work

Phase 5 validation complete; preparing for Phase 6 monitoring and observability enhancements.

---

# Decisions

- risk checks are centralized in `RiskEngine` and evaluated pre-order
- daily loss/drawdown breaches trigger kill switch activation
- volatility is handled via sizing reduction (not immediate rejection)

---

# Known Issues

- Full test suite still requires dependencies not present in minimal environment runners.

---

# Next Phase

Phase 6 — Monitoring & Observability
