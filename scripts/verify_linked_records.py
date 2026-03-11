"""
Script para verificar que todos los campos linked record están creados correctamente.
"""

import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env.mcp')

# Configuración
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
BASE_ID = 'appQ2ZXAR68cqDmJt'

# IDs de tablas
CLIENTES_TABLE_ID = 'tblPcVRnFTKDu7Z9t'
PREFERENCIAS_TABLE_ID = 'tbl6xjlRuyJZMmzOV'
NOTAS_TABLE_ID = 'tbl5RZ31kxSOkGe0U'
RESERVAS_TABLE_ID = 'tblHPyRRo18IwBAUC'

headers = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def check_table_linked_fields(table_id, table_name):
    """Verifica los campos linked record de una tabla."""
    try:
        url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables/{table_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            table_info = response.json()
            linked_fields = [
                f for f in table_info.get('fields', [])
                if f.get('type') == 'multipleRecordLinks'
            ]
            
            print(f"\n{table_name} ({table_id}):")
            if linked_fields:
                for field in linked_fields:
                    linked_table = field.get('options', {}).get('linkedTableId', 'N/A')
                    field_id = field.get('id', 'N/A')
                    print(f"  - {field['name']} (ID: {field_id}) -> {linked_table}")
            else:
                print("  [INFO] No hay campos linked record")
                
    except Exception as e:
        print(f"  [ERROR] Error verificando tabla: {e}")

print("[INFO] Verificando campos linked record en todas las tablas...\n")
print("="*60)

check_table_linked_fields(CLIENTES_TABLE_ID, "Clientes")
check_table_linked_fields(PREFERENCIAS_TABLE_ID, "ClientePreferencias")
check_table_linked_fields(NOTAS_TABLE_ID, "ClienteNotas")
check_table_linked_fields(RESERVAS_TABLE_ID, "Reservas")

print("\n" + "="*60)
print("\n[OK] Verificacion completada!")
