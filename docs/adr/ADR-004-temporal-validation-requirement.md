# ADR-004: Temporal validation requirement

## Context

Financial ML fails silently under leakage: shuffled splits, scaler fit on future rows, and label horizons overlapping test partitions. This repository already implements chronological splits and walk-forward purging as core methodology.

## Decision

All predictive research claims must use **temporal validation**: chronological partitions and/or walk-forward evaluation with train-only preprocessing and horizon-aware purging. Random splits of time-ordered financial rows are forbidden for reported results. Test-set hyperparameter shopping is forbidden.

## Alternatives

1. Sklearn default random `train_test_split` for convenience  
2. Report in-sample training metrics as primary results  
3. Tune on final test fold  

## Consequences

- Diagnostics that use weaker splits must be labeled non-primary  
- Config validation should reject unsafe combinations as pipelines harden  
- Some “accuracy” demos become harder — that is intentional  
