## FastAPI Authentication Example

### Project Structure

```
fastapi-auth-example
├── migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions
│       └── 7dfc9f79011c_initial_migration.py
├── src
│   └── app
│       ├── __init__.py
│       ├── core
│       │   ├── app.py
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── dependencies.py
│       │   └── security.py
│       ├── models
│       │   └── user.py
│       ├── routers
│       │   └── auth.py
│       └── schemas
│           ├── auth.py
│           └── user.py
├── alembic.ini
├── compose.yml
├── pyproject.toml
├── README.md
└── uv.lock
```

### Features

#### Core Features

| Endpoint         | Method | Description                   |
| ---------------- | ------ | ----------------------------- |
| `/auth/register` | POST   | Register a new user           |
| `/auth/login`    | POST   | Authenticate an existing user |

Passwords are securely hashed before storage.

#### Additional Features

| Endpoint       | Method | Description                                  |
| -------------- | ------ | -------------------------------------------- |
| `/auth/me`     | GET    | Retrieve details of currently logged in user |
| `/auth/logout` | GET    | Logout currently logged in user              |

### Setup & Installation

#### Requirements

- Docker installed and running
- UV (Python package manager)

#### Setup Instructions

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

### Tech Stack

- **FastAPI** — API framework
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **PostgreSQL** — persistent database
- **Docker Compose** — running infrastructure services
- **Argon2** — password hashing