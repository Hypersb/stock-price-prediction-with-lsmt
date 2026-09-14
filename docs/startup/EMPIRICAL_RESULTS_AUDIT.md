# Empirical Results Audit

Audit date: 2026-09-13  
Rule: every performance-looking number must have provenance. Do not invent replacements.

Classification:

| Code | Meaning |
|------|---------|
| A | Generated from a reproducible experiment (code + config + data period recoverable) |
| B | Example/demo data |
| C | Placeholder / awaiting execution |
| D | Hardcoded |
| E | Impossible to verify from repository artifacts |

---

## Repository-wide finding

**No committed production empirical study was found** that populates MAE/RMSE/Sharpe/drawdown/backtest P&L as claimed research outcomes.

Evidence:

- `docs/final-research-report.md` sections 1, 3, 8–15, 17 are explicitly `_Awaiting generated results…_`
- `data/raw/` and `data/processed/` contain only `.gitkeep` (no research extracts)
- No committed `*.pt` / `*.pth` / `artifacts/` / experiment metric dumps
- `ml/research/report.py` renders empty empirics when `result is None`
- README states empirical report sections remain placeholders

Therefore: **platform metrics code exists; published empirics do not.**

---

## Documentation claims

| Location | Number / claim | Classification | Provenance |
|----------|----------------|----------------|------------|
| `docs/final-research-report.md` empirical sections | All performance tables/sections | **C** | Explicit placeholders |
| `README.md` / methodology docs | Capability descriptions (Sharpe, walk-forward, etc.) | N/A (capabilities, not results) | Code paths documented |
| `docs/project-status.md` “15 phases complete” | Process status | D/process claim | Prior engineering phases — **not** empirical wins |

No fabricated numeric performance tables were found in docs.

---

## UI surfaces

| Surface | What looks empirical | Classification | Provenance |
|---------|----------------------|----------------|------------|
| Market page MetricCards | cum return, vol, max DD, mean/median | **A*** | Live Yahoo + `ml.analysis` via API (*reproducible only for the exact request window; not a stored experiment) |
| Market cumulative chart | path from closes | **A*** / caution | Frontend recomputes from **paginated** rows; can diverge from analysis metric |
| Features page | feature values | **A*** | On-demand `build_features` over Yahoo |
| Models page | model list / `trained` | **D** | Hardcoded catalog; `trained=False` |
| HeroGraphic | stylized equity path | **D** | Decorative SVG geometry |
| Experiments / metrics | stored metrics | **A** if DB rows exist; else empty | PostgreSQL persistence — **no seed empirics in repo** |
| Walk-forward page | fold metrics | **A** if DB run exists; else empty | DB |
| Backtests page | Sharpe/Sortino/returns/DD/equity | **A** if DB backtest exists; else empty | DB; drawdown series derived in UI from equity |

\*Live Yahoo numbers are real market-derived computations, not model-performance claims. They are **not** durable research artifacts without provenance records.

Empty states intentionally show no fabricated P&L (`StatePanel` messaging).

---

## Tests

| Location | Numbers | Classification | Notes |
|----------|---------|----------------|-------|
| Many `tests/test_*.py` | Exact floats (e.g. accuracy 0.75, MDD -0.2) | **B** | Synthetic fixtures asserting formulas |
| `tests/test_fullstack_integration.py` | Example metric payloads | **B** | Persistence/API wiring |

Test fixture numbers must never be copied into product claims.

---

## Backend model catalog

| Item | Classification | Notes |
|------|----------------|-------|
| `SUPPORTED_MODELS` with `trained=False` | **D** | Metadata only; not performance |

---

## Notebooks

| Location | Classification | Notes |
|----------|----------------|-------|
| `notebooks/01`–`09` | **E** / potentially **B** | Present as exploratory code; no committed executed outputs with verified provenance in this audit |

Do not treat notebook cells as published results unless regenerated under Phase 2 provenance rules.

---

## Code paths that *can* produce class-A results

These produce real metrics only when executed with explicit data/config:

1. `ml/research/pipeline.py` → `run_final_research_evaluation`
2. Walk-forward evaluators → OOS prediction tables → evaluation metrics
3. `ml/backtesting/engine.py` / `fold_aware.py` → strategy metrics
4. Persistence into PostgreSQL → API → UI

Until an operator run is stored with provenance fields (see `ARTIFACT_PROVENANCE.md`), any spoken “LSTM Sharpe / accuracy” claim is **unverified (E)** or **placeholder (C)**.

---

## Summary

| Category | Count / status |
|----------|----------------|
| Committed class-A research performance claims | **0** |
| Explicit placeholders | Final research report empirics |
| Hardcoded decorative / catalog | Hero graphic, model catalog |
| Live analysis numbers | Market/features (Yahoo-derived, not model OOS study) |
| Synthetic test numbers | Many (allowed in tests only) |

**Do not invent replacement results in later prompts until a reproducible experiment is executed and recorded.**
