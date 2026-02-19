#!/bin/bash

# Digital Ocean App Platform startup script
echo "Starting ISO 22000 FSMS Backend..."

# Set environment variables
export PYTHONPATH=/app

# Run database migrations if DATABASE_URL is set
if [ ! -z "$DATABASE_URL" ]; then
    echo "Running database migrations..."
    cd /app
    alembic upgrade head || echo "Migration failed, continuing..."
else
    echo "No DATABASE_URL set, skipping migrations"
fi

# Start the application
echo "Starting uvicorn server on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
