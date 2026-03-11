# Script para verificar disponibilidad de números LOCALES españoles en Twilio
# Creado: 2026-03-10

$AccountSid = $env:TWILIO_ACCOUNT_SID
$AuthToken = $env:TWILIO_AUTH_TOKEN
$credentials = "${AccountSid}:${AuthToken}"
$encodedCredentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes($credentials))

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  INVESTIGACIÓN: NÚMEROS TWILIO ESPAÑA" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$headers = @{
    Authorization = "Basic $encodedCredentials"
}

# RESULTADO 1: Números móviles NO disponibles (ya confirmado)
Write-Host "📱 NÚMEROS MÓVILES (+34 6XX/7XX):" -ForegroundColor Yellow
Write-Host "   ❌ NO DISPONIBLES en Twilio" -ForegroundColor Red
Write-Host "   Razón: Restricciones regulatorias europeas" -ForegroundColor Gray
Write-Host "   Error API: 404 Not Found" -ForegroundColor Gray
Write-Host ""

# INVESTIGACIÓN 2: Números locales/fijos
Write-Host "☎️  NÚMEROS LOCALES/FIJOS (+34 9XX):" -ForegroundColor Yellow

try {
    $uriLocal = "https://api.twilio.com/2010-04-01/Accounts/$AccountSid/AvailablePhoneNumbers/ES/Local.json?PageSize=20"
    $localResponse = Invoke-RestMethod -Uri $uriLocal -Headers $headers -Method Get
    
    if ($localResponse.available_phone_numbers -and $localResponse.available_phone_numbers.Count -gt 0) {
        Write-Host "   ✅ DISPONIBLES: $($localResponse.available_phone_numbers.Count) números encontrados" -ForegroundColor Green
        Write-Host ""
        Write-Host "   📋 Muestra de números disponibles:" -ForegroundColor Cyan
        Write-Host ""
        
        $localResponse.available_phone_numbers | Select-Object -First 10 | ForEach-Object {
            Write-Host "      Número: $($_.phone_number)" -ForegroundColor White
            Write-Host "      Nombre: $($_.friendly_name)" -ForegroundColor Gray
            Write-Host "      Voice: $($_.capabilities.voice) | SMS: $($_.capabilities.SMS) | MMS: $($_.capabilities.MMS)" -ForegroundColor Gray
            Write-Host ""
        }
        
        # Verificar capacidades WhatsApp
        $smsCapable = ($localResponse.available_phone_numbers | Where-Object { $_.capabilities.SMS -eq $true }).Count
        Write-Host "   📊 ANÁLISIS DE CAPACIDADES:" -ForegroundColor Cyan
        Write-Host "      - Números con SMS: $smsCapable de $($localResponse.available_phone_numbers.Count)" -ForegroundColor White
        Write-Host "      - Nota: SMS es requisito para WhatsApp Business API" -ForegroundColor Yellow
        
    } else {
        Write-Host "   ❌ NO HAY NÚMEROS LOCALES DISPONIBLES" -ForegroundColor Red
    }
    
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "   ❌ NO DISPONIBLES (endpoint 404)" -ForegroundColor Red
    } else {
        Write-Host "   ❌ ERROR al consultar:" -ForegroundColor Red
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

# INVESTIGACIÓN 3: Pricing
Write-Host ""
Write-Host "💰 PRECIOS DE NÚMEROS EN ESPAÑA:" -ForegroundColor Yellow
Write-Host ""

try {
    $pricingUri = "https://pricing.twilio.com/v2/PhoneNumbers/Countries/ES"
    $pricingResponse = Invoke-RestMethod -Uri $pricingUri -Headers $headers -Method Get
    
    Write-Host "   País: $($pricingResponse.country)" -ForegroundColor White
    Write-Host "   Código: $($pricingResponse.iso_country)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   📋 PRECIOS MENSUALES:" -ForegroundColor Cyan
    
    $pricingResponse.phone_number_prices | ForEach-Object {
        $priceUSD = $_.current_price
        $priceEUR = [math]::Round($priceUSD * 0.92, 2)  # Conversión aproximada USD -> EUR
        
        Write-Host "      - $($_.number_type): $priceUSD USD/mes (~$priceEUR EUR/mes)" -ForegroundColor White
    }
    
} catch {
    Write-Host "   ❌ ERROR al obtener precios:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan

# CONCLUSIONES Y RECOMENDACIONES
Write-Host ""
Write-Host "📌 CONCLUSIONES Y RECOMENDACIONES:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. NÚMEROS MÓVILES ESPAÑOLES (+34 6XX/7XX):" -ForegroundColor Yellow
Write-Host "   ❌ NO están disponibles en Twilio" -ForegroundColor Red
Write-Host "   📄 Razón: Regulaciones europeas de telecomunicaciones" -ForegroundColor Gray
Write-Host "   🔗 Ref: https://www.twilio.com/docs/phone-numbers/regulatory" -ForegroundColor Gray
Write-Host ""

Write-Host "2. ALTERNATIVAS DISPONIBLES:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   OPCIÓN A: Usar número LOCAL español (+34 9XX)" -ForegroundColor White
Write-Host "   ✅ Ventajas:" -ForegroundColor Green
Write-Host "      - Disponibles en Twilio" -ForegroundColor Gray
Write-Host "      - Soportan SMS (requisito para WhatsApp)" -ForegroundColor Gray
Write-Host "      - Precio competitivo (~1-2 USD/mes)" -ForegroundColor Gray
Write-Host "   ⚠️  Consideraciones:" -ForegroundColor Yellow
Write-Host "      - Requiere aprobación de Meta para WhatsApp Business" -ForegroundColor Gray
Write-Host "      - Verificación de negocio obligatoria" -ForegroundColor Gray
Write-Host "      - Templates de mensajes deben ser pre-aprobados" -ForegroundColor Gray
Write-Host ""

Write-Host "   OPCIÓN B: Mantener número FINLANDÉS actual (+358)" -ForegroundColor White
Write-Host "   ✅ Ventajas:" -ForegroundColor Green
Write-Host "      - Ya configurado y funcionando" -ForegroundColor Gray
Write-Host "      - Testing inmediato" -ForegroundColor Gray
Write-Host "   ❌ Desventajas:" -ForegroundColor Red
Write-Host "      - No es número español (menos confianza de clientes)" -ForegroundColor Gray
Write-Host "      - Costes de SMS internacionales ligeramente más altos" -ForegroundColor Gray
Write-Host ""

Write-Host "   OPCIÓN C: WhatsApp Business API con número EXTERNO" -ForegroundColor White
Write-Host "   ⚠️  Requiere:" -ForegroundColor Yellow
Write-Host "      - Número de teléfono propio (no necesariamente Twilio)" -ForegroundColor Gray
Write-Host "      - Verificación con Meta (proceso separado)" -ForegroundColor Gray
Write-Host "      - Integración vía WhatsApp Business Platform" -ForegroundColor Gray
Write-Host ""

Write-Host "3. PROCESO PARA COMPRAR NÚMERO LOCAL ESPAÑOL:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Paso 1: Verificar cuenta Twilio" -ForegroundColor White
Write-Host "   Paso 2: Completar documentación KYC/regulatory" -ForegroundColor White
Write-Host "   Paso 3: Comprar número local (+34 9XX) desde Twilio Console" -ForegroundColor White
Write-Host "   Paso 4: Configurar número en WhatsApp Business API" -ForegroundColor White
Write-Host "   Paso 5: Solicitar verificación de negocio a Meta" -ForegroundColor White
Write-Host "   Paso 6: Crear y enviar templates para aprobación" -ForegroundColor White
Write-Host "   Paso 7: Esperar aprobación (2-7 días)" -ForegroundColor White
Write-Host ""

Write-Host "4. DOCUMENTACIÓN REQUERIDA (KYC):" -ForegroundColor Yellow
Write-Host "   - CIF/NIF del negocio" -ForegroundColor Gray
Write-Host "   - Dirección fiscal del restaurante" -ForegroundColor Gray
Write-Host "   - Datos del representante legal" -ForegroundColor Gray
Write-Host "   - Descripción del uso (confirmaciones de reservas)" -ForegroundColor Gray
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Investigación completada" -ForegroundColor Green
Write-Host "📁 Script: scripts/check_twilio_local_numbers.ps1" -ForegroundColor Gray
Write-Host ""
