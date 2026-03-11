# Test de conexion directa con Twilio API
# Para verificar si las credenciales funcionan

$AccountSid = $env:TWILIO_ACCOUNT_SID
$AuthToken = $env:TWILIO_AUTH_TOKEN

# Codificar credenciales en Base64 para Basic Auth
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($AccountSid):$($AuthToken)"))

Write-Host "=== TEST DIRECTO TWILIO API ===" -ForegroundColor Cyan
Write-Host ""

# 1. Test de cuenta
Write-Host "[1/4] Probando GET Account..." -ForegroundColor Yellow
try {
    $uri = "https://api.twilio.com/2010-04-01/Accounts/$AccountSid.json"
    $headers = @{
        "Authorization" = "Basic $base64AuthInfo"
    }
    
    $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
    Write-Host "[OK] Cuenta encontrada: $($response.friendly_name)" -ForegroundColor Green
    Write-Host "    Status: $($response.status)" -ForegroundColor Gray
    Write-Host "    Type: $($response.type)" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Fallo al obtener cuenta" -ForegroundColor Red
    Write-Host "    Detalle: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Listar numeros
Write-Host ""
Write-Host "[2/4] Listando numeros de telefono..." -ForegroundColor Yellow
try {
    $uri = "https://api.twilio.com/2010-04-01/Accounts/$AccountSid/IncomingPhoneNumbers.json"
    $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
    
    $numbers = $response.incoming_phone_numbers
    Write-Host "[OK] Numeros encontrados: $($numbers.Count)" -ForegroundColor Green
    
    foreach ($num in $numbers) {
        Write-Host ""
        Write-Host "  Numero: $($num.phone_number)" -ForegroundColor Cyan
        Write-Host "    Friendly Name: $($num.friendly_name)" -ForegroundColor Gray
        Write-Host "    Voice: $($num.capabilities.voice)" -ForegroundColor Gray
        Write-Host "    SMS: $($num.capabilities.sms)" -ForegroundColor Gray
        Write-Host "    MMS: $($num.capabilities.mms)" -ForegroundColor Gray
        Write-Host "    SID: $($num.sid)" -ForegroundColor Gray
    }
} catch {
    Write-Host "[ERROR] Fallo al listar numeros" -ForegroundColor Red
    Write-Host "    Detalle: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Verificar mensajes recientes
Write-Host ""
Write-Host "[3/4] Verificando mensajes recientes (ultimos 5)..." -ForegroundColor Yellow
try {
    $uri = "https://api.twilio.com/2010-04-01/Accounts/$AccountSid/Messages.json?PageSize=5"
    $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
    
    $messages = $response.messages
    Write-Host "[OK] Mensajes encontrados: $($messages.Count)" -ForegroundColor Green
    
    foreach ($msg in $messages) {
        Write-Host ""
        Write-Host "  SID: $($msg.sid)" -ForegroundColor Gray
        Write-Host "    From: $($msg.from)" -ForegroundColor Gray
        Write-Host "    To: $($msg.to)" -ForegroundColor Gray
        Write-Host "    Status: $($msg.status)" -ForegroundColor Gray
        Write-Host "    Direction: $($msg.direction)" -ForegroundColor Gray
        Write-Host "    Date: $($msg.date_sent)" -ForegroundColor Gray
    }
} catch {
    Write-Host "[ERROR] Fallo al obtener mensajes" -ForegroundColor Red
    Write-Host "    Detalle: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Verificar Content API (templates WhatsApp)
Write-Host ""
Write-Host "[4/4] Verificando templates en Content API..." -ForegroundColor Yellow
try {
    $uri = "https://content.twilio.com/v1/Content"
    $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
    
    $contents = $response.contents
    Write-Host "[OK] Templates encontrados: $($contents.Count)" -ForegroundColor Green
    
    foreach ($content in $contents) {
        Write-Host ""
        Write-Host "  Template: $($content.friendly_name)" -ForegroundColor Cyan
        Write-Host "    SID: $($content.sid)" -ForegroundColor Gray
        Write-Host "    Language: $($content.language)" -ForegroundColor Gray
        Write-Host "    Date Created: $($content.date_created)" -ForegroundColor Gray
    }
} catch {
    Write-Host "[ADVERTENCIA] No se pudieron obtener templates (puede ser normal si no hay ninguno)" -ForegroundColor Yellow
    Write-Host "    Detalle: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== FIN DEL TEST ===" -ForegroundColor Cyan
