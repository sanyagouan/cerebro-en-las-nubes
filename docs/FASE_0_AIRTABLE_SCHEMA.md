# FASE 0 - SCHEMA DE AIRTABLE DETALLADO
## Base de Datos Inteligente de Mesas

> **Base ID**: `appQ2ZXAR68cqDmJt`
> **Propósito**: Almacenar configuración física permanente (L3 Memory)
> **Status**: Diseño completo - Listo para implementación

---

## 📊 ARQUITECTURA DE TABLAS

```
MESAS_FISICAS (35 records)
    ↓ referenced by
CONFIGURACIONES_VALIDAS (50-80 records)
    ↓ referenced by
RESTRICCIONES_FISICAS (20-30 records)
    ↑
    └─ references ZONAS (3 records)
```

---

## 1️⃣ TABLA: MESAS_FISICAS

### Propósito
Catálogo master de todas las unidades físicas de mesas en el restaurante.

### Campos

| Campo | Tipo | Configuración | Descripción | Ejemplo |
|-------|------|---------------|-------------|---------|
| **mesa_id** | Single line text | PRIMARY KEY | Identificador único de mesa | `"T1"`, `"S2"`, `"SOFA_1"` |
| **nombre_display** | Single line text | | Nombre amigable para mostrar | `"Terraza 1"`, `"Sala 2"`, `"Sofá 1"` |
| **zona** | Single select | Required | Ubicación principal | `"terraza"`, `"sala"`, `"barra"` |
| **tipo_mesa** | Single select | | Categoría de mobiliario | `"rectangular"`, `"cuadrada"`, `"sofa"`, `"alta"` |
| **capacidad_base** | Number | Integer, ≥ 1 | Personas en configuración estándar | `4`, `6`, `2` |
| **capacidad_maxima** | Number | Integer, ≥ capacidad_base | Máximo absoluto (incómodo) | `5`, `8`, `3` |
| **es_ampliable** | Checkbox | | ¿Se puede agregar mesa auxiliar? | `true` / `false` |
| **mesa_auxiliar_id** | Single line text | | ID de la auxiliar que se usa | `"AUX_1"`, `"AUX_2"` |
| **capacidad_ampliada** | Number | Integer | Capacidad con auxiliar | `8`, `10` |
| **es_movible** | Checkbox | | ¿Se puede mover/juntar? | `true` / `false` |
| **coordenada_x** | Number | Decimal | Posición X en plano (metros) | `2.5`, `10.3` |
| **coordenada_y** | Number | Decimal | Posición Y en plano (metros) | `1.2`, `5.8` |
| **ubicacion_especial** | Multiple select | | Tags de ubicación | `"ventana"`, `"entrada"`, `"baño"`, `"cocina"`, `"rincón"`, `"paso"` |
| **prioridad_default** | Single select | | Preferencia general | `"1-alta"`, `"2-media"`, `"3-baja"`, `"4-overflow"` |
| **notas_operacion** | Long text | | Comentarios del staff | `"Mesa favorita de VIPs"`, `"Ruidosa los fines de semana"` |
| **estado_actual** | Single select | Auto-updated from L1 | Solo para UI | `"libre"`, `"ocupada"`, `"reservada"`, `"deshabilitada"` |
| **ultima_modificacion** | Last modified time | | Timestamp de cambio | Auto |
| **foto_mesa** | Attachment | | Imagen de la mesa | JPG/PNG |

### Registros Ejemplo

```javascript
// Terraza - Mesa individual movible
{
  mesa_id: "T1",
  nombre_display: "Terraza 1",
  zona: "terraza",
  tipo_mesa: "rectangular",
  capacidad_base: 4,
  capacidad_maxima: 5,
  es_ampliable: false,
  es_movible: true,
  coordenada_x: 2.5,
  coordenada_y: 1.0,
  ubicacion_especial: ["esquina"],
  prioridad_default: "2-media",
  notas_operacion: "Primera mesa de la fila inferior"
}

// Sala - Mesa grande ampliable
{
  mesa_id: "S2",
  nombre_display: "Sala 2 (Grande)",
  zona: "sala",
  tipo_mesa: "rectangular",
  capacidad_base: 6,
  capacidad_maxima: 8,
  es_ampliable: true,
  mesa_auxiliar_id: "AUX_1",
  capacidad_ampliada: 10,
  es_movible: false,
  coordenada_x: 8.0,
  coordenada_y: 4.5,
  ubicacion_especial: ["ventana", "rincón"],
  prioridad_default: "1-alta",
  notas_operacion: "Preferida por grupos grandes, buena vista"
}

// Sofá
{
  mesa_id: "SOFA_1",
  nombre_display: "Sofá 1",
  zona: "sala",
  tipo_mesa: "sofa",
  capacidad_base: 2,
  capacidad_maxima: 4,
  es_ampliable: false,
  es_movible: false,
  coordenada_x: 12.0,
  coordenada_y: 2.0,
  ubicacion_especial: ["rincón"],
  prioridad_default: "1-alta",
  notas_operacion: "Muy solicitado por parejas"
}

// Barra - Overflow
{
  mesa_id: "B1",
  nombre_display: "Barra 1",
  zona: "barra",
  tipo_mesa: "alta",
  capacidad_base: 2,
  capacidad_maxima: 3,
  es_ampliable: false,
  es_movible: false,
  coordenada_x: 1.0,
  coordenada_y: 8.0,
  ubicacion_especial: ["barra", "paso"],
  prioridad_default: "4-overflow",
  notas_operacion: "Solo usar si terraza y sala llenas. Avisar incomodidad."
}
```

---

## 2️⃣ TABLA: CONFIGURACIONES_VALIDAS

### Propósito
Define qué combinaciones de mesas son físicamente posibles y viables operativamente.

### Campos

| Campo | Tipo | Configuración | Descripción | Ejemplo |
|-------|------|---------------|-------------|---------|
| **config_id** | Auto number | PRIMARY KEY | ID autogenerado | `1`, `2`, `3`... |
| **nombre_config** | Formula | `{mesas} & " (" & {num_personas} & "p)"` | Nombre legible | `"T1+T2 (8p)"` |
| **mesas** | Multiple select (linked to MESAS_FISICAS) | Required | IDs de mesas en la combo | `["T1", "T2"]` |
| **num_mesas** | Count | Count of {mesas} | Cantidad de mesas | `2`, `3` |
| **num_personas** | Number | Integer, ≥ 1 | Capacidad total de la combo | `8`, `12` |
| **requiere_juntar** | Checkbox | | ¿Hay que mover mesas físicamente? | `true` / `false` |
| **tiempo_setup_min** | Number | Integer, ≥ 0 | Minutos para preparar | `2`, `5`, `10` |
| **dificultad_setup** | Single select | | Complejidad operacional | `"facil"`, `"media"`, `"dificil"` |
| **es_comoda** | Checkbox | | ¿Clientes cómodos? | `true` / `false` |
| **frecuencia_uso** | Single select | | Qué tan común es usarla | `"muy_frecuente"`, `"frecuente"`, `"rara"`, `"excepcional"` |
| **tipo_cliente_ideal** | Multiple select | | ¿Para quién funciona mejor? | `"familias"`, `"parejas"`, `"grupos"`, `"negocios"` |
| **restricciones** | Long text | | Limitaciones operativas | `"Solo usar en exterior"`  |
| **aprobada_por** | Single select | | Validación del staff | `"gerente"`, `"maitre"`, `"equipo"` |
| **foto_configuracion** | Attachment | | Imagen de la combo armada | JPG/PNG |
| **notas** | Long text | | Observaciones del staff | `"Funciona bien para cumpleaños"` |

### Registros Ejemplo

```javascript
// Combo simple terraza (muy frecuente)
{
  mesas: ["T1", "T2"],
  num_personas: 6,
  requiere_juntar: true,
  tiempo_setup_min: 2,
  dificultad_setup: "facil",
  es_comoda: true,
  frecuencia_uso: "muy_frecuente",
  tipo_cliente_ideal: ["familias", "grupos"],
  restricciones: "",
  aprobada_por: "equipo",
  notas: "Combo más usada en terraza"
}

// Combo compleja (excepcional)
{
  mesas: ["T5", "T6", "T7"],
  num_personas: 12,
  requiere_juntar: true,
  tiempo_setup_min: 8,
  dificultad_setup: "dificil",
  es_comoda: false,
  frecuencia_uso: "excepcional",
  tipo_cliente_ideal: ["grupos"],
  restricciones: "Requiere mover árbol-maceta. Solo con reserva previa (2h).",
  aprobada_por: "gerente",
  notas: "Solo para eventos especiales. Verificar clima."
}

// Mesa individual (default)
{
  mesas: ["S2"],
  num_personas: 6,
  requiere_juntar: false,
  tiempo_setup_min: 0,
  dificultad_setup: "facil",
  es_comoda: true,
  frecuencia_uso: "muy_frecuente",
  tipo_cliente_ideal: ["familias", "grupos", "negocios"],
  restricciones: "",
  aprobada_por: "equipo",
  notas: "Mesa grande natural. Primera opción para 6 personas."
}
```

---

## 3️⃣ TABLA: RESTRICCIONES_FISICAS

### Propósito
Documenta obstáculos, limitaciones climáticas y reglas físicas que afectan disponibilidad.

### Campos

| Campo | Tipo | Configuración | Descripción | Ejemplo |
|-------|------|---------------|-------------|---------|
| **restriccion_id** | Auto number | PRIMARY KEY | ID autogenerado | `1`, `2`, `3`... |
| **nombre** | Single line text | Required | Título descriptivo | `"Árbol grande T5-T6"` |
| **tipo** | Single select | Required | Categoría de restricción | `"obstaculo_fijo"`, `"climatica"`, `"espacial"`, `"temporal"`, `"regulatoria"` |
| **zona_afectada** | Linked record (ZONAS) | | Zona principal | Link a `"terraza"` |
| **mesas_afectadas** | Multiple select (linked to MESAS_FISICAS) | | Mesas impactadas | `["T5", "T6"]` |
| **configs_afectadas** | Multiple select (linked to CONFIGURACIONES_VALIDAS) | | Combos imposibles | Links |
| **severidad** | Single select | | Nivel de impacto | `"critica"`, `"alta"`, `"media"`, `"baja"` |
| **condicion_activacion** | Long text | | Cuándo aplica | `"lluvia > 2mm/h"`, `"temp > 35°C"`, `"siempre"` |
| **accion_requerida** | Long text | | Qué hacer cuando aplica | `"Desactivar T5 y T6"`, `"Solo combo T5+T6 (con sombra)"` |
| **es_permanente** | Checkbox | | ¿Siempre activa? | `true` / `false` |
| **horario_activa** | Long text | | Rango temporal | `"14:00-17:00 (verano)"`, `"todo el día"` |
| **override_manual** | Checkbox | | ¿Staff puede ignorarla? | `true` / `false` |
| **foto_restriccion** | Attachment | | Imagen del obstáculo | JPG/PNG |
| **notas** | Long text | | Contexto adicional | `"Instalado por ayuntamiento en 2023"` |

### Registros Ejemplo

```javascript
// Obstáculo fijo - Árbol
{
  nombre: "Árbol grande entre T5-T6",
  tipo: "obstaculo_fijo",
  zona_afectada: "terraza",
  mesas_afectadas: ["T5", "T6"],
  configs_afectadas: ["T5+T6"], // Link al record de config
  severidad: "alta",
  condicion_activacion: "siempre",
  accion_requerida: "Imposible juntar T5 y T6 directamente. Usar T5+T7 o T4+T6 en su lugar.",
  es_permanente: true,
  horario_activa: "todo el día",
  override_manual: false,
  notas: "Árbol plantado por el ayuntamiento. No se puede mover."
}

// Climática - Sol directo
{
  nombre: "Sol directo verano T1-T4",
  tipo: "climatica",
  zona_afectada: "terraza",
  mesas_afectadas: ["T1", "T2", "T3", "T4"],
  severidad: "media",
  condicion_activacion: "temp > 30°C AND hora BETWEEN 14:00-17:00 AND estacion = verano",
  accion_requerida: "Reducir prioridad. Ofrecer alternativas con sombra (T9-T16) primero.",
  es_permanente: false,
  horario_activa: "14:00-17:00 (Jun-Sep)",
  override_manual: true,
  notas: "Clientes pueden solicitar explícitamente estas mesas si les gusta el sol."
}

// Espacial - Paso peatonal
{
  nombre: "Paso peatonal obligatorio",
  tipo: "espacial",
  zona_afectada: "terraza",
  mesas_afectadas: ["T7", "T8", "T15", "T16"],
  severidad: "critica",
  condicion_activacion: "siempre",
  accion_requerida: "Mantener 1.5m mínimo de ancho de paso. No permitir combos que reduzcan el ancho.",
  es_permanente: true,
  horario_activa: "todo el día",
  override_manual: false,
  notas: "Ordenanza municipal. Multa si no se cumple."
}

// Temporal - Mercado semanal
{
  nombre: "Mercado callejero miércoles",
  tipo: "temporal",
  zona_afectada: "terraza",
  mesas_afectadas: ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"],
  severidad: "critica",
  condicion_activacion: "dia_semana = miercoles AND hora BETWEEN 08:00-14:00",
  accion_requerida: "Terraza CERRADA. Solo interior disponible.",
  es_permanente: false,
  horario_activa: "Miércoles 08:00-14:00",
  override_manual: false,
  notas: "Mercado semanal oficial. Toda terraza inaccesible."
}
```

---

## 4️⃣ TABLA: ZONAS

### Propósito
Define las 3 macro-zonas del restaurante con sus características generales.

### Campos

| Campo | Tipo | Configuración | Descripción | Ejemplo |
|-------|------|---------------|-------------|---------|
| **zona_id** | Single line text | PRIMARY KEY | Identificador de zona | `"terraza"`, `"sala"`, `"barra"` |
| **nombre_display** | Single line text | | Nombre amigable | `"Terraza Exterior"`, `"Sala Interior"` |
| **capacidad_total_personas** | Number | Integer | Máximo absoluto | `64`, `80`, `6` |
| **num_mesas_fisicas** | Rollup (MESAS_FISICAS) | Count | Mesas en esta zona | `16`, `17`, `2` |
| **prioridad_default** | Number | 1-5 | Preferencia general | `1` (terraza), `2` (sala), `4` (barra) |
| **caracteristicas** | Multiple select | | Tags descriptivos | `"exterior"`, `"interior"`, `"climatizada"`, `"vista"`, `"overflow"` |
| **restricciones_generales** | Long text | | Limitaciones de zona | `"Sujeta a clima"` |
| **horario_disponible** | Long text | | Cuándo está abierta | `"11:00-00:00"` |
| **notas** | Long text | | Información adicional | `"Zona premium en buen clima"` |

### Registros (3 únicos)

```javascript
{
  zona_id: "terraza",
  nombre_display: "Terraza Exterior",
  capacidad_total_personas: 64,
  prioridad_default: 1,
  caracteristicas: ["exterior", "vista", "fumadores"],
  restricciones_generales: "Sujeta a condiciones climáticas. No disponible con lluvia fuerte.",
  horario_disponible: "11:00-00:00 (variable según clima)",
  notas: "Zona premium. Primera opción cuando clima es favorable."
}

{
  zona_id: "sala",
  nombre_display: "Sala Interior",
  capacidad_total_personas: 80,
  prioridad_default: 2,
  caracteristicas: ["interior", "climatizada", "tranquila"],
  restricciones_generales: "Ninguna restricción climática.",
  horario_disponible: "11:00-00:00",
  notas: "Zona principal y confiable. Sofás muy demandados."
}

{
  zona_id: "barra",
  nombre_display: "Barra (Overflow)",
  capacidad_total_personas: 6,
  prioridad_default: 4,
  caracteristicas: ["interior", "alta", "informal", "overflow"],
  restricciones_generales: "Solo usar cuando terraza y sala llenas. Avisar incomodidad a clientes.",
  horario_disponible: "11:00-00:00",
  notas: "Última opción. Banquetas individuales NO reservables."
}
```

---

## 🔗 RELACIONES ENTRE TABLAS

### Diagrama

```
┌─────────────────┐
│     ZONAS       │
│ (3 records)     │
└────────┬────────┘
         │ 1:N
         ↓
┌─────────────────┐       ┌──────────────────────┐
│ MESAS_FISICAS   │ N:M   │ CONFIGURACIONES_     │
│ (35 records)    │←─────→│    VALIDAS           │
└────────┬────────┘       │ (50-80 records)      │
         │                └──────────┬───────────┘
         │ 1:N                       │ 1:N
         ↓                           ↓
┌─────────────────────────────────────┐
│      RESTRICCIONES_FISICAS          │
│         (20-30 records)             │
└─────────────────────────────────────┘
```

### Links Configurados

1. **MESAS_FISICAS → ZONAS**
   - Campo: `zona` (Single select)
   - Tipo: Many-to-One
   - Permite saber a qué zona pertenece cada mesa

2. **CONFIGURACIONES_VALIDAS → MESAS_FISICAS**
   - Campo: `mesas` (Multiple select linked)
   - Tipo: Many-to-Many
   - Permite definir combos de múltiples mesas

3. **RESTRICCIONES_FISICAS → MESAS_FISICAS**
   - Campo: `mesas_afectadas` (Multiple select linked)
   - Tipo: Many-to-Many
   - Permite marcar qué mesas son afectadas por cada restricción

4. **RESTRICCIONES_FISICAS → CONFIGURACIONES_VALIDAS**
   - Campo: `configs_afectadas` (Multiple select linked)
   - Tipo: Many-to-Many
   - Permite invalidar combos específicos

5. **RESTRICCIONES_FISICAS → ZONAS**
   - Campo: `zona_afectada` (Linked record)
   - Tipo: Many-to-One
   - Permite restricciones a nivel de zona completa

---

## 📈 VISTAS RECOMENDADAS

### Vista 1: "Mesas por Zona"
- Tabla base: MESAS_FISICAS
- Agrupación: Por campo `zona`
- Orden: Por `prioridad_default` ASC, luego `mesa_id` ASC
- Filtros: Ninguno (mostrar todas)
- Uso: Dashboard principal de mesas

### Vista 2: "Combos Frecuentes"
- Tabla base: CONFIGURACIONES_VALIDAS
- Filtro: `frecuencia_uso` = "muy_frecuente" OR "frecuente"
- Orden: Por `frecuencia_uso` DESC, `tiempo_setup_min` ASC
- Uso: Algoritmo de asignación (priorizar estas)

### Vista 3: "Restricciones Activas"
- Tabla base: RESTRICCIONES_FISICAS
- Filtro: `es_permanente` = true OR "condición evaluada como true"
- Orden: Por `severidad` DESC
- Uso: Validación en tiempo real

### Vista 4: "Terraza - Mapa Físico"
- Tabla base: MESAS_FISICAS
- Filtro: `zona` = "terraza"
- Vista: Gallery view (con campo `foto_mesa`)
- Uso: Visualización para staff

### Vista 5: "Setup Rápido (<3 min)"
- Tabla base: CONFIGURACIONES_VALIDAS
- Filtro: `tiempo_setup_min` ≤ 3 AND `dificultad_setup` = "facil"
- Orden: Por `num_personas` DESC
- Uso: Situaciones de alta demanda (asignar rápido)

---

## 🔐 PERMISOS Y ACCESO

### Roles Propuestos

| Rol | Crear | Leer | Actualizar | Eliminar |
|-----|-------|------|------------|----------|
| **Admin (Sistema)** | ✅ | ✅ | ✅ | ✅ |
| **Gerente** | ✅ | ✅ | ✅ | ⚠️ (solo RESTRICCIONES) |
| **Maître** | ❌ | ✅ | ⚠️ (solo `notas_operacion`) | ❌ |
| **Camarero** | ❌ | ✅ | ❌ | ❌ |
| **Algoritmo (API)** | ❌ | ✅ | ⚠️ (solo `estado_actual`) | ❌ |

---

## 🚀 PROCESO DE CARGA INICIAL

### Paso 1: Crear Tablas (30 min)
1. Crear tabla ZONAS (3 records)
2. Crear tabla MESAS_FISICAS (35 records)
3. Crear tabla CONFIGURACIONES_VALIDAS (vacía por ahora)
4. Crear tabla RESTRICCIONES_FISICAS (vacía por ahora)

### Paso 2: Cargar Datos del Workshop (2-3 horas)
5. Ingresar 3 zonas manualmente
6. Ingresar 35 mesas desde notas del workshop
7. Crear configuraciones validadas (empezar con singles, luego combos)
8. Documentar restricciones identificadas

### Paso 3: Validación Cruzada (1 hora)
9. Revisar con 2 miembros del staff
10. Corregir inconsistencias
11. Agregar fotos faltantes
12. Marcar como "✅ Validado"

### Paso 4: Integración con Backend (Siguiente fase)
13. Implementar `TableRepository` con Airtable API
14. Tests de lectura
15. Cache Redis
16. Deploy

---

## 📊 MÉTRICAS DE CALIDAD

### Checklist de Completitud

- [ ] Las 35 mesas tienen `capacidad_base` definida
- [ ] Las 35 mesas tienen coordenadas (x, y)
- [ ] Al menos 20 mesas tienen foto
- [ ] Al menos 30 configuraciones válidas documentadas
- [ ] Top 10 configuraciones tienen `frecuencia_uso` asignada
- [ ] Al menos 10 restricciones físicas documentadas
- [ ] Todas las restricciones críticas tienen `accion_requerida`
- [ ] Las 3 zonas tienen `capacidad_total_personas` calculada

### KPIs de Uso

| Métrica | Target Mes 1 | Target Mes 3 |
|---------|--------------|--------------|
| % Mesas con foto | 60% | 90% |
| % Configs con tiempo_setup medido | 70% | 95% |
| % Restricciones validadas por gerente | 80% | 100% |
| Nuevas configs descubiertas | 5-10 | 15-20 |

---

## 🛠️ MANTENIMIENTO

### Frecuencia de Actualización

| Tabla | Frecuencia | Responsable |
|-------|------------|-------------|
| MESAS_FISICAS | Trimestral | Gerente |
| CONFIGURACIONES_VALIDAS | Mensual | Maître + Feedback ML |
| RESTRICCIONES_FISICAS | Mensual (climáticas) / Anual (fijas) | Gerente |
| ZONAS | Anual | Gerente |

### Proceso de Evolución

**Nuevas configuraciones descubiertas:**
1. Staff reporta combo exitosa en feedback
2. Maître valida con 2+ usos exitosos
3. Gerente aprueba y agrega a CONFIGURACIONES_VALIDAS
4. Algoritmo ML la incorpora automáticamente

**Cambios físicos (obra, renovación):**
1. Gerente actualiza MESAS_FISICAS
2. Revisa configs afectadas (automático por links)
3. Actualiza restricciones si es necesario
4. Notifica al equipo técnico para re-sincronizar cache

---

## 📝 NOTAS DE IMPLEMENTACIÓN

### Consideraciones Técnicas

1. **IDs como Strings**: Usar `"T1"` en vez de `1` para evitar confusiones
2. **Coordenadas**: Escala en metros desde esquina SO del plano
3. **Fotos**: Máx 5MB, formato JPG/PNG, nombrar como `{mesa_id}_foto.jpg`
4. **Consistencia**: Nombres de campos en `snake_case` para API
5. **Validación**: Airtable forms para staff evita errores de tipeo

### Limitaciones Conocidas

- Airtable free tier: 1,200 records (suficiente: ~150 records totales)
- API rate limit: 5 req/sec (cache Redis mitiga esto)
- No support para geolocalización nativa (usar coordenadas x,y)
- Linked records no tienen cascade delete (manejar en backend)

### Futuras Mejoras

- [ ] Integrar con clima API para auto-activar restricciones climáticas
- [ ] Dashboard visual con plano interactivo (Canvas + Airtable)
- [ ] Historial de cambios (Airtable automático, pero exportar periódicamente)
- [ ] Migración a Supabase si necesitamos más control (Fase posterior)

---

**Última actualización**: 12 febrero 2026
**Versión**: 1.0
**Status**: ✅ Listo para implementación post-workshop
