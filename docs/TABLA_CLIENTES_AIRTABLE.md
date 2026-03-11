# Tabla Clientes en Airtable - Documentación Técnica

> **Sistema CRM "En Las Nubes Restobar"**  
> Base de Airtable: `appQ2ZXAR68cqDmJt`  
> Fecha de creación: 2026-03-09  
> Autor: Sistema de Gestión Automatizada

---

## 📋 Resumen Ejecutivo

Se ha implementado una arquitectura CRM normalizada en Airtable para gestionar información de clientes del restobar "En Las Nubes". El sistema consta de **3 tablas relacionadas** que permiten almacenar datos de clientes, sus preferencias y notas del staff de manera estructurada y escalable.

### Objetivos del Sistema

1. ✅ **Persistencia de datos de clientes** independiente de reservas
2. ✅ **Gestión de preferencias** (zonas favoritas, restricciones dietéticas, ocasiones especiales)
3. ✅ **Sistema de notas del staff** con marcado de importancia
4. ✅ **Sistema de tiers** para segmentación de clientes (Regular, Frecuente, VIP, Premium)
5. ✅ **Relaciones bidireccionales** con tabla Reservas para historial completo

---

## 🏗️ Arquitectura de Tres Tablas

```
┌──────────────────────────────────────────────────────────┐
│                  ARQUITECTURA CRM                        │
└──────────────────────────────────────────────────────────┘

                 ┌─────────────────┐
                 │    Clientes     │
                 │ tblPcVRnFTKDu7Z │
                 └────────┬────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────────┐  ┌──────────┐  ┌──────────┐
│ClientePreferenc │  │ClienteNo │  │ Reservas │
│tbl6xjlRuyJZMmzO │  │tbl5RZ31kx│  │tblHPyRRo │
└─────────────────┘  └──────────┘  └──────────┘
    1:N relación      1:N relación  1:N relación
```

### Relaciones Entre Tablas

| Desde | Hacia | Tipo | Campo Linked | Descripción |
|-------|-------|------|--------------|-------------|
| **Clientes** | **ClientePreferencias** | 1:N | `ClientePreferencias` | Un cliente puede tener múltiples preferencias |
| **Clientes** | **ClienteNotas** | 1:N | `ClienteNotas` | Un cliente puede tener múltiples notas del staff |
| **Clientes** | **Reservas** | 1:N | `Reservas` | Un cliente puede tener múltiples reservas |

**Importante:** Todas las relaciones son **bidireccionales**. Airtable crea automáticamente el campo inverso en la tabla relacionada.

---

## 📊 Tabla 1: Clientes

**ID de Tabla:** `tblPcVRnFTKDu7Z9t`  
**Propósito:** Almacena información maestra de cada cliente del restobar.

### Esquema de Campos

| # | Nombre Campo | Tipo | ID Campo | Obligatorio | Descripción | Ejemplo |
|---|--------------|------|----------|-------------|-------------|---------|
| 1 | **Nombre** | singleLineText | (Primary) | ✅ Sí | Nombre completo del cliente | "Juan Perez Garcia" |
| 2 | **Teléfono** | phoneNumber | `fldTTVUG1LZzCldkH` | ✅ Sí | Número en formato internacional | "+34600111222" |
| 3 | **Email** | email | - | ❌ No | Correo electrónico del cliente | "juan.perez@example.com" |
| 4 | **Tier** | singleSelect | - | ❌ No | Nivel de fidelidad del cliente | "VIP" |
| 5 | **Total_Reservas** | number | - | ❌ No | Número total de reservas | 5 |
| 6 | **Reservas_Completadas** | number | - | ❌ No | Reservas completadas exitosamente | 4 |
| 7 | **Reservas_Canceladas** | number | - | ❌ No | Reservas canceladas por el cliente | 1 |
| 8 | **No_Shows** | number | - | ❌ No | Veces que no se presentó | 0 |
| 9 | **Primera_Reserva** | date | - | ❌ No | Fecha de la primera reserva | "2025-01-15" |
| 10 | **Ultima_Reserva** | date | - | ❌ No | Fecha de la reserva más reciente | "2026-03-05" |
| 11 | **Gasto_Promedio** | currency | - | ❌ No | Gasto promedio por visita (EUR) | 45.50 € |
| 12 | **Notas_Staff** | multilineText | - | ❌ No | Notas generales del staff | "Cliente habitual, prefiere terraza" |
| 13 | **ClientePreferencias** | multipleRecordLinks | - | ❌ No | Link a tabla ClientePreferencias | → `tbl6xjlRuyJZMmzOV` |
| 14 | **ClienteNotas** | multipleRecordLinks | - | ❌ No | Link a tabla ClienteNotas | → `tbl5RZ31kxSOkGe0U` |
| 15 | **Reservas** | multipleRecordLinks | - | ❌ No | Link a tabla Reservas | → `tblHPyRRo18IwBAUC` |

### Opciones del Campo "Tier"

| Tier | Criterio | Color Recomendado | Descripción |
|------|----------|-------------------|-------------|
| **Regular** | 0-2 reservas | Gris | Clientes nuevos o esporádicos |
| **Frecuente** | 3-5 reservas | Azul | Clientes que vienen regularmente |
| **VIP** | 6-10 reservas | Amarillo | Clientes muy frecuentes |
| **Premium** | 10+ reservas | Púrpura | Clientes top tier, máxima fidelidad |

### Reglas de Validación

1. **Teléfono único:** Cada cliente debe tener un teléfono único (usar como identificador)
2. **Formato teléfono:** Debe seguir formato E.164 (`+[código país][número]`)
3. **Tier por defecto:** Si no se especifica, usar "Regular"
4. **Números no negativos:** Los campos numéricos no pueden ser negativos

---

## 📝 Tabla 2: ClientePreferencias

**ID de Tabla:** `tbl6xjlRuyJZMmzOV`  
**Propósito:** Almacena preferencias individuales de cada cliente.

### Esquema de Campos

| # | Nombre Campo | Tipo | Obligatorio | Descripción | Ejemplo |
|---|--------------|------|-------------|-------------|---------|
| 1 | **Descripcion** | singleLineText (Primary) | ✅ Sí | Descripción de la preferencia | "Prefiere terraza cuando hace buen tiempo" |
| 2 | **Tipo** | singleSelect | ❌ No | Categoría de la preferencia | "zona_favorita" |
| 3 | **Fecha_Creacion** | singleLineText | ❌ No | Timestamp ISO 8601 (UTC) | "2026-03-09T12:30:00.000Z" |
| 4 | **Cliente** | multipleRecordLinks | ✅ Sí | Link al cliente (bidireccional) | → `tblPcVRnFTKDu7Z9t` |

### Opciones del Campo "Tipo"

| Tipo | Código | Icono Sugerido | Uso |
|------|--------|----------------|-----|
| **Zona Favorita** | `zona_favorita` | 📍 | Preferencias de ubicación (terraza, interior, ventana) |
| **Solicitud Especial** | `solicitud_especial` | ⭐ | Peticiones especiales (tronas, mascotas, mesas juntas) |
| **Restricción Dietética** | `restriccion_dietetica` | ⚠️ | Alergias, intolerancias, preferencias alimentarias |
| **Ocasión de Celebración** | `ocasion_celebracion` | 🎂 | Cumpleaños, aniversarios, eventos especiales |

### Ejemplos de Preferencias Reales

```json
[
  {
    "Descripcion": "Prefiere mesas en la terraza cuando hace buen tiempo",
    "Tipo": "zona_favorita",
    "Fecha_Creacion": "2026-03-09T12:30:00.000Z"
  },
  {
    "Descripcion": "Alérgico a frutos secos (especialmente cacahuetes)",
    "Tipo": "restriccion_dietetica",
    "Fecha_Creacion": "2026-03-09T12:30:00.000Z"
  },
  {
    "Descripcion": "Aniversario de boda cada 14 de febrero",
    "Tipo": "ocasion_celebracion",
    "Fecha_Creacion": "2026-02-10T10:15:00.000Z"
  }
]
```

---

## 📌 Tabla 3: ClienteNotas

**ID de Tabla:** `tbl5RZ31kxSOkGe0U`  
**Propósito:** Almacena notas y observaciones del staff sobre clientes.

### Esquema de Campos

| # | Nombre Campo | Tipo | Obligatorio | Descripción | Ejemplo |
|---|--------------|------|-------------|-------------|---------|
| 1 | **Contenido** | multilineText (Primary) | ✅ Sí | Texto completo de la nota | "Le encanta el cachopo. Siempre pregunta si está disponible." |
| 2 | **Es_Importante** | singleSelect | ✅ Sí | Marcador de importancia | "Sí" |
| 3 | **Staff_Nombre** | singleLineText | ❌ No | Nombre del staff + rol | "Ana (Camarera)" |
| 4 | **Fecha_Creacion** | singleLineText | ❌ No | Timestamp ISO 8601 (UTC) | "2026-03-09T12:30:00.000Z" |
| 5 | **Cliente** | multipleRecordLinks | ✅ Sí | Link al cliente (bidireccional) | → `tblPcVRnFTKDu7Z9t` |

### ⚠️ Campo "Es_Importante" - Consideraciones Críticas

**Tipo:** `singleSelect` (NO es checkbox boolean)  
**Opciones Válidas:** `"Sí"` o `"No"` (con acento en la í)

#### Problema de Acentos

Airtable requiere que los valores de `singleSelect` coincidan **EXACTAMENTE** con las opciones configuradas:

```python
# ✅ CORRECTO
"Es_Importante": "Sí"   # Con acento en la í

# ❌ INCORRECTO - Causa HTTP 422 error
"Es_Importante": "Si"   # Sin acento
```

Error que devuelve Airtable si usas `"Si"` (sin acento):
```json
{
  "error": {
    "type": "INVALID_MULTIPLE_CHOICE_OPTIONS",
    "message": "Insufficient permissions to create new select option \"Si\""
  }
}
```

#### Conversión Backend ↔ Frontend

El frontend espera un **boolean** pero Airtable almacena **string**. El backend debe hacer la conversión:

**Al LEER de Airtable (Backend → Frontend):**
```python
# Python backend
airtable_value = nota["fields"]["Es_Importante"]  # "Sí" o "No"
frontend_value = (airtable_value == "Sí")  # true o false

# Respuesta JSON
{
  "id": "recXXX",
  "contenido": "...",
  "es_importante": true   # Boolean para frontend
}
```

**Al ESCRIBIR a Airtable (Frontend → Backend):**
```python
# Python backend recibe del frontend
frontend_value = request_data["is_important"]  # true o false (boolean)

# Convertir a string para Airtable
airtable_value = "Sí" if frontend_value else "No"

# Crear en Airtable
airtable_client.create_record({
    "Contenido": "...",
    "Es_Importante": airtable_value  # "Sí" o "No" (string)
})
```

### Ejemplos de Notas Reales

```json
[
  {
    "Contenido": "Le encanta el cachopo. Siempre pregunta si está disponible.",
    "Es_Importante": "No",
    "Staff_Nombre": "Ana (Camarera)",
    "Fecha_Creacion": "2026-03-09T12:30:00.000Z"
  },
  {
    "Contenido": "Cliente VIP. Recordar decorar mesa para aniversario cada 14 de febrero.",
    "Es_Importante": "Sí",
    "Staff_Nombre": "Carmen (Encargada)",
    "Fecha_Creacion": "2026-02-10T10:15:00.000Z"
  }
]
```

---

## 🔗 Relación con Tabla Reservas

### Configuración del Linked Record

**Tabla Reservas ID:** `tblHPyRRo18IwBAUC`  
**Campo en Clientes:** `Reservas` (multipleRecordLinks)  
**Campo en Reservas:** Campo automático creado por Airtable (bidireccional)

### Flujo de Sincronización

```
┌──────────────────────────────────────────────────────────┐
│         SINCRONIZACIÓN CLIENTES ↔ RESERVAS              │
└──────────────────────────────────────────────────────────┘

1. Nueva Reserva creada en tabla Reservas
   └─> Campo "Teléfono" contiene número del cliente

2. Backend busca si existe cliente con ese teléfono
   ├─> SI EXISTE: Vincular reserva al cliente existente
   │   └─> Actualizar estadísticas (Total_Reservas, Ultima_Reserva)
   │
   └─> NO EXISTE: Crear nuevo cliente automáticamente
       └─> Asignar Tier "Regular"
       └─> Vincular primera reserva
```

### Actualización Automática de Estadísticas

Cuando cambia el estado de una reserva, actualizar en Clientes:

| Estado de Reserva | Campo a Actualizar |
|-------------------|-------------------|
| **Completada/Confirmed** | `Reservas_Completadas++` |
| **Cancelada/Cancelled** | `Reservas_Canceladas++` |
| **No Show** | `No_Shows++` |
| **Cualquiera** | `Ultima_Reserva` = fecha más reciente |

---

## 💻 Integración con Backend FastAPI

### Endpoints Requeridos

#### 1. Listar Clientes
```http
GET /api/clients?query={search}&tier={tier}&limit={limit}&offset={offset}
```

**Respuesta esperada:**
```json
{
  "customers": [
    {
      "id": "recNsLCESheysjviz",
      "nombre": "Juan Perez Garcia",
      "telefono": "+34600111222",
      "email": "juan.perez@example.com",
      "tier": "Frecuente",
      "total_reservas": 5,
      "reservas_completadas": 4,
      "reservas_canceladas": 1,
      "no_shows": 0,
      "primera_reserva": "2025-01-15",
      "ultima_reserva": "2026-03-05",
      "gasto_promedio": 45.50,
      "preferencias": [
        {
          "id": "recXXX1",
          "tipo": "zona_favorita",
          "descripcion": "Prefiere terraza cuando hace buen tiempo",
          "fecha_creacion": "2026-03-09T12:30:00.000Z"
        },
        {
          "id": "recXXX2",
          "tipo": "restriccion_dietetica",
          "descripcion": "Alérgico a frutos secos",
          "fecha_creacion": "2026-03-09T12:30:00.000Z"
        }
      ],
      "notas": [
        {
          "id": "recYYY1",
          "contenido": "Le encanta el cachopo. Siempre pregunta si está disponible.",
          "es_importante": false,
          "staff_nombre": "Ana (Camarera)",
          "fecha_creacion": "2026-03-09T12:30:00.000Z"
        }
      ],
      "created_at": "2025-01-15T19:23:15.000Z",
      "updated_at": "2026-03-09T12:30:00.000Z"
    }
  ],
  "total": 1,
  "source": "airtable"
}
```

#### 2. Obtener Cliente Individual
```http
GET /api/clients/{customer_id}
```

**Respuesta:** Mismo formato que un elemento del array `customers` anterior.

#### 3. Obtener Preferencias de Cliente
```http
GET /api/clients/{customer_id}/preferences
```

**Respuesta:**
```json
[
  {
    "id": "recXXX1",
    "tipo": "zona_favorita",
    "descripcion": "Prefiere terraza cuando hace buen tiempo",
    "fecha_creacion": "2026-03-09T12:30:00.000Z"
  }
]
```

#### 4. Crear Preferencia
```http
POST /api/clients/{customer_id}/preferences
Content-Type: application/json

{
  "tipo": "restriccion_dietetica",
  "descripcion": "Vegetariano estricto"
}
```

#### 5. Obtener Notas de Cliente
```http
GET /api/clients/{customer_id}/notes
```

**Respuesta:**
```json
[
  {
    "id": "recYYY1",
    "contenido": "Cliente VIP. Decorar mesa para aniversario.",
    "es_importante": true,
    "staff_nombre": "Carmen (Encargada)",
    "fecha_creacion": "2026-02-10T10:15:00.000Z"
  }
]
```

#### 6. Crear Nota
```http
POST /api/clients/{customer_id}/notes
Content-Type: application/json

{
  "contenido": "Solicita mesa junto a ventana siempre que sea posible",
  "is_important": false
}
```

**CRÍTICO:** Observa que el frontend envía `is_important` (boolean) pero Airtable necesita `Es_Importante: "Sí"` o `"No"` (string).

### Código de Ejemplo para Conversión Boolean ↔ String

```python
from pyairtable import Api
from datetime import datetime, timezone
import os

api = Api(os.environ["AIRTABLE_API_KEY"])
BASE_ID = "appQ2ZXAR68cqDmJt"

async def create_customer_note(customer_id: str, contenido: str, is_important: bool, staff_nombre: str):
    """Crea una nueva nota para un cliente.
    
    Args:
        customer_id: ID del cliente en Airtable (ej: "recNsLCESheysjviz")
        contenido: Texto de la nota
        is_important: True si es importante, False si no (BOOLEAN del frontend)
        staff_nombre: Nombre del staff con rol (ej: "Ana (Camarera)")
    
    Returns:
        Dict con la nota creada en formato frontend (con boolean)
    """
    table_notas = api.table(BASE_ID, "tbl5RZ31kxSOkGe0U")
    
    # CONVERSIÓN CRÍTICA: Boolean → String con acento
    es_importante_str = "Sí" if is_important else "No"
    
    # Crear en Airtable
    nota_record = table_notas.create({
        "Contenido": contenido,
        "Es_Importante": es_importante_str,  # ✅ String "Sí" o "No"
        "Staff_Nombre": staff_nombre,
        "Fecha_Creacion": datetime.now(timezone.utc).isoformat(),
        "Cliente": [customer_id]  # Link bidireccional
    })
    
    # CONVERSIÓN DE VUELTA: String → Boolean para frontend
    es_importante_bool = (nota_record["fields"]["Es_Importante"] == "Sí")
    
    # Retornar en formato frontend
    return {
        "id": nota_record["id"],
        "contenido": nota_record["fields"]["Contenido"],
        "es_importante": es_importante_bool,  # ✅ Boolean para frontend
        "staff_nombre": nota_record["fields"]["Staff_Nombre"],
        "fecha_creacion": nota_record["fields"]["Fecha_Creacion"]
    }
```

---

## 📦 Datos de Prueba

### Cl