# Testing Strategy
1. **Unit Tests**: Test indicators, risk math, and agent logic with mocked data.
2. **Integration Tests**: Test BrokerProvider adapters with sandbox/paper APIs. Test DataProviders with fixed static JSON fixtures.
3. **E2E Tests**: Test full flow from DataProvider (mocked) to Strategy to Order (mocked broker).
4. **Backtesting Validation**: Ensure backtest engine matches live paper-trading results over identical historical periods (Golden tests).
