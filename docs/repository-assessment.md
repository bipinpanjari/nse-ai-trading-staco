# Repository Assessment
## 1. What the repository currently does
The repository provides a basic AI trading stack for the NSE. It includes multiple specialized AI agents (Market, News, Risk, etc.) operating on simulated or delayed market data, running a technical analysis screener (VWAP, SuperTrend), and broadcasting updates via Flask-SocketIO.

## 2. What can be reused
- The concept of separated AI agents (Market, News, Risk).
- Basic technical indicator calculations (pandas-ta).
- React/Vite frontend scaffold.

## 3. What should be refactored
- `app.py` is a monolithic file mixing routing, websocket streaming, and a blocking `while True` simulation loop. It must be refactored into the target modular architecture.
- Frontend components need to support the new features (Backtesting, Paper Trading vs Live).

## 4. What should be isolated behind adapters
- Broker APIs (Dhan, Zerodha Kite).
- Market Data Feeds (NSE live feed).

## 5. What should be reimplemented
- The `broadcast_loop` simulation. It needs to be replaced with a proper event-driven architecture and real Time-Series Database (e.g. TimescaleDB).
- The risk manager needs stricter, testable rules rather than AI-driven suggestions.
