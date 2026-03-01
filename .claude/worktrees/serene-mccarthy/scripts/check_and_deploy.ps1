# Deploy con diferentes endpoints
$appUuid = "g40o0os008wc8sgoog84w48c"
$apiUrl = $env:COOLIFY_API_URL
$headers = @{
    Authorization = "Bearer $env:COOLIFY_API_TOKEN"
    Accept = "application/json"
    "Content-Type" = "application/json"
}

# Intentar GET para ver el estado actual de la app
Write-Host "=== Estado actual de la app ===" -ForegroundColor Cyan
try {
    $app = Invoke-RestMethod -Uri "$apiUrl/api/v1/applications/$appUuid" -Headers $headers -Method GET
    Write-Host "Nombre: $($app.name)"
    Write-Host "Estado: $($app.status)"
    Write-Host "Dominio: $($app.fqdn)"
    Write-Host "Repo: $($app.git_repository)"
    Write-Host "Rama: $($app.git_branch)"
    Write-Host "Build: $($app.build_pack)"
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Intentando deploy ===" -ForegroundColor Cyan

# Intentar POST sin body
try {
    $result = Invoke-RestMethod -Uri "$apiUrl/api/v1/applications/$appUuid/deploy" -Headers $headers -Method POST
    Write-Host "[OK] Deploy result: $($result | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL POST] $($_.Exception.Message)" -ForegroundColor Red
}

# Intentar GET deploy
try {
    $result = Invoke-RestMethod -Uri "$apiUrl/api/v1/applications/$appUuid/deploy" -Headers $headers -Method GET
    Write-Host "[OK] Deploy GET: $($result | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL GET] $($_.Exception.Message)" -ForegroundColor Red
}

# Intentar start
try {
    $result = Invoke-RestMethod -Uri "$apiUrl/api/v1/applications/$appUuid/start" -Headers $headers -Method POST
    Write-Host "[OK] Start: $($result | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL start] $($_.Exception.Message)" -ForegroundColor Red
}
