# Production Readiness Scorecard

Audit date: 2026-09-13  
Scale: **0–5** (0 = absent, 5 = production-grade). Scores are intentionally conservative.

| Area | Score | Justification |
|------|------:|---------------|
| Market data | 2 | Yahoo historical provider works with validation; unadjusted closes, no PIT universe, no multi-provider, no SLA |
| Data validation | 3 | Solid OHLCV schema/chrono checks; missing richer OHLC integrity/corporate-action policy |
| Feature engineering | 3 | Broad leakage-aware feature set + tests; absolute level features and no feature store |
| ML methodology | 3 | Chronological splits, train-only scaling, WF purge/retrain are real; single-split purge gap; empirics unpublished |
| Baseline comparison | 3 | Naive/linear/tree/boosting implemented and comparable under shared rules |
| Walk-forward validation | 4 | Expanding/rolling, purge, fold preprocess, OOS collection, aggregates — strongest area |
| Backtesting | 3 | Costed h=1 engine + fold-aware guards; simplified costs; multi-horizon blocked |
| Risk analytics | 2 | Sharpe/Sortino/DD/vol exist; no dedicated risk engine (VaR/ES/factors) |
| Experiment reproducibility | 2 | Seeds/configs exist; dataset/code provenance incomplete; no attested published run |
| Artifact provenance | 1 | Partial DB models; contract defined only in Phase 1 docs |
| Model lifecycle | 1 | Checkpoint helpers + hardcoded catalog; no real registry/promote/rollback |
| Monitoring | 0 | Not implemented |
| News | 0 | Not implemented |
| NLP | 0 | Not implemented |
| Portfolio analytics | 0 | Not implemented |
| Backend architecture | 3 | Clean FastAPI modular monolith services/repos; no auth/jobs |
| Database | 3 | Postgres + Alembic + SQLAlchemy models/tests; SQLite unit path |
| Caching | 2 | Process TTL only; adequate for single-node research API |
| Background jobs | 0 | Not implemented |
| Frontend | 3 | Real Next.js research UI with honest empty states; shallow tests; Node engine caveat |
| Authentication | 0 | Not implemented |
| Security | 2 | Headers, body limits, secret redaction tests; open API, dev creds |
| Testing | 4 | 300 pytest passed; ruff clean; frontend 14 vitest on Node 20+; CI defined |
| CI/CD | 3 | GitHub Actions for backend/frontend/DB; no deploy pipeline |
| Observability | 1 | Basic logging + request context; no metrics/tracing/alerting stack |
| Documentation | 3 | Strong research docs; empirics placeholders honest; new startup docs added |
| Deployment | 2 | Docker Compose local stack; not cloud-hardened |

**Average (26 areas): ~2.0** — solid research prototype / modular monolith foundation; **not** a production multi-tenant SaaS.

---

## Interpretation

- **Ready for:** local/research use, continued engineering, recruiter-honest demos of methodology  
- **Not ready for:** production user accounts, real-time claims, managed model ops, regulated advice surfaces  
