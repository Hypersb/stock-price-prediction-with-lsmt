# Product Definition

**Product name (working):** Fold — AI-Powered Quantitative Research & Market Intelligence Platform  
**Repository heritage:** Began as a Stock Price Prediction with LSTM research codebase; evolved into a modular quantitative research platform.  
**Positioning:** Research and analytics platform. **Not** trading advice. **Not** guaranteed prediction.

---

## Problem

Serious quantitative research requires leakage-safe pipelines, baseline comparisons, walk-forward evaluation, cost-aware backtests, and traceable artifacts. Ad-hoc notebooks and “LSTM demos” routinely:

- leak future information,
- overfit test periods,
- hide negative results,
- and present unverifiable metrics.

Students, practitioners, and researchers need a platform that makes the *honest* path the default path.

---

## Target users

1. Students learning quantitative finance / time-series ML  
2. Quantitative researchers prototyping signal ideas  
3. Technically sophisticated retail investors who want research tooling (not tips)  
4. ML practitioners applying models to financial data carefully  
5. Financial-data researchers studying features, regimes, and robustness  

Non-users (for now): discretionary traders seeking buy/sell alerts as a product promise; regulated advisory clients; HFT firms.

---

## Core use cases

1. Ingest and inspect historical market data for a symbol/universe  
2. Engineer and explore leakage-aware features  
3. Train and compare baselines vs LSTM under chronological rules  
4. Run walk-forward validation and inspect OOS predictions  
5. Backtest signals with transaction costs and risk metrics  
6. Persist experiments and review them in a research dashboard  
7. Produce research reports that can conclude “no edge found”  
8. (Future) query research artifacts in natural language with evidence citations  
9. (Future) incorporate news/NLP features with strict temporal alignment  
10. (Future) monitor deployed research models for drift/decay  

---

## Non-goals

- Guaranteed profitable trading  
- Brokerage execution / live order routing (unless explicitly added later as paper-only)  
- “What should I buy?” recommendations  
- Hiding negative LSTM results  
- Presenting in-sample metrics as out-of-sample performance  
- Claiming real-time data without a documented freshness SLA  
- Building microservices for prestige  

---

## Research philosophy

- Negative results are first-class outcomes.  
- Every important metric must be traceable to an experiment.  
- Diagnostics (regimes, permutation importance, sensitivity) are not causal proof.  
- Prefer simple baselines before complex models.  

---

## ML philosophy

- Chronological evaluation by default.  
- Train-only preprocessing.  
- Purge/embargo for label horizons in walk-forward.  
- No test-set hyperparameter shopping.  
- Predictions are uncertain model outputs, never financial guarantees.  

---

## Financial-data philosophy

- Provider quality limits are product limits.  
- Corporate actions, survivorship, and revisions must be documented.  
- “Real-time” is a defined freshness contract, not a marketing word.  
- Costs and fills in backtests are research assumptions, not broker truth.  

---

## Safety / disclaimer philosophy

Always communicate:

> This platform is for research and education. It is not financial advice. Model outputs are uncertain. Past simulated performance does not imply future results.

UI and docs must not fabricate wins.

---

## Product differentiation

| Typical LSTM demo | This platform |
|-------------------|---------------|
| Single notebook accuracy | Walk-forward + baselines + costs |
| Hidden leakage | Explicit anti-leakage engineering |
| Cherry-picked charts | Empty states over fake P&L |
| “AI picks stocks” | Evidence-first research tooling |

---

## MVP definition (near-term product MVP)

An MVP for the **startup transformation** is reached when:

1. Architecture/domain docs govern development (Phase 1)  
2. At least one reproducible multi-model experiment is persisted with provenance (Phase 2)  
3. Training/evaluation pipelines are operable as jobs with artifact storage (Phases 3–4)  
4. Dashboard shows only provenance-backed metrics  
5. Auth is not required for local research MVP, but production deploy path is defined  

**Current repo status vs MVP:** strong research engine + API/UI shell; **missing** executed provenance-backed empirics, jobs, auth, monitoring, news/NLP, portfolio.

---

## Post-MVP capabilities

Mapped to roadmap Phases 5–15:

- Drift/monitoring  
- News + NLP intelligence  
- AI research copilot (evidence-grounded)  
- Risk engine expansion  
- Portfolio intelligence  
- Real-time/event infrastructure  
- Users, watchlists, saved research, alerts  
- Hardened security, observability, cloud launch  

---

## Naming note

UI currently brands “fold”. Product docs may use that brand while the git repo retains historical naming. Avoid implying the product predicts markets with certainty.
