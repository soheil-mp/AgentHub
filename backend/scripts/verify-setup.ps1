Write-Host "Verifying complete setup..."

# Check Docker services
Write-Host "`n=== Docker Services ==="
docker-compose ps
$services = docker-compose ps --format json | ConvertFrom-Json

# Initialize status object
$status = @{
    mongodb = $false
    redis = $false
    api = $false
}

# Check each service
Write-Host "`nChecking service status..."
$runningServices = docker-compose ps --format "{{.Service}}"
foreach ($service in $runningServices) {
    switch -Exact ($service) {
        "mongodb" { 
            $containerStatus = docker inspect --format='{{.State.Health.Status}}' backend-mongodb-1
            $status.mongodb = ($containerStatus -eq "healthy")
        }
        "redis" { 
            $containerStatus = docker inspect --format='{{.State.Health.Status}}' backend-redis-1
            $status.redis = ($containerStatus -eq "healthy")
        }
        "api" { 
            $containerStatus = docker inspect --format='{{.State.Status}}' backend-api-1
            $status.api = ($containerStatus -eq "running")
        }
    }
}

# Check MongoDB
Write-Host "`n=== MongoDB Status ==="
if ($status.mongodb) {
    .\scripts\check-mongodb-users.ps1
} else {
    Write-Host "MongoDB is not running or not healthy. Start it with: docker-compose up -d mongodb"
}

# Check Redis
Write-Host "`n=== Redis Status ==="
if ($status.redis) {
    try {
        $redisPing = docker exec backend-redis-1 redis-cli ping
        Write-Host "Redis response: $redisPing"
    } catch {
        Write-Host "Error checking Redis: $_"
    }
} else {
    Write-Host "Redis is not running or not healthy. Start it with: docker-compose up -d redis"
}

# Check API
Write-Host "`n=== API Status ==="
if ($status.api) {
    Write-Host "Checking API health endpoint..."
    try {
        Start-Sleep -Seconds 5  # Give API time to start
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get
        $response | ConvertTo-Json
    } catch {
        Write-Host "Error accessing API: $_"
        Write-Host "API might still be starting up. Try again in a few seconds."
    }
} else {
    Write-Host "API is not running. Start it with: docker-compose up -d api"
}

# Summary
Write-Host "`n=== Setup Status Summary ==="
Write-Host "MongoDB: $($status.mongodb ? 'Healthy' : 'Not Healthy')"
Write-Host "Redis: $($status.redis ? 'Healthy' : 'Not Healthy')"
Write-Host "API: $($status.api ? 'Running' : 'Not Running')"

if (-not ($status.mongodb -and $status.redis -and $status.api)) {
    Write-Host "`nTo start all services, run:"
    Write-Host "docker-compose up -d"
}

Write-Host "`nSetup verification complete!" 