# Investigación Profunda: Sistemas Óptimos de Asignación de Mesas en Restaurantes

> **Fecha**: 12 febrero 2026  
> **Propósito**: Investigación exhaustiva de algoritmos, metodologías y sistemas de la industria para implementar asignación inteligente de mesas en Restaurante Verdent  
> **Contexto**: Sistema profesional de reservas con fase de pruebas humanas antes de producción

---

## 📚 RESUMEN EJECUTIVO

Basado en investigación académica y análisis de plataformas líderes de la industria (OpenTable, Resy, SevenRooms), este documento presenta:

1. **Estado del arte** en optimización de mesas 2026
2. **Algoritmos probados** en investigación académica
3. **Arquitectura de sistema** adaptada a Verdent
4. **Plan de implementación** con fase de pruebas humanas
5. **Métricas de éxito** y feedback loops

---

## 🔬 INVESTIGACIÓN: ESTADO DEL ARTE 2026

### Tendencias Actuales en la Industria

**Impacto de IA en Optimización de Mesas:**
- Mejora de 15-20% en rotación de mesas ([CheckLess 2026](https://checkless.io/blog/restaurant-table-turnover-optimization-2026))
- Predicción de no-shows con modelos de ML
- Maximización de utilización del espacio
- Sistemas que rastrean preferencias de huéspedes

**Ganancia de Revenue vs FCFS (First-Come-First-Served):**
- Baja demanda: 0.11% - 2.22% mejora
- Demanda media: 0.16% - 2.96% mejora
- **Alta demanda: 7.65% - 13.13% mejora** ([Claremont 2024](https://scholarship.claremont.edu/cgi/viewcontent.cgi?article=1022&context=hmc_theses))

**Oportunidad más grande:**
- **15-17 minutos por mesa** es el factor de optimización principal
- Seguimiento de tiempo real vs estimado ([CheckLess 2026](https://checkless.io/blog/restaurant-table-turnover-optimization-2026))

### Plataformas Líderes de la Industria

#### SevenRooms (Líder en IA)
- **Algoritmo AI-driven**: Evalúa +10,000 combinaciones por segundo ([Hostie AI 2025](https://www.hostie.ai/resources/ai-reservation-integrations-opentable-resy-sevenrooms-2025-comparison))
- CRM integrado + marketing + operaciones
- Waitlists predictivas con tracking en tiempo real
- Enfoque: experiencia del huésped

#### OpenTable
- API comprehensiva para integración
- Mayor red de comensales
- Enfoque: descubrimiento + reservas

#### Resy
- Seguridad anti-bot robusta
- Integraciones selectivas pero seguras
- Enfoque: restaurantes premium

**Conclusión**: SevenRooms es el benchmark para algoritmos de asignación inteligente de mesas.

---

## 🧮 ALGORITMOS Y METODOLOGÍAS ACADÉMICAS

### 1. Constraint Satisfaction Problem (CSP)

**Definición ([Vidotto PhD, U Toronto](https://tidel.mie.utoronto.ca/pubs/Theses/vidotto.phd.pdf)):**
- Modelar gestión de mesas como problema de scheduling
- Tablas = recursos, reservas = tareas
- Cada reserva tiene inicio, fin, tamaño
- Asignación debe cumplir: capacidad suficiente + no overlap

**Complejidad:**
- Problema NP-completo aunque horarios son fijos ([SpringerLink 2007](https://link.springer.com/chapter/10.1007/978-1-84628-666-7_1))
- Online constrained combinatorial optimization
- Clientes son impredecibles: llegan tarde, no llegan, cambian tamaño

**Soluciones CSP:**
- Modelado con restricciones
- Genera planes flexibles
- Mantiene estabilidad cuando ocurren cambios
- Sistemas implementados que asesoran en tiempo real

### 2. Mixed Integer Programming (MIP)

**Modelo MIP ([SciELO Brazil 2018](https://www.scielo.br/j/pope/a/bkBQnG3YtpX37nKYSzpKhvP/)):**
- Asignación de reservas a mesas considerando combinaciones
- Política de reservas evalúa valores de mesas periódicamente
- Algoritmo MIP para decisiones óptimas

**Programación Dinámica:**
- Decide dinámicamente cuándo sentar un partido entrante
- Integer programming + stochastic programming + approximate dynamic programming
- Método híbrido para día de operación ([Claremont 2024](https://scholarship.claremont.edu/cgi/viewcontent.cgi?article=1022&context=hmc_theses))

### 3. Bin Packing Algorithms

**Concepto ([Wikipedia](https://en.wikipedia.org/wiki/Bin_packing_problem)):**
- Items de diferentes tamaños → bins de capacidad fija
- Minimizar número de bins usados
- Analogía: grupos de comensales → mesas

**Algoritmos Clave:**

**First-Fit (FF):**
- Colocar cada item en el primer bin donde quepa
- Rápido pero no óptimo
- O(n) complejidad

**First-Fit Decreasing (FFD):**
- Ordenar items por tamaño descendente primero
- Aplicar First-Fit
- Mucho más efectivo que FF
- Aproximación: 11/9 OPT + 6/9

**Best-Fit Decreasing (BFD):**
- Ordenar items descendente
- Colocar en bin con menor espacio restante
- Similar a FFD en performance

**Dynamic Bin Packing ([Liverpool 2014](https://livrepository.liverpool.ac.uk/2005382/1/BurceaMih_Oct2014_2002421.pdf)):**
- Items pueden llegar y partir en tiempos arbitrarios
- Minimiza máximo número de bins jamás usado
- Aplicable a terraza con mesas que se juntan/separan dinámicamente

**Karmarkar-Karp (KK):**
- Solución de alta calidad
- Tiempo polinomial
- Diferencing method

### 4. Reinforcement Learning (RL) para Feedback Loops

**Aplicaciones en Restaurantes:**

**Optimización de Flujo de Clientes ([AIS Electronic Library 2024](https://aisel.aisnet.org/icis2024/data_soc/data_soc/9/)):**
- Modelo de predicción de flujo con deep learning ligero
- Deep Reinforcement Learning (DRL) para asignación dinámica
- Condiciones del restaurante en tiempo real

**Feedback Loops Operacionales ([Lilac Labs](https://www.lilaclabs.ai/blog/build-feedback-system-improves-restaurant-operations)):**
- Datos de kitchen display → loop diario
- Managers revisan bottlenecks
- Ajustan staffing o responsabilidades de estación
- **Aplicable**: Feedback diario sobre decisiones de mesas

**Meal Delivery con RL ([arXiv 2104.12000](https://arxiv.org/abs/2104.12000)):**
- Markov Decision Process (MDP)
- Deep RL para decisiones secuenciales
- Maximiza profit mientras reduce delays
- **Adaptable**: Decisiones secuenciales de asignación de mesas

---

## 🏗️ ARQUITECTURA PROPUESTA PARA VERDENT

### Sistema Tri-Nivel (Inspirado en ClawBot/OpenClaw)

```
┌──────────────────────────────────────────────────────┐
│  L1: TIEMPO REAL (Redis + FastAPI)                  │
│  - Estado ocupación actual                          │
│  - Decisiones del servicio en curso                 │
│  - Clima/condiciones del momento                    │
│  - TTL: 24 horas                                     │
└──────────────────────────────────────────────────────┘
                        ↓ Consolidación diaria
┌──────────────────────────────────────────────────────┐
│  L2: APRENDIZAJE (NotebookLM + MCP Memory)          │
│  - Patrones semanales/mensuales                     │
│  - Configuraciones exitosas                         │
│  - Decisiones fallidas (learning)                   │
│  - Reglas heurísticas aprendidas                    │
│  - TTL: 6-12 meses                                   │
└──────────────────────────────────────────────────────┘
                        ↓ Refinamiento mensual
┌──────────────────────────────────────────────────────┐
│  L3: INFRAESTRUCTURA (Airtable)                     │
│  - Configuración física inmutable                   │
│  - Restricciones espaciales (árboles, bancos)       │
│  - Combinaciones válidas de mesas                   │
│  - Capacidades base                                  │
│  - TTL: ∞ (hasta cambio físico)                     │
└──────────────────────────────────────────────────────┘
```

### Algoritmo Híbrido "Tetris Inteligente 2.0"

**Inspiración:**
- SevenRooms: 10,000 combinaciones/segundo
- Constraint Satisfaction: Restricciones duras + blandas
- Bin Packing FFD: Ordenar por tamaño
- RL: Aprendizaje continuo de feedback

**Pipeline de Decisión:**

```python
async def asignar_mesa_inteligente(reserva: Booking) -> TableAssignment:
    """
    Algoritmo híbrido inspirado en SevenRooms + investigación académica
    """
    
    # FASE 1: CARGAR CONTEXTO (Tri-Level Memory)
    contexto = await obtener_contexto_completo(reserva)
    # - L3: Restricciones físicas (Airtable)
    # - L2: Patrones aprendidos (NotebookLM/Memory)
    # - L1: Estado actual (Redis)
    
    # FASE 2: GENERAR CANDIDATOS (CSP + Bin Packing)
    candidatos = await generar_candidatos_csp(reserva, contexto)
    # - Aplicar restricciones duras (capacidad, disponibilidad)
    # - Generar combinaciones válidas (FFD approach)
    # - Filtrar por restricciones espaciales (terraza)
    # - Incluir configuraciones L2 exitosas
    
    # FASE 3: SCORING MULTI-CRITERIO (Weighted Sum)
    scored_options = []
    for candidato in candidatos:
        score = calcular_score_multicriterio(
            candidato, 
            reserva, 
            contexto,
            weights={
                'fit_capacidad': 0.35,      # Minimizar desperdicio
                'experiencia_historica': 0.25,  # Satisfacción pasada
                'preferencias_cliente': 0.20,   # Indoor vs outdoor
                'facilidad_setup': 0.10,     # Tiempo configurar
                'impacto_futuro': 0.10,      # No bloquear después
            }
        )
        scored_options.append((candidato, score))
    
    # FASE 4: SELECCIONAR ÓPTIMO (Top-1 o Monte Carlo si empate)
    mejor_opcion = max(scored_options, key=lambda x: x[1])
    
    # FASE 5: ASIGNAR Y REGISTRAR PARA APRENDIZAJE
    assignment = await ejecutar_asignacion(mejor_opcion[0])
    await registrar_decision_L1(assignment, reserva, contexto)  # Redis
    await crear_observacion_L2(assignment, reserva, score)      # MCP Memory
    
    # FASE 6: PROGRAMAR FEEDBACK POST-SERVICIO
    await schedule_feedback_collection(
        assignment.id, 
        delay_minutes=reserva.duracion_estimada + 15
    )
    
    return assignment


def calcular_score_multicriterio(
    candidato: TableConfiguration,
    reserva: Booking,
    contexto: CompleteContext,
    weights: Dict[str, float]
) -> float:
    """
    Scoring similar a SevenRooms pero adaptado a Verdent
    """
    scores = {}
    
    # 1. FIT DE CAPACIDAD (35%)
    capacidad_mesa = candidato.capacidad_total
    personas = reserva.numero_personas
    if personas == capacidad_mesa:
        scores['fit_capacidad'] = 1.0  # Perfect fit
    elif personas < capacidad_mesa:
        # Penalizar desperdicio: (personas / capacidad)^2
        scores['fit_capacidad'] = (personas / capacidad_mesa) ** 2
    else:
        scores['fit_capacidad'] = 0.0  # No cabe
    
    # 2. EXPERIENCIA HISTÓRICA (25%)
    # Buscar en L2: ¿Esta configuración funcionó bien antes?
    historico = contexto.l2_memory.get_satisfaction_rating(
        configuracion=candidato.id,
        zona=candidato.zona,
        similar_size=personas
    )
    scores['experiencia_historica'] = historico.avg_rating / 5.0
    
    # 3. PREFERENCIAS CLIENTE (20%)
    if reserva.preferencias.zona_preferida == candidato.zona:
        scores['preferencias_cliente'] = 1.0
    elif reserva.preferencias.zona_preferida is None:
        # Sin preferencia: usar patrón aprendido de similar perfil
        patron = contexto.l2_memory.get_zona_preference_pattern(
            hora=reserva.hora,
            dia_semana=reserva.fecha.weekday(),
            tamano_grupo=personas
        )
        scores['preferencias_cliente'] = patron.probability(candidato.zona)
    else:
        scores['preferencias_cliente'] = 0.3  # Penalización pero no descalifica
    
    # 4. FACILIDAD DE SETUP (10%)
    if candidato.requiere_juntar_mesas:
        tiempo_setup = candidato.minutos_setup
        # Normalizar: 0 min = 1.0, 10 min = 0.0
        scores['facilidad_setup'] = max(0, 1 - (tiempo_setup / 10))
    else:
        scores['facilidad_setup'] = 1.0
    
    # 5. IMPACTO EN FUTURAS RESERVAS (10%)
    # ¿Esta asignación bloquea buenas opciones para reservas posteriores?
    proximas_reservas = contexto.l1_redis.get_next_bookings(
        after=reserva.hora_fin,
        hours=2
    )
    if proximas_reservas:
        # Simular: ¿Cuántas opciones quedan después de esta asignación?
        opciones_despues = simular_disponibilidad_post_asignacion(
            candidato, proximas_reservas, contexto
        )
        # Más opciones = mejor score
        scores['impacto_futuro'] = min(1.0, opciones_despues / 5)
    else:
        scores['impacto_futuro'] = 1.0  # Sin impacto
    
    # WEIGHTED SUM
    score_final = sum(scores[k] * weights[k] for k in scores)
    return score_final


async def generar_candidatos_csp(
    reserva: Booking,
    contexto: CompleteContext
) -> List[TableConfiguration]:
    """
    Genera candidatos usando CSP + FFD (First-Fit Decreasing)
    """
    candidatos = []
    personas = reserva.numero_personas
    
    # RESTRICCIÓN DURA 1: Disponibilidad temporal
    mesas_disponibles = await contexto.l1_redis.get_available_tables(
        inicio=reserva.hora_inicio,
        fin=reserva.hora_fin
    )
    
    # RESTRICCIÓN DURA 2: Zona (si terraza, verificar clima)
    if contexto.weather.is_raining or contexto.weather.wind_speed > 40:
        # Bloquear terraza
        mesas_disponibles = [m for m in mesas_disponibles if m.zona != 'terraza']
    
    # RESTRICCIÓN DURA 3: Capacidad física desde L3
    restricciones_fisicas = contexto.l3_airtable.get_spatial_constraints(
        mesas=mesas_disponibles
    )
    
    # ESTRATEGIA 1: MATCH EXACTO (Best-Fit)
    for mesa in mesas_disponibles:
        if mesa.capacidad == personas:
            candidatos.append(TableConfiguration(
                mesas=[mesa],
                capacidad_total=mesa.capacidad,
                requiere_juntar=False,
                minutos_setup=0
            ))
    
    # ESTRATEGIA 2: MESA MÁS GRANDE (con penalización por desperdicio)
    for mesa in mesas_disponibles:
        if mesa.capacidad > personas and mesa.capacidad <= personas + 2:
            candidatos.append(TableConfiguration(
                mesas=[mesa],
                capacidad_total=mesa.capacidad,
                requiere_juntar=False,
                minutos_setup=0
            ))
    
    # ESTRATEGIA 3: COMBINACIONES APRENDIDAS (L2)
    combos_exitosas = contexto.l2_memory.get_successful_combinations(
        personas=personas,
        zona=reserva.zona_preferida
    )
    for combo in combos_exitosas:
        if all(m in mesas_disponibles for m in combo.mesas):
            if combo.es_fisicamente_valida(restricciones_fisicas):
                candidatos.append(combo)
    
    # ESTRATEGIA 4: COMBINACIONES NUEVAS (FFD - Exploration)
    # Ordenar mesas por capacidad descendente
    mesas_sorted = sorted(mesas_disponibles, key=lambda m: m.capacidad, reverse=True)
    
    # Generar combinaciones de 2 mesas (limit: 100 combinaciones)
    from itertools import combinations
    for m1, m2 in combinations(mesas_sorted[:10], 2):
        if m1.capacidad + m2.capacidad >= personas:
            if m1.capacidad + m2.capacidad <= personas + 2:  # No desperdiciar mucho
                # Verificar si son juntables (L3)
                if restricciones_fisicas.son_juntables(m1, m2):
                    candidatos.append(TableConfiguration(
                        mesas=[m1, m2],
                        capacidad_total=m1.capacidad + m2.capacidad,
                        requiere_juntar=True,
                        minutos_setup=contexto.l2_memory.get_avg_setup_time(m1, m2)
                    ))
    
    # Si no hay candidatos, considerar barra (overflow)
    if not candidatos and personas <= 3:
        mesas_barra = [m for m in mesas_disponibles if m.zona == 'barra']
        candidatos.extend([
            TableConfiguration([m], m.capacidad, False, 0) 
            for m in mesas_barra
        ])
    
    return candidatos
```

---

## 📊 COMPARATIVA DE ENFOQUES

| Enfoque | Ventajas | Desventajas | Aplicabilidad Verdent |
|---------|----------|-------------|----------------------|
| **FCFS (First-Come-First-Served)** | Simple, intuitivo | Desperdicia capacidad, no optimiza revenue | ❌ No usar - status quo |
| **CSP Puro** | Garantiza restricciones duras | Lento para decisiones en tiempo real | ⚠️ Usar solo para validación |
| **MIP Puro** | Óptimo matemáticamente | Requiere conocer todas las reservas del día | ⚠️ Solo para análisis offline |
| **Bin Packing FFD** | Rápido, buena aproximación | No considera preferencias, experiencia | ✅ Componente de generación |
| **Scoring Multi-Criterio** | Balancea múltiples objetivos | Requiere tuning de pesos | ✅ Core del sistema |
| **RL con Feedback** | Aprende de experiencia real | Requiere datos históricos | ✅ Fase 2 post-humano |

**Decisión: Algoritmo Híbrido**
- **Base**: CSP para restricciones + FFD para candidatos
- **Optimización**: Scoring multi-criterio
- **Mejora continua**: RL con feedback loops humanos

---

## 🧪 PLAN DE IMPLEMENTACIÓN CON FASE DE PRUEBAS HUMANAS

### FASE 0: PREPARACIÓN (Semanas 1-2)

**Objetivos:**
- Implementar infraestructura L3 (Airtable)
- Documentar configuraciones físicas reales
- Setup de monitoring y logging

**Tareas:**

1. **Migración Completa a Airtable**
   - Tabla `MESAS_FISICAS`: 35 posiciones reales
   - Tabla `RESTRICCIONES_FISICAS`: Árboles, bancos, combinaciones imposibles
   - Tabla `CONFIGURACIONES_VALIDAS`: Combos pre-aprobados (T1+T2, etc.)
   - Tabla `ZONAS`: Metadata (barra, terraza, sala)

2. **Mapeo de Terraza Real**
   - **Workshop con staff (2 horas)**:
     - Imprimir plano de terraza
     - Marcar qué mesas se pueden juntar
     - Identificar obstáculos fijos (árboles = T5+T6 no juntables)
     - Definir configuraciones por clima (lluvia, viento, sol)
   - Documentar en Airtable

3. **Sistema de Logging Detallado**
   - Cada decisión de asignación → log estructurado
   - Capturar: reserva, mesas candidatas, scores, decisión final
   - Preparar para análisis posterior

**Entregable**: Airtable poblado con configuración real + logging ready

---

### FASE 1: ALGORITMO BASE SIN ML (Semanas 3-4)

**Objetivos:**
- Implementar algoritmo híbrido con heurísticas fijas
- Sin machine learning todavía
- Weights manuales basados en mejores prácticas

**Implementación:**

```python
# src/application/services/intelligent_table_assignment.py

class IntelligentTableAssignmentService:
    """
    Versión 1.0: Algoritmo híbrido sin ML
    - CSP para restricciones
    - FFD para candidatos
    - Scoring multi-criterio con weights fijos
    """
    
    def __init__(self):
        self.weights = {
            'fit_capacidad': 0.35,
            'experiencia_historica': 0.25,  # Inicialmente usa defaults
            'preferencias_cliente': 0.20,
            'facilidad_setup': 0.10,
            'impacto_futuro': 0.10,
        }
        self.table_repo = TableRepository()
        self.redis = get_redis_client()
    
    async def assign_table(self, booking: Booking) -> TableAssignment:
        # Implementar pipeline completo descrito arriba
        pass
```

**Testing Interno:**
- Casos de prueba con 50 reservas simuladas
- Verificar que genera candidatos válidos
- Verificar que scoring funciona
- Performance: <200ms por asignación

**Entregable**: Algoritmo funcional en staging, listo para pruebas humanas

---

### FASE 2: OPERACIÓN PARALELA CON HUMANOS (Semanas 5-8) 🔥

**Objetivo Principal:**
> Operar sistema en paralelo con Agora, recopilar feedback real, sin afectar operaciones

**Setup del Experimento:**

```
┌─────────────────────────────────────────────────────┐
│           RESERVA ENTRANTE                          │
└─────────────────────────────────────────────────────┘
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
┌──────────────────┐      ┌──────────────────┐
│   AGORA (Real)   │      │ Verdent AI (Test)│
│  Decisión humana │      │ Decisión algoritmo│
└──────────────────┘      └──────────────────┘
        ↓                           ↓
┌──────────────────┐      ┌──────────────────┐
│ Mesa asignada    │      │ Sugerencia AI    │
│ por host         │      │ (solo registrada)│
└──────────────────┘      └──────────────────┘
        ↓                           ↓
        └─────────────┬─────────────┘
                      ↓
        ┌─────────────────────────────────┐
        │   COMPARACIÓN + FEEDBACK        │
        │                                 │
        │ 1. ¿AI sugirió igual que humano?│
        │ 2. Si diferente, ¿cuál mejor?   │
        │ 3. ¿Cliente satisfecho al final?│
        └─────────────────────────────────┘
```

**Protocolo Operacional:**

1. **Registro de Decisiones**
   - Host usa Agora normalmente (sistema actual)
   - En paralelo, Verdent AI genera sugerencia (invisible para cliente)
   - Ambas decisiones se registran con timestamp

2. **Interface para Host (Tablet/Dashboard)**
   - Pantalla muestra: "AI sugiere: T3 (90% confidence)"
   - Host puede:
     - ✅ Aceptar sugerencia AI (1 tap)
     - ❌ Ignorar y usar su criterio
     - 💬 Comentar por qué rechaza

3. **Captura de Feedback Post-Servicio**
   - Al finalizar servicio (mesa liberada):
   - Host califica experiencia: ⭐⭐⭐⭐⭐
   - Preguntas rápidas (30 segundos):
     - ¿Grupo estaba cómodo en mesa asignada? (Sí/No)
     - ¿Hubo quejas sobre ubicación? (Sí/No)
     - ¿Duración real vs estimada? (±15 min)
     - Comentarios libres (opcional)

**Métricas a Capturar:**

| Métrica | Cómo Medirla | Objetivo |
|---------|--------------|----------|
| **Agreement Rate** | % veces AI = Humano | >70% en semana 4 |
| **AI Acceptance Rate** | % veces host acepta sugerencia AI | >50% en semana 4 |
| **Customer Satisfaction** | Rating 1-5 post-servicio | >4.2 promedio |
| **Table Turnover** | Minutos por mesa | Reducir 10% vs baseline |
| **Wasted Capacity** | Sillas vacías en mesas ocupadas | <15% |
| **Setup Time** | Minutos para juntar mesas | <5 min promedio |

**Cronograma 4 Semanas:**

**Semana 5: Onboarding**
- Lunes: Capacitación staff (2 horas)
  - Explicar objetivo del experimento
  - Demo de interface tablet
  - Protocolo de feedback
- Martes-Domingo: Operación con 25% de reservas (baja demanda primero)
- **Goal**: Staff familiarizado, sistema estable

**Semana 6: Ramping Up**
- Aumentar a 50% de reservas
- Focus: capturar casos de desacuerdo AI-Humano
- Sesión mid-week: revisar casos interesantes con equipo
- **Goal**: Identificar patrones de error del AI

**Semana 7: Full Operation**
- 100% de reservas con sugerencias AI
- Staff tiene confianza en sistema
- Captura intensiva de feedback
- **Goal**: Dataset robusto para análisis

**Semana 8: Análisis y Refinamiento**
- Lunes-Miércoles: Análisis de datos (500+ decisiones)
- Jueves: Workshop con staff
  - Presentar findings
  - Discutir mejoras
  - Votar: ¿Confían en AI para producción?
- Viernes: Decisión GO/NO-GO para Fase 3

**Herramientas de Soporte:**

```python
# src/application/services/feedback_collector.py

class FeedbackCollector:
    """
    Sistema de captura de feedback durante Fase 2
    """
    
    async def log_parallel_decision(
        self,
        booking: Booking,
        human_decision: TableAssignment,
        ai_suggestion: TableAssignment,
        confidence: float
    ):
        """Registra ambas decisiones para comparación"""
        await self.db.insert_decision_log({
            'timestamp': datetime.now(),
            'booking_id': booking.id,
            'human_table': human_decision.table_id,
            'ai_table': ai_suggestion.table_id,
            'ai_confidence': confidence,
            'agreement': human_decision.table_id == ai_suggestion.table_id,
            'context': self.capture_context()
        })
    
    async def collect_post_service_feedback(
        self,
        booking_id: str,
        host_name: str
    ) -> Feedback:
        """
        Interface rápida para host (30 seg)
        """
        return await self.show_feedback_form(
            questions=[
                {
                    'id': 'comfort',
                    'text': '¿Grupo cómodo en mesa?',
                    'type': 'boolean',
                    'required': True
                },
                {
                    'id': 'complaints',
                    'text': '¿Quejas de ubicación?',
                    'type': 'boolean',
                    'required': True
                },
                {
                    'id': 'duration_delta',
                    'text': 'Duración real vs estimada',
                    'type': 'slider',  # -30min a +30min
                    'required': True
                },
                {
                    'id': 'satisfaction',
                    'text': 'Califica experiencia',
                    'type': 'stars',  # 1-5 estrellas
                    'required': True
                },
                {
                    'id': 'comments',
                    'text': 'Comentarios (opcional)',
                    'type': 'text',
                    'required': False
                }
            ]
        )
    
    async def generate_weekly_report(self, week_num: int):
        """
        Reporte semanal para equipo
        """
        decisions = await self.db.get_week_decisions(week_num)
        
        report = {
            'agreement_rate': self.calc_agreement_rate(decisions),
            'ai_acceptance_rate': self.calc_acceptance_rate(decisions),
            'avg_satisfaction': self.calc_avg_satisfaction(decisions),
            'common_disagreements': self.find_disagreement_patterns(decisions),
            'ai_mistakes': self.identify_clear_mistakes(decisions),
            'ai_wins': self.identify_better_than_human(decisions),
            'staff_comments': self.aggregate_comments(decisions)
        }
        
        return report
```

**Casos de Estudio Durante Fase 2:**

Capturar en detalle:
1. **AI Correcto, Humano Incorrecto**: Cliente más feliz con AI
2. **Humano Correcto, AI Incorrecto**: AI no consideró factor X
3. **Empate**: Ambos funcionaron igualmente bien
4. **Ambos Incorrectos**: Aprender del error compartido

---

### FASE 3: APRENDIZAJE SUPERVISADO (Semanas 9-10)

**Objetivo:**
> Usar datos de Fase 2 para entrenar modelo de ML que mejore scoring

**Datos Recopilados:**
- ~800 decisiones humanas (500 reservas × 2 servicios/día × 28 días)
- ~800 sugerencias AI paralelas
- ~800 feedback ratings
- Contexto completo de cada decisión

**Entrenamiento:**

```python
# src/ml/table_assignment_model.py

import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

class TableAssignmentMLModel:
    """
    Modelo ML para mejorar scoring de candidatos
    Entrenado con feedback humano de Fase 2
    """
    
    def prepare_training_data(self, feedback_logs: List[FeedbackLog]):
        """
        Convertir logs a features para ML
        """
        features = []
        labels = []
        
        for log in feedback_logs:
            # FEATURES (X):
            X = {
                # Características de la mesa
                'capacidad_mesa': log.table.capacidad,
                'capacidad_grupo': log.booking.personas,
                'fit_ratio': log.booking.personas / log.table.capacidad,
                'zona_terraza': 1 if log.table.zona == 'terraza' else 0,
                'zona_sala': 1 if log.table.zona == 'sala' else 0,
                'zona_barra': 1 if log.table.zona == 'barra' else 0,
                'requiere_juntar': 1 if log.assignment.mesas_juntadas else 0,
                
                # Características temporales
                'hora_dia': log.booking.hora.hour,
                'dia_semana': log.booking.fecha.weekday(),
                'es_fin_semana': 1 if log.booking.fecha.weekday() >= 5 else 0,
                'servicio_comida': 1 if 12 <= log.booking.hora.hour <= 16 else 0,
                'servicio_cena': 1 if 19 <= log.booking.hora.hour <= 23 else 0,
                
                # Contexto
                'temperatura': log.context.weather.temp,
                'lloviendo': 1 if log.context.weather.is_raining else 0,
                'ocupacion_resto': log.context.occupancy_rate,
                
                # Historial (si existe)
                'cliente_repetidor': 1 if log.booking.cliente.visitas > 1 else 0,
                'zona_preferida_historico': log.booking.cliente.zona_favorita,
            }
            
            # LABEL (y): Satisfacción del cliente (0-1)
            y = log.feedback.satisfaction / 5.0
            
            features.append(X)
            labels.append(y)
        
        return pd.DataFrame(features), pd.Series(labels)
    
    def train_model(self, X_train, y_train):
        """
        Entrenar Gradient Boosting Regressor
        """
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.model.fit(X_train, y_train)
    
    def predict_satisfaction(self, candidato: TableConfiguration, booking: Booking) -> float:
        """
        Predecir satisfacción esperada (0-1)
        Reemplaza scoring manual en Fase 3
        """
        X = self.prepare_features(candidato, booking)
        return self.model.predict([X])[0]


# Integración en algoritmo principal
class IntelligentTableAssignmentService:
    """
    Versión 2.0: Con ML entrenado
    """
    
    def __init__(self):
        self.ml_model = TableAssignmentMLModel.load_from_disk()
        self.fallback_to_heuristic = True  # Si ML falla
    
    async def assign_table(self, booking: Booking) -> TableAssignment:
        contexto = await self.obtener_contexto_completo(booking)
        candidatos = await self.generar_candidatos_csp(booking, contexto)
        
        # SCORING CON ML
        scored_options = []
        for candidato in candidatos:
            if self.ml_model.is_trained:
                # Usar ML para scoring
                score = self.ml_model.predict_satisfaction(candidato, booking)
            else:
                # Fallback a heurística manual
                score = self.calcular_score_multicriterio(candidato, booking, contexto)
            
            scored_options.append((candidato, score))
        
        mejor = max(scored_options, key=lambda x: x[1])
        return await self.ejecutar_asignacion(mejor[0])
```

**Validación del Modelo:**

1. **Split Train/Test**: 80/20
2. **Métricas**:
   - MAE (Mean Absolute Error): <0.15 (en escala 0-1)
   - R²: >0.60
   - Correlación predicciones vs ratings reales: >0.75

3. **A/B Testing Interno**:
   - 50% reservas con ML
   - 50% reservas con heurística
   - Comparar satisfacción durante 1 semana

**Entregable**: Modelo ML validado, listo para producción

---

### FASE 4: PRODUCCIÓN GRADUAL (Semanas 11-12)

**Objetivo:**
> Desplegar sistema con confianza del equipo, con kill-switch disponible

**Week 11: Soft Launch**
- AI toma decisiones para 30% de reservas (baja demanda primero)
- Staff puede override manualmente siempre
- Monitoring intensivo:
  - Satisfaction ratings
  - Override rate (si >30%, revisar)
  - Error logs
  - Performance (<200ms)

**Week 12: Full Production**
- AI maneja 100% de reservas
- Staff interviene solo en casos especiales:
  - VIP guests
  - Grupos >10 personas
  - Solicitudes especiales complejas
- Sistema de alertas:
  - Satisfaction <4.0 → alerta inmediata
  - Override rate >20% → review semanal

**Kill-Switch Protocol:**
```python
# src/core/config.py

class FeatureFlags:
    AI_TABLE_ASSIGNMENT_ENABLED = True  # Master switch
    AI_CONFIDENCE_THRESHOLD = 0.75      # Min confidence para auto-assign
    ALLOW_STAFF_OVERRIDE = True         # Siempre permitir override
    FALLBACK_TO_MANUAL = False          # Si True, solo sugerencias
```

**Monitoreo Continuo:**
- Dashboard en tiempo real:
  - Agreement rate (AI vs eventual outcome)
  - Satisfaction trend (7-day moving average)
  - Table utilization vs baseline
  - Revenue per table vs baseline
- Alertas automáticas si métricas degradas >5%

---

### FASE 5: APRENDIZAJE CONTINUO (Mes 4+)

**Objetivo:**
> Sistema que mejora automáticamente con cada servicio

**Feedback Loop Automatizado:**

```python
# src/application/services/continuous_learning.py

class ContinuousLearningService:
    """
    Sistema de aprendizaje continuo post-producción
    """
    
    async def daily_consolidation(self):
        """
        Cada noche a las 2 AM
        """
        # 1. Recopilar decisiones del día
        today_decisions = await self.db.get_today_decisions()
        
        # 2. Calcular métricas
        metrics = self.calculate_daily_metrics(today_decisions)
        
        # 3. Identificar patrones nuevos
        new_patterns = self.detect_new_patterns(today_decisions)
        
        # 4. Actualizar L2 (NotebookLM + MCP Memory)
        if new_patterns:
            await self.update_l2_memory(new_patterns)
        
        # 5. Mover de L1 (Redis) a L2 (persistente)
        await self.consolidate_l1_to_l2(today_decisions)
        
        # 6. Generar alerta si anomalía
        if metrics.satisfaction < 4.0:
            await self.alert_team(f"Low satisfaction today: {metrics.satisfaction}")
    
    async def weekly_retraining(self):
        """
        Cada domingo a las 3 AM
        """
        # 1. Recopilar última semana de feedback
        week_data = await self.db.get_last_week_data()
        
        # 2. Verificar si hay suficiente data nueva (>100 decisiones)
        if len(week_data) < 100:
            return  # Skip retraining
        
        # 3. Re-entrenar modelo ML
        X, y = self.ml_model.prepare_training_data(week_data)
        self.ml_model.incremental_train(X, y)  # Incremental learning
        
        # 4. Validar nuevo modelo vs producción
        validation_score = await self.validate_new_model()
        
        # 5. Desplegar solo si mejora >2%
        if validation_score > self.current_model_score * 1.02:
            await self.deploy_new_model()
            await self.notify_team("ML model updated - improved by {:.1%}".format(
                validation_score / self.current_model_score - 1
            ))
    
    async def monthly_review(self):
        """
        Primer domingo de cada mes
        """
        # 1. Generar reporte comprehensivo
        report = await self.generate_monthly_report()
        
        # 2. Identificar oportunidades de mejora
        opportunities = self.analyze_improvement_opportunities(report)
        
        # 3. Crear tareas para equipo
        tasks = []
        if opportunities.configuraciones_nuevas:
            tasks.append("Agregar nuevas configuraciones a L3 Airtable")
        if opportunities.restricciones_desactualizadas:
            tasks.append("Actualizar restricciones físicas en L3")
        if opportunities.pesos_suboptimos:
            tasks.append("Revisar weights de scoring multi-criterio")
        
        # 4. Enviar email al manager
        await self.send_monthly_review_email(report, tasks)
```

**Métricas de Éxito Continuo:**

| KPI | Baseline (Pre-AI) | Target Mes 4 | Target Mes 12 |
|-----|-------------------|--------------|---------------|
| Satisfaction Rating | 4.1/5 | 4.3/5 | 4.5/5 |
| Table Turnover | 95 min/mesa | 85 min | 80 min |
| Wasted Capacity | 22% | 15% | 10% |
| No-Shows | 12% | 10% | 8% |
| Revenue per Table | €45 | €48 (+6.6%) | €52 (+15.5%) |
| Staff Override Rate | N/A | <20% | <10% |

---

## 🎯 MÉTRICAS DE ÉXITO Y VALIDACIÓN

### Métricas Técnicas (Sistema)

**Performance:**
- Latencia asignación: <200ms (p95)
- Uptime: >99.5%
- Error rate: <0.1%
- Candidatos generados: 5-15 por reserva

**Precisión:**
- Agreement con humanos: >75% (Fase 2)
- ML prediction MAE: <0.15
- False positives (mal asignados): <5%

### Métricas Operacionales (Negocio)

**Eficiencia:**
- Reducción tiempo asignación: -60% (de 2 min a 45 seg)
- Reducción setup de mesas: <5 min promedio
- Ocupación máxima alcanzada: +15% vs baseline

**Experiencia:**
- Customer satisfaction: >4.3/5
- Quejas sobre ubicación: <3% de reservas
- Clientes repetidores mencionan "buena mesa": +25%

**Revenue:**
- Revenue per table: +10% en 6 meses
- Reducción no-shows: -20%
- Incremento walk-ins sentados: +30%

### Validación Cualitativa

**Feedback del Staff (Survey trimestral):**
- ¿Confías en las sugerencias del AI? (target: >80% Sí)
- ¿Te ahorra tiempo? (target: >90% Sí)
- ¿Ha mejorado experiencia del cliente? (target: >70% Sí)
- ¿Recomendarías a otro restaurante? (NPS: >50)

**Feedback de Clientes (Survey post-visita):**
- ¿Satisfecho con ubicación de mesa? (target: >90% Sí)
- ¿Esperaste más de lo esperado? (target: <10% Sí)
- Probabilidad de volver (target: >85%)

---

## 🚀 RECOMENDACIONES FINALES

### 1. Priorizar Fase 2 (Pruebas Humanas)

**Razón:** Es la fase más crítica. El sistema debe ganarse la confianza del equipo.

**Inversión de tiempo:**
- 4 semanas completas con operación paralela
- No apurar esta fase
- Mejor 6 semanas de pruebas que 1 mes debuggeando en producción

### 2. Comenzar Simple, Iterar Rápido

**Fase 1:** Heurísticas fijas (sin ML) → 2 semanas  
**Fase 2:** Validación humana → 4 semanas  
**Fase 3:** Agregar ML → 2 semanas  
**Fase 4:** Producción → 2 semanas  

**Total:** 10 semanas (2.5 meses) hasta producción completa

### 3. Documentar TODO

Cada decisión de asignación debe loggear:
- Input: reserva completa
- Contexto: clima, ocupación, restricciones
- Candidatos generados (top 5)
- Scores calculados
- Decisión final
- Outcome: satisfaction, duración real, quejas

**Por qué:** Debugging de algoritmos complejos es imposible sin logs detallados.

### 4. Mantener Human-in-the-Loop Permanente

Incluso en producción:
- Staff puede override siempre
- Casos edge (VIPs, grupos grandes) → humano decide
- Sistema aprende de overrides

**Filosofía:** AI asiste, humano decide en casos complejos.

### 5. Preparar para Evolución

**Roadmap futuro:**
- **Q2 2026**: Predicción de no-shows con ML
- **Q3 2026**: Optimización de turnos (lunch vs dinner)
- **Q4 2026**: Personalización por cliente (aprender preferencias individuales)
- **Q1 2027**: Pricing dinámico (mesas premium en horas pico)

---

## 📚 REFERENCIAS Y FUENTES

### Papers Académicos

1. [Vidotto, A. (2006). "Managing Restaurant Tables Using Constraint Programming" - PhD Thesis, University of Toronto](https://tidel.mie.utoronto.ca/pubs/Theses/vidotto.phd.pdf)

2. [Vidotto et al. (2007). "Managing Restaurant Tables using Constraints" - Knowledge-Based Systems, SpringerLink](https://link.springer.com/chapter/10.1007/978-1-84628-666-7_1)

3. [Thompson, G. M. (2008). "Optimizing Restaurant-Table Configurations" - ResearchGate](https://www.researchgate.net/publication/247274132_Optimizing_Restaurant-Table_Configurations_Specifying_Combinable_Tables)

4. ["Restaurant Reservation Management Considering Table Combination" - SciELO Brazil, 2018](https://www.scielo.br/j/pope/a/bkBQnG3YtpX37nKYSzpKhvP/)

5. ["Optimizing Restaurant Reservation Scheduling" - Harvey Mudd College, 2024](https://scholarship.claremont.edu/cgi/viewcontent.cgi?article=1022&context=hmc_theses)

6. [Burcea, M. (2014). "Online Dynamic Bin Packing" - University of Liverpool](https://livrepository.liverpool.ac.uk/2005382/1/BurceaMih_Oct2014_2002421.pdf)

### Artículos de Industria

7. [Hostie AI (2025). "OpenTable, Resy, SevenRooms & More: Which AI Reservation Integrations Actually Work"](https://www.hostie.ai/resources/ai-reservation-integrations-opentable-resy-sevenrooms-2025-comparison)

8. [CheckLess (2026). "Restaurant Table Turnover: Maximizing Revenue"](https://checkless.io/blog/restaurant-table-turnover-optimization-2026)

9. [Lilac Labs. "How to Build a Feedback System That Improves Restaurant Operations"](https://www.lilaclabs.ai/blog/build-feedback-system-improves-restaurant-operations)

10. [Modern Restaurant Management (2024). "Designing Feedback Loops for Seasonal Data Insights"](https://modernrestaurantmanagement.com/designing-feedback-loops-for-seasonal-data-insights/)

11. [SevenRooms Platform Documentation. "Table Management Software"](https://sevenrooms.com/platform/table-management/)

### Recursos Técnicos

12. [Wikipedia. "Bin Packing Problem"](https://en.wikipedia.org/wiki/Bin_packing_problem)

13. [arXiv:2104.12000. "A Deep Reinforcement Learning Approach for the Meal Delivery Problem"](https://arxiv.org/abs/2104.12000)

14. [AIS Electronic Library (2024). "Optimizing Restaurant Customer Flow with Real-Time Coupon Allocation: A DRL Approach"](https://aisel.aisnet.org/icis2024/data_soc/data_soc/9/)

---

## 💡 CONCLUSIÓN

Este sistema combina:
- ✅ **Algoritmos probados académicamente** (CSP, MIP, Bin Packing)
- ✅ **Benchmarks de industria** (SevenRooms: 10K combos/seg)
- ✅ **Aprendizaje continuo** (RL + feedback loops)
- ✅ **Validación humana rigurosa** (4 semanas operación paralela)
- ✅ **Implementación gradual** (de heurísticas a ML)

**Diferenciador clave:** Fase 2 de pruebas humanas asegura que el sistema se adapta a la realidad operacional de Verdent, no solo a teoría académica.

**Próximo paso:** Revisión de este documento con el equipo y decisión sobre aprobación de plan de implementación.

---

**Documento generado**: 12 febrero 2026  
**Versión**: 1.0  
**Requiere aprobación**: Gerente + Staff clave  
**Estimación implementación**: 10 semanas (2.5 meses)
