#!/bin/bash
set -e

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install
fi

# Execute the command passed to the container
exec "$@"

