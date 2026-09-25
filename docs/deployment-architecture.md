# Deployment Architecture
- **Containerization**: Dockerize backend (Flask) and frontend (Nginx/React).
- **Orchestration**: Docker Compose for local/single-node, Kubernetes for scaling.
- **Database**: Managed RDS (PostgreSQL).
- **Reverse Proxy**: Nginx/Traefik for SSL termination and routing.
