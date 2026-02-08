# ========================================
# Start Verdent with MCP Secrets Loaded
# ========================================
# 
# Este script carga las variables de entorno desde .env.mcp
# y luego inicia Verdent en la misma sesión.
#
# USO:
#   .\scripts\start_verdent.ps1
#
# ========================================

$ErrorActionPreference = "Stop"

# Detectar raíz del proyecto
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIANDO VERDENT CON SECRETS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cargar secrets
Write-Host "[PASO 1] Cargando secrets desde .env.mcp..." -ForegroundColor Yellow
$LoadScript = Join-Path $ProjectRoot "scripts\load_mcp_secrets.ps1"

if (Test-Path $LoadScript) {
    . $LoadScript
} else {
    Write-Host "[ERROR] No se encontro load_mcp_secrets.ps1" -ForegroundColor Red
    exit 1
}

# Verificar que las variables críticas están cargadas
Write-Host ""
Write-Host "[PASO 2] Verificando variables críticas..." -ForegroundColor Yellow

$CriticalVars = @(
    "AIRTABLE_API_KEY",
    "TWILIO_ACCOUNT_SID",
    "COOLIFY_API_TOKEN",
    "SUPABASE_ACCESS_TOKEN"
)

$AllLoaded = $true
foreach ($Var in $CriticalVars) {
    $Value = [Environment]::GetEnvironmentVariable($Var, "Process")
    if (-not $Value) {
        Write-Host "  [ERROR] $Var no cargada" -ForegroundColor Red
        $AllLoaded = $false
    } else {
        Write-Host "  [OK] $Var cargada" -ForegroundColor Green
    }
}

if (-not $AllLoaded) {
    Write-Host ""
    Write-Host "[ERROR] Faltan variables críticas. Verifica .env.mcp" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[PASO 3] Iniciando Verdent..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  VERDENT INICIADO CON SECRETS" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Iniciar Verdent
verdent
