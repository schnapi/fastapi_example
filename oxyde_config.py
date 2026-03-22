"""Oxyde ORM configuration."""

from app.config import settings

# List of Python modules containing Model classes
MODELS = ["app.models"]

# Database dialect: "postgres", "sqlite", or "mysql"
DIALECT = "postgres"

# Directory for migration files
MIGRATIONS_DIR = "migrations"

# Database connections
# Keys are connection aliases, values are connection URLs
DATABASES = {
    "default": settings.database_url,
}
