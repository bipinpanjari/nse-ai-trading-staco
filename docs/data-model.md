# Data Model
- `Trade`: ID, Symbol, Action (BUY/SELL), Qty, Price, Timestamp, Status, AgentRef, Confidence.
- `Position`: ID, Symbol, AvgPrice, Qty, CurrentPrice, PnL, UnrealizedPnL.
- `MarketData`: Symbol, Timestamp, Open, High, Low, Close, Volume, Indicators (JSON).
- `AuditLog`: EventID, Timestamp, Source (Agent/User), Action, Details (JSON).
