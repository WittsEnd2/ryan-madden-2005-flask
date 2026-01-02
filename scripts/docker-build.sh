#!/bin/bash

# Docker build script

echo "Building Docker image..."
docker build -t nfl-game:latest .

echo ""
echo "Build complete!"
echo ""
echo "To run the container:"
echo "  docker run -p 5000:5000 -e SECRET_KEY=\$(python3 -c 'import secrets; print(secrets.token_hex(32))') nfl-game:latest"
echo ""
echo "Or use docker-compose:"
echo "  docker-compose up"
