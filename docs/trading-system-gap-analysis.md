# Trading System Gap Analysis
## What is missing for a production-ready research & paper-trading system:
1. **Database**: No time-series database (TimescaleDB) or relational database for trade journals/audit logs.
2. **Backtesting Framework**: Current backtester is a simple script. Needs integration with a robust engine like VectorBT or Backtrader.
3. **Execution Engine**: No proper separation between Research, Paper Trading, and Live execution.
4. **Risk Controls**: Lacks hard-coded, mandatory pre-trade risk checks (max daily loss, max order value) independent of AI agents.
5. **Data Freshness & Confidence**: No tracking of data freshness or evidence scoring for AI decisions.
6. **User Interaction**: No UI for users to reject, edit, or approve AI-generated trade ideas.
