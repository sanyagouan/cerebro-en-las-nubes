# Script para configurar variables de entorno en Coolify
$appUuid = "g40o0os008wc8sgoog84w48c"
$apiUrl = $env:COOLIFY_API_URL
$token = $env:COOLIFY_API_TOKEN

$headers = @{
    Authorization = "Bearer $token"
    Accept = "application/json"
    "Content-Type" = "application/json"
}

$envVars = @(
    @{key="ENVIRONMENT"; value="production"},
    @{key="REDIS_URL"; value="redis://default:EnLasNubesRedis2026%21Secure@pkos04wwkso0sgog0o40o8s0:6379/0"},
    @{key="AIRTABLE_API_KEY"; value=$env:AIRTABLE_API_KEY},
    @{key="TWILIO_ACCOUNT_SID"; value=$env:TWILIO_ACCOUNT_SID},
    @{key="TWILIO_AUTH_TOKEN"; value=$env:TWILIO_AUTH_TOKEN},
    @{key="TWILIO_FROM_NUMBER"; value=$env:TWILIO_FROM_NUMBER},
    @{key="VAPI_API_KEY"; value=$env:VAPI_API_KEY},
    @{key="SUPABASE_URL"; value=$env:SUPABASE_URL},
    @{key="SUPABASE_SERVICE_KEY"; value=$env:SUPABASE_ACCESS_TOKEN},
    @{key="JWT_SECRET_KEY"; value=[guid]::NewGuid().ToString() + "-" + [guid]::NewGuid().ToString()},
    @{key="ALLOWED_ORIGINS"; value="https://cerebro-backend.app.generaia.site"}
)

$successCount = 0
$failCount = 0

foreach ($ev in $envVars) {
    try {
        $body = $ev | ConvertTo-Json -Compress
        $url = "$apiUrl/api/v1/applications/$appUuid/envs"
        $result = Invoke-RestMethod -Uri $url -Headers $headers -Method POST -Body $body
        Write-Host "[OK] $($ev.key)" -ForegroundColor Green
        $successCount++
    } catch {
        # Intentar con PATCH (bulk update)
        Write-Host "[FAIL] $($ev.key) - $($_.Exception.Message)" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "Resultado: $successCount OK, $failCount FAIL"
