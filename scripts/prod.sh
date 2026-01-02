#!/bin/bash

# Production server script (using Gunicorn)

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set production environment
export FLASK_ENV=production

# Validate SECRET_KEY
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-secret-key-here" ]; then
    echo "ERROR: SECRET_KEY must be set to a secure value in production!"
    echo "Generate one with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run production server with Gunicorn
echo "Starting production server with Gunicorn..."
gunicorn --config gunicorn.conf.py wsgi:app
