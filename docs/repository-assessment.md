# Repository Assessment
## Application Purpose

The application is a multi-agent AI trading system for the Indian Stock Market (NSE), capable of monitoring real-time data, performing advanced technical analysis, processing news and global cues, running algorithmic risk management, generating trade signals, and executing them on brokers like Dhan and Zerodha.

The primary users are algorithmic traders, institutional investors, and retail traders interested in systematic AI-driven trading on the NSE.

The main problem it solves is the complexity of monitoring multiple data sources (price, technicals, options chains, news, institutional flows) simultaneously and making disciplined, risk-managed trading decisions without emotional bias.

The expected final result is a robust, reliable, and testable trading platform that runs autonomously, provides clear rationale for its trades, allows for human oversight and review (paper trading / live switch), and handles broker integrations smoothly.


## Current Features
- Multi-agent AI architecture (Market Analyst, News Analyst, Risk Manager, Macro Analyst, Portfolio Manager, Execution Agent, Strategy Agent, Discovery Agent).
- Real-time market data feed & pre-market gap engine.
- Live F&O screener.
- Catalyst hunter (results, order wins).
- Institutional flow analyzer.
- ATM options engine with Greeks.
- Zerodha Kite & Dhan API integration.
- Flask backend with Socket.IO for real-time updates.
- React/Vite frontend.

## Architecture
- Backend: Flask, Flask-SocketIO, Pandas, TA-Lib/pandas-ta, Scikit-learn, Ollama (AI).
- Frontend: React, Vite, Tailwind, Recharts.
- Data Flow: NSE -> Live Feed Module -> Agents (Analysis/Risk/Strategy) -> Socket.IO -> Frontend.

## Technical Debt & Risks
- Error handling in API endpoints needs strengthening.
- Security: API keys and secrets might be exposed if not careful with `.env`. Need robust secret management.
- Testing strategy is mostly backtests (`run_backtest.py`), needs unit/integration tests.
- Mock/Simulated data is deeply intertwined with live data in `app.py`. Needs cleaner separation (adapters).

## Reusability & Refactoring
- The agent classes are good but could use standard interfaces (e.g., standardizing `analyze()` returns).
- `app.py` is monolithic (340+ lines). Should be split into route files (blueprints).
- Broker integrations (`kite_connector.py`, `dhan_api.py`) should implement a common `BrokerProvider` interface.
