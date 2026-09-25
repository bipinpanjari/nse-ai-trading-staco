# API Plan
- `GET /api/v1/market/status`: Market open/close status.
- `GET /api/v1/market/feed?symbol=NIFTY`: Real-time data websocket/polling.
- `GET /api/v1/agents/status`: Health check for AI agents.
- `GET /api/v1/portfolio/summary`: Current holdings and PnL.
- `POST /api/v1/trades/place`: Place manual/override trade.
- `GET /api/v1/trades/history`: Audit log of all trades.
