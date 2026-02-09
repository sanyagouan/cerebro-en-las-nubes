$h = @{
    Authorization = "Bearer $env:COOLIFY_API_TOKEN"
    Accept = "application/json"
}

$appUuid = "g40o0os008wc8sgoog84w48c"

Write-Host "=== Deployments recientes ===" -ForegroundColor Cyan
try {
    $url = "$env:COOLIFY_API_URL/api/v1/applications/$appUuid/deployments"
    $result = Invoke-RestMethod -Uri $url -Headers $h -Method GET
    if ($result -and $result.Count -gt 0) {
        $result | Select-Object -First 5 | ForEach-Object {
            Write-Host "UUID: $($_.deployment_uuid) | Status: $($_.status) | Created: $($_.created_at)" -ForegroundColor Yellow
        }
        $latest = $result[0]
        Write-Host ""
        Write-Host "=== Ultimo deployment detalle ===" -ForegroundColor Cyan
        Write-Host "UUID: $($latest.deployment_uuid)"
        Write-Host "Status: $($latest.status)"
        Write-Host "Commit: $($latest.commit)"
        if ($latest.log) {
            $logLines = $latest.log -split "`n" | Select-Object -Last 30
            Write-Host "--- Ultimas 30 lineas del log ---"
            $logLines | ForEach-Object { Write-Host $_ }
        }
    } else {
        Write-Host "No deployments encontrados" -ForegroundColor Red
    }
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Application Logs ===" -ForegroundColor Cyan
try {
    $url = "$env:COOLIFY_API_URL/api/v1/applications/$appUuid/logs"
    $result = Invoke-RestMethod -Uri $url -Headers $h -Method GET
    if ($result.logs) {
        $result.logs | Select-Object -Last 20 | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host "No app logs disponibles"
    }
} catch {
    Write-Host "Error logs: $($_.Exception.Message)" -ForegroundColor Red
}
