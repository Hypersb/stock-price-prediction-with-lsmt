# ADR-001: Modular monolith first

## Context

The repository already ships a FastAPI application, an in-process `ml/` quantitative engine, PostgreSQL persistence, and a Next.js dashboard. The startup transformation will add many domains (news, NLP, jobs, auth) over time. Premature microservice splits would multiply deployment and versioning cost without proven scale needs.

## Decision

Keep a **modular monolith**: domain logic lives in importable packages/modules; a single API deploy unit orchestrates them. Split into separate network services only when a concrete scaling, isolation, or compliance requirement appears.

## Alternatives

1. Immediate microservices per domain (market data, ML, backtest, …)  
2. Serverless function-per-endpoint architecture  
3. Monorepo with multiple independently deployed backends from day one  

## Consequences

- Faster iteration and a single pytest surface  
- Requires discipline via domain boundaries and ADRs to avoid a ball of mud  
- Horizontal scaling later may need external cache/queue before process-local assumptions break  
