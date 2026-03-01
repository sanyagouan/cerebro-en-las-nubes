# ========================================
# Script de Configuracion NotebookLM MCP
# ========================================

param(
    [string]$MCPConfigPath = "$HOME\.verdent\mcp.json",
    [string]$Profile = "standard"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION NOTEBOOKLM MCP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Node.js/npm
Write-Host "[CHECK] Verificando Node.js y npm..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>$null
    $npmVersion = npm --version 2>$null
    
    if ($nodeVersion -and $npmVersion) {
        Write-Host "  [OK] Node.js $nodeVersion" -ForegroundColor Green
        Write-Host "  [OK] npm $npmVersion" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Node.js/npm no encontrado" -ForegroundColor Red
        Write-Host "  Instala Node.js desde: https://nodejs.org/" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "  [ERROR] Node.js/npm no encontrado" -ForegroundColor Red
    Write-Host "  Instala Node.js desde: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Leer mcp.json actual
Write-Host "[STEP 1] Leyendo configuracion actual..." -ForegroundColor Yellow

if (-not (Test-Path $MCPConfigPath)) {
    Write-Host "  [ERROR] No se encontro $MCPConfigPath" -ForegroundColor Red
    exit 1
}

$mcp_content = Get-Content $MCPConfigPath -Raw | ConvertFrom-Json

# Verificar si NotebookLM ya existe
if ($mcp_content.mcpServers.notebooklm) {
    Write-Host "  [INFO] NotebookLM MCP ya esta configurado" -ForegroundColor Yellow
    Write-Host "  Actualizando configuracion..." -ForegroundColor Yellow
} else {
    Write-Host "  [INFO] Agregando nuevo servidor NotebookLM MCP" -ForegroundColor Green
}

# Crear configuracion NotebookLM
$notebooklm_config = @{
    command = "npx"
    args = @("-y", "notebooklm-mcp@latest")
    env = @{
        NOTEBOOKLM_PROFILE = $Profile
        NOTEBOOKLM_DISABLED_TOOLS = "cleanup_data"
    }
    metadata = @{
        description = "NotebookLM MCP Server - Research documentation with Gemini citations"
        version = "latest"
        configured_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    }
}

# Agregar al mcp.json
$mcp_content.mcpServers | Add-Member -MemberType NoteProperty -Name "notebooklm" -Value $notebooklm_config -Force

# Guardar
$new_mcp_content = $mcp_content | ConvertTo-Json -Depth 10
Set-Content -Path $MCPConfigPath -Value $new_mcp_content -Encoding UTF8

Write-Host "  [OK] NotebookLM MCP configurado" -ForegroundColor Green
Write-Host ""

# Test de instalacion
Write-Host "[STEP 2] Verificando instalacion del paquete..." -ForegroundColor Yellow
Write-Host "  Ejecutando: npx -y notebooklm-mcp@latest --version" -ForegroundColor Gray

try {
    $testOutput = npx -y notebooklm-mcp@latest --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Paquete notebooklm-mcp instalado correctamente" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] No se pudo verificar la version" -ForegroundColor Yellow
        Write-Host "  Esto es normal si el paquete no soporta --version" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [WARNING] No se pudo ejecutar test" -ForegroundColor Yellow
}
Write-Host ""

# Instrucciones finales
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONFIGURACION COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configuracion aplicada:" -ForegroundColor Cyan
Write-Host "  Profile: $Profile" -ForegroundColor White
Write-Host "  Disabled tools: cleanup_data" -ForegroundColor White
Write-Host "  Command: npx -y notebooklm-mcp@latest" -ForegroundColor White
Write-Host ""

Write-Host "[!] PROXIMOS PASOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. REINICIAR Verdent" -ForegroundColor Yellow
Write-Host "   Para que cargue el nuevo servidor MCP" -ForegroundColor White
Write-Host ""

Write-Host "2. AUTENTICARSE EN NOTEBOOKLM (primera vez)" -ForegroundColor Yellow
Write-Host "   En Verdent, di: 'Log me in to NotebookLM'" -ForegroundColor White
Write-Host "   Se abrira Chrome -> inicia sesion con Google" -ForegroundColor White
Write-Host ""

Write-Host "3. CREAR TU BASE DE CONOCIMIENTO" -ForegroundColor Yellow
Write-Host "   Ve a: https://notebooklm.google.com/" -ForegroundColor White
Write-Host "   Sube documentacion del proyecto (PDFs, Markdown, Google Docs)" -ForegroundColor White
Write-Host "   Comparte: Engranaje -> Cualquiera con el enlace -> Copiar" -ForegroundColor White
Write-Host ""

Write-Host "4. USAR EN VERDENT" -ForegroundColor Yellow
Write-Host "   Ejemplo: 'Consulta mi NotebookLM [link] sobre las reglas de negocio del restobar'" -ForegroundColor White
Write-Host ""

Write-Host "Documentacion completa:" -ForegroundColor Cyan
Write-Host "  https://github.com/PleasePrompto/notebooklm-mcp" -ForegroundColor White
Write-Host ""
