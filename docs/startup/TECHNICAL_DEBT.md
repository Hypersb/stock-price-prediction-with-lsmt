# Technical Debt Register

Audit date: 2026-09-13 (Prompt 1)  
Updates: Prompt 2–4 on 2026-09-13; Stage A–E foundation on 2026-09-13  

IDs are stable. Do not delete historical entries.

| ID | Severity | Area | Description | Target | P2 | P3 | P4 | Stage |
|----|----------|------|-------------|--------|----|----|-----|-------|
| TD-001 | HIGH | Market data | Unadjusted Yahoo OHLCV default | 2–3 | DEF | DEF | **REDUCED** | **REDUCED** (optional `adj_close` + price-basis policy; research still unadjusted) |
| TD-002 | HIGH | Survivorship | Static universe | 2,10 | DEF | DEF | DEF | DEF |
| TD-003 | HIGH | Splits | Chronological split lacks purge | 3 | DEF | DEF | DEF | **REDUCED** (`forecast_horizon` purge on single splits) |
| TD-004 | HIGH | Backtest | Multi-horizon unsupported | 3,9 | DEF | DEF | **REDUCED** | DEF |
| TD-005 | MEDIUM | Research config | Horizon vs WF desync | 3 | DEF | DEF | DEF | DEF |
| TD-006 | MEDIUM | Provenance | Incomplete experiment contract in DB | 2,4 | DEF | DEF | **REDUCED** | **REDUCED** (dataset fingerprints; DB still partial) |
| TD-007 | MEDIUM | Registry | Catalog trained=False | 4 | DEF | DEF | DEF | DEF |
| TD-008 | MEDIUM | Frontend | Cum chart vs analysis | 1–2 | DEF | DEF | DEF | DEF |
| TD-009 | MEDIUM | Docker pins | Unpinned docker reqs | 3 | **RES** | — | — | — |
| TD-010 | MEDIUM | Node 18 | Vitest fail | 1 | **RES** | — | — | — |
| TD-011 | MEDIUM | Auth | None | 12,14 | DEF | DEF | DEF | DEF |
| TD-012 | MEDIUM | Jobs | None | 13 | DEF | DEF | DEF | DEF |
| TD-013 | LOW | OHLC checks | Missing | 3 | DEF | DEF | DEF | **RESOLVED** |
| TD-014 | LOW | Zero costs default | Optimistic | 3 | DEF | DEF | DEF | DEF |
| TD-015 | LOW | Absolute MAs | Nonstationary | 3 | DEF | DEF | DEF | DEF |
| TD-016 | LOW | Observability | No OTEL | 8,15 | DEF | RED | DEF | DEF |
| TD-017 | LOW | Docs confusion | Legacy phases | 1 | **RES** | — | — | — |
| TD-018 | LOW | Unused API UI | Predictions/POST BT | 7 | RED | DEF | DEF | DEF |
| TD-019 | LOW | Cache | Process TTL | 14 | DEF | DEF | DEF | DEF |
| TD-020 | MEDIUM | Empirics empty | Report placeholders | 2 | DEF | DEF | DEF | DEF |
| TD-021 | LOW | Risk split | analysis vs backtest metrics | 9 | NEW | DEF | DEF | DEF |
| TD-022 | LOW | Timezones | Naive dates | 11 | NEW | DEF | DEF | DEF |
| TD-023 | LOW | `^INDEX` HTTP | Allow-list | 7/11 | NEW | DEF | DEF | DEF |
| TD-024 | LOW | Symbol helpers | Remaining call sites | 3–4 | NEW | DEF | DEF | DEF |
| TD-025 | LOW | Compose password | Placeholder | 14 | — | NEW | DEF | DEF |
| TD-026 | LOW | Dotenv parser | Minimal | 3–8 | — | NEW | DEF | DEF |
| TD-027 | LOW | Architecture | Future domains not packaged | docs | — | — | **NEW** | DEF |

RES=RESOLVED, RED=REDUCED, DEF=DEFERRED, NEW=NEW

## Prompt 4 outcomes

- **RESOLVED:** missing explicit domain dependency map; missing typed internal contracts package; yfinance leakage risk (already confined, now tested); unclear prediction/experiment/artifact shapes  
- **REDUCED:** TD-001, TD-004, TD-006  
- **DEFERRED:** methodology and product debts above  
- **NEW:** TD-027  

## Stage A–E foundation outcomes

- **RESOLVED:** TD-013 OHLC consistency checks  
- **REDUCED:** TD-001, TD-003, TD-006  
- **DEFERRED:** TD-020 empirics (next critical path)  

## Priority order

1. TD-020 + TD-006 empirics/provenance population  
2. TD-001/TD-003/TD-005 methodology  
3. TD-007 registry  
4. TD-011/TD-012 before public deploy  
