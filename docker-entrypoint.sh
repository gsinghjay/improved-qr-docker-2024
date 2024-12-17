#!/bin/bash

# Exit on error
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h db -p 5432; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Ensure migrations directory and subdirectories exist with correct permissions
echo "Setting up migrations directory..."
mkdir -p /app/migrations/versions
chmod -R 777 /app/migrations

# Initialize migrations directory if env.py doesn't exist
if [ ! -f "/app/migrations/env.py" ]; then
    echo "Initializing migrations directory..."
    # Remove existing directory contents if any
    rm -rf /app/migrations/*
    
    export FLASK_APP=manage.py
    flask db init
    
    # Create initial migration
    echo "Creating initial migration..."
    flask db migrate -m "Initial migration"
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade

# Start the Flask application
echo "Starting Flask application..."
python run.py