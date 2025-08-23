#!/bin/bash
set -euo pipefail

echo "Starting docker-entrypoint.sh"
echo "Current directory: $(pwd)"
echo "Script location: $0"

cd /app

echo "Waiting for database to be ready..."
while ! pg_isready -h "${POSTGRES_SERVER}" -p 5432 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; do
  echo "Waiting for database..."
  sleep 2
done

echo "Database is ready!"

# Ensure PYTHONPATH
export PYTHONPATH=/app:${PYTHONPATH}

# Create tables directly (bootstrap)
python - <<'PY'
from app.db.base import Base, engine
from app.models.user import User  # noqa: F401
print('Creating tables with SQLAlchemy Base.metadata.create_all...')
Base.metadata.create_all(bind=engine)
print('Tables created.')
PY

echo "Starting FastAPI application..."
exec "$@" 