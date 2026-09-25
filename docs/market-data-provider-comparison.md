# Market Data Provider Comparison
1. **Alpaca**: Excellent REST/WebSocket APIs, built-in paper trading. (Good for US markets, less applicable for NSE unless they expand).
2. **Interactive Brokers (IBKR)**: Comprehensive global data (including NSE), robust paper trading. High learning curve, but excellent for institutional grade.
3. **NSE Live Feed (Current)**: Free, but often delayed or rate-limited. Unreliable for high-frequency live trading.
4. **Polygon.io / Yahoo Finance**: Good fallback options for delayed or end-of-day research data.

**Recommendation**: Use IBKR API for robust paper trading and market data via adapters, keep Yahoo/Polygon for fallback research data.
