# PLANO DE MESAS - INTERIOR

> **Restobar "En Las Nubes"** - Logroño, España  
> Última actualización: 2026-03-09  
> Basado en: Fotografías IMG20260309221557.jpg, IMG20260309221619.jpg, IMG20260309221633.jpg, IMG20260309221655.jpg

---

## 📋 Índice

1. [Resumen del Interior](#resumen-del-interior)
2. [Layout General ASCII](#layout-general-ascii)
3. [Zona: Sala Exterior](#zona-sala-exterior)
4. [Zona: Sala Interior](#zona-sala-interior)
5. [Zona: Sofás](#zona-sofás)
6. [Zona: Barra](#zona-barra)
7. [Tabla de Especificaciones Completa](#tabla-de-especificaciones-completa)
8. [Casos de Uso Interior](#casos-de-uso-interior)
9. [Casos Edge](#casos-edge)

---

## Resumen del Interior

### Distribución por Zonas

| Zona | Mesas | Cap. Total Base | Cap. Total Ampliada | Características |
|------|-------|-----------------|---------------------|-----------------|
| **Sala Exterior** | 4 | 28 pax | 38 pax | Cerca entrada, luminosa |
| **Sala Interior** | 3 | 16 pax | 20 pax | Zona íntima, 1 mesa delicada |
| **Sofás** | 4 | 17 pax | 20 pax | 2 zonas combinables |
| **Barra** | 2 | 4 pax | 6 pax | Mesas altas, última opción |
| **TOTAL** | **13** | **65 pax** | **84 pax** | - |

### Prioridades de Asignación

```
PRIORIDAD ALTA (8-10): Sala Exterior, SI-6, SI-7, SOF-2, SOF-4
PRIORIDAD MEDIA (5-7): SOF-1, SOF-3
PRIORIDAD BAJA (1-4): SI-8 (delicada), BAR-5, BAR-8 (altas)
```

---

## Layout General ASCII

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            RESTOBAR EN LAS NUBES                            │
│                              PLANTA INTERIOR                                │
└─────────────────────────────────────────────────────────────────────────────┘

  ╔══════════════════════════════════════════════════════════════════════════╗
  ║  ENTRADA                                                                 ║
  ║  PRINCIPAL    ┌─────────────────────────────────────────────────────────┐║
  ║      ↓        │                  SALA EXTERIOR                          │║
  ║               │                                                         │║
  ║    ┌───┐      │   ┌───────┐    ┌───────┐    ┌───────┐    ┌───────┐     │║
  ║    │   │      │   │ SE-1  │    │ SE-2  │    │ SE-4  │    │ SE-5  │     │║
  ║    │ P │      │   │ 6 PAX │    │ 8 PAX │    │ 6 PAX │    │ 8 PAX │     │║
  ║    │ U │      │   │  +AUX │    │ +AUX  │    │ +AUX  │    │ +AUX  │     │║
  ║    │ E │      │   │  →8   │    │ →10   │    │ →10   │    │ →10   │     │║
  ║    │ R │      │   └───────┘    └───────┘    └───────┘    └───────┘     │║
  ║    │ T │      │         Prioridad: 9          Prioridad: 9             │║
  ║    │ A │      └─────────────────────────────────────────────────────────┘║
  ║    └───┘                              │                                  ║
  ║                                       │                                  ║
  ║    ┌──────────────────────────────────┼──────────────────────────────┐   ║
  ║    │          ZONA DE SOFÁS           │       SALA INTERIOR          │   ║
  ║    │                                  │                              │   ║
  ║    │  ┌─────────────────────────┐     │    ┌───────┐   ┌───────┐    │   ║
  ║    │  │   ZONA 1 COMBINABLE     │     │    │ SI-6  │   │ SI-7  │    │   ║
  ║    │  │  ┌──────┐   ┌──────┐    │     │    │ 8 PAX │   │ 6 PAX │    │   ║
  ║    │  │  │SOF-1 │ + │SOF-2 │    │     │    │ +AUX  │   │       │    │   ║
  ║    │  │  │ 2pax │   │ 6pax │    │     │    │ →10   │   │       │    │   ║
  ║    │  │  └──────┘   └──────┘    │     │    └───────┘   └───────┘    │   ║
  ║    │  │    = 8 PAX combinados   │     │    Prioridad: 8    │        │   ║
  ║    │  └─────────────────────────┘     │                    │        │   ║
  ║    │                                  │    ┌───────────────┴───┐    │   ║
  ║    │  ┌─────────────────────────┐     │    │      SI-8         │    │   ║
  ║    │  │   ZONA 2 COMBINABLE     │     │    │   ⚠️ DELICADA     │    │   ║
  ║    │  │  ┌──────┐   ┌──────┐    │     │    │    2-4 PAX        │    │   ║
  ║    │  │  │SOF-3 │ + │SOF-4 │    │     │    │  JUNTO AL BAÑO    │    │   ║
  ║    │  │  │ 3pax │   │ 6pax │    │     │    │  Prioridad: 2     │    │   ║
  ║    │  │  │⚠️peq │   │      │    │     │    └───────────────────┘    │   ║
  ║    │  │  └──────┘   └──────┘    │     │                    │        │   ║
  ║    │  │    = 8 PAX combinados   │     │               ┌────┴────┐   │   ║
  ║    │  └─────────────────────────┘     │               │  BAÑO   │   │   ║
  ║    │  Prioridad: 5-8                  │               │   WC    │   │   ║
  ║    └──────────────────────────────────┴───────────────┴─────────┴───┘   ║
  ║                                                                          ║
  ║    ┌────────────────────────────────────────────────────────────────┐    ║
  ║    │                         BARRA                                  │    ║
  ║    │         ⚠️ MESAS ALTAS CON BANQUETAS - SIEMPRE AVISAR         │    ║
  ║    │                                                                │    ║
  ║    │    ┌────────────────────────────────────────────────────┐     │    ║
  ║    │    │■■■■■■■■■■■■■■■■ BARRA PRINCIPAL ■■■■■■■■■■■■■■■■■│     │    ║
  ║    │    └────────────────────────────────────────────────────┘     │    ║
  ║    │                                                                │    ║
  ║    │           ┌──────┐              ┌──────┐                       │    ║
  ║    │           │BAR-5 │              │BAR-8 │                       │    ║
  ║    │           │2 PAX │              │2 PAX │                       │    ║
  ║    │           │ →3   │              │ →3   │                       │    ║
  ║    │           │⚠️ALTA│              │⚠️ALTA│                       │    ║
  ║    │           └──────┘              └──────┘                       │    ║
  ║    │           Prioridad: 3          Prioridad: 3                  │    ║
  ║    │                                                      ┌─────┐  │    ║
  ║    │                                                      │COCI │  │    ║
  ║    │                                                      │ NA  │  │    ║
  ║    └──────────────────────────────────────────────────────┴─────┴──┘    ║
  ║                                                                          ║
  ║  ←─────────────────── ACCESO A TERRAZA ───────────────────→             ║
  ╚══════════════════════════════════════════════════════════════════════════╝

  LEYENDA:
  ┌──────┐ = Mesa individual
  ⚠️     = Requiere aviso especial al cliente
  +AUX   = Ampliable con mesa auxiliar
  →N     = Capacidad ampliada
```

---

## Zona: Sala Exterior

### Ubicación y Características

- **Posición:** Zona más cercana a la entrada principal
- **Ambiente:** Luminosa, primer contacto con el local
- **Ideal para:** Parejas, familias, grupos medianos

### Detalle de Mesas

| Mesa | Código | Cap. Base | Cap. Máx | Aux. Necesarias | Prioridad | Avisos |
|------|--------|-----------|----------|-----------------|-----------|--------|
| Mesa 1 | SE-1 | 6 | 8 | 1 | 9 | - |
| Mesa 2 | SE-2 | 8 | 10 | 1 | 9 | - |
| Mesa 4 | SE-4 | 6 | 10 | **2** (+1=8, +2=10) | 9 | - |
| Mesa 5 | SE-5 | 8 | 10 | 1 | 9 | - |

> **Nota SE-4:** Requiere específicamente **2 mesas auxiliares** para alcanzar capacidad máxima de 10 pax. Con 1 auxiliar: 8 pax máximo.

### Reglas de Asignación - Sala Exterior

```python
def asignar_sala_exterior(num_personas):
    """
    Reglas para Sala Exterior (SE-1, SE-2, SE-4, SE-5)
    """
    if num_personas <= 6:
        # Priorizar mesas de capacidad 6
        return buscar_disponible(["SE-1", "SE-4"])
    
    elif num_personas <= 8:
        # Priorizar mesas de capacidad 8
        return buscar_disponible(["SE-2", "SE-5", "SE-1", "SE-4"])
    
    elif num_personas <= 10:
        # Necesita auxiliar - cualquier mesa vale
        mesa = buscar_disponible(["SE-2", "SE-5", "SE-4"])
        if mesa:
            return (mesa, auxiliares_necesarias=1)
    
    else:
        # >10 personas - no cabe en Sala Exterior individual
        return None  # Buscar combinación o otra zona
```

### ASCII Layout Detallado - Sala Exterior

```
    ┌─────────────────────────────────────────────────────────────┐
    │                     SALA EXTERIOR                           │
    │                                                             │
    │    VENTANALES HACIA CALLE                                   │
    │  ═══════════════════════════════════════════════════════   │
    │                                                             │
    │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
    │   │   SE-1      │  │   SE-2      │  │   SE-4      │        │
    │   │             │  │             │  │             │        │
    │   │  ○  ○  ○    │  │ ○  ○  ○  ○  │  │  ○  ○  ○    │        │
    │   │  ┌─────┐    │  │ ┌───────┐   │  │  ┌─────┐    │        │
    │   │  │     │    │  │ │       │   │  │  │     │    │        │
    │   │  └─────┘    │  │ └───────┘   │  │  └─────┘    │        │
    │   │  ○  ○  ○    │  │ ○  ○  ○  ○  │  │  ○  ○  ○    │        │
    │   │    6 PAX    │  │   8 PAX     │  │    6 PAX    │        │
    │   └─────────────┘  └─────────────┘  └─────────────┘        │
    │                                                             │
    │                         ┌─────────────┐                     │
    │                         │   SE-5      │                     │
    │                         │             │                     │
    │                         │ ○  ○  ○  ○  │                     │
    │                         │ ┌───────┐   │                     │
    │                         │ │       │   │                     │
    │                         │ └───────┘   │                     │
    │                         │ ○  ○  ○  ○  │                     │
    │                         │   8 PAX     │                     │
    │                         └─────────────┘                     │
    │                                                             │
    │  ──────────────── PASO A SALA INTERIOR ─────────────────   │
    └─────────────────────────────────────────────────────────────┘
```

---

## Zona: Sala Interior

### Ubicación y Características

- **Posición:** Zona más interna del local
- **Ambiente:** Íntima, más reservada
- **Atención:** Mesa 8 es DELICADA (junto al baño)

### Detalle de Mesas

| Mesa | Código | Cap. Base | Cap. Máx | Aux. Necesarias | Prioridad | Avisos |
|------|--------|-----------|----------|-----------------|-----------|--------|
| Mesa 6 | SI-6 | 8 | 10 | 1 | 8 | - |
| Mesa 7 | SI-7 | 6 | 6 | 0 | 8 | - |
| Mesa 8 | SI-8 | 2 | 4 | 0 | **2** | ⚠️ **JUNTO AL BAÑO - EXPLICAR CLIENTE** |

### ⚠️ REGLA CRÍTICA - Mesa 8 (SI-8)

```python
def asignar_mesa_8():
    """
    Mesa 8 es DELICADA - solo usar como última opción
    SIEMPRE explicar la ubicación al cliente
    """
    # 1. Verificar que no hay NINGUNA otra opción
    otras_disponibles = buscar_cualquier_mesa_excepto("SI-8")
    if otras_disponibles:
        return otras_disponibles[0]
    
    # 2. Si Mesa 8 es la única opción
    mensaje_obligatorio = """
    Esta mesa está ubicada cerca de la zona del baño.
    ¿Te parece bien o prefieres esperar a que se libere otra mesa?
    """
    
    # 3. SIEMPRE esperar confirmación explícita
    confirmacion = solicitar_confirmacion(mensaje_obligatorio)
    
    if confirmacion == "SI":
        return "SI-8"
    else:
        # Ofrecer alternativas
        return ofrecer_alternativas(["lista_espera", "horario_diferente"])
```

### ASCII Layout Detallado - Sala Interior

```
    ┌─────────────────────────────────────────────────────────────┐
    │                     SALA INTERIOR                           │
    │                                                             │
    │  ← Desde Sala Exterior                                      │
    │                                                             │
    │   ┌─────────────┐    ┌─────────────┐                       │
    │   │   SI-6      │    │   SI-7      │                       │
    │   │             │    │             │                       │
    │   │ ○  ○  ○  ○  │    │  ○  ○  ○    │                       │
    │   │ ┌───────┐   │    │  ┌─────┐    │                       │
    │   │ │       │   │    │  │     │    │                       │
    │   │ └───────┘   │    │  └─────┘    │                       │
    │   │ ○  ○  ○  ○  │    │  ○  ○  ○    │                       │
    │   │   8 PAX     │    │   6 PAX     │                       │
    │   │  (+AUX→10)  │    │             │                       │
    │   └─────────────┘    └─────────────┘                       │
    │                                                             │
    │                      ┌─────────────┐   ┌──────────────┐    │
    │                      │   SI-8      │   │              │    │
    │                      │   ⚠️⚠️⚠️    │   │    BAÑO      │    │
    │                      │  DELICADA   │   │     WC       │    │
    │                      │             │   │              │    │
    │                      │   ○    ○    │   │   ┌─────┐    │    │
    │                      │  ┌────┐     │   │   │     │    │    │
    │                      │  │    │     │   │   │ 🚽  │    │    │
    │                      │  └────┘     │   │   │     │    │    │
    │                      │   ○    ○    │   │   └─────┘    │    │
    │                      │  2-4 PAX    │   │              │    │
    │                      │ Prioridad:2 │   │              │    │
    │                      └─────────────┘   └──────────────┘    │
    │                                                             │
    │  ⚠️ SI-8: SIEMPRE explicar ubicación junto al baño        │
    └─────────────────────────────────────────────────────────────┘
```

---

## Zona: Sofás

### Ubicación y Características

- **Posición:** Zona lateral, ambiente acogedor
- **Ambiente:** Cómodo, ideal para largas sobremesas
- **Característica:** Dos zonas independientes combinables

### Detalle de Mesas

| Mesa | Código | Cap. Base | Cap. Máx | Combinable Con | Prioridad | Avisos |
|------|--------|-----------|----------|----------------|-----------|--------|
| Sofá 1 | SOF-1 | **2** | **2** | SOF-2 (→8 pax) | 7 | Mesa pequeña para 2 pax |
| Sofá 2 | SOF-2 | 6 | 6 | SOF-1 (→8 pax) | 8 | - |
| Sofá 3 | SOF-3 | 3 | 3 | SOF-4 (→8 pax) | **5** | ⚠️ **MESA PEQUEÑA - AVISAR** |
| Sofá 4 | SOF-4 | 6 | 6 | SOF-3 (→8 pax) | 8 | - |

### Configuraciones Combinadas

| Configuración | Mesas | Capacidad | Prioridad | Notas |
|---------------|-------|-----------|-----------|-------|
| **SOF-CONF-1** | SOF-1 + SOF-2 | 8 pax | 9 | Zona 1 combinada |
| **SOF-CONF-2** | SOF-3 + SOF-4 | 8 pax | 8 | Zona 2 combinada (S-3 pequeña) |

### Reglas de Asignación - Sofás

```python
def asignar_sofas(num_personas):
    """
    Reglas para zona de Sofás
    """
    if num_personas <= 3:
        # SOF-3 es pequeña pero puede servir
        return buscar_disponible(["SOF-3"])  # Con aviso de mesa pequeña
    
    elif num_personas <= 4:
        return buscar_disponible(["SOF-1", "SOF-3"])
    
    elif num_personas <= 6:
        # Priorizar mesas de capacidad 6
        return buscar_disponible(["SOF-2", "SOF-4"])
    
    elif num_personas <= 8:
        # Necesita combinación
        # Priorizar SOF-CONF-1 (sin la mesa pequeña)
        if configuracion_disponible("SOF-CONF-1"):
            return "SOF-CONF-1"  # SOF-1 + SOF-2
        elif configuracion_disponible("SOF-CONF-2"):
            return "SOF-CONF-2"  # SOF-3 + SOF-4 (avisar S-3 pequeña)
    
    else:
        # >8 personas - no cabe en sofás
        return None
```

### ASCII Layout Detallado - Sofás

```
    ┌─────────────────────────────────────────────────────────────┐
    │                     ZONA DE SOFÁS                           │
    │                                                             │
    │   ╔══════════════════════════════════════════════════════╗  │
    │   ║              ZONA 1 - COMBINABLE                     ║  │
    │   ║                                                      ║  │
    │   ║    ┌──────────────┐     ┌──────────────┐            ║  │
    │   ║    │   SOF-1      │     │   SOF-2      │            ║  │
    │   ║    │   ════════   │     │   ════════   │            ║  │
    │   ║    │   │SOFÁ  │   │ ←→  │   │SOFÁ  │   │            ║  │
    │   ║    │   ════════   │     │   ════════   │            ║  │
    │   ║    │    2 PAX     │     │    6 PAX     │            ║  │
    │   ║    │ (mesa peq.)  │     │              │            ║  │
    │   ║    └──────────────┘     └──────────────┘            ║  │
    │   ║                                                      ║  │
    │   ║    ← Combinados = 8 PAX (SOF-CONF-1) →              ║  │
    │   ╚══════════════════════════════════════════════════════╝  │
    │                                                             │
    │   ╔══════════════════════════════════════════════════════╗  │
    │   ║              ZONA 2 - COMBINABLE                     ║  │
    │   ║                                                      ║  │
    │   ║    ┌──────────────┐     ┌──────────────┐            ║  │
    │   ║    │   SOF-3      │     │   SOF-4      │            ║  │
    │   ║    │   ════════   │     │   ════════   │            ║  │
    │   ║    │   │SOFÁ│     │ ←→  │   │SOFÁ  │   │            ║  │
    │   ║    │   ════════   │     │   ════════   │            ║  │
    │   ║    │ ⚠️ 3 PAX     │     │    6 PAX     │            ║  │
    │   ║    │  PEQUEÑA     │     │              │            ║  │
    │   ║    └──────────────┘     └──────────────┘            ║  │
    │   ║                                                      ║  │
    │   ║    ← Combinados = 8 PAX (SOF-CONF-2) →              ║  │
    │   ║    ⚠️ Avisar que SOF-3 es mesa pequeña              ║  │
    │   ╚══════════════════════════════════════════════════════╝  │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

---

## Zona: Barra

### Ubicación y Características

- **Posición:** Junto a barra principal y cocina
- **Ambiente:** Informal, ideal para comidas rápidas
- **IMPORTANTE:** Mesas altas con banquetas - SIEMPRE avisar

### Detalle de Mesas

| Mesa | Código | Cap. Base | Cap. Máx | Prioridad | Avisos |
|------|--------|-----------|----------|-----------|--------|
| Barra 5 | BAR-5 | 2 | 3 | **3** | ⚠️ **MESA ALTA CON BANQUETAS** |
| Barra 8 | BAR-8 | 2 | 3 | **3** | ⚠️ **MESA ALTA CON BANQUETAS** |

### ⚠️ REGLA CRÍTICA - Mesas de Barra

```python
def asignar_barra():
    """
    Mesas de Barra son ÚLTIMA OPCIÓN
    SIEMPRE avisar que son mesas altas con banquetas
    """
    # 1. Verificar que no hay NINGUNA otra opción
    otras_disponibles = buscar_cualquier_mesa_excepto(["BAR-5", "BAR-8"])
    if otras_disponibles:
        return otras_disponibles[0]
    
    # 2. Si Barra es la única opción
    mensaje_obligatorio = """
    Solo nos quedan mesas altas de barra con banquetas.
    ¿Os viene bien o preferís esperar a que se libere otra mesa?
    """
    
    # 3. SIEMPRE esperar confirmación explícita
    confirmacion = solicitar_confirmacion(mensaje_obligatorio)
    
    if confirmacion == "SI":
        return buscar_disponible(["BAR-5", "BAR-8"])
    else:
        return ofrecer_alternativas(["lista_espera", "horario_diferente"])
```

### ASCII Layout Detallado - Barra

```
    ┌─────────────────────────────────────────────────────────────┐
    │                        ZONA BARRA                           │
    │                                                             │
    │     ⚠️⚠️⚠️ MESAS ALTAS CON BANQUETAS ⚠️⚠️⚠️                │
    │           SIEMPRE AVISAR AL CLIENTE                         │
    │                                                             │
    │   ┌────────────────────────────────────────────────────┐   │
    │   │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│   │
    │   │▓▓▓▓▓▓▓▓▓▓▓▓▓▓ BARRA PRINCIPAL ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│   │
    │   │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│   │
    │   └────────────────────────────────────────────────────┘   │
    │                                                             │
    │             ┌──────────┐        ┌──────────┐               │
    │             │  BAR-5   │        │  BAR-8   │               │
    │             │          │        │          │               │
    │             │  ┌────┐  │        │  ┌────┐  │               │
    │             │  │ALTA│  │        │  │ALTA│  │               │
    │             │  └────┘  │        │  └────┘  │               │
    │             │   ⬛⬛   │        │   ⬛⬛   │  ← Banquetas   │
    │             │  2 PAX   │        │  2 PAX   │               │
    │             │   →3     │        │   →3     │               │
    │             └──────────┘        └──────────┘               │
    │                                                             │
    │   Prioridad: 3 (última opción)                             │
    │                                                             │
    │   ┌──────────────────────────────────────┐ ┌────────────┐  │
    │   │          PASO A COCINA               │ │   COCINA   │  │
    │   └──────────────────────────────────────┘ └────────────┘  │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

---

## Tabla de Especificaciones Completa

### Todas las Mesas del Interior

| Código | Zona | Nombre | Cap.Base | Cap.Máx | Prioridad | Aviso Especial | Combinable |
|--------|------|--------|----------|---------|-----------|----------------|------------|
| SE-1 | Sala Exterior | Mesa 1 | 6 | 8 | 9 | - | No |
| SE-2 | Sala Exterior | Mesa 2 | 8 | 10 | 9 | - | No |
| SE-4 | Sala Exterior | Mesa 4 | 6 | 10 | 9 | Requiere 2 aux para 10 pax | No |
| SE-5 | Sala Exterior | Mesa 5 | 8 | 10 | 9 | - | No |
| SI-6 | Sala Interior | Mesa 6 | 8 | 10 | 8 | - | No |
| SI-7 | Sala Interior | Mesa 7 | 6 | 6 | 8 | - | No |
| SI-8 | Sala Interior | Mesa 8 | 2 | 4 | **2** | ⚠️ Junto baño | No |
| SOF-1 | Sofás | Sofá 1 | **2** | **2** | 7 | Mesa pequeña 2 pax | SOF-2 |
| SOF-2 | Sofás | Sofá 2 | 6 | 6 | 8 | - | SOF-1 |
| SOF-3 | Sofás | Sofá 3 | 3 | 3 | **5** | ⚠️ Mesa pequeña | SOF-4 |
| SOF-4 | Sofás | Sofá 4 | 6 | 6 | 8 | - | SOF-3 |
| BAR-5 | Barra | Barra 5 | 2 | 3 | **3** | ⚠️ Mesa alta | No |
| BAR-8 | Barra | Barra 8 | 2 | 3 | **3** | ⚠️ Mesa alta | No |

---

## Casos de Uso Interior

### Caso 1: Pareja (2 personas)

| Prioridad | Mesa | Justificación |
|-----------|------|---------------|
| 1ª | SOF-1 | **2 pax, capacidad exacta** |
| 2ª | SOF-3 | 3 pax, mínimo desperdicio (avisar tamaño) |
| 3ª | BAR-5/BAR-8 | Si aceptan mesa alta |
| 4ª | SI-8 | Solo si confirman ubicación baño |

### Caso 2: Grupo pequeño (4 personas)

| Prioridad | Mesa | Justificación |
|-----------|------|---------------|
| 1ª | SE-1 o SE-4 | 6 pax, desperdicio mínimo |
| 2ª | SI-8 | Solo si confirman (cap. máx 4) |
| ~~SOF-1~~ | ~~Sofá 1~~ | **SOF-1 es 2 pax, NO sirve para 4 personas** |

### Caso 3: Familia mediana (6 personas)

| Prioridad | Mesa | Justificación |
|-----------|------|---------------|
| 1ª | SE-1 o SE-4 | Capacidad exacta 6 pax |
| 2ª | SOF-2 o SOF-4 | Capacidad exacta, ambiente sofá |
| 3ª | SI-7 | Sala interior, capacidad exacta |

### Caso 4: Grupo grande (8 personas)

| Prioridad | Mesa | Justificación |
|-----------|------|---------------|
| 1ª | SE-2 o SE-5 | Capacidad 8 pax base |
| 2ª | SI-6 | Capacidad 8 pax base |
| 3ª | SOF-CONF-1 | SOF-1+SOF-2 combinados |
| 4ª | SOF-CONF-2 | SOF-3+SOF-4 (avisar S-3 pequeña) |

### Caso 5: Grupo muy grande (10 personas)

| Prioridad | Mesa | Justificación |
|-----------|------|---------------|
| 1ª | SE-2 + 1 auxiliar | 10 pax con 1 auxiliar |
| 2ª | SE-5 + 1 auxiliar | 10 pax con 1 auxiliar |
| 3ª | SE-4 + **2 auxiliares** | 10 pax (requiere 2 aux, no 1) |
| 4ª | SI-6 + 1 auxiliar | 10 pax con 1 auxiliar |

> **⚠️ Nota sobre auxiliares:** Solo hay **4 mesas auxiliares** disponibles en total. SE-4 consume 2 auxiliares para 10 pax.

### Caso 6: Grupo grande interior (12 personas)

**⚠️ Requiere combinación o derivación a terraza**

| Opción | Mesas | Capacidad | Notas |
|--------|-------|-----------|-------|
| A | SE-2 (10) + SOF individual | ~12-14 | Dividir grupo |
| B | SOF-CONF-1 (8) + SOF-CONF-2 (8) | ~16 | Si ambas zonas libres |
| C | Derivar a terraza | - | Si disponible |
| D | Handoff a staff | - | Validar manualmente |

---

## Casos Edge

### Edge 1: Mesa 8 como Única Opción

```
Escenario: Pareja llega a las 21:00, TODO lleno excepto SI-8

Flujo:
1. Sistema detecta: solo SI-8 disponible
2. Alba comunica:
   "Ahora mismo solo nos queda una mesita en la sala interior,
   pero te aviso que está cerquita de la zona del baño.
   ¿Os parece bien o preferís esperar un ratito a ver si se libera otra?"
3. Si aceptan → Asignar SI-8
4. Si rechazan → Lista de espera o sugerir horario alternativo
```

### Edge 2: Todas las Mesas de Sala Exterior Ocupadas

```
Escenario: Cliente pide Sala Exterior, pero está llena

Flujo:
1. Sistema detecta: zona preferida no disponible
2. Alba comunica:
   "La sala exterior está completa ahora mismo.
   Tenemos disponibilidad en la zona de sofás que es muy acogedora,
   o si preferís puedo apuntaros en lista de espera para Sala Exterior."
3. Ofrecer alternativas:
   - Sofás
   - Sala Interior
   - Lista de espera
   - Horario diferente
```

### Edge 3: Barra Llena y Solo Quedan Mesas de Capacidad Grande

```
Escenario: Pareja (2 pax), solo disponible SE-2 (8 pax)

Flujo:
1. Sistema detecta: desperdicio de 6 plazas
2. Política de negocio: ¿Permitir?
   - Opción A: Permitir con nota interna "mesa grande para 2"
   - Opción B: Sugerir barra primero (si están de acuerdo con alta)
   - Opción C: Lista de espera para mesa más adecuada
3. Alba comunica según política configurada
```

### Edge 4: Grupo Solicita Sofás pero Solo SOF-3 Libre

```
Escenario: 4 personas piden sofás, solo SOF-3 (3 pax) libre

Flujo:
1. Sistema detecta: capacidad insuficiente (3 < 4)
2. Alba comunica:
   "En sofás ahora mismo solo tenemos una mesita de 3 personas.
   ¿Os parece si os pongo en Sala Exterior donde tenemos mesas de 6?
   Son muy cómodas también."
3. Redirigir a Sala Exterior o Interior
```

### Edge 5: Todas las Auxiliares Agotadas

```
Escenario: Cliente pide mesa para 10, SE-2 disponible pero sin auxiliares

Flujo:
1. Sistema detecta: SE-2 cap. base = 8, necesita auxiliar para 10
2. Verificar: ¿Hay auxiliares disponibles?
3. Si NO hay auxiliares:
   Alba comunica:
   "Para 10 personas necesitaríamos añadir una mesita auxiliar,
   pero ahora mismo las tenemos todas ocupadas.
   ¿Os vendría bien venir 8 personas, o preferís otro horario?"
4. Alternativas:
   - Reducir grupo a 8
   - Horario diferente
   - Derivar a terraza (si disponible y >10 pax)
```

---

## Notas de Implementación

### Queries Airtable para Interior

```python
# Obtener todas las mesas del interior disponibles
formula = """
AND(
    OR(
        {Zona} = 'Sala Exterior',
        {Zona} = 'Sala Interior',
        {Zona} = 'Sofás',
        {Zona} = 'Barra'
    ),
    {Disponible} = TRUE()
)
"""

# Obtener mesas con capacidad suficiente
formula_capacidad = """
AND(
    {Capacidad_Maxima} >= {num_personas},
    {Disponible} = TRUE()
)
"""

# Ordenar por prioridad y desperdicio mínimo
sort = [
    {"field": "Prioridad_Asignacion", "direction": "desc"},
    {"field": "Capacidad_Base", "direction": "asc"}
]
```

---

*Documento generado: 2026-03-09*  
*Fuentes: IMG20260309221557.jpg, IMG20260309221619.jpg, IMG20260309221633.jpg, IMG20260309221655.jpg*
