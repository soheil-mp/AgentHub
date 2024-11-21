Write-Host "Verifying MongoDB setup..."

# Check MongoDB connection
Write-Host "Checking MongoDB connection..."
docker exec backend-mongodb-1 mongosh --eval "db.adminCommand('ping')" "mongodb://admin:password123@localhost:27017/admin"

# List collections
Write-Host "`nListing collections..."
docker exec backend-mongodb-1 mongosh --eval "db.getCollectionNames()" "mongodb://agenthub_user:password123@localhost:27017/agenthub?authSource=admin"

# Check indexes for each collection
Write-Host "`nChecking indexes..."
$collections = @("users", "conversations", "messages", "flight_bookings", "hotel_bookings", "car_rentals", "excursions")
foreach ($collection in $collections) {
    Write-Host "`nIndexes for collection: $collection"
    docker exec backend-mongodb-1 mongosh --eval "db.$($collection).getIndexes()" "mongodb://agenthub_user:password123@localhost:27017/agenthub?authSource=admin"
} 