# Acceptance Criteria for First MVP
- Codebase is cleanly separated (API, Domain, Providers).
- System can ingest a static CSV of historical NSE data and run the Strategy Agent to produce a reproducible list of signals.
- System can execute a mock trade through a `MockBrokerProvider` and record it in a SQLite database.
- Frontend can display the historical trades and current mock portfolio.
- At least 50% unit test coverage for core business logic (risk, math).
