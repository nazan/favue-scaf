#!/bin/bash
set -e

# Load test environment variables
set -a
. ./test.env
set +a

# Run migrations first to ensure test database is up to date
echo "Running test database migrations..."
alembic upgrade head

# Run tests
echo "Running tests..."
pytest "$@"

