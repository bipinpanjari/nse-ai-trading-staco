# Implementation Roadmap
## Phase 1: Research Only (Current MVP)
- Build the data ingestion pipeline (Adapters).
- Implement TimescaleDB storage.
- Build the UI for historical charting and basic TA indicators.

## Phase 2: Signal Generation & Backtesting
- Integrate VectorBT for backtesting.
- Implement FinBERT for sentiment analysis.
- Generate `TradeIdea` objects based on rule-based strategies.

## Phase 3: Paper Trading & Human Approval
- Implement `PaperBroker` adapter.
- Build UI for reviewing, approving, and rejecting AI trade ideas.
- Implement strict Risk Engine checks.

## Phase 4: Live Trading (Disabled by Default)
- Implement `IBKRBroker` or live `DhanBroker` adapters.
- Add robust account verification and kill switches.
