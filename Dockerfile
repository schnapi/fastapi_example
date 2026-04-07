# syntax=docker/dockerfile:1.4
# STAGE 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /build
COPY requirements.txt .
# Use a cache mount to speed up pip installs in future builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/install -r requirements.txt

# STAGE 2: Runner
FROM python:3.13-slim

WORKDIR /app
# Copy only the installed packages from the builder
COPY --from=builder /install /usr/local
COPY . /app

# Install curl for healthcheck and postgresql-client for pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends curl postgresql-client && rm -rf /var/lib/apt/lists/*

# Create non-root user and set ownership of /app
RUN useradd -m myuser \
    && chown -R myuser:myuser /app

# Switch to non-root user
USER myuser

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 --start-period=15s \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["fastapi", "run", "main.py", "--port", "8000"]