## FastAPI Authentication Example

![CI](https://github.com/torbet/fastapi-auth-example/actions/workflows/tests.yml/badge.svg)

A simple authentication API built with FastAPI, SQLAlchemy, and PostgreSQL, providing endpoints for user registration and login.

> Note: The original assignment requested Flask; this implementation uses FastAPI instead, while still fulfilling the same API contract and database requirements.

### Project Structure

```
fastapi-auth-example
├── migrations                      # Alembic database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── 7dfc9f79011c_initial_migration.py
├── src
│   └── app
│       ├── __init__.py
│       ├── core                    # Application configuration & utilities
│       │   ├── app.py              # FastAPI app instance + router loading
│       │   ├── config.py           # Environment variables & settings
│       │   ├── database.py         # Async SQLAlchemy engine & session setup
│       │   ├── dependencies.py     # Common FastAPI dependencies
│       │   └── security.py         # Auth helpers: hashing, JWT, OAuth cookie
│       ├── models                  # SQLAlchemy ORM models
│       │   └── user.py
│       ├── routers                 # API route handlers
│       │   └── auth.py             # /auth routes (register, login, me, logout)
│       └── schemas                 # Pydantic schemas for validation & responses
│           ├── auth.py
│           └── user.py
├── alembic.ini                     # Alembic configuration
├── compose.yml                     # Local Postgres + app + migrations via Docker
├── Dockerfile                      # Application container build with uv
├── pyproject.toml                  # Dependencies & entrypoint
├── README.md                       # Documentation
└── uv.lock                         # Locked dependencies
```

### Features

#### Core Features

| Endpoint         | Method | Description                   |
| ---------------- | ------ | ----------------------------- |
| `/auth/register` | POST   | Register a new user           |
| `/auth/login`    | POST   | Authenticate an existing user |

Passwords are securely hashed before storage.

On successful login, an HTTP-only `token` cookie is set with the JWT-encoded credentials.

#### Additional Features

| Endpoint       | Method | Description                                  |
| -------------- | ------ | -------------------------------------------- |
| `/auth/me`     | GET    | Retrieve details of currently logged in user |
| `/auth/logout` | GET    | Logout currently logged in user              |

### Setup & Installation

#### Requirements

- Docker installed and running
- UV (Python package manager)

#### Run with Docker

1. Create environment config:

```bash
cp .env.example .env
```

2. Build & start the app:

```bash
docker compose up --build
```

This will automatically:

- Start PostgreSQL
- Apply Alembic migrations
- Launch the FastAPI backend

To stop everything:

```bash
docker compose down -v
```

> `-v` clears the database volume for a fresh start

#### Manual Setup Instructions

1. Sync dependencies and activate virtual environment:

```bash
uv sync
source .venv/bin/activate
```

2. Create environment config:

```bash
cp .env.example .env
```

3. Start PostgreSQL database via Docker:

```bash
docker compose up -d database
```

4. Apply alembic database migrations:

```bash
alembic upgrade head
```

5. Start the FastAPI server:

```bash
uv run start
```

The API will be available at `http://localhost:8000` with an interactive Swagger UI at `http://localhost:8000/docs`

### Example Requests

I would recomend playing around with the `/docs` page, but here are some quick curl commands to get started!

#### Register

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My name",
    "email": "user@example.com",
    "password": "test123"
  }'

```

#### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "test123"
  }' \
  -i
```

#### Full Flow

Login and store cookies:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "test123"}' \
  -c cookies.txt
```

Call `/auth/me` sending stored cookie::

```bash
curl http://localhost:8000/auth/me \
  -b cookies.txt
```

### Testing

This project includes a full test suite using pytest, FastAPI’s TestClient, and an in-memory SQLite test database.

It also included a github action workflow to automatically run these tests on push to main branch.

Install test dependencies:

```bash
uv sync --group dev
```

Run the tests:

```bash
uv run pytest
```

Tests automatically:

- Spin up an isolated in-memory SQLite database (no external DB required)
- Override the app’s database dependency
- Exercise all authentication endpoints:
  - `/auth/register`
  - `/auth/login`
  - `/auth/me`
  - `/auth/logout`

### Tech Stack

- **FastAPI** - API framework
- **SQLAlchemy** - ORM
- **Alembic** - database migrations
- **PostgreSQL** - persistent database
- **Docker Compose** - running infrastructure services
- **Argon2** - password hashing
