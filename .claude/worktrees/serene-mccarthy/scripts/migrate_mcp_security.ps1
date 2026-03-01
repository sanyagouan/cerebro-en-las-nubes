# ========================================
# Script de Migracion Automatica de Seguridad MCP
# ========================================
# Version: 2.0 - Actualizado para MCP.JSON actual
# Fecha: 2026-02-08

param(
    [string]$MCPConfigPath = "$HOME\.verdent\mcp.json"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MIGRACION DE SEGURIDAD MCP v2.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Rutas
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
$ENV_MCP = Join-Path $PROJECT_ROOT ".env.mcp"
$BACKUP_DIR = Join-Path $PROJECT_ROOT ".backups"

# Crear directorio de backups
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
}

# ========================================
# PASO 1: Backup del mcp.json original
# ========================================
Write-Host "[PASO 1] Creando backup..." -ForegroundColor Yellow

if (-not (Test-Path $MCPConfigPath)) {
    Write-Host "[ERROR] No se encontro $MCPConfigPath" -ForegroundColor Red
    exit 1
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup_file = Join-Path $BACKUP_DIR "mcp_$timestamp.json"
Copy-Item $MCPConfigPath $backup_file -Force
Write-Host "  [OK] Backup guardado: $backup_file" -ForegroundColor Green
Write-Host ""

# ========================================
# PASO 2: Leer mcp.json actual
# ========================================
Write-Host "[PASO 2] Leyendo configuracion actual..." -ForegroundColor Yellow

$mcp_content = Get-Content $MCPConfigPath -Raw | ConvertFrom-Json

# ========================================
# PASO 3: Extraer secrets y crear .env.mcp
# ========================================
Write-Host "[PASO 3] Extrayendo secrets..." -ForegroundColor Yellow

$env_lines = @(
    "# ========================================"
    "# MCP Server Credentials"
    "# ========================================"
    "# Generado: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    "# "
    "# NUNCA commitees este archivo"
    "# Para cargar: . .\scripts\load_mcp_secrets.ps1"
    "# ========================================"
    ""
    "# ========================================"
    "# SERVIDORES MCP ACTIVOS (enabled=true)"
    "# ========================================"
    ""
)

$secrets_count = 0
$servers_processed = @()

# Extraer GitHub Token (GITHUB_PERSONAL_ACCESS_TOKEN)
if ($mcp_content.mcpServers.github) {
    $token = $mcp_content.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN
    if ($token) {
        $env_lines += "# GitHub Integration (ACTIVO)"
        $env_lines += "GITHUB_PERSONAL_ACCESS_TOKEN=$token"
        $env_lines += ""
        $secrets_count++
        $servers_processed += "GitHub"
        Write-Host "  [OK] GitHub (1 variable)" -ForegroundColor Green
    }
}

# Extraer Coolify
if ($mcp_content.mcpServers.coolify) {
    $token = $mcp_content.mcpServers.coolify.env.COOLIFY_API_TOKEN
    $url = $mcp_content.mcpServers.coolify.env.COOLIFY_API_URL
    if ($token -and $url) {
        $env_lines += "# Coolify Deployment (ACTIVO - CRITICO)"
        $env_lines += "COOLIFY_API_URL=$url"
        $env_lines += "COOLIFY_API_TOKEN=$token"
        $env_lines += ""
        $secrets_count += 2
        $servers_processed += "Coolify"
        Write-Host "  [OK] Coolify (2 variables)" -ForegroundColor Green
    }
}

# Extraer Twilio
if ($mcp_content.mcpServers.twilio) {
    $sid = $mcp_content.mcpServers.twilio.env.ACCOUNT_SID
    $token = $mcp_content.mcpServers.twilio.env.AUTH_TOKEN
    $from = $mcp_content.mcpServers.twilio.env.FROM_NUMBER
    if ($sid -and $token -and $from) {
        $env_lines += "# Twilio WhatsApp/SMS (ACTIVO - CRITICO)"
        $env_lines += "TWILIO_ACCOUNT_SID=$sid"
        $env_lines += "TWILIO_AUTH_TOKEN=$token"
        $env_lines += "TWILIO_FROM_NUMBER=$from"
        $env_lines += ""
        $secrets_count += 3
        $servers_processed += "Twilio"
        Write-Host "  [OK] Twilio (3 variables)" -ForegroundColor Green
    }
}

# Extraer Airtable
if ($mcp_content.mcpServers.airtable) {
    $api_key = $mcp_content.mcpServers.airtable.env.AIRTABLE_API_KEY
    if ($api_key) {
        $env_lines += "# Airtable Database (ACTIVO - CRITICO)"
        $env_lines += "# Regenerar desde: https://airtable.com/create/tokens"
        $env_lines += "# Scopes: data.records:read, data.records:write, schema.bases:read"
        $env_lines += "AIRTABLE_API_KEY=$api_key"
        $env_lines += ""
        $secrets_count++
        $servers_processed += "Airtable"
        Write-Host "  [OK] Airtable (1 variable)" -ForegroundColor Green
    }
}

# Extraer Supabase (CASO ESPECIAL: args en lugar de env)
if ($mcp_content.mcpServers.'supabase-mcp-server') {
    $args = $mcp_content.mcpServers.'supabase-mcp-server'.args
    $url = $null
    $token = $null
    
    # Buscar --url y --access-token en args
    for ($i = 0; $i -lt $args.Count; $i++) {
        if ($args[$i] -eq "--url" -and ($i + 1) -lt $args.Count) {
            $url = $args[$i + 1]
        }
        if ($args[$i] -eq "--access-token" -and ($i + 1) -lt $args.Count) {
            $token = $args[$i + 1]
        }
    }
    
    if ($url -and $token) {
        $env_lines += "# Supabase Backend (ACTIVO - CRITICO)"
        $env_lines += "# NOTA: Estos valores van en args del comando, no en env"
        $env_lines += "SUPABASE_URL=$url"
        $env_lines += "SUPABASE_ACCESS_TOKEN=$token"
        $env_lines += ""
        $secrets_count += 2
        $servers_processed += "Supabase"
        Write-Host "  [OK] Supabase (2 variables en args)" -ForegroundColor Green
    }
}

# Servidores deshabilitados
$env_lines += ""
$env_lines += "# ========================================"
$env_lines += "# SERVIDORES MCP DESHABILITADOS"
$env_lines += "# ========================================"
$env_lines += ""

# Extraer n8n (DESHABILITADO)
if ($mcp_content.mcpServers.'n8n-mcp') {
    $api_key = $mcp_content.mcpServers.'n8n-mcp'.env.N8N_API_KEY
    $api_url = $mcp_content.mcpServers.'n8n-mcp'.env.N8N_API_URL
    if ($api_key -and $api_url) {
        $env_lines += "# n8n Workflow Automation (DESHABILITADO)"
        $env_lines += "N8N_API_URL=$api_url"
        $env_lines += "N8N_API_KEY=$api_key"
        $env_lines += ""
        $secrets_count += 2
        $servers_processed += "n8n (disabled)"
        Write-Host "  [OK] n8n (2 variables - deshabilitado)" -ForegroundColor Yellow
    }
}

# Extraer Perplexity (DESHABILITADO)
if ($mcp_content.mcpServers.'perplexity-ask') {
    $api_key = $mcp_content.mcpServers.'perplexity-ask'.env.PERPLEXITY_API_KEY
    if ($api_key) {
        $env_lines += "# Perplexity AI Search (DESHABILITADO)"
        $env_lines += "PERPLEXITY_API_KEY=$api_key"
        $env_lines += ""
        $secrets_count++
        $servers_processed += "Perplexity (disabled)"
        Write-Host "  [OK] Perplexity (1 variable - deshabilitado)" -ForegroundColor Yellow
    }
}

# Escribir .env.mcp
$env_content = $env_lines -join "`n"
Set-Content -Path $ENV_MCP -Value $env_content -Encoding UTF8 -NoNewline

Write-Host ""
Write-Host "  [OK] Extraidos $secrets_count secrets de $($servers_processed.Count) servidores" -ForegroundColor Green
Write-Host "  [OK] Creado: .env.mcp" -ForegroundColor Green
Write-Host ""

# ========================================
# PASO 4: Refactorizar mcp.json
# ========================================
Write-Host "[PASO 4] Refactorizando mcp.json..." -ForegroundColor Yellow

# Actualizar GitHub
if ($mcp_content.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN) {
    $mcp_content.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN = '${GITHUB_PERSONAL_ACCESS_TOKEN}'
}

# Actualizar Coolify
if ($mcp_content.mcpServers.coolify.env.COOLIFY_API_TOKEN) {
    $mcp_content.mcpServers.coolify.env.COOLIFY_API_TOKEN = '${COOLIFY_API_TOKEN}'
    $mcp_content.mcpServers.coolify.env.COOLIFY_API_URL = '${COOLIFY_API_URL}'
}

# Actualizar Twilio
if ($mcp_content.mcpServers.twilio.env.ACCOUNT_SID) {
    $mcp_content.mcpServers.twilio.env.ACCOUNT_SID = '${TWILIO_ACCOUNT_SID}'
    $mcp_content.mcpServers.twilio.env.AUTH_TOKEN = '${TWILIO_AUTH_TOKEN}'
    $mcp_content.mcpServers.twilio.env.FROM_NUMBER = '${TWILIO_FROM_NUMBER}'
}

# Actualizar Airtable
if ($mcp_content.mcpServers.airtable.env.AIRTABLE_API_KEY) {
    $mcp_content.mcpServers.airtable.env.AIRTABLE_API_KEY = '${AIRTABLE_API_KEY}'
}

# Actualizar Supabase (en args)
if ($mcp_content.mcpServers.'supabase-mcp-server'.args) {
    $args = $mcp_content.mcpServers.'supabase-mcp-server'.args
    for ($i = 0; $i -lt $args.Count; $i++) {
        if ($args[$i] -eq "--url" -and ($i + 1) -lt $args.Count) {
            $args[$i + 1] = '${SUPABASE_URL}'
        }
        if ($args[$i] -eq "--access-token" -and ($i + 1) -lt $args.Count) {
            $args[$i + 1] = '${SUPABASE_ACCESS_TOKEN}'
        }
    }
}

# Actualizar n8n (deshabilitado)
if ($mcp_content.mcpServers.'n8n-mcp'.env.N8N_API_KEY) {
    $mcp_content.mcpServers.'n8n-mcp'.env.N8N_API_KEY = '${N8N_API_KEY}'
    $mcp_content.mcpServers.'n8n-mcp'.env.N8N_API_URL = '${N8N_API_URL}'
}

# Actualizar Perplexity (deshabilitado)
if ($mcp_content.mcpServers.'perplexity-ask'.env.PERPLEXITY_API_KEY) {
    $mcp_content.mcpServers.'perplexity-ask'.env.PERPLEXITY_API_KEY = '${PERPLEXITY_API_KEY}'
}

# Escribir nuevo mcp.json
$new_mcp_content = $mcp_content | ConvertTo-Json -Depth 10
Set-Content -Path $MCPConfigPath -Value $new_mcp_content -Encoding UTF8

Write-Host "  [OK] mcp.json refactorizado" -ForegroundColor Green
Write-Host ""

# ========================================
# PASO 5: Cargar variables de entorno
# ========================================
Write-Host "[PASO 5] Cargando variables de entorno..." -ForegroundColor Yellow

$load_script = Join-Path $PROJECT_ROOT "scripts\load_mcp_secrets.ps1"
if (Test-Path $load_script) {
    . $load_script
} else {
    Write-Host "  [WARNING] No se encontro load_mcp_secrets.ps1" -ForegroundColor Yellow
}

# ========================================
# PASO 6: Validacion
# ========================================
Write-Host ""
Write-Host "[PASO 6] Validando migracion..." -ForegroundColor Yellow

# Verificar que NO hay secrets en texto plano
$mcp_text = Get-Content $MCPConfigPath -Raw

$found_secrets = @()
if ($mcp_text -match 'ghp_[a-zA-Z0-9]{36}') { $found_secrets += "GitHub Token" }
if ($mcp_text -match 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[^"]+') { $found_secrets += "JWT Token" }
if ($mcp_text -match 'AC[a-f0-9]{32}') { $found_secrets += "Twilio SID" }
if ($mcp_text -match 'pat[a-zA-Z0-9]{8,}\.') { $found_secrets += "Airtable Token" }
if ($mcp_text -match 'pplx-[a-zA-Z0-9]{40,}') { $found_secrets += "Perplexity Token" }
if ($mcp_text -match '1[34]\|[a-zA-Z0-9]{40,}') { $found_secrets += "Coolify Token" }

if ($found_secrets.Count -gt 0) {
    Write-Host "  [WARNING] Se encontraron secrets en texto plano:" -ForegroundColor Red
    foreach ($secret in $found_secrets) {
        Write-Host "    - $secret" -ForegroundColor Red
    }
} else {
    Write-Host "  [OK] NO hay secrets en texto plano en mcp.json" -ForegroundColor Green
}

# Verificar .gitignore
$gitignore_path = Join-Path $PROJECT_ROOT ".gitignore"
if (Test-Path $gitignore_path) {
    $gitignore = Get-Content $gitignore_path -Raw
    if ($gitignore -match '\.env\.mcp') {
        Write-Host "  [OK] .env.mcp esta en .gitignore" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] .env.mcp NO esta en .gitignore" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MIGRACION COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Resumen:" -ForegroundColor Cyan
Write-Host "  Servidores procesados: $($servers_processed.Count)" -ForegroundColor White
foreach ($server in $servers_processed) {
    Write-Host "    - $server" -ForegroundColor White
}
Write-Host "  Secrets extraidos: $secrets_count" -ForegroundColor White
Write-Host "  Backup original: $backup_file" -ForegroundColor White
Write-Host ""

Write-Host "[!] PROXIMOS PASOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. VERIFICAR .env.mcp:" -ForegroundColor Yellow
Write-Host "   Abre el archivo y confirma que todos los tokens son correctos" -ForegroundColor White
Write-Host ""

Write-Host "2. REGENERAR Tokens si es necesario:" -ForegroundColor Yellow
Write-Host "   - Airtable: https://airtable.com/create/tokens" -ForegroundColor White
Write-Host "   - GitHub: https://github.com/settings/tokens" -ForegroundColor White
Write-Host "   - Coolify: https://coolify.generaia.site/security/api-tokens" -ForegroundColor White
Write-Host ""

Write-Host "3. REINICIAR Verdent:" -ForegroundColor Yellow
Write-Host "   Ejecuta: . .\scripts\load_mcp_secrets.ps1" -ForegroundColor White
Write-Host "   Luego reinicia Verdent para aplicar cambios" -ForegroundColor White
Write-Host ""
