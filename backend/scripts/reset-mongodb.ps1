Write-Host "Resetting MongoDB..."

# Stop containers
docker-compose down -v

# Remove volumes
docker volume prune -f

# Start MongoDB
docker-compose up -d mongodb

# Wait for MongoDB to be ready
Write-Host "Waiting for MongoDB to initialize..."
Start-Sleep -Seconds 30

# Verify setup
& "$PSScriptRoot\verify-mongodb.ps1" 