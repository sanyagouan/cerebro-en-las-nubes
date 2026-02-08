# ========================================
# Set MCP Environment Variables Permanently
# ========================================
# 
# Este script configura las variables de entorno de forma PERMANENTE
# en el sistema Windows para el usuario actual.
#
# ADVERTENCIA: Solo ejecutar si quieres que las variables persistan
# despues de reiniciar Windows.
#
# USO:
#   .\scripts\set_permanent_env_vars.ps1
#
# ========================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION PERMANENTE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que se ejecuta como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARNING] Este script NO requiere privilegios de administrador" -ForegroundColor Yellow
    Write-Host "           Se configuraran variables a nivel de USUARIO" -ForegroundColor Yellow
    Write-Host ""
}

# Confirmar con el usuario
Write-Host "Este script configurara las variables de entorno de forma PERMANENTE." -ForegroundColor Yellow
Write-Host "Las variables estaran disponibles despues de reiniciar Windows." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Deseas continuar? (S/N)"

if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "[CANCELADO] No se realizaron cambios" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[PASO 1] Leyendo .env.mcp..." -ForegroundColor Yellow

# Detectar raíz del proyecto
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $ProjectRoot ".env.mcp"

if (-Not (Test-Path $EnvFile)) {
    Write-Host "[ERROR] No se encontro .env.mcp" -ForegroundColor Red
    exit 1
}

# Leer variables
$varsSet = 0
$varsFailed = @()

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
            
            try {
                # Setear variable de entorno permanente (User level)
                [System.Environment]::SetEnvironmentVariable($Key, $Value, [System.EnvironmentVariableTarget]::User)
                
                # Mostrar (ocultando el valor real)
                $MaskedValue = if ($Value.Length -gt 10) {
                    $Value.Substring(0, 6) + "..." + $Value.Substring($Value.Length - 4)
                } else {
                    "***"
                }
                
                Write-Host "  [OK] $Key = $MaskedValue (PERMANENTE)" -ForegroundColor Green
                $varsSet++
            }
            catch {
                Write-Host "  [ERROR] $Key = Fallo al configurar" -ForegroundColor Red
                $varsFailed += $Key
            }
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Variables configuradas: $varsSet" -ForegroundColor White

if ($varsFailed.Count -gt 0) {
    Write-Host ""
    Write-Host "[WARNING] Variables que fallaron:" -ForegroundColor Yellow
    foreach ($var in $varsFailed) {
        Write-Host "  - $var" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[!] IMPORTANTE:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Las variables estan configuradas a nivel de USUARIO" -ForegroundColor White
Write-Host "2. Para que Verdent las vea, debes:" -ForegroundColor White
Write-Host "   a) CERRAR Verdent completamente" -ForegroundColor Cyan
Write-Host "   b) Abrir una NUEVA ventana de PowerShell" -ForegroundColor Cyan
Write-Host "   c) Ejecutar: verdent" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Ahora las variables estaran disponibles siempre" -ForegroundColor White
Write-Host "   (incluso despues de reiniciar Windows)" -ForegroundColor White
Write-Host ""

Write-Host "[SUCCESS] Configuracion permanente completada" -ForegroundColor Green
Write-Host ""
