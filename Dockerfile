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
COPY ./app /app

# Run as a non-root user (2026 Security Standard)
RUN useradd -m myuser
USER myuser

CMD ["fastapi", "run", "main.py", "--port", "8000"]