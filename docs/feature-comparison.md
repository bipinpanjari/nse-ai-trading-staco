# Feature Comparison
| Feature | Existing Repo | Freqtrade | Recommendation |
|---|---|---|---|
| Domain | NSE Stocks/Options | Crypto | Stick to NSE focus, borrow Freqtrade's plugin architecture |
| Backtesting | Basic script | Advanced (Hyperopt) | Implement standardized backtesting engine inspired by Freqtrade |
| AI Integration | Native (Agents) | Third-party/Custom | Keep native agents, standardise interfaces |
| Broker API | Zerodha/Dhan | Binance/Kraken etc | Abstract broker API to allow easy addition of more NSE brokers |
| Data Storage | In-memory/CSV | SQLite/PostgreSQL | Add SQLite/PostgreSQL for persistent history and audit logs |
