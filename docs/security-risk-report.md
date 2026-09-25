# Security Risk Report
- **Live Trading**: Must be disabled by default via feature flags to prevent accidental real-money losses.
- **API Keys**: Currently stored in `.env`. Must ensure `.env` is never committed.
- **Authentication**: No user authentication exists. Anyone with access to the UI can trigger agent actions.
- **Broker Connections**: Must require explicit manual test and account verification before enabling live mode.
