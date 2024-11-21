#!/bin/bash

echo "Verifying MongoDB setup..."

# Check MongoDB connection
echo "Checking MongoDB connection..."
docker exec backend-mongodb-1 mongosh \
    --eval "db.adminCommand('ping')" \
    "mongodb://admin:password123@localhost:27017/admin"

# List collections
echo -e "\nListing collections..."
docker exec backend-mongodb-1 mongosh \
    --eval "db.getCollectionNames()" \
    "mongodb://agenthub_user:password123@localhost:27017/agenthub?authSource=admin"

# Check indexes for each collection
echo -e "\nChecking indexes..."
collections=("users" "conversations" "messages" "flight_bookings" "hotel_bookings" "car_rentals" "excursions")
for collection in "${collections[@]}"; do
    echo -e "\nIndexes for $collection:"
    docker exec backend-mongodb-1 mongosh \
        --eval "db.$collection.getIndexes()" \
        "mongodb://agenthub_user:password123@localhost:27017/agenthub?authSource=admin"
done 