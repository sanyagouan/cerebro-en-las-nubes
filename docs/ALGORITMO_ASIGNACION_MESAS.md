# ALGORITMO DE ASIGNACIÓN DE MESAS

> **Restobar "En Las Nubes"** - Logroño, España  
> Última actualización: 2026-03-09  
> Versión: 1.0.0

---

## 📋 Índice

1. [Visión General](#visión-general)
2. [Arquitectura del Algoritmo](#arquitectura-del-algoritmo)
3. [Sistema de Prioridades](#sistema-de-prioridades)
4. [Flujo de Decisión Principal](#flujo-de-decisión-principal)
5. [Pseudocódigo Detallado](#pseudocódigo-detallado)
6. [Matriz de Casos de Uso](#matriz-de-casos-de-uso)
7. [Casos Edge Exhaustivos](#casos-edge-exhaustivos)
8. [Validaciones y Restricciones](#validaciones-y-restricciones)
9. [Mensajes de Respuesta](#mensajes-de-respuesta)

---

## Visión General

### Objetivo del Algoritmo

El algoritmo de asignación tiene como objetivo principal:

1. **Minimizar desperdicio** de capacidad (no asignar mesa de 10 a 2 personas)
2. **Maximizar satisfacción** del cliente (respetar preferencias)
3. **Priorizar mesas cómodas** sobre mesas con avisos especiales
4. **Evitar errores** comunicando avisos obligatorios cuando aplique

### Principios Fundamentales

```
┌─────────────────────────────────────────────────────────────────┐
│                  PRINCIPIOS DE ASIGNACIÓN                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CAPACIDAD JUSTA                                             │
│     → Asignar mesa con capacidad más cercana a num_personas    │
│     → Desperdicio = Capacidad_Mesa - Num_Personas              │
│     → Objetivo: Desperdicio mínimo                             │
│                                                                 │
│  2. PRIORIDAD POR COMODIDAD                                     │
│     → Primero mesas normales (sin avisos)                      │
│     → Después mesas con avisos leves                           │
│     → Al final mesas delicadas (última opción)                 │
│                                                                 │
│  3. PREFERENCIAS DEL CLIENTE                                    │
│     → Respetar zona preferida si está disponible               │
│     → Ofrecer alternativas si no disponible                    │
│                                                                 │
│  4. COMUNICACIÓN OBLIGATORIA                                    │
│     → SI-8: Siempre explicar ubicación junto a baño            │
│     → B-*: Siempre avisar que son mesas altas                  │
│     → SOF-3: Avisar que es mesa pequeña                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Arquitectura del Algoritmo

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MOTOR DE ASIGNACIÓN DE MESAS                     │
└─────────────────────────────────────────────────────────────────────┘

  ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
  │    INPUT       │     │   PROCESADOR   │     │    OUTPUT      │
  │                │     │                │     │                │
  │ • num_personas │────▶│ 1. Validar     │────▶│ • Mesa/Config  │
  │ • zona_pref    │     │ 2. Filtrar     │     │ • Mensaje      │
  │ • preferencias │     │ 3. Ordenar     │     │ • Avisos       │
  │ • fecha/hora   │     │ 4. Seleccionar │     │ • Alternativas │
  └────────────────┘     └────────────────┘     └────────────────┘
                                │
                                ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │                        DATA SOURCES                             │
  │                                                                 │
  │  ┌──────────────┐  ┌──────────────────┐  ┌────────────────┐   │
  │  │    Mesas     │  │ConfiguracionesMesas│  │   Reservas     │   │
  │  │  (Airtable)  │  │    (Airtable)     │  │   (Airtable)   │   │
  │  └──────────────┘  └──────────────────┘  └────────────────┘   │
  │                                                                 │
  └─────────────────────────────────────────────────────────────────┘
```

### Capas del Sistema

```python
# Estructura de capas
src/
├── services/
│   └── booking_engine.py          # Lógica principal de asignación
│
├── domain/
│   ├── models/
│   │   ├── mesa.py                 # Modelo Mesa
│   │   └── configuracion.py        # Modelo Configuración
│   │
│   └── rules/
│       ├── priority_rules.py       # Reglas de prioridad
│       ├── capacity_rules.py       # Reglas de capacidad
│       └── notification_rules.py   # Reglas de avisos
│
└── infrastructure/
    └── airtable/
        ├── mesas_repository.py     # CRUD Mesas
        └── config_repository.py    # CRUD Configuraciones
```

---

## Sistema de Prioridades

### Escala de Prioridad (1-10)

| Prioridad | Categoría | Mesas | Descripción |
|-----------|-----------|-------|-------------|
| **10** | Óptimas | SE-1, SE-2, SE-4, SE-5 | Sala Exterior - Primera opción |
| **9** | Muy buenas | T-CONF-2, T-CONF-5 | Configuraciones grandes terraza (18-20 pax) |
| **8** | Buenas | SI-6, SI-7, SOF-2, SOF-4 | Interior y sofás principales |
| **7** | Aceptables | SOF-1 | Sofá pequeño (2 pax) |
| **6** | Con aviso leve | T-* pares (6 pax) | Terraza en pares (clima) |
| **5** | Con aviso | SOF-3 | ⚠️ Mesa pequeña - avisar |
| **4** | Última opción | Configuraciones ad-hoc | Combinaciones no predefinidas |
| **3** | Última opción | B-5, B-8 | ⚠️ Mesas altas - avisar |
| **2** | Muy última | SI-8 | ⚠️ Junto baño - explicar |
| **1** | Solo emergencia | Handoff manual | Derivar a staff |

### Matriz de Prioridad Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                    MATRIZ DE PRIORIDAD                          │
└─────────────────────────────────────────────────────────────────┘

  PRIORIDAD ───────────────────────────────────────────────────▶
  
  10    │ SE-1  SE-2  SE-4  SE-5
   9    │ T-CONF-2  T-CONF-5 (grupos 18-20 pax)
   8    │ SI-6  SI-7  SOF-2  SOF-4
   7    │ SOF-1 (2 pax)
   6    │ T-pares (6 pax máx): T-01+T-02, T-03+T-04, etc. (excepto T-12 sola)
   5    │ SOF-3  ⚠️
   4    │ Combinaciones ad-hoc
   3    │ B-5  B-8  ⚠️⚠️
   2    │ SI-8  ⚠️⚠️⚠️
   1    │ → Handoff a staff humano
        │
        └─────────────────────────────────────────────────────────
```

---

## Flujo de Decisión Principal

### Diagrama de Flujo ASCII

```
                            ┌─────────────────┐
                            │     INICIO      │
                            │ asignar_mesa()  │
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  VALIDAR INPUT  │
                            │ num_personas,   │
                            │ zona, fecha     │
                            └────────┬────────┘
                                     │
                                     ▼
                          ┌──────────┴──────────┐
                          │   ¿num_personas     │
                          │     válido?         │
                          │  (1-100)            │
                          └──────────┬──────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     │ NO                            │ SÍ
                     ▼                               ▼
            ┌────────────────┐              ┌────────────────┐
            │  ERROR:        │              │  ¿num_personas │
            │  "Cantidad     │              │     > 20?      │
            │   inválida"    │              └────────┬───────┘
            └────────────────┘                       │
                                     ┌───────────────┼───────────────┐
                                     │ SÍ                            │ NO
                                     ▼                               ▼
                            ┌────────────────┐              ┌────────────────┐
                            │   HANDOFF a    │              │  ¿Zona pref    │
                            │   staff humano │              │   = Terraza?   │
                            │   (grupos >20) │              └────────┬───────┘
                            └────────────────┘                       │
                                                     ┌───────────────┼───────────────┐
                                                     │ SÍ                            │ NO
                                                     ▼                               ▼
                                            ┌────────────────┐              ┌────────────────┐
                                            │  EVALUAR CLIMA │              │   BUSCAR EN    │
                                            │  ¿Terraza OK?  │              │   INTERIOR     │
                                            └────────┬───────┘              └────────┬───────┘
                                                     │                               │
                                     ┌───────────────┼───────────────┐               │
                                     │ SÍ                            │ NO            │
                                     ▼                               ▼               │
                            ┌────────────────┐              ┌────────────────┐       │
                            │  BUSCAR EN     │              │  Redirigir a   │       │
                            │  TERRAZA       │              │  Interior      │       │
                            └────────┬───────┘              └────────────────┘       │
                                     │                                               │
                                     └──────────────────────┬────────────────────────┘
                                                            │
                                                            ▼
                                                   ┌────────────────┐
                                                   │  FASE 1:       │
                                                   │  Mesas normales│
                                                   │  (prioridad    │
                                                   │   8-10)        │
                                                   └────────┬───────┘
                                                            │
                                              ┌─────────────┼─────────────┐
                                              │ Encontró                  │ No encontró
                                              ▼                           ▼
                                     ┌────────────────┐          ┌────────────────┐
                                     │  RETORNAR      │          │  FASE 2:       │
                                     │  mesa asignada │          │  Mesas con     │
                                     │  + mensaje OK  │          │  avisos leves  │
                                     └────────────────┘          │  (prioridad    │
                                                                 │   5-7)         │
                                                                 └────────┬───────┘
                                                                          │
                                                            ┌─────────────┼─────────────┐
                                                            │ Encontró                  │ No encontró
                                                            ▼                           ▼
                                                   ┌────────────────┐          ┌────────────────┐
                                                   │  RETORNAR      │          │  FASE 3:       │
                                                   │  mesa + aviso  │          │  Mesas         │
                                                   │  obligatorio   │          │  delicadas     │
                                                   └────────────────┘          │  (prioridad    │
                                                                               │   1-4)         │
                                                                               └────────┬───────┘
                                                                                        │
                                                                          ┌─────────────┼─────────────┐
                                                                          │ Encontró                  │ No encontró
                                                                          ▼                           ▼
                                                                 ┌────────────────┐          ┌────────────────┐
                                                                 │  RETORNAR      │          │  SIN           │
                                                                 │  mesa + aviso  │          │  DISPONIBILIDAD│
                                                                 │  EXPLICACIÓN   │          │  → Alternativas│
                                                                 │  CONFIRMACIÓN  │          │  → Lista espera│
                                                                 └────────────────┘          └────────────────┘
```

---

## Pseudocódigo Detallado

### Función Principal

```python
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass

class Zona(Enum):
    SALA_EXTERIOR = "Sala Exterior"
    SALA_INTERIOR = "Sala Interior"
    SOFAS = "Sofás"
    BARRA = "Barra"
    TERRAZA = "Terraza"

class TipoAviso(Enum):
    NINGUNO = None
    MESA_ALTA = "mesa_alta"
    MESA_PEQUENA = "mesa_pequena"
    JUNTO_BANO = "junto_bano"
    CLIMA = "clima"

@dataclass
class ResultadoAsignacion:
    exito: bool
    mesa_id: Optional[str]
    configuracion_id: Optional[str]
    mensaje_cliente: str
    avisos: List[TipoAviso]
    requiere_confirmacion: bool
    alternativas: Optional[List[Dict]]

def asignar_mesa_optima(
    num_personas: int,
    zona_preferida: Optional[Zona] = None,
    fecha: str = None,
    hora: str = None,
    preferencias: Dict[str, Any] = None
) -> ResultadoAsignacion:
    """
    Función principal de asignación de mesas.
    
    Args:
        num_personas: Número de comensales (1-100)
        zona_preferida: Zona preferida por el cliente
        fecha: Fecha de la reserva (YYYY-MM-DD)
        hora: Hora de la reserva (HH:MM)
        preferencias: Dict con preferencias adicionales
            - mascota: bool
            - sombra: bool
            - terraza_cubierta: bool
            - accesibilidad: bool
    
    Returns:
        ResultadoAsignacion con mesa asignada o alternativas
    """
    
    # ============================================
    # PASO 1: VALIDACIONES INICIALES
    # ============================================
    
    if not validar_num_personas(num_personas):
        return ResultadoAsignacion(
            exito=False,
            mesa_id=None,
            configuracion_id=None,
            mensaje_cliente="Lo siento, el número de personas no es válido.",
            avisos=[],
            requiere_confirmacion=False,
            alternativas=None
        )
    
    # ============================================
    # PASO 2: DERIVAR GRUPOS MUY GRANDES
    # ============================================
    
    if num_personas > 20:
        return derivar_a_staff_humano(
            num_personas=num_personas,
            motivo="grupo_grande",
            mensaje="Para un grupo tan grande necesito coordinar con mi compañera. "
                   "¿Me dejas tu teléfono y te llamamos en 15 minutos?"
        )
    
    # ============================================
    # PASO 3: EVALUAR CLIMA (si terraza)
    # ============================================
    
    if zona_preferida == Zona.TERRAZA:
        evaluacion_clima = evaluar_clima_terraza(fecha, hora)
        
        if not evaluacion_clima["disponible"]:
            # Redirigir a interior
            zona_preferida = None
            mensaje_clima = evaluacion_clima["mensaje"]
        else:
            mensaje_clima = evaluacion_clima.get("mensaje")
    else:
        mensaje_clima = None
    
    # ============================================
    # PASO 4: BUSCAR MESAS POR FASES
    # ============================================
    
    # FASE 1: Mesas normales (prioridad 8-10)
    resultado_fase1 = buscar_fase_1(num_personas, zona_preferida, fecha, hora)
    if resultado_fase1:
        return construir_respuesta_exitosa(resultado_fase1, mensaje_clima)
    
    # FASE 2: Mesas con avisos leves (prioridad 5-7)
    resultado_fase2 = buscar_fase_2(num_personas, zona_preferida, fecha, hora)
    if resultado_fase2:
        return construir_respuesta_con_aviso(resultado_fase2, mensaje_clima)
    
    # FASE 3: Mesas delicadas (prioridad 1-4)
    resultado_fase3 = buscar_fase_3(num_personas, zona_preferida, fecha, hora)
    if resultado_fase3:
        return construir_respuesta_delicada(resultado_fase3, mensaje_clima)
    
    # ============================================
    # PASO 5: SIN DISPONIBILIDAD
    # ============================================
    
    alternativas = generar_alternativas(num_personas, fecha, hora)
    
    return ResultadoAsignacion(
        exito=False,
        mesa_id=None,
        configuracion_id=None,
        mensaje_cliente=f"Lo siento, no tenemos disponibilidad para {num_personas} "
                       f"personas a esa hora. {alternativas['mensaje']}",
        avisos=[],
        requiere_confirmacion=False,
        alternativas=alternativas["opciones"]
    )
```

### Funciones de Búsqueda por Fases

```python
def buscar_fase_1(
    num_personas: int,
    zona_preferida: Optional[Zona],
    fecha: str,
    hora: str
) -> Optional[Dict]:
    """
    FASE 1: Buscar mesas normales (prioridad 8-10)
    
    Orden de búsqueda:
    1. Zona preferida (si existe)
    2. Resto de zonas por prioridad
    
    Criterios dentro de cada zona:
    - Capacidad >= num_personas
    - Capacidad_Maxima >= num_personas (si necesita auxiliar)
    - Minimizar desperdicio (cap - num)
    """
    
    # Obtener mesas disponibles para fecha/hora
    mesas_disponibles = obtener_mesas_disponibles(fecha, hora)
    
    # Filtrar por prioridad 8-10
    mesas_fase1 = [m for m in mesas_disponibles if m.prioridad >= 8]
    
    # Si hay zona preferida, priorizar
    if zona_preferida:
        mesas_zona = [m for m in mesas_fase1 if m.zona == zona_preferida]
        if mesas_zona:
            return seleccionar_mejor_mesa(mesas_zona, num_personas)
    
    # Buscar en todas las zonas
    return seleccionar_mejor_mesa(mesas_fase1, num_personas)


def buscar_fase_2(
    num_personas: int,
    zona_preferida: Optional[Zona],
    fecha: str,
    hora: str
) -> Optional[Dict]:
    """
    FASE 2: Buscar mesas con avisos leves (prioridad 5-7)
    
    Incluye:
    - SOF-1 (prioridad 7)
    - Mesas de terraza individuales (prioridad 6, aviso clima)
    - SOF-3 (prioridad 5, aviso mesa pequeña)
    """
    
    mesas_disponibles = obtener_mesas_disponibles(fecha, hora)
    mesas_fase2 = [m for m in mesas_disponibles if 5 <= m.prioridad <= 7]
    
    if not mesas_fase2:
        return None
    
    mejor_mesa = seleccionar_mejor_mesa(mesas_fase2, num_personas)
    
    if mejor_mesa:
        # Determinar aviso según mesa
        aviso = determinar_aviso_mesa(mejor_mesa)
        mejor_mesa["aviso"] = aviso
    
    return mejor_mesa


def buscar_fase_3(
    num_personas: int,
    zona_preferida: Optional[Zona],
    fecha: str,
    hora: str
) -> Optional[Dict]:
    """
    FASE 3: Buscar mesas delicadas (prioridad 1-4)
    
    Incluye:
    - B-5, B-8 (prioridad 3, aviso mesa alta)
    - SI-8 (prioridad 2, aviso junto a baño)
    
    REQUIERE CONFIRMACIÓN EXPLÍCITA
    """
    
    mesas_disponibles = obtener_mesas_disponibles(fecha, hora)
    mesas_fase3 = [m for m in mesas_disponibles if m.prioridad <= 4]
    
    # Ordenar por prioridad descendente (3 antes que 2)
    mesas_fase3.sort(key=lambda m: m.prioridad, reverse=True)
    
    for mesa in mesas_fase3:
        if mesa.capacidad_maxima >= num_personas:
            mesa["aviso"] = determinar_aviso_mesa(mesa)
            mesa["requiere_confirmacion"] = True
            return mesa
    
    return None
```

### Funciones de Selección

```python
def seleccionar_mejor_mesa(
    mesas: List[Dict],
    num_personas: int
) -> Optional[Dict]:
    """
    Selecciona la mejor mesa minimizando desperdicio.
    
    Criterios de ordenación:
    1. Prioridad descendente (más alta primero)
    2. Desperdicio ascendente (menor desperdicio primero)
    3. No necesita auxiliar > Necesita auxiliar
    """
    
    # Filtrar mesas con capacidad suficiente
    mesas_validas = []
    
    for mesa in mesas:
        if mesa.capacidad >= num_personas:
            # Cabe sin auxiliar
            mesas_validas.append({
                **mesa,
                "necesita_auxiliar": False,
                "desperdicio": mesa.capacidad - num_personas
            })
        elif mesa.capacidad_maxima >= num_personas:
            # Cabe con auxiliar
            mesas_validas.append({
                **mesa,
                "necesita_auxiliar": True,
                "desperdicio": mesa.capacidad_maxima - num_personas
            })
    
    if not mesas_validas:
        return None
    
    # Ordenar por criterios
    mesas_validas.sort(key=lambda m: (
        -m["prioridad"],           # Mayor prioridad primero
        m["necesita_auxiliar"],     # Sin auxiliar primero
        m["desperdicio"]           # Menor desperdicio primero
    ))
    
    return mesas_validas[0]


def determinar_aviso_mesa(mesa: Dict) -> Optional[TipoAviso]:
    """
    Determina el tipo de aviso según la mesa.
    """
    
    codigo = mesa.get("codigo_mesa", "")
    
    if codigo.startswith("B-"):
        return TipoAviso.MESA_ALTA
    
    if codigo == "SI-8":
        return TipoAviso.JUNTO_BANO
    
    if codigo == "SOF-3":
        return TipoAviso.MESA_PEQUENA
    
    if codigo.startswith("T-") and mesa.get("zona") == "Terraza":
        # Aviso de clima solo si hay condiciones especiales
        return TipoAviso.CLIMA
    
    return TipoAviso.NINGUNO
```

### Funciones de Construcción de Respuestas

```python
def construir_respuesta_exitosa(
    mesa: Dict,
    mensaje_clima: Optional[str] = None
) -> ResultadoAsignacion:
    """
    Construye respuesta para asignación exitosa (sin avisos especiales).
    """
    
    nombre_mesa = mesa.get("nombre_display", mesa["codigo_mesa"])
    zona = mesa.get("zona", "")
    capacidad = mesa.get("capacidad")
    
    mensaje = f"¡Perfecto! Te he reservado la {nombre_mesa}"
    
    if zona == "Terraza":
        mensaje += " en la terraza"
    elif zona == "Sala Exterior":
        mensaje += " en la sala exterior"
    elif zona == "Sofás":
        mensaje += " en la zona de sofás"
    
    mensaje += "."
    
    if mesa.get("necesita_auxiliar"):
        mensaje += " Os pondremos una mesita auxiliar para que estéis cómodos."
    
    if mensaje_clima:
        mensaje = mensaje_clima + " " + mensaje
    
    return ResultadoAsignacion(
        exito=True,
        mesa_id=mesa["id"],
        configuracion_id=mesa.get("configuracion_id"),
        mensaje_cliente=mensaje,
        avisos=[],
        requiere_confirmacion=False,
        alternativas=None
    )


def construir_respuesta_con_aviso(
    mesa: Dict,
    mensaje_clima: Optional[str] = None
) -> ResultadoAsignacion:
    """
    Construye respuesta para mesa con aviso leve.
    """
    
    aviso = mesa.get("aviso")
    mensaje_base = construir_respuesta_exitosa(mesa, mensaje_clima).mensaje_cliente
    
    if aviso == TipoAviso.MESA_PEQUENA:
        mensaje_aviso = " Es una mesita más pequeñita, pero muy acogedora."
    else:
        mensaje_aviso = ""
    
    return ResultadoAsignacion(
        exito=True,
        mesa_id=mesa["id"],
        configuracion_id=mesa.get("configuracion_id"),
        mensaje_cliente=mensaje_base + mensaje_aviso,
        avisos=[aviso] if aviso else [],
        requiere_confirmacion=False,
        alternativas=None
    )


def construir_respuesta_delicada(
    mesa: Dict,
    mensaje_clima: Optional[str] = None
) -> ResultadoAsignacion:
    """
    Construye respuesta para mesa delicada (REQUIERE CONFIRMACIÓN).
    """
    
    aviso = mesa.get("aviso")
    
    if aviso == TipoAviso.JUNTO_BANO:
        mensaje = (
            "Ahora mismo solo nos queda una mesita en la sala interior, "
            "pero te aviso que está cerquita de la zona del baño. "
            "¿Os parece bien o preferís esperar a que se libere otra?"
        )
    
    elif aviso == TipoAviso.MESA_ALTA:
        mensaje = (
            "Solo nos quedan mesas altas de barra con banquetas. "
            "¿Os viene bien o preferís esperar a que se libere otra mesa?"
        )
    
    else:
        mensaje = f"Te puedo ofrecer la {mesa['nombre_display']}, ¿os parece bien?"
    
    # Generar alternativas
    alternativas = [
        {"tipo": "lista_espera", "descripcion": "Apuntarte en lista de espera"},
        {"tipo": "horario_alternativo", "descripcion": "Buscar otro horario"}
    ]
    
    return ResultadoAsignacion(
        exito=True,  # Éxito provisional, pendiente confirmación
        mesa_id=mesa["id"],
        configuracion_id=None,
        mensaje_cliente=mensaje,
        avisos=[aviso] if aviso else [],
        requiere_confirmacion=True,
        alternativas=alternativas
    )
```

### Funciones de Configuraciones (Grupos)

```python
def buscar_configuracion_terraza(
    num_personas: int,
    fecha: str,
    hora: str
) -> Optional[Dict]:
    """
    Busca configuración predefinida de terraza para grupos.
    
    REGLA: Para >4 personas en terraza, buscar primero en ConfiguracionesMesas
    """
    
    if num_personas <= 10:
        configs_objetivo = ["T-CONF-1", "T-CONF-3", "T-CONF-4", "T-CONF-6"]
    elif num_personas <= 20:
        configs_objetivo = ["T-CONF-2", "T-CONF-5"]
    else:
        return None  # Derivar a staff
    
    for config_id in configs_objetivo:
        if configuracion_disponible(config_id, fecha, hora):
            return obtener_configuracion(config_id)
    
    return None


def configuracion_disponible(
    config_id: str,
    fecha: str,
    hora: str
) -> bool:
    """
    Verifica que TODAS las mesas de una configuración están disponibles.
    """
    
    config = obtener_configuracion(config_id)
    mesas_incluidas = config.get("mesas_incluidas", [])
    
    for mesa_id in mesas_incluidas:
        if not mesa_disponible(mesa_id, fecha, hora):
            return False
    
    return True


def buscar_combinacion_sofas(
    num_personas: int,
    fecha: str,
    hora: str
) -> Optional[Dict]:
    """
    Busca combinación de sofás para grupos de 7-8 personas.
    
    REGLA: Solo ofrecer combinación si >6 personas
    """
    
    if num_personas <= 6:
        return None  # No necesita combinación
    
    if num_personas <= 8:
        # Buscar SOF-CONF-1 (SOF-1 + SOF-2)
        if configuracion_disponible("SOF-CONF-1", fecha, hora):
            return obtener_configuracion("SOF-CONF-1")
        
        # Buscar SOF-CONF-2 (SOF-3 + SOF-4)
        if configuracion_disponible("SOF-CONF-2", fecha, hora):
            config = obtener_configuracion("SOF-CONF-2")
            config["aviso"] = TipoAviso.MESA_PEQUENA  # SOF-3 es pequeña
            return config
    
    return None
```

---

## Matriz de Casos de Uso

### Casos 1-10: Grupos Pequeños (1-4 personas)

| # | Personas | Zona Pref | Disponibilidad | Mesa Asignada | Aviso | Justificación |
|---|----------|-----------|----------------|---------------|-------|---------------|
| 1 | 2 | Ninguna | Todo disponible | SE-1 (6 pax) | - | Menor desperdicio en zona principal |
| 2 | 2 | Terraza | Todo disponible | T-02 (4 pax) | Clima | Terraza solicitada |
| 3 | 2 | Ninguna | Solo B libre | B-5 (2 pax) | Mesa alta | ⚠️ Confirmación |
| 4 | 2 | Ninguna | Solo SI-8 libre | SI-8 (2 pax) | Junto baño | ⚠️ Confirmación |
| 5 | 3 | Sofás | Todo disponible | SOF-3 (3 pax) | Pequeña | ⚠️ Avisar tamaño |
| 6 | 2 | Sofás | Todo disponible | SOF-1 (2 pax) | - | Capacidad exacta |
| 7 | 4 | Terraza | Solo interior | SE-1 (6 pax) | - | Redirigir a interior |
| 8 | 4 | Interior | Todo disponible | SI-7 (6 pax) | - | Interior solicitado |
| 9 | 4 | Ninguna | SE lleno | SI-6 (6 pax) | - | Siguiente mejor opción |
| 10 | 4 | Ninguna | Todo lleno | - | - | Lista espera/alternativa |

### Casos 11-20: Grupos Medianos (5-10 personas)

| # | Personas | Zona Pref | Disponibilidad | Mesa Asignada | Aviso | Justificación |
|---|----------|-----------|----------------|---------------|-------|---------------|
| 11 | 5 | Ninguna | Todo disponible | SE-1 (6 pax) | - | Desperdicio 1 |
| 12 | 6 | Ninguna | Todo disponible | SE-1 (6 pax) | - | Capacidad exacta |
| 13 | 6 | Terraza | Todo disponible | T-04 (8 pax) | Clima | Terraza individual |
| 14 | 6 | Sofás | Todo disponible | SOF-2 (6 pax) | - | Capacidad exacta |
| 15 | 7 | Sofás | Todo disponible | SOF-CONF-1 (8) | - | Combinación zona 1 |
| 16 | 8 | Ninguna | Todo disponible | SE-2 (8 pax) | - | Capacidad exacta |
| 17 | 8 | Terraza | Todo disponible | T-CONF-1 (10) | Clima | Config predefinida |
| 18 | 8 | Sofás | SOF-1+2 ocupados | SOF-CONF-2 (8) | Pequeña | ⚠️ SOF-3 pequeña |
| 19 | 10 | Ninguna | Todo disponible | SE-2+aux (10) | - | Con auxiliar |
| 20 | 10 | Terraza | Todo disponible | T-CONF-1 (10) | Clima | Config predefinida |

### Casos 21-30: Grupos Grandes (11-20 personas)

| # | Personas | Zona Pref | Disponibilidad | Mesa Asignada | Aviso | Justificación |
|---|----------|-----------|----------------|---------------|-------|---------------|
| 21 | 12 | Ninguna | Todo disponible | T-CONF-2 (18) | Clima | Config grande terraza |
| 22 | 12 | Interior | Todo disponible | SE-2+SE-5 | - | Combinación interior |
| 23 | 15 | Terraza | Todo disponible | T-CONF-2 (18) | Clima | Config grande terraza |
| 24 | 15 | Interior | Sin config | - | - | Handoff staff |
| 25 | 18 | Terraza | Todo disponible | T-CONF-5 (20) | Clima | Config grande terraza |
| 26 | 20 | Terraza | T-CONF-5 ocupado | T-CONF-2 (18) | - | No cabe: alternativa |
| 27 | 20 | Interior | - | - | - | Handoff staff |
| 28 | 15 | Ninguna | Lluvia | Interior combo | - | Redirigir de terraza |
| 29 | 18 | Terraza | Parcial ocupado | - | - | Handoff staff |
| 30 | 20 | Ninguna | Todo disponible | T-CONF-5 (20) | Clima | Mejor opción |

### Casos 31-40: Casos Especiales

| # | Personas | Condición Especial | Mesa Asignada | Aviso | Justificación |
|---|----------|-------------------|---------------|-------|---------------|
| 31 | 2 | Mascota | T-08 o T-16 | Clima | Terraza obligatoria |
| 32 | 4 | Mascota + lluvia | - | - | No disponible (interior no mascotas) |
| 33 | 2 | Accesibilidad | SI-13 (reserva) | - | Mesa adaptada |
| 34 | 4 | Sombra | T-09 o T-02 | Clima | Zona arbolada |
| 35 | 8 | Evento privado | - | - | Handoff staff |
| 36 | 2 | Sin preferencia | SE-1 | - | Algoritmo estándar |
| 37 | 6 | Bebé + trona | SE-4 (amplia) | Trona | Confirmar trona disponible |
| 38 | 4 | Alergia | Cualquiera | - | Marcar en notas |
| 39 | 10 | Cumpleaños | SE-2+aux o T-CONF | - | Notas especiales |
| 40 | 2 | VIP conocido | SE-1 o mejor | - | Prioridad especial |

---

## Casos Edge Exhaustivos

### Edge 1: Mesa Delicada como Única Opción

```
┌─────────────────────────────────────────────────────────────────┐
│ CASO EDGE: SI-8 (Junto Baño) Como Única Opción                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ESCENARIO:                                                      │
│ - 2 personas llegan sin reserva                                 │
│ - Viernes noche 21:30, todo lleno excepto SI-8                 │
│                                                                 │
│ FLUJO:                                                          │
│                                                                 │
│ 1. Sistema busca Fase 1 → No disponible                        │
│ 2. Sistema busca Fase 2 → No disponible                        │
│ 3. Sistema busca Fase 3 → SI-8 disponible                      │
│ 4. Sistema detecta: aviso = JUNTO_BANO                         │
│ 5. Alba comunica:                                               │
│    "Ahora mismo solo nos queda una mesita en la sala           │
│    interior, pero te aviso que está cerquita de la zona        │
│    del baño. ¿Os parece bien o preferís esperar?"              │
│                                                                 │
│ SI ACEPTA:                                                      │
│ → Asignar SI-8                                                  │
│ → Marcar en notas: "Cliente avisado ubicación baño"            │
│                                                                 │
│ SI RECHAZA:                                                     │
│ → Ofrecer lista de espera                                       │
│ → Ofrecer horario alternativo (22:30)                          │
│ → Guardar teléfono para callback                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Edge 2: Todas las Mesas de Barra Ocupadas + 2 Personas

```
┌─────────────────────────────────────────────────────────────────┐
│ CASO EDGE: Pareja y Solo Mesas Grandes Disponibles              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ESCENARIO:                                                      │
│ - 2 personas                                                    │
│ - Disponible: SE-2 (8 pax), SI-6 (8 pax), T-04 (10 pax)       │
│ - Desperdicio mínimo: 6 plazas                                 │
│                                                                 │
│ DECISIÓN DEL NEGOCIO:                                           │
│                                                                 │
│ Opción A: Permitir con desperdicio                              │
│ → Asignar SE-2 (menor desperdicio)                             │
│ → Nota interna: "Mesa grande para 2 - viernes noche"           │
│                                                                 │
│ Opción B: Sugerir espera                                        │
│ → "Ahora tenemos mesas más grandecitas. ¿Os importa            │
│    esperar 15 minutos a ver si se libera una más íntima?"      │
│                                                                 │
│ CONFIGURACIÓN RECOMENDADA:                                      │
│ → Permitir si es horario valle (martes mediodía)               │
│ → Sugerir espera si es horario pico (viernes noche)            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Edge 3: Configuración Terraza Parcialmente Ocupada

```
┌─────────────────────────────────────────────────────────────────┐
│ CASO EDGE: T-CONF-2 Parcialmente Ocupada                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ESCENARIO:                                                      │
│ - 15 personas piden terraza                                     │
│ - T-CONF-2 (T-11+T-12+T-13) necesaria                          │
│ - T-11 y T-13 libres, T-12 OCUPADA                             │
│                                                                 │
│ FLUJO:                                                          │
│                                                                 │
│ 1. configuracion_disponible("T-CONF-2") → FALSE                │
│    (T-12 está ocupada)                                         │
│                                                                 │
│ 2. Buscar alternativas:                                         │
│    - T-CONF-5 (T-04+T-05) → Verificar disponibilidad           │
│    - Si disponible → Ofrecer                                    │
│                                                                 │
│ 3. Si ninguna configuración predefinida:                        │
│    - ¿Es posible combinación ad-hoc?                           │
│      T-11 (8) + T-13 (8) = 16 pax ✓                           │
│    - PERO: requiere validación staff (no es predefinida)       │
│                                                                 │
│ 4. Alba comunica:                                               │
│    "Para 15 personas en terraza necesito consultar con         │
│    mi compañera cómo organizamos las mesas. ¿Me dejas          │
│    tu teléfono y te confirmo en 10 minutos?"                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Edge 4: Mascota + Lluvia

```
┌─────────────────────────────────────────────────────────────────┐
│ CASO EDGE: Mascota + Condiciones de Lluvia                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ESCENARIO:                                                      │
│ - 4 personas con perro                                          │
│ - Lluvia moderada, terraza no disponible                       │
│ - Interior NO permite mascotas                                  │
│                                                                 │
│ CONFLICTO:                                                      │
│ - Mascota → Solo terraza                                        │
│ - Lluvia → Solo interior                                        │
│ - INCOMPATIBLE                                                  │
│                                                                 │
│ FLUJO:                                                          │
│                                                                 │
│ 1. evaluar_clima() → terraza_no_disponible                     │
│ 2. preferencias.mascota = True                                  │
│ 3. Detectar conflicto                                           │
│                                                                 │
│ 4. Alba comunica:                                               │
│    "Hoy con esta lluvia no podemos usar la terraza,            │
│    y en el interior no podemos tener perritos.                 │
│    ¿Queréis que os apunte para mañana si hace mejor            │
│    tiempo, o podéis dejar al peque en casa?"                   │
│                                                                 │
│ ALTERNATIVAS:                                                   │
│ A) Reservar para otro día                                       │
│ B) Venir sin mascota                                            │
│ C) Lista de espera por si para de llover                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Edge 5: Auxiliares Agotadas

```
┌─────────────────────────────────────────────────────────────────┐
│ CASO EDGE: Necesita Auxiliar pero Todas Ocupadas                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ESCENARIO:                                                      │
│ - 10 personas                                                   │
│ - SE-2 disponible (cap base 8, máx 10 con auxiliar)            │
│ - Las 4 mesas auxiliares ya están en uso                       │
│                                                                 │
│ FLUJO:                                                          │
│                                                                 │
│ 1. seleccionar_mejor_mesa() → SE-2 candidata                   │
│2. verificar_auxiliares() → 0 disponibles                      │
│ 3. SE-2 cap efectiva = 8 (sin auxiliar)                        │
│ 4. 8 < 10 → No cabe                                            │
│                                                                 │
│ 5. Buscar alternativas:                                         │
│    - T-CONF-1 (10 pax sin auxiliar) → Ofrecer terraza          │
│    - Esperar a que se libere auxiliar                          │
│                                                                 │
│ 6. Alba comunica:                                               │
│    "Para 10 personas necesitamos añadir una mesita extra,      │
│    pero ahora mismo están todas ocupadas. Os puedo ofrecer     │
│    la terraza donde tenemos una configuración perfecta         │
│    para 10, o si preferís interior podéis esperar unos         │
│    20 minutos a que se libere una auxiliar."                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Validaciones y Restricciones

### Validaciones de Input

```python
def validar_num_personas(num: int) -> bool:
    """
    Valida número de personas.
    
    Reglas:
    - Mínimo: 1
    - Máximo automatizado: 20
    - Máximo con handoff: 100 (eventos privados)
    """
    return 1 <= num <= 100


def validar_fecha(fecha: str) -> bool:
    """
    Valida fecha de reserva.
    
    Reglas:
    - Formato: YYYY-MM-DD
    - No puede ser pasado (excepto hoy)
    - Máximo: 60 días en el futuro
    """
    from datetime import datetime, timedelta
    
    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    except ValueError:
        return False
    
    hoy = datetime.now().date()
    max_fecha = hoy + timedelta(days=60)
    
    return hoy <= fecha_obj <= max_fecha


def validar_hora(hora: str, fecha: str) -> Dict:
    """
    Valida hora de reserva contra horarios del restaurante.
    
    Horarios:
    - Martes-Viernes: 13:00-17:00, 20:00-23:00
    - Sábado: 13:00-17:00, 20:00-00:00
    - Domingo: 13:00-17:00, 20:00-23:00
    - Lunes: CERRADO (excepto festivos)
    """
    from datetime import datetime
    
    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
    dia_semana = fecha_obj.weekday()  # 0=Lunes, 6=Domingo
    
    if dia_semana == 0 and not es_festivo(fecha):
        return {
            "valido": False,
            "error": "Los lunes estamos cerrados. ¿Qué te parece el martes?"
        }
    
    hora_obj = datetime.strptime(hora, "%H:%M").time()
    
    # Verificar turno comidas
    if datetime.strptime("13:00", "%H:%M").time() <= hora_obj <= datetime.strptime("17:00", "%H:%M").time():
        return {"valido": True, "turno": "comidas"}
    
    # Verificar turno cenas
    hora_cierre = "00:00" if dia_semana == 5 else "23:00"
    if datetime.strptime("20:00", "%H:%M").time() <= hora_obj <= datetime.strptime(hora_cierre, "%H:%M").time():
        return {"valido": True, "turno": "cenas"}
    
    return {
        "valido": False,
        "error": "A esa hora no estamos abiertos. Servimos comidas de 13:00 a 17:00 y cenas de 20:00 a 23:00."
    }
```

### Restricciones de Negocio

```python
# Configuración de restricciones
RESTRICCIONES = {
    "max_personas_auto": 20,          # Handoff si > 20
    "max_desperdicio_permitido": 6,   # Alerta si desperdicio > 6
    "dias_max_reserva_anticipada": 60,
    "mesas_delicadas": ["SI-8", "B-5", "B-8"],
    "mesas_con_aviso": ["SOF-3"],
    "mascotas_permitido": ["Terraza"],
    "accesibilidad_mesas": ["SI-13"],  # ⚠️ Verificar código real
}

# Combinaciones NO válidas
COMBINACIONES_PROHIBIDAS = [
    # No juntar mesas de diferentes zonas
    ("SE-*", "SI-*"),
    ("SOF-*", "BAR-*"),
    # No crear configuraciones ad-hoc en terraza > 20 pax
    ("T-*", "T-*", "T-*", "T-*"),  # Máx 3 mesas ad-hoc
]
```

---

## Mensajes de Respuesta

### Plantillas de Mensajes

```python
MENSAJES = {
    # Éxito
    "asignacion_exitosa": """
        ¡Perfecto! Te he reservado la {mesa} {ubicacion} para {personas} personas
        {fecha_hora}. Te voy a mandar un WhatsApp para que confirmes.
        {nota_adicional}
    """,
    
    # Avisos
    "aviso_mesa_alta": """
        Solo nos quedan mesas altas de barra con banquetas.
        ¿Os viene bien o preferís esperar a que se libere otra mesa?
    """,
    
    "aviso_junto_bano": """
        Ahora mismo solo nos queda una mesita en la sala interior,
        pero te aviso que está cerquita de la zona del baño.
        ¿Os parece bien o preferís esperar?
    """,
    
    "aviso_mesa_pequena": """
        Es una mesita más pequeñita, pero muy acogedora.
        ¿Os parece bien?
    """,
    
    # Sin disponibilidad
    "sin_disponibilidad": """
        Lo siento, para {personas} personas a esa hora no tenemos disponibilidad.
        {alternativas}
    """,
    
    "alternativas_horario": """
        Tenemos hueco a las {hora_anterior} o a las {hora_posterior}.
        ¿Te viene bien alguno de esos horarios?
    """,
    
    "alternativas_lista_espera": """
        ¿Te apunto en lista de espera? Si hay alguna cancelación te aviso.
    """,
    
    # Handoff
    "handoff_grupo_grande": """
        Para un grupo tan grande necesito coordinar con mi compañera.
        ¿Me dejas tu teléfono y te llamamos en 15 minutos?
    """,
    
    # Clima
    "clima_lluvia": """
        Hoy con esta lluvia la terraza está cerrada.
        ¿Te pongo en el interior?
    """,
    
    "clima_frio": """
        Hoy hace fresquito en terraza.
        ¿Preferís dentro o tenéis abrigo?
    """,
}
```

---

## Notas de Implementación

### Archivos a Crear/Modificar

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `src/services/booking_engine.py` | MODIFICAR | Implementar algoritmo completo |
| `src/domain/rules/priority_rules.py` | CREAR | Reglas de prioridad |
| `src/domain/rules/capacity_rules.py` | CREAR | Reglas de capacidad |
| `src/domain/rules/notification_rules.py` | CREAR | Reglas de avisos |
| `src/infrastructure/airtable/mesas_repository.py` | CREAR | CRUD Mesas |
| `src/infrastructure/airtable/config_repository.py` | CREAR | CRUD Configuraciones |
| `tests/unit/test_booking_engine.py` | MODIFICAR | Tests del algoritmo |

### Tests Requeridos

```python
# tests/unit/test_booking_engine.py

import pytest
from src.services.booking_engine import asignar_mesa_optima

class TestAsignacionBasica:
    """Tests básicos de asignación"""
    
    def test_2_personas_sin_preferencia(self):
        resultado = asignar_mesa_optima(2)
        assert resultado.exito
        assert resultado.mesa_id is not None
        assert not resultado.requiere_confirmacion
    
    def test_20_personas_requiere_handoff(self):
        resultado = asignar_mesa_optima(25)
        assert not resultado.exito
        assert "coordinar" in resultado.mensaje_cliente.lower()
    
    def test_mesa_delicada_requiere_confirmacion(self):
        # Simular que solo SI-8 está disponible
        resultado = asignar_mesa_optima(2, mesas_disponibles=["SI-8"])
        assert resultado.requiere_confirmacion
        assert "baño" in resultado.mensaje_cliente.lower()

class TestPreferencias:
    """Tests de preferencias de zona"""
    
    def test_preferencia_terraza_respetada(self):
        resultado = asignar_mesa_optima(4, zona_preferida="Terraza")
        assert "T-" in resultado.mesa_id or "terraza" in resultado.mensaje_cliente.lower()
    
    def test_preferencia_interior_respetada(self):
        resultado = asignar_mesa_optima(4, zona_preferida="Sala Interior")
        assert "SI-" in resultado.mesa_id or "interior" in resultado.mensaje_cliente.lower()

class TestAvisos:
    """Tests de avisos obligatorios"""
    
    def test_aviso_mesa_alta_barra(self):
        resultado = asignar_mesa_optima(2, forzar_mesa="B-5")
        assert TipoAviso.MESA_ALTA in resultado.avisos
        assert "alta" in resultado.mensaje_cliente.lower()
    
    def test_aviso_junto_bano_si8(self):
        resultado = asignar_mesa_optima(2, forzar_mesa="SI-8")
        assert TipoAviso.JUNTO_BANO in resultado.avisos
        assert "baño" in resultado.mensaje_cliente.lower()
```

---

*Documento generado: 2026-03-09*  
*Versión: 1.0.0*  
*Estado: Listo para implementación*
