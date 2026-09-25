# Security Assessment
- **Secrets Management**: Configuration uses `.env` which is fine, but keys could be leaked if not careful. A secure vault or environment variable injection at runtime is needed for production.
- **Dependency Vulnerabilities**: Need to run `pip audit` and `npm audit` to check for known vulnerabilities in dependencies.
- **Authentication**: No current authentication on the APIs. Open endpoints can be accessed by anyone.
- **Input Validation**: API endpoints trust the request payload. Need strict schema validation (e.g., using Pydantic).
