# ADR-003: Reproducible experiment provenance

## Context

Empirical sections of the research report are placeholders. The platform can compute metrics, but committed attested results do not exist. Without provenance, any future UI number is unverifiable.

## Decision

Adopt a **provenance contract** before expanding empirics: experiment, dataset version, feature set, target, split strategy, model version, hyperparameters, seed, code version, evaluation window, metrics, and artifact paths. No published performance claim without this record.

## Alternatives

1. Ad-hoc notebook screenshots as “results”  
2. Full MLflow/W&B platform immediately  
3. Store metrics only with no dataset/code linkage  

## Consequences

- Phase 2 prioritizes one honest reproducible run over many unverifiable charts  
- Schema/API work must extend existing experiment tables toward the contract  
- Heavier experiment platform tooling can wait until the contract is enforced  
