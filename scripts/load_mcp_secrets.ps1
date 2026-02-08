# ========================================
# Load MCP Secrets from .env.mcp
# ========================================
# 
# USO:
#   . .\scripts\load_mcp_secrets.ps1
#
# Este script carga las variables de entorno desde .env.mcp
# de forma segura para que los servidores MCP puedan acceder a ellas.
# ========================================

$ErrorActionPreference = "Stop"

# Detectar raíz del proyecto
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# Ruta al archivo de secrets
$EnvFile = Join-Path $ProjectRoot ".env.mcp"

# Verificar que el archivo existe
if (-Not (Test-Path $EnvFile)) {
    Write-Host "[ERROR] No se encontro .env.mcp" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "1. Copia .env.mcp.example a .env.mcp" -ForegroundColor Yellow
    Write-Host "2. Completa los valores reales de tus secrets" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Comando:" -ForegroundColor Cyan
    Write-Host "  Copy-Item .env.mcp.example .env.mcp" -ForegroundColor Cyan
    exit 1
}

Write-Host "[CARGANDO] Secrets desde .env.mcp..." -ForegroundColor Cyan
Write-Host ""

# Contador de variables cargadas
$LoadedCount = 0

# Leer archivo línea por línea
Get-Content $EnvFile | ForEach-Object {
    $Line = $_.Trim()
    
    # Ignorar líneas vacías y comentarios
    if ($Line -and -not $Line.StartsWith("#")) {
        # Separar clave=valor
        if ($Line -match "^([^=]+)=(.*)$") {
            $Key = $matches[1].Trim()
            $Value = $matches[2].Trim()
            
            # Remover comillas si existen
            $Value = $Value -replace '^"(.*)"$', '$1'
            $Value = $Value -replace "^'(.*)'$", '$1'
            
            # Setear variable de entorno
            [Environment]::SetEnvironmentVariable($Key, $Value, "Process")
            
            # Mostrar (ocultando el valor real)
            $MaskedValue = if ($Value.Length -gt 10) {
                $Value.Substring(0, 6) + "..." + $Value.Substring($Value.Length - 4)
            } else {
                "***"
            }
            
            Write-Host "  [OK] $Key = $MaskedValue" -ForegroundColor Green
            $LoadedCount++
        }
    }
}

Write-Host ""
Write-Host "[SUCCESS] Cargadas $LoadedCount variables de entorno" -ForegroundColor Green
Write-Host ""
Write-Host "Ahora puedes ejecutar Verdent y los MCPs tendran acceso a los secrets." -ForegroundColor Cyan
Write-Host ""

# Validar que las variables críticas estén cargadas
$CriticalVars = @(
    "AIRTABLE_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "COOLIFY_API_TOKEN",
    "SUPABASE_ACCESS_TOKEN"
)

$MissingCritical = @()
foreach ($Var in $CriticalVars) {
    if (-not [Environment]::GetEnvironmentVariable($Var, "Process")) {
        $MissingCritical += $Var
    }
}

if ($MissingCritical.Count -gt 0) {
    Write-Host "[WARNING] Faltan variables criticas:" -ForegroundColor Yellow
    foreach ($Var in $MissingCritical) {
        Write-Host "   - $Var" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "El sistema puede no funcionar correctamente en produccion." -ForegroundColor Yellow
    Write-Host ""
}
