param(
    [string]$service = "all",  # Filter by service: all, mongodb, redis, api
    [string]$level = "all",    # Filter by log level: all, info, error, warning
    [int]$tail = 0            # Number of previous logs to show (0 for none)
)

Write-Host "Starting log monitoring..."

# Function to format log output with colors
function Format-LogOutput {
    param (
        [string]$service,
        [string]$log
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # Determine log level and color
    $color = "White"
    if ($log -match "error|fail|exception|Authentication failed" -or $log -match '"s":"E"') {
        $color = "Red"
    }
    elseif ($log -match "warn|Authentication succeeded" -or $log -match '"s":"W"') {
        $color = "Yellow"
    }
    elseif ($log -match "info|success|healthy" -or $log -match '"s":"I"') {
        $color = "Green"
    }
    
    # Format service name
    $serviceName = switch ($service.Trim()) {
        "backend-mongodb-1" { "MongoDB" }
        "backend-redis-1" { "Redis" }
        "backend-api-1" { "API" }
        default { $service }
    }
    
    # Write colored output
    Write-Host -NoNewline "[$timestamp] "
    Write-Host -NoNewline -ForegroundColor Cyan "[$serviceName] "
    Write-Host -ForegroundColor $color $log
}

# Function to check if log matches filters
function Should-ShowLog {
    param (
        [string]$serviceMatch,
        [string]$logText
    )
    
    # Service filter
    if ($service -ne "all" -and -not $serviceMatch.Contains($service)) {
        return $false
    }
    
    # Level filter
    if ($level -ne "all") {
        switch ($level.ToLower()) {
            "error" { 
                if (-not ($logText -match "error|fail|exception" -or $logText -match '"s":"E"')) {
                    return $false
                }
            }
            "warning" {
                if (-not ($logText -match "warn" -or $logText -match '"s":"W"')) {
                    return $false
                }
            }
            "info" {
                if (-not ($logText -match "info|success" -or $logText -match '"s":"I"')) {
                    return $false
                }
            }
        }
    }
    
    return $true
}

# Show usage information
Write-Host @"
Log Monitor Options:
  Service: $service (all, mongodb, redis, api)
  Level: $level (all, info, error, warning)
  Tail: $tail lines

Controls:
  Ctrl+C to stop monitoring
  
Monitoring logs...

"@

# Monitor logs from all services
try {
    docker-compose logs --tail=$tail -f | ForEach-Object {
        if ($_ -match "^(?<service>[^|]+)\s+\|\s+(?<log>.*)$") {
            $serviceMatch = $matches['service'].Trim()
            $logText = $matches['log']
            
            if (Should-ShowLog -serviceMatch $serviceMatch -logText $logText) {
                Format-LogOutput -service $serviceMatch -log $logText
            }
        }
        else {
            if (Should-ShowLog -serviceMatch "system" -logText $_) {
                Format-LogOutput -service "system" -log $_
            }
        }
    }
} catch {
    Write-Host "`nStopped monitoring logs"
} 