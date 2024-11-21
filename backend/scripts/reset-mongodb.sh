#!/bin/bash

echo "Resetting MongoDB..."

# Stop containers
docker-compose down -v

# Remove volumes
docker volume prune -f

# Start MongoDB
docker-compose up -d mongodb

# Wait for MongoDB to be ready
echo "Waiting for MongoDB to initialize..."
sleep 30

# Verify setup
./scripts/verify-mongodb.sh 