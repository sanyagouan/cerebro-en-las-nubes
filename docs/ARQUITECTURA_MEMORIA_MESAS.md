# Sistema de Memoria Multi-Nivel para Asignación de Mesas
## Arquitectura "Verdent Memory System"

> **Inspiración**: OpenClaw/ClawBot memory system
> **Objetivo**: Gestión inteligente tipo Tetris con aprendizaje continuo
> **Fecha**: 12 febrero 2026

---

## 🧠 Capas de Memoria

### **L3: Memoria de Largo Plazo** (Inmutable/Estructural)
**Storage**: Airtable + Archivos de configuración
**Duración**: Permanente (solo cambia con remodelaciones físicas)
**Contenido**: Verdades absolutas del espacio físico

#### Tablas en Airtable:

##### `MESAS_FISICAS`
Cada mesa/posición física real del restaurante.

```
Campos:
- ID (text): "T1", "S2", "B1", etc.
- Nombre (text): "Terraza 1", "Sala Mesa 2", etc.
- Zona (enum): "Terraza", "Sala", "Barra"
- TipoMesa (enum): "Individual", "Sofá", "Alta"
- PosicionX (number): Coordenada X en plano
- PosicionY (number): Coordenada Y en plano
- CapacidadMinima (number): 2
- CapacidadMaxima (number): 4, 6, 8, etc.
- Movible (boolean): ¿Se puede reubicar?
- Estado (enum): "Activa", "Fuera_Servicio", "Temporal"
- Notas (text): "Junto a ventana", "Cerca del baño", etc.
```

##### `CONFIGURACIONES_VALIDAS`
Combinaciones físicamente posibles de mesas.

```
Campos:
- ID (text): "T1+T2", "S5+AUX1", etc.
- MesaPrincipal (link): → MESAS_FISICAS
- MesasSecundarias (link multiple): → MESAS_FISICAS
- CapacidadTotal (number): 6, 8, 10, etc.
- DificultadMontaje (enum): "Fácil", "Media", "Difícil"
- TiempoMontaje (number): minutos
- RequiereAprobacion (boolean): ¿Gerente debe aprobar?
- Notas (text): "Solo si no llueve", "Obstruye paso", etc.
```

##### `RESTRICCIONES_FISICAS`
Reglas inmutables del espacio.

```
Campos:
- ID (text): "R001", "R002", etc.
- Tipo (enum): "Obstaculo_Fijo", "Regulacion", "Seguridad"
- Descripcion (text): "Árbol entre T5 y T6 impide juntarlas"
- MesasAfectadas (link multiple): → MESAS_FISICAS
- Severidad (enum): "Bloqueante", "Advertencia"
- Activa (boolean): true/false
```

##### `ZONAS`
Metadatos de cada zona del restaurante.

```
Campos:
- ID (text): "terraza", "sala", "barra"
- Nombre (text): "Terraza Exterior", etc.
- CapacidadMaximaPersonas (number): 64, 80, etc.
- CondicionesClima (boolean): ¿Afectada por clima?
- PrioridadAsignacion (number): 1 (alta) - 5 (baja)
- HorarioPico (text): "13:00-15:00, 20:00-22:30"
```

---

### **L2: Memoria de Medio Plazo** (Patrones Aprendidos)
**Storage**: NotebookLM + MCP Memory Graph
**Duración**: Semanas/meses (se revisa y actualiza)
**Contenido**: Patrones operativos y heurísticas aprendidas

#### En NotebookLM (Documentación Rica):

**Documentos a mantener:**

1. **Patrones_Estacionales.md**
   - "En verano, terraza se llena 30min antes"
   - "En invierno, preferencia 80% sala"
   - "Diciembre: grupos grandes (+6) aumentan 40%"

2. **Configuraciones_Habituales.md**
   - "Viernes 21h: configuración T1+T2, T3+T4, T5+T6"
   - "Domingos comida: familias grandes, usar S2+S6 ampliadas"
   - "Grupos corporativos: prefieren sala alejada (S7-S8)"

3. **Decisiones_Exitosas.md**
   - "Cliente pidió 6 personas terraza lunes 14h → T1+T2 OK"
   - "Grupo 8 con niños → S2 ampliada mejor que terraza"
   - "Pareja romántica → evitar B1/B2, preferir S8 si disponible"

4. **Decisiones_Fallidas.md** (Aprendizaje de errores)
   - "Asignamos T9+T10 con lluvia → clientes se mojaron"
   - "Grupo 3 en B1 → se quejaron de incomodidad"
   - "Juntamos S5+S6 → obstruyó paso a cocina"

#### En MCP Memory (Knowledge Graph):

```javascript
// Entidades dinámicas
create_entities([
  {
    name: "Patrón Viernes Noche",
    entityType: "PatronUso",
    observations: [
      "Terraza se llena primero 20:00-21:30",
      "Grupos 4-6 personas predominan",
      "Configuración típica: 4 combos de 2 mesas",
      "Rotación promedio: 2 horas"
    ]
  },
  {
    name: "Configuración T1+T2",
    entityType: "ConfiguracionAprendida",
    observations: [
      "Usada 47 veces último mes",
      "Satisfacción 4.7/5",
      "Tiempo montaje: 2 min",
      "Nunca falla, sin obstáculos"
    ]
  }
])

// Relaciones aprendidas
create_relations([
  {
    from: "Grupo Familiar 6+",
    to: "Mesa S2 Ampliada",
    relationType: "prefiere_historicamente"
  },
  {
    from: "Clima Lluvioso",
    to: "Zona Terraza",
    relationType: "invalida_asignacion_en"
  }
])
```

---

### **L1: Memoria de Corto Plazo** (Sesión/Día Actual)
**Storage**: Redis Cache + MCP Memory temporal
**Duración**: 1 día (se resetea cada noche)
**Contenido**: Estado en tiempo real y decisiones del día

#### En Redis:

```javascript
// Estado en tiempo real
{
  "mesas_ocupadas": ["T1", "T2", "S5", "S8", "SOFA2"],
  "configuraciones_activas": [
    {"id": "T1+T2", "reserva_id": "R123", "hasta": "14:30"}
  ],
  "clima_actual": {
    "condicion": "soleado",
    "temperatura": 22,
    "terraza_disponible": true
  },
  "restricciones_temporales": [
    {"tipo": "obras_calle", "mesas_afectadas": ["T9", "T10"], "hasta": "15:00"}
  ],
  "ocupacion_actual": {
    "terraza": "40%",
    "sala": "65%",
    "barra": "0%"
  }
}
```

#### En MCP Memory (sesión conversacional):

```javascript
// Decisiones y contexto de la conversación actual
add_observations({
  entityName: "Sesión Actual",
  contents: [
    "Reserva R456: buscamos mesa para 4 a las 21:00",
    "Terraza casi llena, considerando sala",
    "Cliente prefiere exterior si posible",
    "Propuesta: T7+T8 si disponible, sino S3"
  ]
})
```

---

## 🎲 Algoritmo de Asignación: "Tetris Inteligente"

### Fase 1: Recolección de Contexto

```python
def obtener_contexto_completo(reserva, momento):
    """Agrega las 3 capas de memoria"""

    # L3: Restricciones físicas (Airtable)
    mesas_disponibles = get_mesas_activas()
    configuraciones_posibles = get_configuraciones_validas()
    restricciones = get_restricciones_activas()

    # L2: Patrones aprendidos (NotebookLM + Memory)
    patrones_horario = ask_notebooklm(
        f"¿Qué patrones hay para {reserva.dia_semana} a las {reserva.hora}?"
    )
    configuraciones_exitosas = search_memory(
        f"configuraciones exitosas para {reserva.num_personas} personas"
    )

    # L1: Estado actual (Redis + Memory temporal)
    ocupacion_actual = redis.get("ocupacion_actual")
    clima = redis.get("clima_actual")
    restricciones_temporales = redis.get("restricciones_temporales")

    return {
        "fisico": {"mesas": mesas_disponibles, "config": configuraciones_posibles},
        "aprendido": {"patrones": patrones_horario, "exitos": configuraciones_exitosas},
        "tiempo_real": {"ocupacion": ocupacion_actual, "clima": clima}
    }
```

### Fase 2: Generación de Candidatos (Heurísticas)

```python
def generar_candidatos(reserva, contexto):
    """Bin Packing con heurísticas aprendidas"""

    candidatos = []

    # Heurística 1: Tamaño exacto (mejor fit)
    for mesa in contexto["fisico"]["mesas"]:
        if mesa.capacidad_minima <= reserva.personas <= mesa.capacidad_maxima:
            candidatos.append({
                "mesas": [mesa],
                "score": calcular_score(mesa, reserva, contexto),
                "tipo": "exacta"
            })

    # Heurística 2: Configuraciones aprendidas
    for config in contexto["aprendido"]["exitos"]:
        if config.capacidad >= reserva.personas:
            candidatos.append({
                "mesas": config.mesas,
                "score": calcular_score_configuracion(config, reserva, contexto),
                "tipo": "aprendida"
            })

    # Heurística 3: Combinaciones nuevas (exploración)
    for combo in generar_combinaciones_validas(contexto["fisico"]["config"]):
        if combo.capacidad >= reserva.personas:
            candidatos.append({
                "mesas": combo.mesas,
                "score": calcular_score_exploracion(combo, reserva, contexto),
                "tipo": "exploracion"
            })

    return sorted(candidatos, key=lambda x: x["score"], reverse=True)
```

### Fase 3: Scoring Multi-Criterio

```python
def calcular_score(opcion, reserva, contexto):
    """
    Score = Σ (peso_i × factor_i)

    Factores:
    - Ajuste de capacidad (40%): Menor desperdicio mejor
    - Experiencia histórica (25%): Configuraciones con alta satisfacción
    - Preferencias cliente (20%): Terraza vs sala, ventana, etc.
    - Facilidad montaje (10%): Menos tiempo = mejor
    - Impacto futuro (5%): No bloquear mesas para reservas posteriores
    """

    score = 0

    # Factor 1: Ajuste capacidad (evita desperdiciar mesa grande)
    capacidad_total = sum(m.capacidad_maxima for m in opcion["mesas"])
    desperdicio = capacidad_total - reserva.personas
    score += (1 - desperdicio / capacidad_total) * 0.40

    # Factor 2: Experiencia histórica
    config_id = "+".join(m.id for m in opcion["mesas"])
    historial = search_memory(f"satisfaccion {config_id}")
    if historial:
        score += (historial.rating / 5.0) * 0.25

    # Factor 3: Preferencias
    if reserva.preferencias.exterior and opcion["zona"] == "terraza":
        score += 0.20

    # Factor 4: Facilidad montaje
    if len(opcion["mesas"]) == 1:  # Mesa individual
        score += 0.10
    elif opcion["tipo"] == "aprendida":  # Ya se hace habitualmente
        score += 0.08

    # Factor 5: Impacto futuro
    reservas_posteriores = get_reservas_posteriores(reserva.fecha)
    if not bloquea_futuras(opcion["mesas"], reservas_posteriores):
        score += 0.05

    return score
```

### Fase 4: Validación y Feedback Loop

```python
async def asignar_y_aprender(reserva, opcion_elegida):
    """Asigna mesa y registra para aprendizaje"""

    # Asignación
    asignacion = await crear_asignacion(reserva, opcion_elegida)

    # Registro L1 (Redis - corto plazo)
    redis.lpush("decisiones_hoy", {
        "reserva_id": reserva.id,
        "opcion": opcion_elegida,
        "timestamp": now(),
        "score": opcion_elegida["score"]
    })

    # Registro L2 (Memory - medio plazo)
    add_observations({
        "entityName": f"Asignación {reserva.id}",
        "contents": [
            f"Asignadas {opcion_elegida['mesas']} para {reserva.personas} personas",
            f"Score inicial: {opcion_elegida['score']}",
            f"Preferencias: {reserva.preferencias}"
        ]
    })

    # Trigger feedback posterior (cuando termine la reserva)
    schedule_feedback_collection(reserva.id, reserva.hora_fin + timedelta(hours=1))

    return asignacion


async def procesar_feedback(reserva_id, feedback):
    """Actualiza memoria medio plazo con resultado real"""

    asignacion = get_asignacion(reserva_id)

    # Actualizar score de configuración
    add_observations({
        "entityName": f"Configuración {asignacion.config_id}",
        "contents": [
            f"Uso #{asignacion.uso_count}: satisfacción {feedback.rating}/5",
            f"Comentario: {feedback.comentario}",
            f"¿Repetiría?: {feedback.repetiria}"
        ]
    })

    # Si fue decisión exitosa, documentar en NotebookLM
    if feedback.rating >= 4:
        agregar_a_notebooklm(
            notebook="verdent-restaurant-layout-oper",
            contenido=f"✅ Config exitosa: {asignacion.config_id} para {asignacion.personas}p - Rating {feedback.rating}/5"
        )
    else:
        agregar_a_notebooklm(
            notebook="verdent-restaurant-layout-oper",
            contenido=f"❌ Evitar: {asignacion.config_id} para {asignacion.personas}p - Problema: {feedback.comentario}"
        )
```

---

## 🔄 Retroalimentación y Evolución

### Revisión Semanal (Automatizada)

```python
async def revision_semanal():
    """Consolida aprendizajes L1 → L2"""

    # Analizar decisiones de la semana
    decisiones = redis.lrange("decisiones_semana", 0, -1)

    # Identificar patrones
    patrones = {
        "configuraciones_mas_usadas": Counter(d["opcion"]["config_id"] for d in decisiones).most_common(10),
        "horarios_pico": agrupar_por_horario(decisiones),
        "preferencias_clima": correlacion_clima_zona(decisiones)
    }

    # Actualizar NotebookLM
    documento = generar_reporte_semanal(patrones)
    actualizar_notebooklm("Patrones_Semanales.md", documento)

    # Actualizar Memory Graph
    for config_id, count in patrones["configuraciones_mas_usadas"]:
        add_observations({
            "entityName": f"Configuración {config_id}",
            "contents": [f"Semana {week_number()}: usada {count} veces"]
        })
```

### Revisión Mensual (Manual + IA)

```python
async def revision_mensual():
    """Claude revisa y sugiere optimizaciones"""

    # Claude analiza documentos de NotebookLM
    analisis = await ask_notebooklm(
        notebook="verdent-restaurant-layout-oper",
        question="""
        Analiza los patrones del último mes:
        1. ¿Qué configuraciones tienen mejor satisfacción?
        2. ¿Hay mesas infrautilizadas?
        3. ¿Restricciones que ya no aplican?
        4. ¿Nuevas configuraciones a probar?
        """
    )

    # Genera reporte para gerente
    reporte = generar_reporte_mensual(analisis)

    # Sugiere cambios en L3 (Airtable)
    if analisis.tiene_sugerencias_estructurales:
        notificar_gerente(
            "Sugerencias de optimización de layout disponibles",
            reporte
        )
```

---

## 📊 Métricas de Éxito del Sistema

### KPIs a Trackear:

1. **Tasa de Aceptación Primera Propuesta**: >85%
2. **Satisfacción Post-Asignación**: >4.2/5
3. **Utilización de Capacidad**: >75% en horario pico
4. **Tiempo Decisión**: <5 segundos
5. **Precisión Predictiva**: >90% en estimaciones de ocupación

---

## 🚀 Implementación por Fases

### Fase 1: Base (Semana 1-2)
- ✅ Crear schema Airtable (L3)
- ✅ Migrar configuración actual de Agora
- ✅ Implementar algoritmo básico (Best-Fit)

### Fase 2: Aprendizaje (Semana 3-4)
- ⬜ Integrar NotebookLM (L2)
- ⬜ Implementar feedback loop
- ⬜ Sistema de scoring multi-criterio

### Fase 3: Optimización (Semana 5-6)
- ⬜ Redis cache (L1)
- ⬜ Revisiones automáticas
- ⬜ Dashboard de métricas

---

**Próximos pasos inmediatos:**
1. Validar schema Airtable propuesto
2. Documentar mesas reales en detalle (sin S8 redonda)
3. Implementar algoritmo base de asignación

