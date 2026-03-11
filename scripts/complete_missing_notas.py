"""
Script para completar las notas faltantes de los clientes ya creados.
Solo crea las notas que fallaron por el error de "Si" vs "Sí".

Base ID: appQ2ZXAR68cqDmJt
Tabla: ClienteNotas (tbl5RZ31kxSOkGe0U)
"""

import os
from datetime import datetime, timezone
from pyairtable import Api

# Configuracion
BASE_ID = "appQ2ZXAR68cqDmJt"
NOTAS_TABLE_ID = "tbl5RZ31kxSOkGe0U"

# IDs de clientes ya creados
MARIA_ID = "recvkIZd1hw8JRGkj"  # Maria Lopez Sanchez
CARLOS_ID = "rec8tontbbQVC7NvF"  # Carlos Fernandez Ruiz

# Verificar API key
api_key = os.environ.get("AIRTABLE_API_KEY")
if not api_key:
    raise ValueError("AIRTABLE_API_KEY no encontrada en variables de entorno")

# Inicializar cliente
api = Api(api_key)
table_notas = api.table(BASE_ID, NOTAS_TABLE_ID)

# Timestamp ISO 8601 actual
ahora = datetime.now(timezone.utc).isoformat()

print("=" * 80)
print("COMPLETANDO NOTAS FALTANTES")
print("=" * 80)

# ============================================================================
# Nota para Maria Lopez Sanchez
# ============================================================================
print("\n[1/3] Creando nota faltante para Maria Lopez Sanchez...")

try:
    nota_maria = table_notas.create({
        "Contenido": "Cliente VIP. Recordar decorar mesa para aniversario cada 14 de febrero.",
        "Es_Importante": "Sí",  # Corregido con tilde
        "Staff_Nombre": "Carmen (Encargada)",
        "Fecha_Creacion": ahora,
        "Cliente": [MARIA_ID]
    })
    print(f"  [OK] Nota creada: {nota_maria['id']}")
except Exception as e:
    print(f"  [ERROR] {e}")

# ============================================================================
# Notas para Carlos Fernandez Ruiz
# ============================================================================
print("\n[2/3] Creando primera nota faltante para Carlos Fernandez Ruiz...")

try:
    nota_carlos_1 = table_notas.create({
        "Contenido": "Tiene 2 ninos de 3 y 5 anos. Siempre pide 2 tronas. Muy educados.",
        "Es_Importante": "Sí",  # Corregido con tilde
        "Staff_Nombre": "Laura (Camarera)",
        "Fecha_Creacion": ahora,
        "Cliente": [CARLOS_ID]
    })
    print(f"  [OK] Nota creada: {nota_carlos_1['id']}")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n[3/3] Creando segunda nota para Carlos Fernandez Ruiz...")

try:
    nota_carlos_2 = table_notas.create({
        "Contenido": "Los ninos aman las croquetas. Siempre pedir racion extra.",
        "Es_Importante": "No",
        "Staff_Nombre": "Miguel (Camarero)",
        "Fecha_Creacion": ahora,
        "Cliente": [CARLOS_ID]
    })
    print(f"  [OK] Nota creada: {nota_carlos_2['id']}")
except Exception as e:
    print(f"  [ERROR] {e}")

print("\n" + "=" * 80)
print("[OK] PROCESO COMPLETADO")
print("=" * 80)
print("\nResumen:")
print("  * 3 notas creadas")
print("  * Maria Lopez Sanchez: 1 nota")
print("  * Carlos Fernandez Ruiz: 2 notas")
print("\nVerifica los datos en Airtable:")
print("  https://airtable.com/appQ2ZXAR68cqDmJt/tbl5RZ31kxSOkGe0U")
