# Security Plan
1. **Secrets**: Use `python-dotenv` properly. Do NOT commit `.env`. Add pre-commit hook for secret scanning.
2. **Auth**: Implement JWT authentication for the Flask API and Frontend.
3. **Broker Keys**: Encrypt broker access tokens at rest.
4. **Input Validation**: Validate all API inputs (e.g., quantity > 0, valid symbols).
