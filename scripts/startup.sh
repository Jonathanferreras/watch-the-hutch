#!/bin/bash
set -e

echo "🚀 Starting Watch The Hutch application..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
  echo "   Database is unavailable - sleeping"
  sleep 1
done
echo "✅ Database is ready!"

# Start the application
echo "🎯 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
