#!/bin/bash

# Create logs directory
mkdir -p logs
echo "Created logs directory"

# Create necessary directories
mkdir -p app/services/agents/{booking,support}

# Make sure we're in the backend directory
cd "$(dirname "$0")/.."

# Stop and remove existing containers
docker-compose down -v

# Remove existing volumes
docker volume prune -f

# Start services
docker-compose up -d

# Wait for MongoDB to initialize
echo "Waiting for MongoDB to initialize..."
sleep 15

# Check services health
echo "Checking services health..."
docker-compose ps

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate || source venv/Scripts/activate
pip install --upgrade pip
pip install -e ".[dev]"

echo "Setup complete! You can now start the application with:"
echo "uvicorn app.main:app --reload" 