# Target Architecture
## Layers
1. **Frontend**: React/Vite dashboard for research, paper trading, and approval workflows.
2. **API**: FastAPI or Flask Blueprints routing to specific domains (Analysis, News, Orders).
3. **Services Layer**:
   - `MarketDataService` (ingestion, normalization).
   - `AnalysisService` (pandas-ta, FinBERT integration).
   - `StrategyEngine` (generates `TradeIdea`).
   - `RiskEngine` (pre-trade checks, max loss).
4. **Providers Layer (Adapters)**: `IBKRBroker`, `PaperBroker`, `YahooData`, `NSEData`.
5. **Storage**: TimescaleDB for time-series, PostgreSQL/SQLite for relational data (Orders, Journals).
