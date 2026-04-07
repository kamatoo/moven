# FastAPI Template

A production-oriented FastAPI starter template with:

- FastAPI + SQLAlchemy 2
- PostgreSQL
- Alembic migrations
- JWT auth with roles
- seed admin for development
- Docker + docker compose
- tests with an isolated test database
- clean separation of API, services, repositories, schemas, and database models

## What's Included?

This template already includes the things you usually need in a real project:

- `GET /health` for liveness
- `GET /ready` for readiness including a database check
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/users` admin only
- `GET /api/v1/users/{user_id}` self or admin
- `PUT /api/v1/users/{user_id}` self or admin
- `DELETE /api/v1/users/{user_id}` self or admin

## Project Structure

```text
app/
  api/              FastAPI routers, dependencies, endpoints
  core/             settings, logging, security
  db/               SQLAlchemy base, session, models
  repositories/     data access layer
  schemas/          Pydantic request/response models
  services/         business logic
alembic/            migrations
tests/              API and service tests
```

## Requirements

- Python 3.12+
- Docker Desktop or Docker Engine
- optional: a virtual environment

## Recommended Startup: Docker

This template is intended to be started with Docker by default.

### 1. Create the environment file

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

CMD:

```cmd
copy .env.example .env
```

### 2. Start the full stack

```powershell
docker compose up --build
```

After that:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

Important:

- the API container runs migrations automatically on startup
- the API container uses the Docker database host `db:5432`
- CORS origins can be configured with `CORS_ALLOW_ORIGINS` as a comma-separated list
- auth uses a JWT in an HttpOnly cookie by default, configurable via `AUTH_COOKIE_*`
- the seed admin is created on startup if enabled

If you want a completely fresh start:

```powershell
docker compose down -v
docker compose up --build
```

## Local Development Without Docker

Use this only if you explicitly want to run the API directly on your machine instead of through Docker.

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate
```

### 2. Create the environment file

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

CMD:

```cmd
copy .env.example .env
```

For local non-Docker execution, `.env` points to:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/app_db
CORS_ALLOW_ORIGINS=http://localhost:5174,http://127.0.0.1:5174
AUTH_COOKIE_NAME=access_token
AUTH_COOKIE_SECURE=false
AUTH_COOKIE_SAMESITE=lax
```

### 3. Install dependencies

```powershell
python -m pip install -e .[dev]
```

### 4. Start the database

```powershell
docker compose up -d db
```

### 5. Run migrations

```powershell
python -m alembic upgrade head
```

### 6. Start the API directly

```powershell
python -m uvicorn app.main:app --reload
```

After that:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

Important:

- locally outside Docker, `.env` uses `localhost`
- inside Docker, `docker-compose.yaml` overrides `DATABASE_URL` to use `db:5432`

## Seed Admin

For development, an admin user is created on startup by default if no user with that email exists yet.

Default values from `.env`:

- `SEED_ADMIN_ENABLED=true`
- `SEED_ADMIN_NAME=Admin User`
- `SEED_ADMIN_EMAIL=admin@example.com`
- `SEED_ADMIN_PASSWORD=admin123456`

You can log in with these credentials right away.

Important:

- seeding is idempotent
- if the user already exists, it will not be created twice
- for production, you should disable this or override the values

## First Login

### Option 1: via Swagger

1. Open `http://127.0.0.1:8000/docs`
2. Run `POST /api/v1/auth/login`
3. Username: `admin@example.com`
4. Password: `admin123456`
5. Copy the access token
6. Click `Authorize` in the top right
7. Paste `Bearer <token>`

### Option 2: via HTTP

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123456"
```

## Important Commands

Run tests:

```powershell
python -m pytest -p no:cacheprovider
```

Run lint:

```powershell
python -m ruff check . --no-cache
```

Create a new migration:

```powershell
python -m alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```powershell
python -m alembic upgrade head
```

## What Do `health` and `ready` Mean?

- `/health`: the app is basically alive
- `/ready`: the app is actually ready to serve traffic and can reach the database

These endpoints are important for Docker, orchestration, load balancers, and monitoring.

## How to Extend the Template Cleanly

When you add a new feature, follow this structure:

1. add a new database model in `app/db/models/`
2. add Pydantic schemas in `app/schemas/`
3. add data access logic in `app/repositories/`
4. add business logic in `app/services/`
5. add the endpoint in `app/api/v1/endpoints/`
6. register the route in `app/api/router.py`
7. create an Alembic migration
8. write API and service tests in `tests/`

The goal is:

- endpoints stay thin
- services contain business logic
- repositories encapsulate database access
- schemas define API contracts

## Typical Next Steps for Real Projects

If you want to push this template further, these are strong next additions:

- refresh tokens
- forgot password / reset password flow
- more granular roles and permissions
- pagination and filters
- standardized error responses
- CI pipeline
- observability: structured logs, tracing, metrics
- background jobs with Celery or RQ
- Redis for caching or rate limiting

## Notes About Docker and TLS

The Dockerfile currently uses `pip install` with `--trusted-host` so builds work even in restrictive corporate environments.

This is a workaround. A more secure approach would be:

- trusting your company CA inside the image
- or using an internal PyPI proxy with a proper certificate

## Using This Template for New Projects

If you want to reuse this repository as your standard starter, a good workflow is:

1. keep this template stable
2. copy it for a new project or use it as a template repository
3. adjust `.env` for the new project
4. update the app name, database name, and seed data
5. introduce your first domain models and migrations

That way you are not starting from scratch every time, but from a solid foundation.
