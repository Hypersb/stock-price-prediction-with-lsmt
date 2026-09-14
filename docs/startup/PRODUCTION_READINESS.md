# Startup Readiness Scorecard (post-transformation pass)

Scored 0–5. Do not inflate.

| Category | Score | Notes |
|----------|------:|-------|
| market data | 4 | Provider + quality + adj_close optional; still Yahoo-only |
| data quality | 4 | Strict OHLC + gaps |
| feature pipeline | 4 | Deterministic + identity helper |
| ML | 4 | Baselines + LSTM real |
| validation | 4 | WF purge; single-split purge optional |
| backtesting | 3 | Solid h=1; multi-horizon blocked |
| risk | 3 | VaR/ES/Calmar/beta added; not portfolio VaR suite |
| experiments | 3 | Config fingerprint + empirics artifacts; DB provenance partial |
| registry | 2 | Filesystem registry; catalog mostly untrained |
| monitoring | 2 | Helpers exist; no scheduled production monitors |
| news | 2 | Port + null provider; no live feed configured |
| NLP | 2 | Keyword lexicon baseline only |
| AI research | 2 | Tools + safety; no LLM provider wired |
| portfolio | 2 | Analytics library; no multi-user portfolios |
| backend | 4 | FastAPI modular |
| database | 3 | Alembic schema present; provenance gaps |
| jobs | 2 | In-process queue only |
| cache | 2 | Process TTL |
| frontend | 3 | Research UI exists; not full product surface |
| auth | 2 | Optional API key; no user accounts UI |
| security | 3 | Headers/limits/secret hygiene; open API default |
| testing | 4 | Large pytest + vitest + contracts |
| CI/CD | 3 | GH Actions present |
| observability | 2 | Logs/request ids; no OTEL |
| deployment | 2 | Compose/dev; not hardened prod |
| documentation | 4 | Startup docs + system design + empirics |

**Average (approx):** ~2.9 / 5  

**Release decision:** STARTUP RELEASE CANDIDATE **BLOCKED** — missing multi-user auth, production workers/cache, live news credentials, and hardened deploy despite strong research core + honest empirics.
