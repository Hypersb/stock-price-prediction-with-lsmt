# Dependency Audit

Audit date: 2026-09-13  
Policy for this prompt: **document only — no broad upgrades.**

---

## Python runtime (`requirements.txt`)

| Package | Role | Notes |
|---------|------|-------|
| pandas≈3.0 | Data frames | Core |
| numpy≈1.26 | Arrays | Core; pinned below 2.x via `~=1.26` |
| matplotlib≈3.9 | Plots | Used by `ml/visualization`; not required for API runtime |
| scikit-learn≈1.5 | Baselines + scaler | Core ML |
| jupyter≈1.1 | Notebooks | Dev/research local; **excluded from Docker API image** |
| yfinance≈0.2 | Market data | Provider; network-dependent quality |
| fastapi≈0.115 | API | Core |
| uvicorn≈0.30 | ASGI server | Core |
| sqlalchemy≈2.0 | ORM | Core |
| alembic≈1.13 | Migrations | Core |
| psycopg[binary]≈3.2 | Postgres driver | Core |
| pydantic≈2.7 | Schemas (via FastAPI ecosystem) | Present; FastAPI also pulls pydantic |
| torch≈2.2 | LSTM | Heavy; CI installs CPU wheel separately |

### Dev (`requirements-dev.txt`)

| Package | Role |
|---------|------|
| pytest≈9.0 | Tests |
| ruff≈0.8 | Lint (local install may be newer; CI uses this range) |

### Docker API (`requirements-docker.txt`)

Pinned with the same compatible-release operators as `requirements.txt` for the
shared API runtime set (pandas, numpy, scikit-learn, yfinance, fastapi, uvicorn,
sqlalchemy, alembic, psycopg[binary], pydantic).

**Excludes** jupyter and torch intentionally (API image is inference/research-serving
oriented without training stack).

**Prompt 2:** unpinned Docker requirements debt (TD-009) resolved via aligned `~=` pins.
Does **not** freeze an entire developer virtualenv into the image.

---

## JavaScript / TypeScript (`frontend/package.json`)

### Dependencies

| Package | Role |
|---------|------|
| next 16.3.4 | App framework |
| react / react-dom 19.2.8 | UI |
| recharts ^2.15.4 | Charts |

### DevDependencies

| Package | Role |
|---------|------|
| typescript ^5 | Types |
| eslint + eslint-config-next 16.3.4 | Lint |
| tailwindcss ^4 + `@tailwindcss/postcss` | Styling |
| `@types/*` | Types |
| vitest ^3.2.4 | Unit tests |

No Redux, no chart-library duplicates, no auth SDKs, no ORMs on the frontend.

---

## Findings

### Duplicate / overlapping

| Finding | Severity | Recommendation |
|---------|----------|----------------|
| matplotlib + Recharts both visualize series | Low | Keep: matplotlib for research notebooks/scripts; Recharts for UI |
| Analysis metrics exist in `ml/analysis` and again conceptually in backtest metrics | Low | Different domains; avoid copying formulas into frontend (mostly already avoided) |
| pydantic listed explicitly while FastAPI depends on it | Low | Keep explicit pin for clarity |

### Unused / questionable major deps

| Finding | Notes |
|---------|-------|
| jupyter in root requirements | Needed for notebooks; not needed for API. Already excluded from Docker. Consider moving to an optional `requirements-notebooks.txt` later |
| matplotlib in root requirements | Visualization helpers + notebooks; API may not need it in all images |

### Conflicts / fragility

| Finding | Notes |
|---------|-------|
| torch heavy + CI special-case CPU index | Documented in workflow; keep |
| Node 18 vs Vite/Vitest ESM | Frontend tests require Node ≥20 |
| Unpinned `requirements-docker.txt` | **Resolved in Prompt 2** — aligned `~=` pins |

### Obsolete

None obviously obsolete among declared majors. Stack versions are relatively current (Next 16, React 19, FastAPI 0.115, SQLAlchemy 2).

### Security-sensitive

| Dependency / surface | Notes |
|----------------------|-------|
| yfinance | Third-party network data; treat as untrusted input after validation |
| psycopg / DATABASE_URL | Credential in env; not committed (verified `.env` gitignored) |
| MARKET_DATA_API_KEY | Optional env; empty by default |
| No Redis/auth JWT libs yet | N/A |

### ML / DB / viz grouping

- **ML:** torch, scikit-learn, numpy, pandas  
- **DB:** sqlalchemy, alembic, psycopg  
- **API:** fastapi, uvicorn, pydantic  
- **Viz:** matplotlib (Python), recharts (TS)  
- **Data:** yfinance  

---

## Recommendations (later prompts)

1. Pin `requirements-docker.txt` to the same lower bounds as `requirements.txt` (minus torch/jupyter). **Done (Prompt 2).**
2. Split notebook extras from API runtime deps.
3. Document Node 20+/22 in README developer prerequisites. **Done (Prompt 1–2; engines enforced).**
4. Periodic `pip audit` / `npm audit` in Phase 14 — not now.
5. Do not add microservices libraries, Kafka, or unused cloud SDKs until a concrete requirement exists.
