#!/bin/sh
set -e

echo "AutoInvest Backend starting..."

# Render.com provides DATABASE_URL in the form:
#   postgresql://user:pass@host/db
# but asyncpg (async SQLAlchemy) requires:
#   postgresql+asyncpg://user:pass@host/db
# We normalise both env vars here so the app works on every platform.
if [ -n "$DATABASE_URL" ]; then
  # Strip any existing driver prefix then re-apply the correct ones
  DB_CLEAN=$(echo "$DATABASE_URL" \
    | sed 's|^postgres://|postgresql://|' \
    | sed 's|^postgresql+asyncpg://|postgresql://|')
  export DATABASE_URL="postgresql+asyncpg://${DB_CLEAN#postgresql://}"
  export DATABASE_URL_SYNC="${DB_CLEAN}"
fi

# Wait for PostgreSQL to be ready
echo "Waiting for database..."
until python -c "
import psycopg2, os, sys
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL_SYNC'])
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f'DB not ready: {e}')
    sys.exit(1)
" 2>/dev/null; do
  echo "Database not ready yet, retrying in 2s..."
  sleep 2
done
echo "Database is ready."

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete."

# Start the application
# We use a single worker by default because:
#  - The free tier on Render/Railway has limited RAM and CPU.
#  - The FastAPI app already uses async I/O (asyncpg, httpx) for concurrency.
# Set WEB_CONCURRENCY > 1 to enable multiple Uvicorn workers when you have
# more resources available (e.g. WEB_CONCURRENCY=4).
echo "Starting uvicorn (workers=${WEB_CONCURRENCY:-1})..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-1}"
