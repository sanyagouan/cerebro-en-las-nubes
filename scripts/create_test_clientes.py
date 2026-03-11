"""
Script para crear 3 clientes de ejemplo con sus preferencias y notas.
Base ID: appQ2ZXAR68cqDmJt

Tablas:
- Clientes: tblPcVRnFTKDu7Z9t
- ClientePreferencias: tbl6xjlRuyJZMmzOV
- ClienteNotas: tbl5RZ31kxSOkGe0U
"""

import os
from datetime import datetime, timezone
from pyairtable import Api

# Configuracion
BASE_ID = "appQ2ZXAR68cqDmJt"
CLIENTES_TABLE_ID = "tblPcVRnFTKDu7Z9t"
PREFERENCIAS_TABLE_ID = "tbl6xjlRuyJZMmzOV"
NOTAS_TABLE_ID = "tbl5RZ31kxSOkGe0U"

# Verificar API key
api_key = os.environ.get("AIRTABLE_API_KEY")
if not api_key:
    raise ValueError("AIRTABLE_API_KEY no encontrada en variables de entorno")

# Inicializar cliente
api = Api(api_key)
table_clientes = api.table(BASE_ID, CLIENTES_TABLE_ID)
table_preferencias = api.table(BASE_ID, PREFERENCIAS_TABLE_ID)
table_notas = api.table(BASE_ID, NOTAS_TABLE_ID)

# Timestamp ISO 8601 actual
ahora = datetime.now(timezone.utc).isoformat()

print("=" * 80)
print("CREANDO CLIENTES DE EJEMPLO")
print("=" * 80)

# ============================================================================
# CLIENTE 1: Juan Perez Garcia
# ============================================================================
print("\n[1/3] Creando cliente: Juan Perez Garcia...")

cliente1_data = {
    "Nombre": "Juan Perez Garcia",
    "Teléfono": "+34600111222",
    "Email": "juan.perez@example.com",
    "Tier": "Regular",
    "Total_Reservas": 0,
    "Reservas_Completadas": 0,
    "Reservas_Canceladas": 0,
    "No_Shows": 0,
    "Notas_Staff": "Cliente habitual, viene los viernes"
}

try:
    cliente1 = table_clientes.create(cliente1_data)
    cliente1_id = cliente1["id"]
    print(f"  [OK] Cliente creado: {cliente1_id}")
    
    # Preferencias Cliente 1
    print("  Creando preferencias...")
    
    # Preferencia 1: Zona favorita
    pref1_1 = table_preferencias.create({
        "Descripcion": "Prefiere terraza con vistas",
        "Tipo": "zona_favorita",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente1_id]
    })
    print(f"    [OK] Preferencia 1: {pref1_1['id']}")
    
    # Preferencia 2: Restriccion dietetica
    pref1_2 = table_preferencias.create({
        "Descripcion": "Alergico a frutos secos",
        "Tipo": "restriccion_dietetica",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente1_id]
    })
    print(f"    [OK] Preferencia 2: {pref1_2['id']}")
    
    # Notas Cliente 1
    print("  Creando notas...")
    
    nota1_1 = table_notas.create({
        "Contenido": "Siempre pide el cachopo. Muy puntual y educado.",
        "Es_Importante": "No",
        "Staff_Nombre": "Alba (Recepcion)",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente1_id]
    })
    print(f"    [OK] Nota 1: {nota1_1['id']}")
    
except Exception as e:
    print(f"  [ERROR] {e}")

# ============================================================================
# CLIENTE 2: Maria Lopez Sanchez
# ============================================================================
print("\n[2/3] Creando cliente: Maria Lopez Sanchez...")

cliente2_data = {
    "Nombre": "Maria Lopez Sanchez",
    "Teléfono": "+34600222333",
    "Email": "maria.lopez@example.com",
    "Tier": "Regular",
    "Total_Reservas": 0,
    "Reservas_Completadas": 0,
    "Reservas_Canceladas": 0,
    "No_Shows": 0,
    "Notas_Staff": "Reserva para aniversario cada ano en febrero"
}

try:
    cliente2 = table_clientes.create(cliente2_data)
    cliente2_id = cliente2["id"]
    print(f"  [OK] Cliente creado: {cliente2_id}")
    
    # Preferencias Cliente 2
    print("  Creando preferencias...")
    
    pref2_1 = table_preferencias.create({
        "Descripcion": "Vegetariana estricta",
        "Tipo": "restriccion_dietetica",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente2_id]
    })
    print(f"    [OK] Preferencia 1: {pref2_1['id']}")
    
    pref2_2 = table_preferencias.create({
        "Descripcion": "Prefiere interior, mesa tranquila",
        "Tipo": "zona_favorita",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente2_id]
    })
    print(f"    [OK] Preferencia 2: {pref2_2['id']}")
    
    pref2_3 = table_preferencias.create({
        "Descripcion": "Aniversario en febrero - decoracion especial",
        "Tipo": "ocasion_celebracion",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente2_id]
    })
    print(f"    [OK] Preferencia 3: {pref2_3['id']}")
    
    # Notas Cliente 2
    print("  Creando notas...")
    
    nota2_1 = table_notas.create({
        "Contenido": "Cliente VIP. Recordar decorar mesa para aniversario cada 14 de febrero.",
        "Es_Importante": "Sí",
        "Staff_Nombre": "Carmen (Encargada)",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente2_id]
    })
    print(f"    [OK] Nota 1: {nota2_1['id']}")
    
except Exception as e:
    print(f"  [ERROR] {e}")

# ============================================================================
# CLIENTE 3: Carlos Fernandez Ruiz
# ============================================================================
print("\n[3/3] Creando cliente: Carlos Fernandez Ruiz...")

cliente3_data = {
    "Nombre": "Carlos Fernandez Ruiz",
    "Teléfono": "+34600333444",
    "Tier": "Regular",
    "Total_Reservas": 0,
    "Reservas_Completadas": 0,
    "Reservas_Canceladas": 0,
    "No_Shows": 0,
    "Notas_Staff": "Familia numerosa, suele reservar mesa de 6"
}

try:
    cliente3 = table_clientes.create(cliente3_data)
    cliente3_id = cliente3["id"]
    print(f"  [OK] Cliente creado: {cliente3_id}")
    
    # Preferencias Cliente 3
    print("  Creando preferencias...")
    
    pref3_1 = table_preferencias.create({
        "Descripcion": "Viene con ninos pequenos, necesita trona",
        "Tipo": "solicitud_especial",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente3_id]
    })
    print(f"    [OK] Preferencia 1: {pref3_1['id']}")
    
    pref3_2 = table_preferencias.create({
        "Descripcion": "Prefiere mesas amplias para 6 personas",
        "Tipo": "solicitud_especial",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente3_id]
    })
    print(f"    [OK] Preferencia 2: {pref3_2['id']}")
    
    # Notas Cliente 3
    print("  Creando notas...")
    
    nota3_1 = table_notas.create({
        "Contenido": "Tiene 2 ninos de 3 y 5 anos. Siempre pide 2 tronas. Muy educados.",
        "Es_Importante": "Sí",
        "Staff_Nombre": "Laura (Camarera)",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente3_id]
    })
    print(f"    [OK] Nota 1: {nota3_1['id']}")
    
    nota3_2 = table_notas.create({
        "Contenido": "Los ninos aman las croquetas. Siempre pedir racion extra.",
        "Es_Importante": "No",
        "Staff_Nombre": "Miguel (Camarero)",
        "Fecha_Creacion": ahora,
        "Cliente": [cliente3_id]
    })
    print(f"    [OK] Nota 2: {nota3_2['id']}")
    
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n" + "=" * 80)
print("[OK] PROCESO COMPLETADO")
print("=" * 80)
print("\nResumen:")
print("  * 3 clientes creados")
print("  * 7 preferencias creadas (2 + 3 + 2)")
print("  * 4 notas creadas (1 + 1 + 2)")
print("\nVerifica los datos en Airtable:")
print("  https://airtable.com/appQ2ZXAR68cqDmJt")
