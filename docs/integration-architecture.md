# Integration Architecture
- **Broker Interface (`BrokerProvider`)**: Abstract methods `get_holdings()`, `place_order()`, `cancel_order()`.
- **Data Interface (`DataProvider`)**: Abstract methods `get_historical_candles()`, `subscribe_live_ticks()`.
- **AI Interface (`AIProvider`)**: Abstract methods `analyze_sentiment()`, `generate_summary()`.
