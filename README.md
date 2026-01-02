NeuroNetComplete
=================

NeuroNetComplete is the full-stack reference implementation for the NeuroNet platform — a modular system for training, serving, and evaluating neural models with an emphasis on reproducibility and deployment simplicity.

Key features
- Full docker-compose stack for local development and testing
- API service (FastAPI / Uvicorn suggested)
- Background worker (Celery/RQ) for async tasks
- PostgreSQL for persistent storage
- Redis for caching / task broker
- Frontend (React/Vite) served during development and via Nginx in production

Quickstart
1. Copy the example environment file and customize:
   cp .env.example .env
   Edit .env to configure DB/REDIS/PGADMIN credentials and API URLs.

2. Build and start the full stack:
   docker-compose up --build

3. Access services:
- Frontend: http://localhost:3000 (or http://localhost for nginx proxy)
- API: http://localhost:8000
- PGAdmin: http://localhost:8081 (use PGADMIN_DEFAULT_EMAIL / PASSWORD)

Development notes
- The repo expects the following directories for local builds:
  - ./api        -> API service Dockerfile and source
  - ./worker     -> background worker service
  - ./frontend   -> frontend app Dockerfile and source
  - ./nginx      -> nginx config and extra static assets

- When building locally, the frontend build artifacts are copied to the frontend_build volume which nginx mounts in production mode. Adjust Dockerfiles to write the production build to /app/build or similar.

Environment
- Use .env for runtime configuration. Example keys:
  - POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
  - PGADMIN_DEFAULT_EMAIL, PGADMIN_DEFAULT_PASSWORD
  - REACT_APP_API_URL

Testing
- Unit tests for API should live under ./api/tests and can be run with pytest inside the api container:
  docker-compose run --rm api pytest -q

Cleanup
- A helper script is provided at scripts/cleanup.sh to safely tear down the stack and remove local volumes/images. Review it before running.

Contributing
- Open issues and PRs on the repository. Follow the existing code style and include tests for new functionality.

License
- Specify license details here.
