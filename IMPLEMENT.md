# Implementation Rules

Codex must follow these rules when implementing this project.

## Source of Truth
PLAN.md defines what should be built.

## Workflow

For every phase:

1. Review current implementation
2. Fix architectural weaknesses
3. Ensure tests pass
4. Update DOCUMENTATION.md
5. Implement next milestone
6. Commit scoped changes
7. Update PLAN.md checkboxes
8. Continue until phase is complete

Do not jump phases.

## Engineering Standards

- Modular architecture
- Strong typing where possible
- Clear separation between research and execution code
- No hardcoded secrets
- Use environment variables
- Use config files where possible

## Design Principles

Prefer:

simple > clever  
modular > monolithic  
explicit > implicit

## Dependency Policy

Use minimal dependencies.

Preferred stack:

Python  
FastAPI  
PostgreSQL  
Pandas  
NumPy  
vectorbt  
pytest  
Docker

Avoid unnecessary frameworks.

## Strategy Research Rules

Strategies must:

- survive fees
- survive slippage
- survive out-of-sample testing
- have sufficient trade count
- show parameter stability

Reject fragile strategies.

## Risk Rules

Default risk controls:

- max 10% per position
- max 25% per strategy
- max daily loss 2%
- max drawdown 10%

Risk limits must be configurable.

## Promotion Pipeline

A strategy moves to paper trading only if:

- OOS performance acceptable
- drawdown acceptable
- stability acceptable
- trade count sufficient
