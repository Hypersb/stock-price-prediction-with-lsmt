# ADR-002: Financial research, not trading advice

## Context

The product uses forecasting models, backtests, and market data. Users may misread research outputs as buy/sell recommendations. Legal and ethical risk is high if the product implies guaranteed profits or personalized advice.

## Decision

Position the system as an **AI-powered quantitative research and market-intelligence platform**. Predictions are uncertain model outputs. The product must not promise profitable trades, and UI/docs must prefer empty/negative results over fabricated wins.

## Alternatives

1. Consumer “stock picker” positioning  
2. Brokerage/robo-advisor product  
3. Signal marketplace with performance marketing  

## Consequences

- Disclaimers and honest empty states are mandatory  
- Marketing language is constrained  
- Features like alerts must be framed as research notifications, not advice  
