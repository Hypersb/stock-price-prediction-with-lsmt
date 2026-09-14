# Master Startup Transformation — Execution Plan

**Date:** 2026-09-13  
**Branch:** `main` (local commits only; do not push unless requested)  
**Source of truth:** repository state after Phase 1 Prompts 1–4

## Verified starting baseline

| Check | Result |
|-------|--------|
| Branch | `main` even with `origin/main` |
| Dirty tree | clean |
| Phase 1 tracker | Prompts 1–4 COMPLETE; 5–10 NOT STARTED |
| pytest | 334 passed when Postgres unavailable (skip); flaky fail if `DATABASE_URL` points at down Postgres |
| ruff | clean |
| frontend vitest | 15 passed |
| health | passed |

## Principles

1. Research integrity over impressive numbers  
2. Modular monolith; adapters for external systems  
3. No fabricated empirics, news, monitoring, or user data  
4. Small units → test → commit → continue  
5. Mark external blockers honestly  

## Stage dependency order

```
A Foundation remainder
  → B Market-data integrity
  → C Dataset provenance
  → D Features
  → E Targets / temporal leakage
  → F–L Empirical study + report (critical path)
  → M–R Experiment registry + monitoring
  → S–X News / NLP / ablation (provider-optional)
  → Y–AB AI research tools (evidence-grounded)
  → AC–AJ Portfolio + users + watchlists
  → AK–AO Jobs + cache
  → AP–AX API/frontend product surfaces
  → AY–BF Observability / security / deploy docs
  → BG–BZ Final audits + release decision
```

## Stage A scope (this wave)

Condense Phase 1 Prompts 5–10 into durable foundation without fake completeness:

- Data contracts / schemas docs  
- Persistence boundary docs  
- Error/logging foundation polish  
- Harden Postgres migration smoke (skip on connect failure)  
- Developer workflow + architecture invariants updates  

## Critical path after A

**B → C → E → F–L** must land before claiming research product readiness.  
News/NLP/AI/auth/jobs are valuable but secondary to honest empirics + provenance.

## Release honesty

Default stance: **RELEASE CANDIDATE BLOCKED** until empirics, provenance, auth (or explicit single-user mode), and security baseline are real. Inflating readiness is forbidden.
