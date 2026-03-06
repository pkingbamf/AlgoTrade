# Quant Hedge Fund in a Box — Development Plan

This file is the authoritative roadmap for the project.
Codex must treat this as the source of truth for what to build next.

Work sequentially through phases unless blocked.

---

# Phase 1 — Foundation

Goal: Establish repository structure and infrastructure.

Tasks:
- [x] Repository scaffold
- [x] Project folder structure
- [x] Python environment configuration
- [x] Docker + Docker Compose
- [x] Environment variable handling
- [x] PostgreSQL setup
- [x] Database models
- [x] Initial README
- [x] Basic logging

Deliverables:
- Project runs locally
- Database connects successfully
- Basic services start

---

# Phase 2 — Research Engine

Goal: Enable strategy research and experimentation.

Tasks:
- [x] Market data ingestion
- [x] Data storage (parquet + PostgreSQL metadata)
- [x] Data validation utilities
- [x] Strategy specification schema (YAML)
- [x] Strategy generator
- [x] Feature calculation utilities
- [x] Factor library
- [x] Parameter sweep engine
- [x] Experiment runner
- [x] Experiment results persistence

Deliverables:
- Load historical market data
- Run parameter sweeps
- Store experiment results

---

# Phase 3 — Backtesting & Validation

Goal: Build robust strategy testing.

Tasks:
- [x] Backtesting engine
- [x] Fee model
- [x] Slippage model
- [x] Portfolio simulation
- [x] Performance metrics
- [x] Walk-forward validation
- [x] Train/test split logic
- [x] Monte Carlo trade resampling
- [x] Parameter sensitivity analysis
- [x] Strategy promotion scoring

Deliverables:
- Complete backtest report
- Strategy ranking

---

# Phase 4 — Paper Trading System

Goal: Simulate live trading safely.

Tasks:
- [x] Paper broker interface
- [x] Order execution simulator
- [x] Position tracking
- [x] PnL calculation
- [x] Strategy deployment registry
- [x] Order audit logs
- [x] Portfolio monitor

Deliverables:
- Strategies can run in simulated environment

---

# Phase 5 — Risk Management

Goal: Prevent catastrophic losses.

Tasks:
- [x] Max position sizing
- [x] Strategy allocation limits
- [x] Portfolio exposure limits
- [x] Daily loss limit
- [x] Max drawdown control
- [x] Kill switch
- [x] Strategy disable control
- [x] Volatility targeting

Deliverables:
- Risk engine integrated with paper trading

---

# Phase 6 — Monitoring & Observability

Goal: Ensure reliability.

Tasks:
- [x] Structured logging
- [x] Health checks
- [x] Alerting hooks
- [x] System metrics
- [x] Job monitoring
- [x] Data freshness monitoring

Deliverables:
- System health dashboard

---

# Phase 7 — API

Goal: Programmatic access to platform.

Tasks:
- [x] FastAPI backend
- [x] Strategy endpoints
- [x] Backtest endpoints
- [x] Rankings endpoint
- [x] Paper trading endpoints
- [x] Risk state endpoint
- [x] Metrics endpoint

Deliverables:
- Fully functional REST API

---

# Phase 8 — Dashboard

Goal: Human interface.

Tasks:
- [x] Overview page
- [x] Strategy library page
- [x] Backtest viewer
- [x] Rankings page
- [x] Paper trading monitor
- [x] Risk monitor
- [x] System health page

Deliverables:
- Working UI dashboard

---

# Phase 9 — Testing & Hardening

Goal: Production readiness.

Tasks:
- [ ] Unit tests
- [ ] Integration tests
- [ ] Backtest correctness tests
- [ ] Risk enforcement tests
- [ ] API endpoint tests
- [ ] CI/CD pipeline

Deliverables:
- Reliable system
