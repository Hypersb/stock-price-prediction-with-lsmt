# Price Basis Policy

**Status:** CURRENT  
**Default research price basis:** **unadjusted** Yahoo `close` (`auto_adjust=False`)

## Why this is explicit

Prompt 1 flagged unadjusted Yahoo data as HIGH technical debt (TD-001). Silently
switching all historical research to adjusted closes would invalidate prior
methodology without a controlled migration.

## CURRENT contract

| Field | Meaning |
|-------|---------|
| `open/high/low/close/volume` | Required unadjusted OHLCV from Yahoo when `auto_adjust=False` |
| `adj_close` | Optional; retained when the provider supplies Adj Close |
| `MarketDataSemantics.adjustment_policy` | Default `unadjusted` |
| Research features/targets | Use `close` unless a run opts into adjusted semantics |

## Allowed future change

A future experiment may set `adjustment_policy=adjusted` and require `adj_close`,
with a new dataset fingerprint and explicit report documentation. That change
must not rewrite past experiment artifacts.
