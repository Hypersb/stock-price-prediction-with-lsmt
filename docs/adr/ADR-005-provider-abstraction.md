# ADR-005: Provider abstraction for market data

## Context

Market data currently comes from Yahoo Finance via yfinance. Quality, licensing, adjustment policy, and availability will change as the product grows. Hardcoding Yahoo types through the stack would block licensed feeds and testing.

## Decision

All market-data access goes through a **provider abstraction** (`MarketDataProvider`) with request validation, normalization, and schema validation before research code consumes frames. New vendors implement the interface; research code depends on normalized OHLCV, not vendor payloads.

## Alternatives

1. Call yfinance directly from API routes and notebooks  
2. Build a fully normalized commercial data lake on day one  
3. Support only CSV uploads  

## Consequences

- Fake providers remain the unit-test strategy  
- Adjustment/freshness policy becomes provider+ingestion metadata  
- Switching providers still requires scientific re-validation of empirics  
