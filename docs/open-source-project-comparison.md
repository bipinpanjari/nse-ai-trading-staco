# Open Source Project Comparison
1. **VectorBT**: Excellent for vectorized backtesting and parameter sweeps. Will use for research mode.
2. **FinRL**: Great for financial data processing and RL. **Will not use for core strategy** as we need rule-based, transparent signals first.
3. **FinRL-Trading**: Good architectural reference for separation of research, backtest, and execution layers.
4. **Alpaca/IBKR SDKs**: Crucial for execution layer adapters. Must not be hardcoded into the domain.
5. **FinBERT**: Highly suitable for financial news sentiment analysis. Use as an input, not a sole decision maker.
6. **Freqtrade/Backtrader**: Excellent references for event-driven execution and risk controls. Avoid direct code copying if GPL licensing conflicts.
7. **TA-Lib/pandas-ta**: Standard, reliable indicator libraries. Will reuse extensively.
8. **TimescaleDB**: Ideal for OHLCV storage and time-series indexing.
