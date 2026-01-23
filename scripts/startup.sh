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

# Seed admin user if ADMIN_PASSWORD is set
if [ -n "$ADMIN_PASSWORD" ]; then
  echo "🌱 Seeding admin user..."
  if python scripts/seed_admin.py; then
    echo "✅ Admin seeding completed"
  else
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
      echo "ℹ️  Admin user already exists, skipping creation"
    else
      echo "❌ Admin seeding failed with exit code $exit_code"
      echo "   Continuing anyway, but login may not work..."
    fi
  fi
else
  echo "⚠️  ADMIN_PASSWORD not set, skipping admin seeding"
fi

# Start the application
echo "🎯 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
