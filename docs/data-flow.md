# Data Flow Architecture
1. **Market Data Feed**: Connects to NSE/Brokers, fetches ticks/candles.
2. **Event Bus**: Distributes data updates to listening agents.
3. **Analysis Agents**: Process data, generate insights.
4. **Strategy Agent**: Aggregates insights, generates trade signals.
5. **Risk Manager**: Validates signals against rules and capital limits.
6. **Execution Agent**: Routes approved orders to the Broker Provider.
7. **Database**: Logs all ticks, signals, and orders for auditing.
