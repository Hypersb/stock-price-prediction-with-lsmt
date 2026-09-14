# Artifact Provenance Contract

Status: **contract only** (Phase 1). Do not build a full ML platform in this prompt.

Goal: every future empirical result shown in docs/UI must be traceable.

---

## Minimum provenance record

Every experiment (or equivalent run) should eventually carry:

| Field | Purpose |
|-------|---------|
| `experiment_id` | Stable unique id (UUID) |
| `dataset_id` | Logical dataset identity |
| `dataset_version` | Immutable version / hash of rows used |
| `symbol` / `universe` | Asset scope |
| `data_period` | Inclusive start/end timestamps + calendar notes |
| `feature_set` | Name/version of feature configuration |
| `target_definition` | e.g. `future_return_1`, direction rule |
| `split_strategy` | chronological fractions or walk-forward config |
| `model_name` | naive / lr / rf / gb / lstm / … |
| `model_version` | Registry version or artifact semver |
| `hyperparameters` | JSON-serializable train/model params |
| `random_seed` | Reproducibility seed |
| `code_version` | git commit SHA |
| `training_timestamp` | UTC start/end |
| `evaluation_period` | OOS window(s) |
| `metrics` | Dict of metric_name → value with split label |
| `artifact_paths` | URIs for weights, preds, reports |
| `notes` | Human caveats (costs, assumptions) |

Optional but recommended:

- `data_provider` + `adjustment_policy` (`raw` vs `adjusted`)  
- `purge_horizon` / `embargo`  
- `cost_model` parameters  
- `environment` (CPU/GPU, library versions lockfile hash)  

---

## Mapping to current schema (gap analysis)

Existing PostgreSQL models (`backend/app/db/models/`) already store experiments, metrics, walk-forward runs, predictions, backtests — a **partial** foundation.

Likely gaps vs contract (to address in Phase 2–4, not now):

- explicit `dataset_version` / content hash  
- `code_version` commit capture  
- feature_set versioning  
- model registry version distinct from catalog name  
- artifact URI table  
- adjustment/provider policy fields  

Do not claim full provenance until these are populated automatically.

---

## Provenance rules

1. **No metric without an `experiment_id`.**  
2. UI copy must link or at least display experiment identity for OOS metrics.  
3. Regenerating a report requires the same provenance fields or a new experiment id.  
4. Placeholder reports (`render_final_research_report(None)`) must remain obviously empty.  
5. Test fixture metrics are never copied into production report docs.  

---

## Minimal API/JSON shape (illustrative)

```json
{
  "experiment_id": "uuid",
  "code_version": "gitsha",
  "dataset": {
    "dataset_id": "yahoo_ohlcv_aapl",
    "dataset_version": "sha256:…",
    "symbol": "AAPL",
    "data_period": {"start": "2015-01-01", "end": "2024-12-31"},
    "provider": "yahoo",
    "adjustment_policy": "unadjusted"
  },
  "features": {"feature_set": "default_v1"},
  "target": {"name": "future_return", "horizon": 1},
  "split_strategy": {"type": "walk_forward", "config": {}},
  "model": {"name": "lstm", "version": "1", "hyperparameters": {}, "random_seed": 42},
  "evaluation_period": {"folds": "oos_union"},
  "metrics": [{"split": "oos", "name": "rmse", "value": null}],
  "artifact_paths": {"predictions": "s3://…", "checkpoint": "s3://…"}
}
```

Values above are illustrative. **Do not treat as real results.**

---

## Acceptance for “reproducible empirics”

An empirical claim may be published only if:

1. Provenance record is complete for required fields,  
2. Code version is recorded,  
3. Dataset version is recoverable or re-fetch policy is documented,  
4. Metrics match recomputation within documented tolerance,  
5. Report clearly states assumptions and limitations.  
