# Startup Roadmap (15 Phases)

This is the **new** product roadmap for transforming the repository into a production-ready quantitative research platform. It supersedes the legacy “core phases 1–15 complete” engineering narrative for planning purposes. Legacy completion means the research engine foundation exists; it does **not** mean the startup platform is launched.

Do not implement future phases in Prompt 1.

---

## Phase 1 — Startup Foundation & Architecture

- **Objective:** Establish truthful baseline, product boundaries, architecture, and trackers  
- **Why:** Prevent feature thrash and fake completeness  
- **Deliverables:** `docs/startup/*`, ADRs, README discipline, Phase 1 tracker  
- **Dependencies:** Existing repo  
- **Exit criteria:** Prompt 1–10 complete; docs reference real paths; no fabricated metrics  

## Phase 2 — Empirical Research & Reproducibility

- **Objective:** Execute and record at least one honest multi-model experiment with provenance  
- **Why:** Empirics are currently placeholders  
- **Deliverables:** Provenance-populated experiment(s), updated final report from real run, dataset versioning policy  
- **Dependencies:** Phase 1 contracts  
- **Exit criteria:** Class-A metrics exist with recoverable config/code/data policy; negatives allowed  

## Phase 3 — Production ML Pipeline

- **Objective:** Harden training/evaluation pipelines (purge on single splits, config enforcement, artifact packaging)  
- **Why:** Methodology gaps remain (TD-003, TD-005, adjustment policy)  
- **Deliverables:** Pipeline entrypoints, stricter validation, pinned runtime deps  
- **Dependencies:** Phase 2 provenance fields  
- **Exit criteria:** Leakage tests green; configs reject unsafe combos  

## Phase 4 — Experiment Tracking & Model Registry

- **Objective:** Replace hardcoded catalog with versioned registry metadata  
- **Why:** Lifecycle score is near-zero  
- **Deliverables:** Registry schema, artifact URIs, experiment UI linkage  
- **Dependencies:** Phases 2–3  
- **Exit criteria:** UI `trained`/versions reflect real artifacts  

## Phase 5 — Model Monitoring & Drift Detection

- **Objective:** Detect feature/prediction drift and performance decay  
- **Why:** Models go stale; silent failure is unacceptable  
- **Deliverables:** Monitors, alert hooks (basic), dashboards  
- **Dependencies:** Phase 4 serving predictions  
- **Exit criteria:** Drift jobs run on schedule with stored diagnostics  

## Phase 6 — Financial News Data Platform

- **Objective:** Ingest timestamped financial news  
- **Why:** Alternative data for research — only with PIT discipline  
- **Deliverables:** News schema, ingest jobs, storage  
- **Dependencies:** Jobs foundation ideally started; can begin schemas earlier  
- **Exit criteria:** News retrievable by time/symbol without leaking future text into past features  

## Phase 7 — Financial NLP & Sentiment Intelligence

- **Objective:** Sentiment/theme features with temporal alignment  
- **Why:** NLP without alignment is leakage  
- **Deliverables:** NLP models/pipelines, feature contracts  
- **Dependencies:** Phase 6  
- **Exit criteria:** NLP features pass leakage tests  

## Phase 8 — AI Research Copilot

- **Objective:** Evidence-grounded natural-language research over artifacts  
- **Why:** Differentiate as research intelligence, not tip bot  
- **Deliverables:** Copilot API that cites experiment ids; refusal on missing evidence  
- **Dependencies:** Phases 2–4  
- **Exit criteria:** Cannot invent metrics; answers cite provenance  

## Phase 9 — Quantitative Risk Engine

- **Objective:** Expand risk analytics beyond basic Sharpe/DD  
- **Why:** Research users need coherent risk domain  
- **Deliverables:** Risk service module, tests, API  
- **Dependencies:** Backtest results provenance  
- **Exit criteria:** Risk metrics tested and documented (annualization policy clear)  

## Phase 10 — Portfolio Intelligence

- **Objective:** Multi-asset portfolio analytics (not broker execution)  
- **Why:** Bridge from single-name research to portfolio views  
- **Deliverables:** Holdings/analytics modules, UI views  
- **Dependencies:** Phases 3, 9  
- **Exit criteria:** Portfolio metrics reproducible; no advice language  

## Phase 11 — Real-Time Data & Event Infrastructure

- **Objective:** Defined near-real-time freshness + event ingestion  
- **Why:** “Real-time” must be contractual  
- **Deliverables:** Streaming/event bus or polling with SLA docs  
- **Dependencies:** Market data domain maturity  
- **Exit criteria:** Freshness SLO documented and measured  

## Phase 12 — User Platform, Watchlists & Saved Research

- **Objective:** Accounts, watchlists, saved views/experiments  
- **Why:** Multi-user product requirements  
- **Deliverables:** Authn, user schema, watchlists, saved research  
- **Dependencies:** Security baseline starting  
- **Exit criteria:** User data isolated; public anonymous mode explicit  

## Phase 13 — Alerts, Jobs & Automation

- **Objective:** Background jobs, schedules, alert delivery  
- **Why:** Research automation without blocking HTTP  
- **Deliverables:** Worker, scheduler, alert rules  
- **Dependencies:** Phase 12 identity; Phase 5 monitors optional  
- **Exit criteria:** Long WF/training runs execute as jobs with status  

## Phase 14 — Security, Reliability & Production Backend

- **Objective:** Harden API security, rate limits, secrets, HA patterns  
- **Why:** Public exposure currently unsafe  
- **Deliverables:** Authz audits, Redis if needed, backup/restore, abuse controls  
- **Dependencies:** Phases 12–13  
- **Exit criteria:** Security checklist passed; no secret leakage  

## Phase 15 — Cloud Deployment, Observability & Launch Readiness

- **Objective:** Deployable cloud environment with observability  
- **Why:** Launch requires ops reality  
- **Deliverables:** IaC/deploy docs, metrics/traces/alerts, runbooks  
- **Dependencies:** Phase 14  
- **Exit criteria:** Staging deploy healthy; dashboards live; launch checklist signed  

---

## Sequencing note

Phases are numbered for governance, not strict total order. Limited parallelization is allowed when dependencies are respected (e.g., docs vs code). Empirics (Phase 2) should precede marketing claims always.
