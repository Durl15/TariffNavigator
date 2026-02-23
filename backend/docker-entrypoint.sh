#!/bin/bash
set -e

echo "=== TariffNavigator Backend Starting ==="

# Wait for database to be ready using Python
echo "Waiting for database..."
python << 'PYTHON_SCRIPT'
import time
import os
import sys

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Extract host and port from DATABASE_URL
if "postgresql" in DATABASE_URL:
    import socket
    try:
        # Parse: postgresql+asyncpg://user:pass@host:port/db
        host = DATABASE_URL.split("@")[1].split(":")[0]
        port = int(DATABASE_URL.split("@")[1].split(":")[1].split("/")[0])

        for i in range(30):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                sock.connect((host, port))
                sock.close()
                print(f"✓ Database connection available at {host}:{port}")
                sys.exit(0)
            except Exception:
                print(f"Attempt {i+1}/30: Database not ready yet, waiting 2 seconds...")
                time.sleep(2)

        print("⚠️  Database not available after 60 seconds, proceeding anyway...")
    except Exception as e:
        print(f"⚠️  Error parsing DATABASE_URL: {e}, proceeding anyway...")
else:
    print("✓ Using SQLite, no wait needed")
PYTHON_SCRIPT

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
echo "✓ Migrations complete"

# Optional: Seed data for development
if [ "$ENVIRONMENT" = "development" ]; then
  echo "Development mode - checking for seed data..."
  python -c "from app.db.seed_data import seed_if_empty; import asyncio; asyncio.run(seed_if_empty())" || true
fi

echo "=== Starting application server ==="
# Execute the main command (gunicorn)
exec "$@"
