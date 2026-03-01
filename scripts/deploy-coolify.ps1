# Script de deployment para Coolify (Windows/PowerShell)
# Uso: .\scripts\deploy-coolify.ps1

param(
    [string]$Domain = "api.cerebro-en-las-nubes.com",
    [string]$Environment = "production"
)

Write-Host "=== Iniciando deployment de Cerebro En Las Nubes ===" -ForegroundColor Cyan
Write-Host ""

# Verificar variables de entorno
if (-not $env:COOLIFY_API_TOKEN) {
    Write-Host "ERROR: COOLIFY_API_TOKEN no esta configurado" -ForegroundColor Red
    Write-Host "Ejecuta primero: .\scripts\load_mcp_secrets.ps1" -ForegroundColor Yellow
    exit 1
}

if (-not $env:COOLIFY_API_URL) {
    Write-Host "ERROR: COOLIFY_API_URL no esta configurado" -ForegroundColor Red
    exit 1
}

Write-Host "Resumen de configuracion:" -ForegroundColor Yellow
Write-Host "  - Dominio: $Domain" -ForegroundColor White
Write-Host "  - Environment: $Environment" -ForegroundColor White
Write-Host "  - Coolify URL: $env:COOLIFY_API_URL" -ForegroundColor White
Write-Host ""

# Build Docker image
Write-Host "Construyendo imagen Docker..." -ForegroundColor Yellow
try {
    docker build -t cerebro-en-las-nubes:latest .
    Write-Host "OK: Imagen Docker construida" -ForegroundColor Green
} catch {
    Write-Host "Error construyendo imagen Docker: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SIGUIENTES PASOS MANUALES EN COOLIFY UI:" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Ve a tu panel de Coolify: $env:COOLIFY_API_URL" -ForegroundColor White
Write-Host ""
Write-Host "2. Crea un nuevo proyecto llamado: 'cerebro-en-las-nubes'" -ForegroundColor White
Write-Host ""
Write-Host "3. Anade una nueva aplicacion con estos datos:" -ForegroundColor White
Write-Host "   - Nombre: cerebro-backend" -ForegroundColor Yellow
Write-Host "   - Repositorio: https://github.com/sanyagouan/cerebro-en-las-nubes" -ForegroundColor Yellow
Write-Host "   - Rama: final-clean" -ForegroundColor Yellow
Write-Host "   - Build Pack: Dockerfile" -ForegroundColor Yellow
Write-Host "   - Puerto: 8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Configura las variables de entorno:" -ForegroundColor White
Write-Host "   (Se cargaran automaticamente desde .env.mcp)" -ForegroundColor Yellow
Write-Host ""
Write-Host "5. Configura el dominio:" -ForegroundColor White
Write-Host "   - Dominio: $Domain" -ForegroundColor Yellow
Write-Host "   - HTTPS: Habilitado" -ForegroundColor Yellow
Write-Host ""
Write-Host "6. Conecta los servicios existentes:" -ForegroundColor White
Write-Host "   - PostgreSQL (usa el existente)" -ForegroundColor Yellow
Write-Host "   - Redis (usa el existente)" -ForegroundColor Yellow
Write-Host "   - Supabase (usa el existente)" -ForegroundColor Yellow
Write-Host ""
Write-Host "7. Haz clic en 'Deploy'" -ForegroundColor White
Write-Host ""
