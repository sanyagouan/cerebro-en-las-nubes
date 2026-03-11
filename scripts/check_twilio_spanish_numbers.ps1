# Script para verificar disponibilidad de números móviles españoles en Twilio
# Creado: 2026-03-10

$AccountSid = $env:TWILIO_ACCOUNT_SID
$AuthToken = $env:TWILIO_AUTH_TOKEN
$credentials = "${AccountSid}:${AuthToken}"
$encodedCredentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($credentials))

Write-Host "🔍 Buscando números móviles disponibles en España..." -ForegroundColor Cyan
Write-Host ""

try {
    # Buscar números móviles (Mobile)
    $headers = @{
        Authorization = "Basic $encodedCredentials"
    }
    
    $uri = "https://api.twilio.com/2010-04-01/Accounts/$AccountSid/AvailablePhoneNumbers/ES/Mobile.json"
    
    Write-Host "📞 Consultando números MÓVILES (+34 6XXXXXXXX o +34 7XXXXXXXX)..." -ForegroundColor Yellow
    $mobileResponse = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
    
    if ($mobileResponse.available_phone_numbers -and $mobileResponse.available_phone_numbers.Count -gt 0) {
        Write-Host "✅ NÚMEROS MÓVILES DISPONIBLES: $($mobileResponse.available_phone_numbers.Count)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Primeros 5 números disponibles:" -ForegroundColor Cyan
        $mobileResponse.available_phone_numbers | Select-Object -First 5 | ForEach-Object {
            Write-Host "  📱 $($_.phone_number) - $($_.friendly_name)" -ForegroundColor White
            Write-Host "     Capabilities: Voice=$($_.capabilities.voice), SMS=$($_.capabilities.SMS), MMS=$($_.capabilities.MMS)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ NO HAY NÚMEROS MÓVILES DISPONIBLES en España" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "-----------------------------------" -ForegroundColor DarkGray
    Write-Host ""
    
    # Intentar también con números locales (Local/Fixed)
    $uriLocal = "https://api.twilio.com/2010-04-01/Accounts/$AccountSid/AvailablePhoneNumbers/ES/Local.json"
    
    Write-Host "📞 Consultando números LOCALES/FIJOS (+34 9XXXXXXXX)..." -ForegroundColor Yellow
    $localResponse = Invoke-RestMethod -Uri $uriLocal -Headers $headers -Method Get
    
    if ($localResponse.available_phone_numbers -and $localResponse.available_phone_numbers.Count -gt 0) {
        Write-Host "✅ NÚMEROS LOCALES DISPONIBLES: $($localResponse.available_phone_numbers.Count)" -ForegroundColor Green
        Write-Host ""
        Write-Host "Primeros 5 números disponibles:" -ForegroundColor Cyan
        $localResponse.available_phone_numbers | Select-Object -First 5 | ForEach-Object {
            Write-Host "  ☎️  $($_.phone_number) - $($_.friendly_name)" -ForegroundColor White
            Write-Host "     Capabilities: Voice=$($_.capabilities.voice), SMS=$($_.capabilities.SMS), MMS=$($_.capabilities.MMS)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ NO HAY NÚMEROS LOCALES DISPONIBLES en España" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "-----------------------------------" -ForegroundColor DarkGray
    Write-Host ""
    
    # Obtener información de pricing
    Write-Host "💰 Consultando precios de números en España..." -ForegroundColor Yellow
    $pricingUri = "https://pricing.twilio.com/v2/PhoneNumbers/Countries/ES"
    $pricingResponse = Invoke-RestMethod -Uri $pricingUri -Headers $headers -Method Get
    
    Write-Host ""
    Write-Host "PRECIOS MENSUALES:" -ForegroundColor Cyan
    $pricingResponse.phone_number_prices | ForEach-Object {
        Write-Host "  - $($_.number_type): $($_.current_price) USD/mes" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "✅ Consulta completada exitosamente" -ForegroundColor Green
    
} catch {
    Write-Host "❌ ERROR al consultar Twilio API:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Detalles del error:" -ForegroundColor Yellow
    Write-Host $_ -ForegroundColor Gray
}

Write-Host ""
Write-Host "📋 NOTAS IMPORTANTES:" -ForegroundColor Cyan
Write-Host "  1. Para usar WhatsApp Business API, Twilio requiere:" -ForegroundColor White
Write-Host "     - Verificación de negocio con Meta" -ForegroundColor Gray
Write-Host "     - Aprobación de templates de mensajes" -ForegroundColor Gray
Write-Host "     - Documentación KYC (Know Your Customer)" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Los números móviles españoles (+34 6XX/7XX) suelen estar" -ForegroundColor White
Write-Host "     muy limitados por regulaciones europeas." -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Alternativa: Usar número local (+34 9XX) con WhatsApp" -ForegroundColor White
Write-Host "     (si Meta aprueba el uso comercial)" -ForegroundColor Gray
