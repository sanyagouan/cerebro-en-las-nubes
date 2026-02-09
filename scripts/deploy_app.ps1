# Conectar app a red Docker y lanzar deploy
$appUuid = "g40o0os008wc8sgoog84w48c"
$apiUrl = $env:COOLIFY_API_URL
$token = $env:COOLIFY_API_TOKEN

$headers = @{
    Authorization = "Bearer $token"
    Accept = "application/json"
    "Content-Type" = "application/json"
}

# Paso 1: Actualizar configuracion de red
Write-Host "[1/2] Configurando red Docker..." -ForegroundColor Yellow
try {
    $body = '{"connect_to_docker_network":true}'
    $url = "$apiUrl/api/v1/applications/$appUuid"
    Invoke-RestMethod -Uri $url -Headers $headers -Method PATCH -Body $body
    Write-Host "[OK] Red Docker configurada" -ForegroundColor Green
} catch {
    Write-Host "[WARN] No se pudo configurar red: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Paso 2: Lanzar deploy
Write-Host "[2/2] Lanzando deploy..." -ForegroundColor Yellow
try {
    $url = "$apiUrl/api/v1/applications/$appUuid/deploy"
    $result = Invoke-RestMethod -Uri $url -Headers $headers -Method POST
    $result | ConvertTo-Json -Depth 3
    Write-Host "[OK] Deploy iniciado" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] Error en deploy: $($_.Exception.Message)" -ForegroundColor Red
}
