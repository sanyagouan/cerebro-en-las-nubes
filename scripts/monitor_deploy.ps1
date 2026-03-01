# Monitorear estado del deployment
$appUuid = "g40o0os008wc8sgoog84w48c"
$deployUuid = "vogocogk08w8w4wsks0oo0oo"
$apiUrl = $env:COOLIFY_API_URL
$headers = @{
    Authorization = "Bearer $env:COOLIFY_API_TOKEN"
    Accept = "application/json"
}

Write-Host "=== Monitoreando deployment ===" -ForegroundColor Cyan
Write-Host "App: $appUuid"
Write-Host "Deploy: $deployUuid"
Write-Host ""

# Obtener deployments
try {
    $deploys = Invoke-RestMethod -Uri "$apiUrl/api/v1/deployments/$appUuid" -Headers $headers -Method GET
    foreach ($d in $deploys) {
        Write-Host "Deployment: $($d.deployment_uuid)" -ForegroundColor Yellow
        Write-Host "  Status: $($d.status)"
        Write-Host "  Created: $($d.created_at)"
        Write-Host ""
    }
} catch {
    Write-Host "Error listando deployments: $($_.Exception.Message)" -ForegroundColor Red
}

# Obtener estado actual de la app
try {
    $app = Invoke-RestMethod -Uri "$apiUrl/api/v1/applications/$appUuid" -Headers $headers -Method GET
    Write-Host "=== Estado de la app ===" -ForegroundColor Cyan
    Write-Host "Estado: $($app.status)" -ForegroundColor $(if ($app.status -like '*running*') {'Green'} else {'Yellow'})
    Write-Host "Dominio: $($app.fqdn)"
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
