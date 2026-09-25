# Target Architecture
## Clean Architecture Approach
1. **Core Domain**: Models (Trade, Position, Signal, MarketData).
2. **Interfaces/Adapters**: `DataProvider` (NSE, Yahoo), `BrokerProvider` (Zerodha, Dhan), `AIProvider` (Ollama, OpenAI).
3. **Services**: `TradingEngine`, `RiskEngine`, `BacktestEngine`.
4. **API Layer**: Flask Blueprints (REST + WebSockets).
5. **Frontend**: React UI consuming API Layer.

## Data Flow
Market Data Source -> DataProvider Adapter -> Event Bus -> Agents -> Strategy -> Signal -> RiskManager -> Order -> BrokerProvider.
