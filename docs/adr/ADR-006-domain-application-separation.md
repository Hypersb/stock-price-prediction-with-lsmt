# ADR-006: Domain / application separation

## Context

The repository is a modular monolith. Without explicit separation, FastAPI routes and SQLAlchemy sessions tend to absorb quantitative formulas, while domain code risks importing HTTP concerns as product features grow (news, jobs, auth).

## Decision

Keep quantitative algorithms and research contracts in `ml/` (domain).  
Keep HTTP, env, cache, and persistence orchestration in `backend/app` (application/infrastructure).  
Application services may import `ml`; `ml` must not import `backend` or FastAPI.

## Alternatives

1. Pass SQLAlchemy sessions into model training code  
2. Put feature engineering inside API route handlers  
3. Split into microservices per domain now  

## Consequences

- Clear testability of domain code without network/DB  
- Future domains integrate via services/ports  
- Occasional duplication of thin DTO mapping is accepted  
