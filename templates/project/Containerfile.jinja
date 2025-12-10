# =============================================================================
# DEVELOPMENT ONLY - DO NOT USE IN PRODUCTION
# =============================================================================
# This Containerfile is for local development and testing only.
# It uses Django's runserver which is not suitable for production workloads.
# =============================================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
ENV UV_NO_CACHE=1

WORKDIR /app

# Install git (required for django-ansible-base from git)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy application code
COPY . .

# Ensure files are readable
RUN chmod -R a+r /app

# Install the project
RUN uv sync --frozen

EXPOSE 8000

# Run migrations and start server using uv run
CMD ["/bin/sh", "-c", "uv run --no-sync python manage.py migrate && uv run --no-sync python manage.py runserver 0.0.0.0:8000"]
