# Security Architecture
- **API Gateway**: Handles rate limiting and JWT verification.
- **Role-Based Access Control (RBAC)**: Differentiates between Viewers and Administrators.
- **Secret Storage**: Use AWS Secrets Manager or HashiCorp Vault in production.
- **Data Masking**: Redact API keys and PII in logs.
