# ML / Quantitative Research Audit

Audit date: 2026-09-13  
Scope: `ml/` research path and related API/persistence usage.  
Method: code inspection and existing unit tests. No methodology changes in this prompt.

**Overall verdict:** The primary walk-forward → horizon=1 backtest path is largely implemented with chronological evaluation, train-only scaling, per-fold retrain + purge, and conservative fold-aware stitching. No CRITICAL silent leakage was found on that primary path. Important HIGH/MEDIUM risks remain around data quality (unadjusted Yahoo), survivorship, unpurged single chronological splits, and multi-horizon economics.

---

## End-to-end path

```text
Yahoo/provider OHLCV
  → request validation / normalize / validate_ohlcv
  → feature engineering (trailing windows)
  → target construction (future return / direction)
  → prepare_model_ready + assemble_supervised
  → chronological split OR walk-forward folds
  → train-only StandardScaler on features (not targets)
  → model fit (baselines / LSTM)
  → predict OOS
  → evaluation metrics
  → signals → execution align (h=1) → costs → equity/risk
  → optional fold-aware stitch
  → research pipeline / report renderer
  → optional PostgreSQL persistence → FastAPI → Next.js
```

| Stage | Status | Primary files |
|-------|--------|---------------|
| Raw market data | IMPLEMENTED | `ml/data/yahoo.py`, `ingestion.py`, `storage.py` |
| Validation | IMPLEMENTED | `ml/data/validation.py`, `normalize.py` |
| Feature engineering | IMPLEMENTED | `ml/features/*` |
| Targets | IMPLEMENTED | `ml/targets/*` |
| Preprocessing | IMPLEMENTED | `ml/preprocessing.py`, `ml/validation/preprocessing.py` |
| Splitting | IMPLEMENTED | `ml/splitting.py`, `ml/split_validation.py` |
| Training | IMPLEMENTED | `ml/models/*`, `ml/neural/*`, `ml/training/*` |
| Inverse transform | NOT IMPLEMENTED | Not required for unscaled return targets |
| Evaluation | IMPLEMENTED | `ml/evaluation/*` |
| Walk-forward | IMPLEMENTED | `ml/validation/*` |
| Backtesting | IMPLEMENTED (h=1 only) | `ml/backtesting/*` |
| Research report | IMPLEMENTED code / PLACEHOLDER empirics | `ml/research/*`, `docs/final-research-report.md` |

---

## Issue register

### CRITICAL

None identified in the implemented primary walk-forward + horizon=1 backtest path.

### HIGH

| ID | Issue | Evidence | Impact |
|----|-------|----------|--------|
| ML-H1 | Yahoo download uses `auto_adjust=False` | `ml/data/yahoo.py` `get_historical_data` | Split/dividend jumps distort returns, features, and backtests |
| ML-H2 | Survivorship / non point-in-time universe | `ml/research/universe.py`; Yahoo history | Inflated robustness claims if treated as investable history |
| ML-H3 | Single chronological splits lack label purging | `ml/splitting.py` + research ablation/complexity/explainability paths | When `horizon > 1`, train labels can overlap next partition’s information window |
| ML-H4 | Multi-horizon strategy backtest blocked, not implemented | `ml/backtesting/execution.py` raises if `forecast_horizon != 1` | Economic evaluation incomplete for h>1 (fail-loud, not silently wrong) |

### MEDIUM

| ID | Issue | Evidence | Impact |
|----|-------|----------|--------|
| ML-M1 | Horizon=1 still has boundary label overlap on unpurged single splits | `chronological_split` without `purge_fold` | Mild contamination at partition edges |
| ML-M2 | `FinalResearchConfig.horizon` can disagree with `walk_forward.forecast_horizon` | `ml/research/config.py`; note-only in multi-asset path | Misaligned targets vs purge/backtest assumptions |
| ML-M3 | Absolute price-level SMA/EMA features | `ml/features/trend.py`, `ema.py` | Distribution shift; scaler does not fix nonstationarity |
| ML-M4 | Cost/threshold sensitivity on OOS predictions | `ml/research/sensitivity.py` | Diagnostic misuse can become holdout cherry-picking |
| ML-M5 | Classification long-short defaults both 0.5 | `ml/backtesting/signals.py` | Little/no flat zone |
| ML-M6 | Ablation/complexity/explainability use unpurged chronological split | `ml/research/pipeline.py` | Fine as diagnostics; unsafe if presented as primary OOS |

### LOW

| ID | Issue | Evidence | Impact |
|----|-------|----------|--------|
| ML-L1 | No OHLC consistency checks (high≥low etc.) | `ml/data/validation.py` | Bad ticks can pass |
| ML-L2 | Same-bar close/volume features assume EOD decision | feature builders | Look-ahead if used for intraday decisions |
| ML-L3 | Explainability may fit unscaled linear model while other paths scale | `ml/research/pipeline.py` | Comparability friction |
| ML-L4 | Directional accuracy uses sign equality | `ml/evaluation/regression.py` | Zero/edge quirks |
| ML-L5 | Default backtest costs can be 0 | `ml/backtesting/config.py` | Optimistic net returns if unset |
| ML-L6 | LSTM early stopping selects on validation | `ml/training/` | Mild selection leakage into checkpoint |
| ML-L7 | Sortino uses full-sample downside including zeros | `ml/backtesting/metrics.py` | Definition choice; document |

---

## Checklist answers

| Check | Finding |
|-------|---------|
| Temporal / look-ahead in features | Not found for trailing lag/window features |
| Scaler leakage | Mitigated on main paths (train/fold-train only) |
| Target columns in X | Mitigated (`assemble_supervised` + forbidden names) |
| Random time-series splits | Not present |
| Test-set hyperparameter search | Not found |
| Walk-forward retrains per fold | Yes (baselines + LSTM) |
| Inverse transform | Absent; acceptable while targets remain unscaled |
| Backtest horizon | Correct for h=1; refused for h≠1 |
| Fabricated empirical metrics in code path | Report renderer does not invent results when `result is None` |

---

## What is not implemented (ML-adjacent)

- News / NLP / sentiment
- Model monitoring / drift / performance decay
- Portfolio optimization / multi-asset allocation book
- Live/paper trading
- Licensed real-time feeds
- Transformers
- Nested CV hyperparameter search
- Point-in-time universes
- Adjusted-price default path

---

## Recommended hardening (document only; do not implement here)

1. Add purge/embargo to single chronological splits used outside walk-forward.
2. Enforce `horizon == walk_forward.forecast_horizon` in research config.
3. Add adjusted-close provider option; document corporate-action policy.
4. Keep sensitivity labeled diagnostic-only in UI/reports.
5. Persist experiment provenance before publishing any empirical claims (see `ARTIFACT_PROVENANCE.md`).
