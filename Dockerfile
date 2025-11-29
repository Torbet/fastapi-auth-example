FROM python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Ensure uv uses a project env at /app/.venv
ENV UV_COMPILE_BYTECODE=1
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Install dependencies only (no project, no dev deps)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the code
COPY . .

# Install the project itself (still without dev deps)
RUN uv sync --frozen --no-dev

# Make sure the venv's bin is used
ENV PATH="/app/.venv/bin:$PATH"