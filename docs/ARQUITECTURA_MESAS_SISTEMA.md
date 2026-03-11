# ARQUITECTURA DEL SISTEMA DE GESTIÓN DE MESAS

> **Restobar "En Las Nubes"** - Logroño, España  
> Última actualización: 2026-03-09  
> Estado: Diseño basado en análisis visual de planos manuscritos

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis de Fuentes Visuales](#análisis-de-fuentes-visuales)
3. [Arquitectura de Datos](#arquitectura-de-datos)
4. [Esquema de Tablas Airtable](#esquema-de-tablas-airtable)
5. [Integración con Backend](#integración-con-backend)
6. [Discrepancias Detectadas](#discrepancias-detectadas)

---

## Resumen Ejecutivo

### Distribución Total de Mesas

| Zona | Subzona | Mesas | Capacidad Total |
|------|---------|-------|-----------------|
| **INTERIOR** | Sala Exterior | 4 | 24-40 pax |
| **INTERIOR** | Sala Interior | 3 | 17-24 pax |
| **INTERIOR** | Sofás | 4 | 16-20 pax |
| **INTERIOR** | Barra | 2 | 4-6 pax |
| **TERRAZA** | Fila Superior + Inferior | 14+ | ~100+ pax |
| **TOTAL** | - | **27+** | **161+ pax** |

### Mesas con Avisos Especiales

| Mesa | Aviso | Acción Requerida |
|------|-------|------------------|
| **Mesa 8 (SI-8)** | Junto al baño | ⚠️ SIEMPRE explicar ubicación al cliente |
| **S-3 (SOF-3)** | Mesa pequeña | ⚠️ AVISAR que solo caben 2-3 personas |
| **B-5, B-8 (BAR-*)** | Mesas altas | ⚠️ SIEMPRE avisar que son mesas altas con banquetas |

---

## Análisis de Fuentes Visuales

### IMG20260309221509.jpg - TERRAZA ✅

**Información Confirmada:**
- ✅ Distribución en dos filas separadas por "CALLE PEATONAL"
- ✅ 14 mesas identificadas: 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16
- ✅ Puntos azules = elementos arquitectónicos (árboles/farolas)
- ✅ Configuraciones combinables documentadas con capacidades

**Combinaciones Terraza (Fila Superior):**
| Combo | Mesas | Capacidad | Notas |
|-------|-------|-----------|-------|
| T-CONF-1 | 9 + 10 | 6 pax | 2 mesas juntas (par estándar) |
| T-CONF-2 | 11 + 13 | 18-20 pax | Zona central - grupos grandes (T-12 es individual, no participa) |
| T-CONF-3 | 15 + 16 | 6 pax | 2 mesas juntas (par estándar) |

**Combinaciones Terraza (Fila Inferior):**
| Combo | Mesas | Capacidad | Notas |
|-------|-------|-----------|-------|
| T-CONF-4 | 2 + 3 | 6 pax | 2 mesas juntas (par estándar) |
| T-CONF-5 | 4 + 5 | 18-20 pax | Zona central - grupos grandes |
| T-CONF-6 | 7 + 8 | 6 pax | 2 mesas juntas (par estándar) |

**Información Parcial:**
- ⚠️ Mesas 1, 6, 14 no visibles en plano
- ⚠️ Usuario indica 25 mesas, solo 14 visibles

**No Visible - Requiere Validación:**
- ❌ Mesas 17-25 (si existen)
- ❌ Capacidad exacta de cada mesa individual

---

### IMG20260309221557.jpg - SALA EXTERIOR ✅

**Información Confirmada:**
- ✅ 4 mesas identificadas: 1, 2, 4, 5
- ✅ Todas con opción de mesa auxiliar para ampliar capacidad
- ✅ Layout cerca de entrada principal

**Detalle de Mesas:**
| Mesa | Cap. Base | Cap. Ampliada | Notas |
|------|-----------|---------------|-------|
| **Mesa 1** | 6 pax | Con auxiliar | "OPCION DE AUX" |
| **Mesa 2** | 7-8 pax | 10 pax | Con auxiliar |
| **Mesa 4** | 6 pax | 8-10 pax | - |
| **Mesa 5** | 7-8 pax | 10 pax | Con auxiliar |

**No Visible - Requiere Validación:**
- ❌ ¿Dónde está Mesa 3? (no aparece en ningún plano)

---

### IMG20260309221619.jpg - SALA INTERIOR ✅

**Información Confirmada:**
- ✅ 3 mesas identificadas: 6, 7, 8
- ✅ Mesa 8 = MESA DELICADA junto al baño
- ✅ Zona más interna del local

**Detalle de Mesas:**
| Mesa | Cap. Base | Cap. Ampliada | Avisos |
|------|-----------|---------------|--------|
| **Mesa 6** | 7-8 pax | 10 pax | Con auxiliar |
| **Mesa 7** | 6 pax | - | Nota tachada sobre auxiliares |
| **Mesa 8** | 2-4 pax | 4 pax máx | ⚠️ **JUNTO BAÑO - EXPLICAR CLIENTE** |

**Regla de Negocio - Mesa 8:**
```
SI Mesa 8 es asignada:
  SIEMPRE informar: "Esta mesa está cerca de la zona del baño"
  CONFIRMAR: "¿Te parece bien?"
  SI cliente rechaza:
    Ofrecer alternativas o lista de espera
```

---

### IMG20260309221633.jpg - SOFÁS ✅

**Información Confirmada:**
- ✅ 4 mesas en zona de sofás: S-1, S-2, S-3, S-4
- ✅ Dos zonas combinables de 8 pax cada una
- ✅ S-3 es mesa pequeña (avisar)

**Detalle de Mesas:**
| Mesa | Cap. Base | Combinable Con | Notas |
|------|-----------|----------------|-------|
| **S-1** | 2 pax | S-2 | ⚠️ Mesa pequeña (similar a S-3). Combinación = 8 pax |
| **S-2** | 6 pax | S-1 | Combinación = 8 pax |
| **S-3** | 2-3 pax | S-4 | ⚠️ **AVISAR MESA PEQUEÑA** |
| **S-4** | 6 pax | S-3 | Combinación = 8 pax |

**Regla de Negocio - Sofás:**
```
SI num_personas > 6 AND zona_preferida == "Sofás":
  Ofrecer combinación S-1+S-2 o S-3+S-4
SINO:
  Asignar mesa individual más adecuada
```

---

### IMG20260309221655.jpg - BARRA ✅

**Información Confirmada:**
- ✅ Título: "BARRA" - "SON MESAS ALTAS"
- ✅ 2 mesas de barra: B-8 y B-5
- ✅ Capacidad: 2 pax normal, hasta 3 pax si necesario
- ✅ **SIEMPRE AVISAR: Son mesas altas con banquetas**

**Detalle de Mesas:**
| Mesa | Cap. Normal | Cap. Máxima | Avisos |
|------|-------------|-------------|--------|
| **B-8** | 2 pax | 3 pax | ⚠️ **MESA ALTA - AVISAR** |
| **B-5** | 2 pax | 3 pax | ⚠️ **MESA ALTA - AVISAR** |

**Regla de Negocio - Barra:**
```
SI Mesa de Barra es asignada:
  SIEMPRE informar: "Esta es una mesa alta de barra con banquetas"
  CONFIRMAR: "¿Os viene bien una mesa alta?"
  SI cliente rechaza:
    Buscar alternativas en otras zonas
```

**Nomenclatura Confirmada:**
- ✅ B-8 y B-5 es la nomenclatura oficial del staff (confirmado por usuario)
- ✅ No usar BAR-1, BAR-2 - usar siempre B-5 y B-8

---

## Arquitectura de Datos

### Diagrama de Relaciones

```
┌─────────────────────────────────────────────────────────────────┐
│                    AIRTABLE DATABASE                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐       ┌──────────────────────────┐
│      Mesas       │       │  ConfiguracionesMesas    │
├──────────────────┤       ├──────────────────────────┤
│ Codigo_Mesa (PK) │◀──────│ Mesas_Incluidas (FK[])   │
│ Nombre_Display   │       │ ID_Configuracion (PK)    │
│ Zona             │       │ Nombre_Configuracion     │
│ Sub_Zona         │       │ Capacidad_Total          │
│ Capacidad_Base   │       │ Zona                     │
│ Capacidad_Ideal  │       │ Prioridad                │
│ Capacidad_Maxima │       │ Notas_Staff              │
│ Prioridad        │       │ Es_Activa                │
│ Avisos_Especiales│       └──────────────────────────┘
│ Es_Combinable    │              │
│ Combinables_Con──┼──────────────┘ (para ref. simple)
│ Disponible       │
└────────┬─────────┘
         │
         │ Linked Record
         ▼
┌──────────────────┐
│    Reservas      │
├──────────────────┤
│ ID               │
│ Cliente          │
│ Fecha_Hora       │
│ Num_Personas     │
│ Mesa (FK)        │◀── Linked to Mesas.Codigo_Mesa
│ Estado           │
│ Notas            │
└──────────────────┘
```

### Flujo de Asignación de Mesas

```
                    SOLICITUD DE RESERVA
                           │
                           ▼
              ┌────────────────────────┐
              │ ¿Hay zona preferida?   │
              └────────────────────────┘
                    │           │
                   SÍ          NO
                    │           │
                    ▼           ▼
          ┌─────────────┐ ┌─────────────────┐
          │ Filtrar por │ │ Buscar en todas │
          │ zona        │ │ las zonas       │
          └─────────────┘ └─────────────────┘
                    │           │
                    └─────┬─────┘
                          ▼
              ┌────────────────────────┐
              │ FASE 1: Mesas normales │
              │ (Prioridad 8-10)       │
              └────────────────────────┘
                          │
                    ¿Encontrada?
                    │         │
                   SÍ        NO
                    │         │
                    ▼         ▼
          ┌─────────────┐ ┌─────────────────┐
          │ Asignar     │ │ FASE 2: Mesas   │
          │ mesa        │ │ con avisos leves│
          └─────────────┘ │ (Prioridad 5-7) │
                          └─────────────────┘
                                  │
                            ¿Encontrada?
                            │         │
                           SÍ        NO
                            │         │
                            ▼         ▼
                  ┌─────────────┐ ┌─────────────────┐
                  │ Asignar con │ │ FASE 3: Mesas   │
                  │ aviso       │ │ delicadas       │
                  └─────────────┘ │ (Prioridad 1-4) │
                                  └─────────────────┘
                                          │
                                    ¿Encontrada?
                                    │         │
                                   SÍ        NO
                                    │         │
                                    ▼         ▼
                          ┌─────────────┐ ┌──────────────┐
                          │ CONFIRMAR   │ │ Ofrecer:     │
                          │ con cliente │ │ - Horario    │
                          │ ubicación   │ │   alternativo│
                          └─────────────┘ │ - Espera     │
                                          │ - Handoff    │
                                          └──────────────┘
```

---

## Esquema de Tablas Airtable

### Tabla: Mesas (Actualización)

| Campo | Tipo Airtable | Obligatorio | Validación | Descripción |
|-------|---------------|-------------|------------|-------------|
| `Codigo_Mesa` | Single line text | ✅ | `^(SE\|SI\|SOF\|B\|T)-\d{1,2}$` | PK único. Ej: SE-1, SI-8, SOF-3, B-5, T-01 |
| `Nombre_Display` | Single line text | ✅ | Max 50 chars | Nombre amigable. Ej: "Mesa 1 Sala Exterior" |
| `Zona` | Single select | ✅ | Enum | `Sala Exterior`, `Sala Interior`, `Sofás`, `Barra`, `Terraza` |
| `Sub_Zona` | Single line text | ❌ | - | Para Terraza: "Fila Superior", "Zona Árbol", etc. |
| `Capacidad_Base` | Number | ✅ | 1-20 | Capacidad estándar sin auxiliares |
| `Capacidad_Ideal` | Number | ❌ | 1-20 | Capacidad ideal para mesas delicadas (ej: Mesa 8 = 2) |
| `Capacidad_Maxima` | Number | ✅ | 1-20 | Con auxiliares o configuración ampliada |
| `Auxiliares_Necesarias` | Number | ❌ | 0-4 | Cuántas mesas auxiliares se requieren para max cap |
| `Prioridad_Asignacion` | Number | ✅ | 1-10 | 10=alta prioridad, 1=última opción (delicada) |
| `Avisos_Especiales` | Long text | ❌ | - | Texto que DEBE comunicarse al cliente |
| `Es_Combinable` | Checkbox | ✅ | boolean | true si puede combinarse con otras |
| `Mesas_Combinables_Con` | Linked records | ❌ | FK a Mesas | Referencias a mesas con las que combina |
| `Posicion_X` | Number | ❌ | 0-100 | Coordenada para visualización en dashboard |
| `Posicion_Y` | Number | ❌ | 0-100 | Coordenada para visualización en dashboard |
| `Disponible` | Checkbox | ✅ | boolean | Default true. false = fuera de servicio |
| `Notas_Internas` | Long text | ❌ | - | Solo visible para staff |
| `Foto_Mesa` | Attachment | ❌ | - | Foto identificativa de la mesa |

### Ejemplos de Registros - Tabla Mesas

| Codigo_Mesa | Nombre_Display | Zona | Capacidad_Base | Capacidad_Maxima | Prioridad | Avisos_Especiales |
|-------------|----------------|------|----------------|------------------|-----------|-------------------|
| SE-1 | Mesa 1 Sala Exterior | Sala Exterior | 6 | 8 | 9 | - |
| SE-2 | Mesa 2 Sala Exterior | Sala Exterior | 8 | 10 | 9 | - |
| SE-4 | Mesa 4 Sala Exterior | Sala Exterior | 6 | 10 | 9 | - |
| SE-5 | Mesa 5 Sala Exterior | Sala Exterior | 8 | 10 | 9 | - |
| SI-6 | Mesa 6 Sala Interior | Sala Interior | 8 | 10 | 8 | - |
| SI-7 | Mesa 7 Sala Interior | Sala Interior | 6 | 6 | 8 | - |
| SI-8 | Mesa 8 Sala Interior | Sala Interior | 2 | 4 | 2 | ⚠️ Junto al baño - explicar ubicación al cliente |
| SOF-1 | Sofá 1 | Sofás | 2 | 2 | 7 | - |
| SOF-2 | Sofá 2 | Sofás | 6 | 6 | 8 | - |
| SOF-3 | Sofá 3 | Sofás | 3 | 3 | 5 | ⚠️ Mesa pequeña - avisar tamaño reducido |
| SOF-4 | Sofá 4 | Sofás | 6 | 6 | 8 | - |
| B-5 | Mesa Barra 5 | Barra | 2 | 3 | 3 | ⚠️ Mesa alta con banquetas - confirmar con cliente |
| B-8 | Mesa Barra 8 | Barra | 2 | 3 | 3 | ⚠️ Mesa alta con banquetas - confirmar con cliente |

---

### Tabla: ConfiguracionesMesas (Nueva)

| Campo | Tipo Airtable | Obligatorio | Validación | Descripción |
|-------|---------------|-------------|------------|-------------|
| `ID_Configuracion` | Single line text | ✅ | `^(T\|SOF)-CONF-\d{1,2}[A-Z]?$` | PK único. Ej: T-CONF-1, SOF-CONF-1A |
| `Nombre_Configuracion` | Single line text | ✅ | Max 100 chars | Descripción clara. Ej: "3 mesas zona árbol" |
| `Capacidad_Total` | Number | ✅ | 4-30 | Capacidad total de la configuración |
| `Mesas_Incluidas` | Linked records | ✅ | FK[] a Mesas | Mesas que componen la configuración |
| `Zona` | Single select | ✅ | Enum | Filtrar configuraciones por zona |
| `Prioridad` | Number | ✅ | 1-10 | Para ordenar opciones (10=preferida) |
| `Foto_Referencia` | Attachment | ❌ | - | Foto de la configuración montada |
| `Notas_Staff` | Long text | ❌ | - | Instrucciones de montaje |
| `Es_Activa` | Checkbox | ✅ | boolean | true = se puede usar actualmente |
| `Restricciones` | Long text | ❌ | - | Clima, eventos especiales, etc. |

### Ejemplos de Registros - Tabla ConfiguracionesMesas

| ID_Configuracion | Nombre_Configuracion | Capacidad_Total | Mesas_Incluidas | Zona | Prioridad | Notas_Staff |
|------------------|----------------------|-----------------|-----------------|------|-----------|-------------|
| SOF-CONF-1 | Sofás Zona 1 combinados | 8 | SOF-1, SOF-2 | Sofás | 9 | Juntar S-1 y S-2. Sofás en L. |
| SOF-CONF-2 | Sofás Zona 2 combinados | 8 | SOF-3, SOF-4 | Sofás | 8 | Juntar S-3 y S-4. Avisar S-3 pequeña. |
| T-CONF-1 | Terraza Par 9+10 | 6 | T-09, T-10 | Terraza | 9 | 2 mesas juntas (par estándar) fila superior |
| T-CONF-2 | Terraza Grupos Grandes | 18-20 | T-11, T-13 | Terraza | 10 | Mesas 11+13 para grupos grandes. T-12 es individual, no participa. |
| T-CONF-3 | Terraza Par 15+16 | 6 | T-15, T-16 | Terraza | 9 | 2 mesas juntas (par estándar) fila superior |
| T-CONF-4 | Terraza Par 2+3 | 6 | T-02, T-03 | Terraza | 9 | 2 mesas juntas (par estándar) fila inferior |
| T-CONF-5 | Terraza Grupos Grandes Centro | 18-20 | T-04, T-05 | Terraza | 10 | Mesas 4+5 para grupos grandes fila inferior |
| T-CONF-6 | Terraza Par 7+8 | 6 | T-07, T-08 | Terraza | 9 | 2 mesas juntas (par estándar) fila inferior |
| T-CONF-GRANDE | Terraza Máx Capacidad | 18-20 | T-11, T-13 + T-04, T-05 | Terraza | 10 | Máximo terraza. Solo zonas centrales. Requiere validación staff. |

---

## Integración con Backend

### Archivos a Modificar/Crear

```
src/
├── services/
│   └── booking_engine.py          # Algoritmo de asignación (MODIFICAR)
│
├── infrastructure/
│   └── airtable/
│       ├── mesas_service.py       # CRUD para Mesas (CREAR)
│       ├── config_mesas_service.py # CRUD para ConfiguracionesMesas (CREAR)
│       └── airtable_client.py     # Cliente base (VERIFICAR campos)
│
├── api/
│   └── vapi_tools_router.py       # Herramientas VAPI (MODIFICAR)
│
└── domain/
    └── models/
        ├── mesa.py                # Entidad Mesa (CREAR)
        └── configuracion_mesa.py  # Entidad ConfigMesa (CREAR)
```

### Endpoint de Disponibilidad (API)

```python
# GET /api/v1/mesas/disponibilidad
# Query params: fecha, hora, num_personas, zona_preferida (opcional)

{
  "fecha": "2026-03-15",
  "hora": "21:00",
  "num_personas": 6,
  "zona_preferida": "Terraza",
  "mesas_disponibles": [
    {
      "codigo": "T-02",
      "nombre": "Mesa 2 Terraza",
      "capacidad": 6,
      "prioridad": 9,
      "avisos": null
    },
    {
      "codigo": "T-04",
      "nombre": "Mesa 4 Terraza",
      "capacidad": 8,
      "prioridad": 8,
      "avisos": null
    }
  ],
  "configuraciones_disponibles": [
    {
      "id": "T-CONF-4",
      "nombre": "Terraza Izq Inferior",
      "capacidad": 10,
      "mesas": ["T-02", "T-03"]
    }
  ]
}
```

---

## Discrepancias Detectadas

### ⚠️ REQUIEREN VALIDACIÓN CON USUARIO

| # | Discrepancia | Fuente A | Fuente B | Acción Requerida |
|---|--------------|----------|----------|------------------|
| 1 | **Número de mesas Terraza** | Usuario: 25 mesas | Foto: 14 visibles | Confirmar mesas 1, 6, 14, 17-25 |
| 2 | ~~**Nomenclatura Barra**~~ | ~~Esperado: B-1, B-2~~ | ~~Foto: B-8, B-5~~ | ✅ **CONFIRMADO**: B-5 y B-8 son la nomenclatura oficial del staff |
| 3 | ~~**Mesa 3 Interior**~~ | ~~No aparece en ningún plano~~ | ~~¿Existe?~~ | ✅ **CONFIRMADO**: Mesa 3 NO existe intencionalmente. La numeración salta de 2 a 4. |
| 4 | **Capacidad exacta Terraza** | Par estándar = 6 pax | Grupos grandes = 18-20 pax | ✅ **CONFIRMADO**: 2 mesas juntas = 6 pax máximo |
| 5 | **Mesas auxiliares** | Usuario: 4 disponibles | Solo 4 en total | ✅ **CONFIRMADO**: SE-4 necesita 2 auxiliares para 10 pax |
| 6 | ~~**Sofá S-1 capacidad**~~ | ~~No especificada claramente~~ | ~~Estimación: 4 pax~~ | ✅ **CONFIRMADO**: SOF-1 = 2 pax (mesa pequeña para 2 personas) |

### ✅ INFORMACIÓN CONFIRMADA

| Elemento | Confirmación | Fuente |
|----------|--------------|--------|
| Mesa 8 junto al baño | ✅ Delicada, explicar cliente | IMG...619.jpg |
| Mesas Barra son altas | ✅ Siempre avisar banquetas | IMG...655.jpg |
| S-3 es mesa pequeña | ✅ Avisar 2-3 pax máximo | IMG...633.jpg |
| Sofás combinables en 2 zonas | ✅ 8 pax cada combinación | IMG...633.jpg |
| Terraza tiene calle peatonal | ✅ Separa filas | IMG...509.jpg |
| Configuraciones predefinidas | ✅ Ver tabla T-CONF-* | IMG...509.jpg |

---

## Próximos Pasos

1. **Validar discrepancias** con usuario/staff del restobar
2. **Crear tabla Mesas** en Airtable con schema actualizado
3. **Crear tabla ConfiguracionesMesas** en Airtable
4. **Migrar datos** existentes al nuevo formato
5. **Actualizar booking_engine.py** con algoritmo de asignación
6. **Testing** exhaustivo con matriz de casos de uso

---

*Documento generado: 2026-03-09 22:00 CET*  
*Próxima revisión: Después de validación de discrepancias*
