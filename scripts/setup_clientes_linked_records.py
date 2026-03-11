"""
Script para crear campos linked record en las tablas relacionadas con Clientes.

Este script usa la API REST de Airtable para crear los campos multipleRecordLinks
que no se pueden crear mediante el MCP de Airtable.

Campos a crear:
1. ClientePreferencias.Cliente -> Clientes
2. ClienteNotas.Cliente -> Clientes
3. Reservas.Cliente -> Clientes (NUEVO)

Usage:
    python scripts/setup_clientes_linked_records.py
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.mcp')

# Configuración
AIRTABLE_TOKEN = os.getenv('AIRTABLE_API_KEY')
BASE_ID = "appQ2ZXAR68cqDmJt"

# IDs de tablas
CLIENTES_TABLE_ID = "tblPcVRnFTKDu7Z9t"
CLIENTE_PREFERENCIAS_TABLE_ID = "tbl6xjlRuyJZMmzOV"
CLIENTE_NOTAS_TABLE_ID = "tbl5RZ31kxSOkGe0U"
RESERVAS_TABLE_ID = "tblHPyRRo18IwBAUC"

# URL base de la API
BASE_URL = "https://api.airtable.com/v0/meta"

# Headers para autenticación
headers = {
    "Authorization": f"Bearer {AIRTABLE_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("CONFIGURACIÓN DE LINKED RECORDS - TABLA CLIENTES")
print("=" * 60)
print(f"Base ID: {BASE_ID}")
print(f"Tablas:")
print(f"  - Clientes: {CLIENTES_TABLE_ID}")
print(f"  - ClientePreferencias: {CLIENTE_PREFERENCIAS_TABLE_ID}")
print(f"  - ClienteNotas: {CLIENTE_NOTAS_TABLE_ID}")
print(f"  - Reservas: {RESERVAS_TABLE_ID}")
print("=" * 60)

# ============================================================
# PASO 1: Vincular ClientePreferencias con Clientes
# ============================================================
print("\n1. Creando campo 'Cliente' en ClientePreferencias...")

# URL para crear campo en tabla ClientePreferencias
preferencias_url = f"{BASE_URL}/bases/{BASE_ID}/tables/{CLIENTE_PREFERENCIAS_TABLE_ID}/fields"

# Crear campo Cliente en ClientePreferencias
preferencias_field_data = {
    "name": "Cliente",
    "type": "multipleRecordLinks",
    "options": {
        "linkedTableId": CLIENTES_TABLE_ID
    }
}

try:
    response = requests.post(preferencias_url, json=preferencias_field_data, headers=headers)
    
    if response.status_code in [200, 201]:
        field_info = response.json()
        field_id = field_info.get('id', 'UNKNOWN')
        print(f"   [OK] Campo 'Cliente' creado en ClientePreferencias (ID: {field_id})")
    else:
        print(f"   [ERROR] Codigo {response.status_code}: {response.text}")
except Exception as e:
    print(f"   [ERROR] Excepcion: {e}")

# ============================================================
# PASO 2: Vincular ClienteNotas con Clientes
# ============================================================
print("\n2. Creando campo 'Cliente' en ClienteNotas...")

# URL para crear campo en tabla ClienteNotas
notas_url = f"{BASE_URL}/bases/{BASE_ID}/tables/{CLIENTE_NOTAS_TABLE_ID}/fields"

# Crear campo Cliente en ClienteNotas
notas_field_data = {
    "name": "Cliente",
    "type": "multipleRecordLinks",
    "options": {
        "linkedTableId": CLIENTES_TABLE_ID
    }
}

try:
    response = requests.post(notas_url, json=notas_field_data, headers=headers)
    
    if response.status_code in [200, 201]:
        field_info = response.json()
        field_id = field_info.get('id', 'UNKNOWN')
        print(f"   [OK] Campo 'Cliente' creado en ClienteNotas (ID: {field_id})")
    else:
        print(f"   [ERROR] Codigo {response.status_code}: {response.text}")
except Exception as e:
    print(f"   [ERROR] Excepcion: {e}")

# ============================================================
# PASO 3: Vincular Clientes con Reservas
# ============================================================
print("\n3. Creando campo 'Cliente' en Reservas...")

# URL para crear campo en tabla Reservas
reservas_url = f"{BASE_URL}/bases/{BASE_ID}/tables/{RESERVAS_TABLE_ID}/fields"

# Crear campo Cliente en Reservas
reservas_field_data = {
    "name": "Cliente",
    "type": "multipleRecordLinks",
    "options": {
        "linkedTableId": CLIENTES_TABLE_ID
    }
}

try:
    response = requests.post(reservas_url, json=reservas_field_data, headers=headers)
    
    if response.status_code in [200, 201]:
        field_info = response.json()
        field_id = field_info.get('id', 'UNKNOWN')
        print(f"   [OK] Campo 'Cliente' creado en Reservas (ID: {field_id})")
    else:
        print(f"   [ERROR] Codigo {response.status_code}: {response.text}")
except Exception as e:
    print(f"   [ERROR] Excepcion: {e}")

print("\n" + "=" * 60)
print("PROCESO COMPLETADO")
print("=" * 60)
print("\nVerifica los campos creados en Airtable:")
print("1. ClientePreferencias.Cliente -> Clientes")
print("2. ClienteNotas.Cliente -> Clientes")
print("3. Reservas.Cliente -> Clientes")
print("\nLos campos inversos se crean automaticamente en la tabla Clientes:")
print("- Clientes.ClientePreferencias")
print("- Clientes.ClienteNotas")
print("- Clientes.Reservas")
print("=" * 60)
