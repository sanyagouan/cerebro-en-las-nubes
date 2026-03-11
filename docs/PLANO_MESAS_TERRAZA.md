# PLANO DE MESAS - TERRAZA

> **Restobar "En Las Nubes"** - Logroño, España  
> Última actualización: 2026-03-09  
> Basado en: Fotografía IMG20260309221509.jpg

---

## 📋 Índice

1. [Resumen de Terraza](#resumen-de-terraza)
2. [Layout General ASCII](#layout-general-ascii)
3. [Mesas Individuales](#mesas-individuales)
4. [Configuraciones Predefinidas](#configuraciones-predefinidas)
5. [Elementos Arquitectónicos](#elementos-arquitectónicos)
6. [Casos de Uso Terraza](#casos-de-uso-terraza)
7. [Gestión de Clima](#gestión-de-clima)
8. [Discrepancias Pendientes](#discrepancias-pendientes)

---

## Resumen de Terraza

### ✅ ESTRUCTURA CONFIRMADA POR USUARIO

```
┌──────────────────────────────────────────────────────────┐
│         ESTRUCTURA REAL DE MESAS - TERRAZA               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  📌 TOTAL: 25 mesas INDIVIDUALES                         │
│                                                          │
│  📌 CONFIGURACIÓN NORMAL: Pares de 2 mesas               │
│     - 2 mesas juntas = 1 unidad de 6 PAX MÁXIMO         │
│     - Total: ~12 pares + 1 mesa individual               │
│                                                          │
│  📌 EXCEPCIÓN: Mesa 12 es INDIVIDUAL (no se junta)       │
│     - Capacidad: 2-3 pax                                 │
│     - No tiene mesa compañera                            │
│                                                          │
│  📌 ELEMENTOS ARQUITECTÓNICOS (puntos en croquis):       │
│     - Árboles, farolas, elementos decorativos           │
│     - NO relevantes para asignación normal               │
│     - Solo considerar para grupos grandes (18-20 pax)    │
│                                                          │
│  📌 MÁXIMO GRUPO EN TERRAZA: 18-20 personas              │
│     - Solo posible en zonas específicas del croquis      │
│     - Requiere validación manual                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Información Visual

| Elemento | Dato | Fuente |
|----------|------|--------|
| **Mesas individuales** | **25** | ✅ Confirmado usuario |
| **Configuraciones (pares)** | ~13 | 12 pares + 1 sola (Mesa 12) |
| **Distribución** | 2 filas | Confirmado |
| **Separación** | Calle peatonal | Confirmado |
| **Capacidad por par** | **6 pax máx** | ✅ Confirmado usuario |
| **Máximo grupo** | **18-20 pax** | ✅ Confirmado usuario |

### Distribución por Filas

| Fila | Unidades (Pares) | Cap. por Unidad | Cap. Total | Notas |
|------|------------------|-----------------|------------|-------|
| **Superior** | ~6-7 unidades | 6 pax c/u | ~40 pax | Incluye Mesa 12 (sola) |
| **Inferior** | ~6 unidades | 6 pax c/u | ~36 pax | Todas en pares |
| **TOTAL** | **~13** | **6 pax** | **~76 pax** | 25 mesas = 12 pares + 1 |

---

## Layout General ASCII

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RESTOBAR EN LAS NUBES                            │
│                              TERRAZA EXTERIOR                               │
└─────────────────────────────────────────────────────────────────────────────┘

  ╔══════════════════════════════════════════════════════════════════════════╗
  ║                                                                          ║
  ║  ┌────────────────────────────────────────────────────────────────────┐  ║
  ║  │                     FILA SUPERIOR (Junto edificio)                  │  ║
  ║  │                                                                     │  ║
  ║  │    ┌───────────────┐  ┌───────────────────────────┐  ┌──────────┐ │  ║
  ║  │    │  ZONA IZQ     │  │       ZONA CENTRAL        │  │ ZONA DER │ │  ║
  ║  │    │               │  │                           │  │          │ │  ║
  ║  │    │ ┌────┐ ┌────┐ │  │ ┌────┐ ┌────┐ ┌────┐     │  │ ┌────┐   │ │  ║
  ║  │    │ │T-09│ │T-10│ │  │ │T-11│ │T-12│ │T-13│     │  │ │T-15│   │ │  ║
  ║  │    │ │    │ │    │ │  │ │    │ │SOLA│ │    │     │  │ │    │   │ │  ║
  ║  │    │ └────┘ └────┘ │  │ └────┘ └────┘ └────┘     │  │ └────┘   │ │  ║
  ║  │    │   ↓     ↓     │  │   ↓           ↓          │  │   ↓      │ │  ║
  ║  │    │ T-CONF-1      │  │ T-CONF-2 (T-11+T-13)     │  │          │ │  ║
  ║  │    │   6 PAX       │  │  18-20 PAX (sin T-12)    │  │ ┌────┐   │ │  ║
  ║  │    └───────────────┘  │                           │  │ │T-16│   │ │  ║
  ║  │                       │                           │  │ │    │   │ │  ║
  ║  │    🌳                  │                           │  │ └────┘   │ │  ║
  ║  │   Árbol/Farola        │                           │  │  ↓       │ │  ║
  ║  │                       └───────────────────────────┘  │ T-CONF-3 │ │  ║
  ║  │                                                      │   6 PAX  │ │  ║
  ║  │                                                      └──────────┘ │  ║
  ║  │                                                                    │  ║
  ║  └────────────────────────────────────────────────────────────────────┘  ║
  ║                                                                          ║
  ║  ═══════════════════════ CALLE PEATONAL ════════════════════════════════ ║
  ║                                                                          ║
  ║  ┌────────────────────────────────────────────────────────────────────┐  ║
  ║  │                     FILA INFERIOR (Lado calle)                      │  ║
  ║  │                                                                     │  ║
  ║  │    ┌───────────────┐  ┌───────────────────────┐  ┌──────────────┐  │  ║
  ║  │    │  ZONA IZQ     │  │     ZONA CENTRAL      │  │   ZONA DER   │  │  ║
  ║  │    │               │  │                       │  │              │  │  ║
  ║  │    │ ┌────┐ ┌────┐ │  │   ┌────┐   ┌────┐     │  │ ┌────┐ ┌────┐│  │  ║
  ║  │    │ │T-02│ │T-03│ │  │   │T-04│   │T-05│     │  │ │T-07│ │T-08││  │  ║
  ║  │    │ │    │ │    │ │  │   │    │   │    │     │  │ │    │ │    ││  │  ║
  ║  │    │ └────┘ └────┘ │  │   └────┘   └────┘     │  │ └────┘ └────┘│  │  ║
  ║  │    │   ↓     ↓     │  │     ↓         ↓       │  │   ↓     ↓    │  │  ║
  ║  │    │ T-CONF-4      │  │   T-CONF-5 (grande)   │  │ T-CONF-6     │  │  ║
  ║  │    │   6 PAX       │  │    18-20 PAX          │  │   6 PAX      │  │  ║
  ║  │    │               │  │                       │  │              │  │  ║
  ║  │    │    🌳         │  │       🏮              │  │              │  │  ║
  ║  │    └───────────────┘  └───────────────────────┘  └──────────────┘  │  ║
  ║  │                                                                     │  ║
  ║  └────────────────────────────────────────────────────────────────────┘  ║
  ║                                                                          ║
  ║  🌳 = Árbol       🏮 = Farola/Banco público                              ║
  ║                                                                          ║
  ╚══════════════════════════════════════════════════════════════════════════╝

  LEYENDA:
  ┌────┐ = Mesa individual
  T-XX  = Código de mesa terraza
  T-CONF-X = Configuración combinada predefinida
  🌳 = Elemento arquitectónico (árbol, farola, banco)
```

---

## Mesas Individuales

### Fila Superior (Junto al Edificio)

| Mesa | Código | Cap. Ind. | Mesa Compañera | Unidad | Cap. Par | Notas |
|------|--------|-----------|----------------|--------|----------|-------|
| Mesa 9 | T-09 | 3 pax | T-10 | Par 1 | **6 pax** | Zona arbolada |
| Mesa 10 | T-10 | 3 pax | T-09 | Par 1 | **6 pax** | Junto a T-09 |
| Mesa 11 | T-11 | 3 pax | T-13 | Par 2 | **6 pax** | Zona central |
| **Mesa 12** | **T-12** | **2-3 pax** | **❌ NINGUNA** | **SOLA** | **2-3 pax** | ⚠️ **Mesa individual - NO se junta** |
| Mesa 13 | T-13 | 3 pax | T-11 | Par 2 | **6 pax** | Zona central |
| Mesa 15 | T-15 | 3 pax | T-16 | Par 3 | **6 pax** | Derecha |
| Mesa 16 | T-16 | 3 pax | T-15 | Par 3 | **6 pax** | Esquina |

### Fila Inferior (Lado Calle)

| Mesa | Código | Cap. Est. | Combinable Con | Zona | Notas |
|------|--------|-----------|----------------|------|-------|
| Mesa 2 | T-02 | 4-5 pax | T-03 | Izquierda | Cerca de árbol |
| Mesa 3 | T-03 | 4-5 pax | T-02 | Izquierda | - |
| Mesa 4 | T-04 | 8-10 pax | T-05 | Central | Mesa grande |
| Mesa 5 | T-05 | 8-10 pax | T-04 | Central | Mesa grande |
| Mesa 7 | T-07 | 4-5 pax | T-08 | Derecha | - |
| Mesa 8 | T-08 | 4-5 pax | T-07 | Derecha | Esquina |

### ⚠️ Mesas NO Visibles en Plano

| Mesa | Código Propuesto | Estado | Acción |
|------|------------------|--------|--------|
| Mesa 1 | T-01 | ❌ No visible | Validar existencia |
| Mesa 6 | T-06 | ❌ No visible | Validar existencia |
| Mesa 14 | T-14 | ❌ No visible | Validar existencia |
| Mesas 17-25 | T-17 a T-25 | ❌ No visible | Validar si existen |

---

## Configuraciones Predefinidas

### Tabla ConfiguracionesMesas - Terraza

| ID | Nombre | Capacidad | Mesas | Zona | Prioridad | Notas |
|----|--------|-----------|-------|------|-----------|-------|
| **T-CONF-1** | Terraza Izq Superior | 6 pax | T-09, T-10 | Fila Superior | 9 | 2 mesas juntas zona árbol |
| **T-CONF-2** | Terraza Centro Superior | 18-20 pax | T-11, T-13 | Fila Superior | 10 | Para grupos grandes (⚠️ T-12 es individual - NO incluida) |
| **T-CONF-3** | Terraza Der Superior | 6 pax | T-15, T-16 | Fila Superior | 9 | 2 mesas esquina |
| **T-CONF-4** | Terraza Izq Inferior | 6 pax | T-02, T-03 | Fila Inferior | 9 | Junto a árbol |
| **T-CONF-5** | Terraza Centro Inferior | 18-20 pax | T-04, T-05 | Fila Inferior | 10 | Para grupos grandes |
| **T-CONF-6** | Terraza Der Inferior | 6 pax | T-07, T-08 | Fila Inferior | 9 | 2 mesas esquina |
| **T-CONF-GRANDE-SUP** | Terraza Superior Completa | **18-20 pax** | T-11, T-13 | Fila Superior | 10 | ⚠️ Máximo terraza - Validación staff |
| **T-CONF-GRANDE-INF** | Terraza Inferior Completa | **18-20 pax** | T-04, T-05 | Fila Inferior | 10 | ⚠️ Máximo terraza - Validación staff |

### Diagrama de Configuraciones

```
┌─────────────────────────────────────────────────────────────────┐
│                  CONFIGURACIONES PREDEFINIDAS                   │
└─────────────────────────────────────────────────────────────────┘

  FILA SUPERIOR:
  ┌─────────────┐    ┌───────────────────────┐    ┌─────────────┐
  │  T-CONF-1   │    │      T-CONF-2         │    │  T-CONF-3   │
  │  T-09+T-10  │    │     T-11+T-13         │    │  T-15+T-16  │
  │    6 PAX    │    │     18-20 PAX         │    │    6 PAX    │
  └─────────────┘    │  (⚠️ T-12 es SOLA)    │    └─────────────┘
                     └───────────────────────┘

  ══════════════════════ CALLE PEATONAL ═══════════════════════

  FILA INFERIOR:
  ┌─────────────┐    ┌───────────────────────┐    ┌─────────────┐
  │  T-CONF-4   │    │      T-CONF-5         │    │  T-CONF-6   │
  │  T-02+T-03  │    │    T-04+T-05          │    │  T-07+T-08  │
  │    6 PAX    │    │     18-20 PAX         │    │    6 PAX    │
  └─────────────┘    └───────────────────────┘    └─────────────┘

  MÁXIMO GRUPO EN TERRAZA:
  ┌─────────────────────────────────────────────────────────────┐
  │  T-CONF-2 (T-11+T-13):       18-20 PAX máximo               │
  │  T-CONF-5 (T-04+T-05):       18-20 PAX máximo               │
  │  ⚠️ LÍMITE ABSOLUTO TERRAZA: 18-20 personas                 │
  │  ⚠️ Requiere validación manual con staff para grupos >12    │
  └─────────────────────────────────────────────────────────────┘
```

---

## Elementos Arquitectónicos

### Obstáculos Identificados en Plano

| Elemento | Ubicación Aproximada | Impacto | Notas |
|----------|----------------------|---------|-------|
| 🌳 Árbol 1 | Entre T-09/T-10 y calle | Sombra en verano | Positivo |
| 🌳 Árbol 2 | Cerca de T-02/T-03 | Sombra en verano | Positivo |
| 🏮 Farola | Zona central inferior | Iluminación nocturna | Positivo |
| Banco público | Variable | Puede interferir | Validar ubicación |

### Consideraciones de Layout

```
┌─────────────────────────────────────────────────────────────────┐
│              GESTIÓN DE OBSTÁCULOS ARQUITECTÓNICOS              │
└─────────────────────────────────────────────────────────────────┘

  REGLA 1: Árboles como ventaja
  ─────────────────────────────
  - En verano: Ofrecer mesas cerca de árboles para sombra
  - Mesas T-09, T-10, T-02, T-03 → "zona con sombra natural"

  REGLA 2: Farolas como ventaja
  ─────────────────────────────
  - En cenas: Iluminación ambiente
  - No requiere consideración especial en asignación

  REGLA 3: Bancos públicos como restricción
  ─────────────────────────────────────────
  - Pueden ocupar espacio entre mesas
  - Si hay evento público → algunas configuraciones no disponibles
  - Marcar en ConfiguracionesMesas: Restricciones = "evento_publico"
```

---

## Casos de Uso Terraza

### Caso 1: Pareja/Grupo pequeño (2-4 personas)

| Prioridad | Mesa | Justificación |
|-----------|------|---------------|
| 1ª | T-02, T-03, T-07, T-08 | Mesas pequeñas fila inferior |
| 2ª | T-09, T-10, T-15, T-16 | Mesas pequeñas fila superior |
| 3ª | Interior | Si terraza llena |

### Caso 2: Grupo mediano (5-6 personas)

| Prioridad | Mesa/Config | Justificación |
|-----------|-------------|---------------|
| 1ª | T-11, T-12, T-13 | Mesas individuales grandes |
| 2ª | T-04, T-05 | Mesas individuales grandes |
| 3ª | T-CONF-1 o T-CONF-4 | Combinaciones si individual no disponible |

### Caso 3: Grupo grande (8-10 personas)

| Prioridad | Configuración | Mesas | Capacidad |
|-----------|---------------|-------|-----------|
| 1ª | T-CONF-1 | T-09 + T-10 | 6 pax |
| 2ª | T-CONF-3 | T-15 + T-16 | 6 pax |
| 3ª | T-CONF-4 | T-02 + T-03 | 6 pax |
| 4ª | T-CONF-6 | T-07 + T-08 | 6 pax |

### Caso 4: Grupo muy grande (12-15 personas)

| Prioridad | Configuración | Mesas | Capacidad |
|-----------|---------------|-------|-----------|
| 1ª | T-CONF-5 | T-04 + T-05 | 18-20 pax |
| 2ª | T-CONF-2 | T-11 + T-13 | 18-20 pax (⚠️ T-12 es SOLA) |
| 3ª | Combinación ad-hoc | Validar manual | Variable |

### Caso 5: Evento/Celebración (18-20 personas) - ⚠️ MÁXIMO TERRAZA

| Opción | Configuración | Capacidad | Notas |
|--------|---------------|-----------|-------|
| A | T-CONF-2 | 18-20 pax | Fila superior central (T-11+T-13) |
| B | T-CONF-5 | 18-20 pax | Fila inferior central (T-04+T-05) |
| ⚠️ | **MÁXIMO** | **18-20 pax** | **Límite absoluto terraza** |

### Caso 6: Mascotas

```
┌─────────────────────────────────────────────────────────────────┐
│                  POLÍTICA DE MASCOTAS - TERRAZA                 │
└─────────────────────────────────────────────────────────────────┘

  ✅ PERMITIDO en TODA la terraza
  
  Recomendaciones:
  - Mesas de esquina (T-08, T-16): Más espacio para mascota
  - Mesas zona árbol (T-02, T-09): Sombra natural
  
  Flujo en reserva:
  IF mascota = True:
      priorizar = ["T-08", "T-16", "T-02", "T-09"]
      avisar = "Agua disponible para mascota"
```

---

## Gestión de Clima

### Reglas por Condiciones Meteorológicas

| Clima | Disponibilidad Terraza | Configuraciones Afectadas |
|-------|------------------------|---------------------------|
| ☀️ Sol intenso | ✅ Completa (priorizar sombra) | Preferir T-09, T-10, T-02, T-03 |
| 🌤️ Nublado | ✅ Completa | Todas disponibles |
| 🌧️ Lluvia leve | ⚠️ Parcial (cubiertas) | Solo bajo toldos (validar) |
| 🌧️ Lluvia fuerte | ❌ Cerrada | Derivar a interior |
| ❄️ Frío (<10°C) | ⚠️ Avisar cliente | Ofrecer interior como alternativa |

### Implementación en Sistema

```python
def evaluar_terraza(condiciones_clima):
    """
    Evalúa disponibilidad de terraza según clima
    """
    if condiciones_clima.lluvia_fuerte:
        return {
            "disponible": False,
            "mensaje": "La terraza está cerrada por lluvia. ¿Te pongo en interior?"
        }
    
    elif condiciones_clima.lluvia_leve:
        return {
            "disponible": True,
            "restringido": True,
            "mesas_disponibles": obtener_mesas_cubiertas(),
            "mensaje": "Hay algo de lluvia, pero tenemos mesas cubiertas disponibles."
        }
    
    elif condiciones_clima.temperatura < 10:
        return {
            "disponible": True,
            "avisar": True,
            "mensaje": "Hoy hace fresquito en terraza. ¿Preferís dentro o tenéis abrigo?"
        }
    
    elif condiciones_clima.sol_intenso:
        return {
            "disponible": True,
            "priorizar": ["T-09", "T-10", "T-02", "T-03"],  # Zona con sombra
            "mensaje": "Tenemos mesas con sombra natural si preferís."
        }
    
    else:
        return {
            "disponible": True,
            "mensaje": None
        }
```

---

## Discrepancias Pendientes

### ❌ REQUIEREN VALIDACIÓN URGENTE

| # | Discrepancia | Impacto | Acción |
|---|--------------|---------|--------|
| 1 | **Solo 14 mesas visibles de 25** | ALTO | Confirmar existencia de T-01, T-06, T-14, T-17 a T-25 |
| 2 | **Capacidades estimadas** | MEDIO | Confirmar capacidad real de cada mesa |
| 3 | **Nomenclatura gaps (1,6,14)** | MEDIO | ¿Es intencional o error de plano? |
| 4 | **Mesas cubiertas** | MEDIO | ¿Hay toldos? ¿Cuáles mesas cubren? |
| 5 | **Combinaciones válidas** | BAJO | Confirmar que las combinaciones indicadas son correctas |

### ✅ INFORMACIÓN CONFIRMADA

| Elemento | Confirmación | Fuente |
|----------|--------------|--------|
| 2 filas separadas por calle | ✅ | IMG...509.jpg |
| Combinaciones T-CONF-1 a T-CONF-6 | ✅ | Indicado en plano |
| Elementos arquitectónicos (puntos azules) | ✅ | IMG...509.jpg |
| Mesas 9+10 combinables | ✅ | Flechas en plano |
| Mesas 11+13 combinables (⚠️ **T-12 es INDIVIDUAL**) | ✅ | Confirmado usuario |
| Mesas 15+16 combinables | ✅ | Flechas en plano |
| Mesas 2+3 combinables | ✅ | Flechas en plano |
| Mesas 4+5 combinables | ✅ | Flechas en plano |
| Mesas 7+8 combinables | ✅ | Flechas en plano |
| **Mesa 12 = SOLA (no tiene compañera)** | ✅ | **Confirmado usuario** |

---

## Algoritmo de Asignación - Terraza

```python
def asignar_terraza(num_personas, preferencias=None):
    """
    Asigna mesa óptima en terraza
    
    Args:
        num_personas: int (1-100)
        preferencias: dict {zona, sombra, esquina, mascota}
    
    Returns:
        Mesa o Configuración asignada
    """
    
    # PASO 1: Evaluar clima
    clima = evaluar_terraza(obtener_clima_actual())
    if not clima["disponible"]:
        return derivar_a_interior()
    
    # PASO 2: Determinar si necesita configuración
    if num_personas <= 8:
        # Buscar mesa individual
        return buscar_mesa_individual_terraza(num_personas, preferencias)
    
    elif num_personas <= 10:
        # Buscar configuración de 2 mesas
        configs_10 = ["T-CONF-1", "T-CONF-3", "T-CONF-4", "T-CONF-6"]
        return buscar_configuracion_disponible(configs_10)
    
    elif num_personas <= 20:
        # Buscar configuración grande
        configs_20 = ["T-CONF-2", "T-CONF-5"]
        return buscar_configuracion_disponible(configs_20)
    
    else:
        # >20 personas: Requiere validación manual
        return handoff_a_staff("Grupo grande terraza", num_personas)


def buscar_mesa_individual_terraza(num_personas, preferencias):
    """
    Busca mesa individual óptima en terraza
    """
    # Obtener todas las mesas disponibles
    mesas = obtener_mesas_terraza_disponibles()
    
    # Aplicar preferencias
    if preferencias.get("sombra"):
        mesas = priorizar(mesas, ["T-09", "T-10", "T-02", "T-03"])
    
    if preferencias.get("esquina"):
        mesas = priorizar(mesas, ["T-08", "T-16"])
    
    if preferencias.get("mascota"):
        mesas = priorizar(mesas, ["T-08", "T-16", "T-02", "T-09"])
    
    # Filtrar por capacidad
    mesas_validas = [m for m in mesas if m.capacidad >= num_personas]
    
    # Ordenar por desperdicio mínimo
    mesas_validas.sort(key=lambda m: m.capacidad - num_personas)
    
    return mesas_validas[0] if mesas_validas else None
```

---

## Notas de Implementación

### Queries Airtable para Terraza

```python
# Obtener todas las mesas de terraza disponibles
formula = """
AND(
    {Zona} = 'Terraza',
    {Disponible} = TRUE()
)
"""

# Obtener configuraciones disponibles para X personas
formula_config = """
AND(
    {Zona} = 'Terraza',
    {Capacidad_Total} >= {num_personas},
    {Es_Activa} = TRUE(),
    # Verificar que todas las mesas de la config están libres
)
"""

# Ordenar por capacidad (menor desperdicio)
sort = [
    {"field": "Capacidad_Total", "direction": "asc"}
]
```

### Validación de Configuraciones

```python
def configuracion_disponible(config_id):
    """
    Verifica que TODAS las mesas de una configuración están libres
    """
    config = obtener_configuracion(config_id)
    mesas_incluidas = config["Mesas_Incluidas"]
    
    for mesa_id in mesas_incluidas:
        if not mesa_disponible(mesa_id):
            return False
    
    return True
```

---

*Documento generado: 2026-03-09*  
*Fuente principal: IMG20260309221509.jpg*  
*Estado: Pendiente validación de mesas 1, 6, 14 y 17-25*
