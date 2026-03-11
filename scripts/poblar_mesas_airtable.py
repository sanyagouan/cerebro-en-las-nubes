#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para poblar la tabla Mesas de Airtable según los planos físicos.

Basado en:
- docs/PLANO_MESAS_INTERIOR.md (4 zonas, 11 mesas)
- docs/PLANO_MESAS_TERRAZA.md (25 mesas individuales combinables)
- docs/ARQUITECTURA_MESAS_SISTEMA.md (schema propuesto)

Uso:
    python scripts/poblar_mesas_airtable.py
"""

import os
import sys
import io
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pyairtable import Api

# Configuración
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = "appQ2ZXAR68cqDmJt"
MESAS_TABLE_ID = "tblRSjdDIa5SrudL5"
CONFIGURACIONES_TABLE_NAME = "ConfiguracionesMesas"

# Datos de mesas según planos físicos

MESAS_INTERIOR = [
    # SALA EXTERIOR (4 mesas)
    {
        "id_mesa": "SE-1",
        "nombre": "Mesa Sala Exterior 1",
        "zona": "Sala Exterior",
        "ubicacion_detallada": "Junto a ventana principal",
        "capacidad_estandar": 4,
        "capacidad_ampliada": 6,
        "mesas_auxiliares": "A1,A2",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 1,
        "notas": "Mesa popular con vistas a la calle"
    },
    {
        "id_mesa": "SE-2",
        "nombre": "Mesa Sala Exterior 2",
        "zona": "Sala Exterior",
        "ubicacion_detallada": "Junto a ventana",
        "capacidad_estandar": 4,
        "capacidad_ampliada": 6,
        "mesas_auxiliares": "A3,A4",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 2,
        "notas": ""
    },
    {
        "id_mesa": "SE-3",
        "nombre": "Mesa Sala Exterior 3",
        "zona": "Sala Exterior",
        "ubicacion_detallada": "Zona central exterior",
        "capacidad_estandar": 4,
        "capacidad_ampliada": 6,
        "mesas_auxiliares": "A5,A6",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 3,
        "notas": ""
    },
    {
        "id_mesa": "SE-4",
        "nombre": "Mesa Sala Exterior 4",
        "zona": "Sala Exterior",
        "ubicacion_detallada": "Mesa grande exterior",
        "capacidad_estandar": 8,
        "capacidad_ampliada": 10,
        "mesas_auxiliares": "A7,A8",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 4,
        "notas": "Ideal para grupos grandes"
    },
    # SALA INTERIOR (4 mesas)
    {
        "id_mesa": "SI-1",
        "nombre": "Mesa Sala Interior 1",
        "zona": "Sala Interior",
        "ubicacion_detallada": "Entrada sala interior",
        "capacidad_estandar": 4,
        "capacidad_ampliada": 6,
        "mesas_auxiliares": "",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 5,
        "notas": ""
    },
    {
        "id_mesa": "SI-2",
        "nombre": "Mesa Sala Interior 2",
        "zona": "Sala Interior",
        "ubicacion_detallada": "Zona central interior",
        "capacidad_estandar": 4,
        "capacidad_ampliada": 6,
        "mesas_auxiliares": "",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 6,
        "notas": ""
    },
    {
        "id_mesa": "SI-3",
        "nombre": "Mesa Sala Interior 3",
        "zona": "Sala Interior",
        "ubicacion_detallada": "Mesa grande interior",
        "capacidad_estandar": 8,
        "capacidad_ampliada": 10,
        "mesas_auxiliares": "",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 7,
        "notas": "Mesa más grande del interior"
    },
    {
        "id_mesa": "SI-4",
        "nombre": "Mesa Sala Interior 4",
        "zona": "Sala Interior",
        "ubicacion_detallada": "Rincón interior",
        "capacidad_estandar": 4,
        "capacidad_ampliada": 6,
        "mesas_auxiliares": "",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 8,
        "notas": ""
    },
    # SOFÁS (1 mesa)
    {
        "id_mesa": "SOF-1",
        "nombre": "Mesa Sofás",
        "zona": "Sofás",
        "ubicacion_detallada": "Zona de sofás",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 9,
        "notas": "Ambiente relajado, ideal para parejas"
    },
    # BARRA (2 mesas)
    {
        "id_mesa": "B-5",
        "nombre": "Mesa Barra 5",
        "zona": "Barra",
        "ubicacion_detallada": "Extremo barra",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 10,
        "notas": ""
    },
    {
        "id_mesa": "B-8",
        "nombre": "Mesa Barra 8",
        "zona": "Barra",
        "ubicacion_detallada": "Centro barra",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "",
        "estado": "Libre",
        "prioridad": 11,
        "notas": ""
    },
]

MESAS_TERRAZA = [
    # 25 mesas individuales de terraza (T-1 a T-25)
    # Cada mesa tiene capacidad estándar 2, ampliable a 4
    # Son combinables con las mesas adyacentes
    {
        "id_mesa": "T-1",
        "nombre": "Mesa Terraza 1",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 1, posición 1",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-2",
        "estado": "Libre",
        "prioridad": 12,
        "notas": "Combinable con T-2"
    },
    {
        "id_mesa": "T-2",
        "nombre": "Mesa Terraza 2",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 1, posición 2",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-1,T-3",
        "estado": "Libre",
        "prioridad": 13,
        "notas": "Combinable con T-1 y T-3"
    },
    {
        "id_mesa": "T-3",
        "nombre": "Mesa Terraza 3",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 1, posición 3",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-2,T-4",
        "estado": "Libre",
        "prioridad": 14,
        "notas": ""
    },
    {
        "id_mesa": "T-4",
        "nombre": "Mesa Terraza 4",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 1, posición 4",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-3,T-5",
        "estado": "Libre",
        "prioridad": 15,
        "notas": ""
    },
    {
        "id_mesa": "T-5",
        "nombre": "Mesa Terraza 5",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 1, posición 5",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-4,T-6",
        "estado": "Libre",
        "prioridad": 16,
        "notas": ""
    },
    {
        "id_mesa": "T-6",
        "nombre": "Mesa Terraza 6",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 2, posición 1",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-5,T-7",
        "estado": "Libre",
        "prioridad": 17,
        "notas": ""
    },
    {
        "id_mesa": "T-7",
        "nombre": "Mesa Terraza 7",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 2, posición 2",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-6,T-8",
        "estado": "Libre",
        "prioridad": 18,
        "notas": ""
    },
    {
        "id_mesa": "T-8",
        "nombre": "Mesa Terraza 8",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 2, posición 3",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-7,T-9",
        "estado": "Libre",
        "prioridad": 19,
        "notas": ""
    },
    {
        "id_mesa": "T-9",
        "nombre": "Mesa Terraza 9",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 2, posición 4",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-8,T-10",
        "estado": "Libre",
        "prioridad": 20,
        "notas": ""
    },
    {
        "id_mesa": "T-10",
        "nombre": "Mesa Terraza 10",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 2, posición 5",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-9,T-11",
        "estado": "Libre",
        "prioridad": 21,
        "notas": ""
    },
    {
        "id_mesa": "T-11",
        "nombre": "Mesa Terraza 11",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 3, posición 1",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-10,T-12",
        "estado": "Libre",
        "prioridad": 22,
        "notas": ""
    },
    {
        "id_mesa": "T-12",
        "nombre": "Mesa Terraza 12",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 3, posición 2",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-11,T-13",
        "estado": "Libre",
        "prioridad": 23,
        "notas": ""
    },
    {
        "id_mesa": "T-13",
        "nombre": "Mesa Terraza 13",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 3, posición 3",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-12,T-14",
        "estado": "Libre",
        "prioridad": 24,
        "notas": ""
    },
    {
        "id_mesa": "T-14",
        "nombre": "Mesa Terraza 14",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 3, posición 4",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-13,T-15",
        "estado": "Libre",
        "prioridad": 25,
        "notas": ""
    },
    {
        "id_mesa": "T-15",
        "nombre": "Mesa Terraza 15",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 3, posición 5",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-14,T-16",
        "estado": "Libre",
        "prioridad": 26,
        "notas": ""
    },
    {
        "id_mesa": "T-16",
        "nombre": "Mesa Terraza 16",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 4, posición 1",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-15,T-17",
        "estado": "Libre",
        "prioridad": 27,
        "notas": ""
    },
    {
        "id_mesa": "T-17",
        "nombre": "Mesa Terraza 17",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 4, posición 2",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-16,T-18",
        "estado": "Libre",
        "prioridad": 28,
        "notas": ""
    },
    {
        "id_mesa": "T-18",
        "nombre": "Mesa Terraza 18",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 4, posición 3",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-17,T-19",
        "estado": "Libre",
        "prioridad": 29,
        "notas": ""
    },
    {
        "id_mesa": "T-19",
        "nombre": "Mesa Terraza 19",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 4, posición 4",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-18,T-20",
        "estado": "Libre",
        "prioridad": 30,
        "notas": ""
    },
    {
        "id_mesa": "T-20",
        "nombre": "Mesa Terraza 20",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 4, posición 5",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-19,T-21",
        "estado": "Libre",
        "prioridad": 31,
        "notas": ""
    },
    {
        "id_mesa": "T-21",
        "nombre": "Mesa Terraza 21",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 5, posición 1",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-20,T-22",
        "estado": "Libre",
        "prioridad": 32,
        "notas": ""
    },
    {
        "id_mesa": "T-22",
        "nombre": "Mesa Terraza 22",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 5, posición 2",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-21,T-23",
        "estado": "Libre",
        "prioridad": 33,
        "notas": ""
    },
    {
        "id_mesa": "T-23",
        "nombre": "Mesa Terraza 23",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 5, posición 3",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-22,T-24",
        "estado": "Libre",
        "prioridad": 34,
        "notas": ""
    },
    {
        "id_mesa": "T-24",
        "nombre": "Mesa Terraza 24",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 5, posición 4",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-23,T-25",
        "estado": "Libre",
        "prioridad": 35,
        "notas": ""
    },
    {
        "id_mesa": "T-25",
        "nombre": "Mesa Terraza 25",
        "zona": "Terraza",
        "ubicacion_detallada": "Fila 5, posición 5",
        "capacidad_estandar": 2,
        "capacidad_ampliada": 4,
        "mesas_auxiliares": "",
        "mesas_compatibles": "T-24",
        "estado": "Libre",
        "prioridad": 36,
        "notas": "Última mesa de la terraza"
    },
]

CONFIGURACIONES_TERRAZA = [
    # Configuraciones predefinidas para grupos
    {
        "id_configuracion": "CONF-T-1-2",
        "nombre": "Terraza Pareja 1-2",
        "mesas_incluidas": "T-1,T-2",
        "capacidad_total": 4,
        "ubicacion": "Terraza",
        "notas": "Para 4 personas (capacidad estándar) o hasta 8 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-3-4",
        "nombre": "Terraza Pareja 3-4",
        "mesas_incluidas": "T-3,T-4",
        "capacidad_total": 4,
        "ubicacion": "Terraza",
        "notas": "Para 4 personas (capacidad estándar) o hasta 8 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-5-6",
        "nombre": "Terraza Pareja 5-6",
        "mesas_incluidas": "T-5,T-6",
        "capacidad_total": 4,
        "ubicacion": "Terraza",
        "notas": "Para 4 personas (capacidad estándar) o hasta 8 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-7-8",
        "nombre": "Terraza Pareja 7-8",
        "mesas_incluidas": "T-7,T-8",
        "capacidad_total": 4,
        "ubicacion": "Terraza",
        "notas": "Para 4 personas (capacidad estándar) o hasta 8 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-9-10",
        "nombre": "Terraza Pareja 9-10",
        "mesas_incluidas": "T-9,T-10",
        "capacidad_total": 4,
        "ubicacion": "Terraza",
        "notas": "Para 4 personas (capacidad estándar) o hasta 8 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-1-2-3",
        "nombre": "Terraza Grupo 6 personas",
        "mesas_incluidas": "T-1,T-2,T-3",
        "capacidad_total": 6,
        "ubicacion": "Terraza",
        "notas": "Para 6 personas (capacidad estándar) o hasta 12 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-2-3-4",
        "nombre": "Terraza Grupo 6 personas (alt)",
        "mesas_incluidas": "T-2,T-3,T-4",
        "capacidad_total": 6,
        "ubicacion": "Terraza",
        "notas": "Para 6 personas (capacidad estándar) o hasta 12 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-1-2-3-4",
        "nombre": "Terraza Grupo 8 personas",
        "mesas_incluidas": "T-1,T-2,T-3,T-4",
        "capacidad_total": 8,
        "ubicacion": "Terraza",
        "notas": "Para 8 personas (capacidad estándar) o hasta 16 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-5-6-7-8",
        "nombre": "Terraza Grupo 8 personas (centro)",
        "mesas_incluidas": "T-5,T-6,T-7,T-8",
        "capacidad_total": 8,
        "ubicacion": "Terraza",
        "notas": "Para 8 personas (capacidad estándar) o hasta 16 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-1-2-3-4-5",
        "nombre": "Terraza Grupo 10 personas",
        "mesas_incluidas": "T-1,T-2,T-3,T-4,T-5",
        "capacidad_total": 10,
        "ubicacion": "Terraza",
        "notas": "Para 10 personas (capacidad estándar) o hasta 20 (ampliada)"
    },
    {
        "id_configuracion": "CONF-T-1-2-3-4-5-6",
        "nombre": "Terraza Grupo 12 personas",
        "mesas_incluidas": "T-1,T-2,T-3,T-4,T-5,T-6",
        "capacidad_total": 12,
        "ubicacion": "Terraza",
        "notas": "Para 12 personas (capacidad estándar) o hasta 24 (ampliada)"
    },
]


def main():
    """Poblar tablas de Airtable con datos de mesas."""
    
    if not AIRTABLE_API_KEY:
        print("❌ Error: AIRTABLE_API_KEY no está configurada")
        print("   Exporta la variable: export AIRTABLE_API_KEY='tu_api_key'")
        return 1
    
    print("=" * 60)
    print("POBLANDO TABLAS DE MESAS EN AIRTABLE")
    print("=" * 60)
    
    api = Api(AIRTABLE_API_KEY)
    mesas_table = api.table(BASE_ID, MESAS_TABLE_ID)
    configuraciones_table = api.table(BASE_ID, CONFIGURACIONES_TABLE_NAME)
    
    # 1. Limpiar mesas existentes (opcional - comentar si no se desea)
    print("\n📋 Paso 1: Obteniendo mesas existentes...")
    existing_mesas = mesas_table.all()
    print(f"   Encontradas {len(existing_mesas)} mesas existentes")
    
    # Mapear por ID_Mesa para actualizar
    existing_by_id = {}
    for record in existing_mesas:
        id_mesa = record["fields"].get("ID Mesa", "")
        if id_mesa:
            existing_by_id[id_mesa] = record["id"]
    
    # 2. Poblar mesas de interior
    print("\n📋 Paso 2: Poblando mesas de INTERIOR (11 mesas)...")
    interior_count = 0
    for mesa_data in MESAS_INTERIOR:
        fields = {
            "ID Mesa": mesa_data["id_mesa"],
            "Nombre de Mesa": mesa_data["nombre"],
            "Zona": mesa_data["zona"],
            "Ubicación": mesa_data["ubicacion_detallada"],
            "Capacidad": mesa_data["capacidad_estandar"],
            "Capacidad Ampliada": mesa_data["capacidad_ampliada"],
            "Tipo": "Ampliable" if mesa_data["capacidad_ampliada"] > mesa_data["capacidad_estandar"] else "Fija",
            "Estado": mesa_data["estado"],
            "Disponible": True,
            "Prioridad": mesa_data["prioridad"],
            "Notas": mesa_data["notas"],
            "Mesa Auxiliar Requerida": mesa_data["mesas_auxiliares"],
            "Mesas_Compatibles": mesa_data["mesas_compatibles"],
        }
        
        # Si ya existe, actualizar; si no, crear
        if mesa_data["id_mesa"] in existing_by_id:
            mesas_table.update(existing_by_id[mesa_data["id_mesa"]], fields)
            print(f"   ✅ Actualizada: {mesa_data['id_mesa']} - {mesa_data['nombre']}")
        else:
            mesas_table.create(fields)
            print(f"   ✅ Creada: {mesa_data['id_mesa']} - {mesa_data['nombre']}")
        interior_count += 1
    
    print(f"   Total interior: {interior_count} mesas")
    
    # 3. Poblar mesas de terraza
    print("\n📋 Paso 3: Poblando mesas de TERRAZA (25 mesas)...")
    terraza_count = 0
    for mesa_data in MESAS_TERRAZA:
        fields = {
            "ID Mesa": mesa_data["id_mesa"],
            "Nombre de Mesa": mesa_data["nombre"],
            "Zona": mesa_data["zona"],
            "Ubicación": mesa_data["ubicacion_detallada"],
            "Capacidad": mesa_data["capacidad_estandar"],
            "Capacidad Ampliada": mesa_data["capacidad_ampliada"],
            "Tipo": "Ampliable",
            "Estado": mesa_data["estado"],
            "Disponible": True,
            "Prioridad": mesa_data["prioridad"],
            "Notas": mesa_data["notas"],
            "Mesa Auxiliar Requerida": mesa_data["mesas_auxiliares"],
            "Mesas_Compatibles": mesa_data["mesas_compatibles"],
        }
        
        if mesa_data["id_mesa"] in existing_by_id:
            mesas_table.update(existing_by_id[mesa_data["id_mesa"]], fields)
            print(f"   ✅ Actualizada: {mesa_data['id_mesa']} - {mesa_data['nombre']}")
        else:
            mesas_table.create(fields)
            print(f"   ✅ Creada: {mesa_data['id_mesa']} - {mesa_data['nombre']}")
        terraza_count += 1
    
    print(f"   Total terraza: {terraza_count} mesas")
    
    # 4. Poblar configuraciones de terraza
    print("\n📋 Paso 4: Poblando CONFIGURACIONES de terraza...")
    
    # Obtener configuraciones existentes
    existing_configs = configuraciones_table.all()
    existing_config_ids = {
        r["fields"].get("ID_Configuracion", ""): r["id"] 
        for r in existing_configs
    }
    
    config_count = 0
    for config_data in CONFIGURACIONES_TERRAZA:
        fields = {
            "ID_Configuracion": config_data["id_configuracion"],
            "Nombre": config_data["nombre"],
            "Mesas_Incluidas": config_data["mesas_incluidas"],
            "Capacidad_Total": config_data["capacidad_total"],
            "Ubicacion": config_data["ubicacion"],
            "Notas": config_data["notas"],
        }
        
        if config_data["id_configuracion"] in existing_config_ids:
            configuraciones_table.update(existing_config_ids[config_data["id_configuracion"]], fields)
            print(f"   ✅ Actualizada: {config_data['id_configuracion']} - {config_data['nombre']}")
        else:
            configuraciones_table.create(fields)
            print(f"   ✅ Creada: {config_data['id_configuracion']} - {config_data['nombre']}")
        config_count += 1
    
    print(f"   Total configuraciones: {config_count}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("✅ POBLACIÓN COMPLETADA")
    print("=" * 60)
    print(f"📊 Resumen:")
    print(f"   - Mesas Interior: {interior_count}")
    print(f"   - Mesas Terraza: {terraza_count}")
    print(f"   - Configuraciones: {config_count}")
    print(f"   - TOTAL Mesas: {interior_count + terraza_count}")
    print(f"\n🔗 Ver en Airtable:")
    print(f"   https://airtable.com/{BASE_ID}/tblRSjdDIa5SrudL5")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
