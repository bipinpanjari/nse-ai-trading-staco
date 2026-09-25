# Testing Strategy
- **Unit Tests**: Test indicator calculations (comparing against known TA-Lib outputs), risk limits, and strict business rules.
- **Integration Tests**: Test provider adapters (Broker, Data) against sandbox environments.
- **Backtesting Validation**: Use VectorBT to validate historical performance against known datasets.
- **Paper Trading**: Run the system in paper trading mode continuously as a form of staging/UAT before any human can enable live mode.
