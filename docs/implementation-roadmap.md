# Implementation Roadmap
1. **Phase 1: Stabilization & Refactoring**:
   - Refactor `app.py` into smaller blueprints.
   - Implement Provider interfaces (Data, Broker).
   - Add unit tests for core math/risk.
2. **Phase 2: Persistence & Audit**:
   - Add SQLite database.
   - Implement Trade and Position ORM models.
   - Save agent signals and trades for auditing.
3. **Phase 3: Security & Auth**:
   - Add JWT auth.
   - Secure broker keys.
4. **Phase 4: Advanced Features**:
   - Live AI agent optimization.
   - Advanced reporting frontend.
