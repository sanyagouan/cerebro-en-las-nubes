$h = @{ Authorization = "Bearer $env:COOLIFY_API_TOKEN"; Accept = "application/json" }

# Obtener deployment logs
$deployUuid = "y4g0k8ogog4kcs44kok4cwws"
Write-Host "=== Deployment Logs ===" -ForegroundColor Cyan

try {
    $url = $env:COOLIFY_API_URL + "/api/v1/deployments/$deployUuid"
    $result = Invoke-RestMethod -Uri $url -Headers $h
    Write-Host "Status: $($result.status)" -ForegroundColor Yellow
    Write-Host "Log:"
    Write-Host $result.log
} catch {
    Write-Host "Error obteniendo deployment: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Application Logs ===" -ForegroundColor Cyan
try {
    $url = $env:COOLIFY_API_URL + "/api/v1/applications/g40o0os008wc8sgoog84w48c/logs"
    $result = Invoke-RestMethod -Uri $url -Headers $h
    if ($result) {
        $result | Select-Object -First 30
    } else {
        Write-Host "No logs disponibles"
    }
} catch {
    Write-Host "Error obteniendo logs: $($_.Exception.Message)" -ForegroundColor Red
}
