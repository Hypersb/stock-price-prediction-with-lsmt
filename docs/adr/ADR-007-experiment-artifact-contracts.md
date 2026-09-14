# ADR-007: Experiment and artifact contracts without an experiment platform

## Context

Prompt 1 found incomplete provenance and empty empirics. Building MLflow/W&B now would add operational weight before the contract is enforced in code paths.

## Decision

Introduce minimal in-repo contracts (`ExperimentSpec`, `ArtifactRef`, `DatasetSpec`, prediction records) under `ml/contracts/`. Persist richer schema later (Phase 4 product roadmap). Do not invent metrics to fill contracts.

## Alternatives

1. Adopt MLflow immediately  
2. Continue with ad-hoc dicts only  
3. Block all research until a full registry ships  

## Consequences

- Provenance fields are typed and testable now  
- UI/DB can adopt fields incrementally  
- Operators must still run real experiments to populate results  
