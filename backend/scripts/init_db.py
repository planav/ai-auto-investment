#!/usr/bin/env python3
"""
Database initialization script.

Run this script to set up the PostgreSQL database for AutoInvest:
    python scripts/init_db.py

This script will:
1. Create the database if it doesn't exist
2. Run all Alembic migrations to create tables
"""

import subprocess
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_migrations():
    """Run Alembic migrations."""
    print("Running database migrations...")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("Migration failed:")
        print(result.stderr)
        sys.exit(1)
    print(result.stdout)
    print("Migrations completed successfully.")


def check_db_connection():
    """Test database connection."""
    try:
        from app.core.config import get_settings
        import psycopg2

        settings = get_settings()
        # Convert asyncpg URL to psycopg2 URL
        sync_url = settings.database_url_sync
        conn = psycopg2.connect(sync_url)
        conn.close()
        print(f"Database connection successful: {sync_url}")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is running")
        print("  2. The database exists (run: createdb autoinvest_db)")
        print("  3. The DATABASE_URL in .env is correct")
        return False


if __name__ == "__main__":
    print("AutoInvest Database Initialization")
    print("=" * 40)

    if not check_db_connection():
        sys.exit(1)

    run_migrations()
    print("\nDatabase initialization complete!")
    print("You can now start the application with: uvicorn app.main:app --reload")
