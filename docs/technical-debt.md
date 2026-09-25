# Technical Debt
- **Tight Coupling**: `app.py` has too much logic mixed between websocket streaming, simulation loops, and HTTP routes.
- **Hardcoded State**: The `broadcast_loop` maintains state in global variables which is not scalable or stateless.
- **Lack of Tests**: No unit tests exist for core mathematical calculations and agent logic.
- **Missing Interfaces**: Agents and broker connections do not use formal abstract base classes, making mocking difficult.
