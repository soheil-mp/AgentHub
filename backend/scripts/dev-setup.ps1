Write-Host "Setting up development environment..."

# Check if Docker is running
Write-Host "`n=== Checking Docker ==="
try {
    docker info | Out-Null
    Write-Host "Docker is running"
} catch {
    Write-Host "Error: Docker is not running. Please start Docker Desktop first."
    exit 1
}

# Reset environment
Write-Host "`n=== Resetting Environment ==="
docker-compose down -v
docker volume prune -f

# Build images
Write-Host "`n=== Building Images ==="
docker-compose build --no-cache

# Start services
Write-Host "`n=== Starting Services ==="
docker-compose up -d

# Wait for services to be ready
Write-Host "`n=== Waiting for Services ==="
Write-Host "Waiting 30 seconds for services to initialize..."
Start-Sleep -Seconds 30

# Verify setup
Write-Host "`n=== Verifying Setup ==="
.\scripts\verify-setup.ps1

Write-Host "`nDevelopment environment setup complete!"
Write-Host "API Documentation: http://localhost:8000/docs"
Write-Host "API Health Check: http://localhost:8000/api/v1/health"
Write-Host "MongoDB Admin: http://localhost:27017"
Write-Host "Redis Port: 6379" 