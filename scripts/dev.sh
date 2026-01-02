#!/bin/bash

# Development server script

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set development environment
export FLASK_ENV=development

# Activate virtual environment
source venv/bin/activate

# Run development server
echo "Starting development server..."
python app.py
