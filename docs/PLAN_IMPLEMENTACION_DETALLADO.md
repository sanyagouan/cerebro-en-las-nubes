# Plan de Implementación Detallado - Sistema Inteligente de Asignación de Mesas

> **Restaurante**: En Las Nubes (Verdent)  
> **Fecha**: 12 febrero 2026  
> **Duración Total**: 10 semanas (2.5 meses)  
> **Enfoque**: Gradual, con validación humana exhaustiva antes de producción

---

## 🎯 OBJETIVO GLOBAL

Implementar un sistema de asignación inteligente de mesas que:
- Mejore la satisfacción del cliente (target: 4.3/5)
- Optimice la utilización del espacio (+15%)
- Ahorre tiempo al staff (60% reducción en asignación manual)
- Aprenda continuamente de feedback real

**Filosofía**: **"Humano valida primero, AI aprende después, luego AI sugiere y humano supervisa"**

---

## 📅 TIMELINE GENERAL

```
┌─────────────────────────────────────────────────────────────────┐
│ FASE 0: PREPARACIÓN         │ Semanas 1-2  │ 10 días          │
│ FASE 1: ALGORITMO BASE      │ Semanas 3-4  │ 10 días          │
│ FASE 2: PRUEBAS HUMANAS 🔥  │ Semanas 5-8  │ 20 días          │
│ FASE 3: APRENDIZAJE ML      │ Semanas 9-10 │ 10 días          │
│ FASE 4: PRODUCCIÓN GRADUAL  │ Semanas 11-12│ 10 días          │
├─────────────────────────────────────────────────────────────────┤
│ TOTAL                                      │ 60 días laborables│
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 FASE 0: PREPARACIÓN (Semanas 1-2)

### Objetivo
Establecer infraestructura base y documentar configuración física real del restaurante.

### Día 1-2: Workshop con Staff

**Actividad: Mapeo Físico de Mesas**

**Participantes:**
- Gerente del restaurante
- Host/hostess principal
- 1-2 meseros senior
- Tú (como implementador/facilitador)

**Materiales:**
- Plano impreso de terraza (16+ mesas)
- Plano de sala (17 posiciones)
- Post-its de colores
- Cámara/tablet para fotos

**Agenda (2 horas):**

**Hora 1: Terraza**
1. Identificar cada mesa en plano (T1-T16)
2. Marcar con post-its:
   - 🟢 Verde: Mesas que se pueden juntar fácilmente
   - 🟡 Amarillo: Se pueden juntar pero requiere esfuerzo
   - 🔴 Rojo: NO se pueden juntar (obstáculo físico)
3. Documentar obstáculos:
   - Árboles → Afectan a qué mesas
   - Bancos públicos → Bloquean qué combinaciones
   - Señales de tráfico → Restricciones
   - Farolas, alcorques, etc.
4. Configuraciones por clima:
   - ☀️ Sol directo: ¿Qué mesas evitar 14:00-17:00?
   - 🌧️ Lluvia: ¿Qué mesas se mojan primero?
   - 💨 Viento: ¿Qué mesas son incómodas con viento >30 km/h?

**Hora 2: Sala Interior**
1. Validar 17 posiciones identificadas:
   - S1-S8 (mesas principales)
   - SOFA 1-4 (zona sofás)
   - B5, B8 (mesas tipo barra en sala)
2. Capacidades exactas:
   - ¿S2 es realmente para 6-8 o más?
   - ¿Los sofás son 2-4 personas o hay variación?
3. Ubicaciones especiales:
   - 🪟 Mesas junto a ventana (premium)
   - 🚪 Mesas junto a entrada (menos deseables)
   - 🚻 Mesas cerca del baño (evitar si posible)
   - 🍴 Mesas cercanas a cocina (ruido)
4. Mesas ampliables:
   - ¿Qué mesas tienen auxiliares disponibles?
   - ¿Cuánto tiempo toma ampliar?

**Outputs:**
- Planos anotados (digitalizar después)
- Lista de combinaciones válidas (ej: T1+T2 ✅, T5+T6 ❌)
- Matriz de restricciones climáticas
- Fotos de configuraciones típicas

### Día 3-4: Implementar Schema Airtable L3

**Tablas a crear en Base `appQ2ZXAR68cqDmJt`:**

#### Tabla 1: `MESAS_FISICAS`

```javascript
Campos:
- mesa_id (Single line text, Primary) - Ej: "T1", "S2", "SOFA_1"
- nombre_display (Single line text) - Ej: "Terraza 1", "Sala 2", "Sofá 1"
- zona (Single select) - Opciones: Terraza, Sala, Barra
- capacidad_base (Number, integer) - Ej: 4, 6, 2
- capacidad_maxima (Number, integer) - Ej: 4, 8, 3 (con apretones)
- tipo_mesa (Single select) - Opciones: Rectangular, Cuadrada, Sofá, Alta (barra)
- es_movible (Checkbox) - ¿Se puede mover fácilmente?
- coordenada_x (Number, decimal) - Posición en plano (metros)
- coordenada_y (Number, decimal)
- ubicacion_especial (Multiple select) - Opciones: Ventana, Entrada, Baño, Cocina, Premium
- notas (Long text) - Observaciones libres
- foto (Attachment) - Foto de la mesa
- activa (Checkbox) - Default: true
- fecha_creacion (Created time)
- ultima_modificacion (Last modified time)
```

**Migrar datos:**
```python
# Script: scripts/migrate_tables_to_airtable.py

import asyncio
from pyairtable import Api
from src.core.entities.table import TABLES_CONFIG  # 23 hardcoded

AIRTABLE_TOKEN = "patAif9A1ul2XaLID..."
BASE_ID = "appQ2ZXAR68cqDmJt"

async def migrate_all_tables():
    api = Api(AIRTABLE_TOKEN)
    table = api.table(BASE_ID, 'MESAS_FISICAS')
    
    # Data desde workshop + hardcoded inicial
    mesas_reales = [
        # Barra (2)
        {
            'mesa_id': 'B1',
            'nombre_display': 'Barra 1',
            'zona': 'Barra',
            'capacidad_base': 2,
            'capacidad_maxima': 3,
            'tipo_mesa': 'Alta (barra)',
            'es_movible': False,
            'ubicacion_especial': ['Premium'],  # Vista barra
            'notas': 'Banquetas altas, incómodo para 3',
            'activa': True
        },
        # ... B2 similar
        
        # Terraza (16 identificadas en Agora, mapear en workshop)
        {
            'mesa_id': 'T1',
            'nombre_display': 'Terraza 1',
            'zona': 'Terraza',
            'capacidad_base': 4,
            'capacidad_maxima': 4,
            'tipo_mesa': 'Rectangular',
            'es_movible': True,
            'coordenada_x': 1.5,  # Rellenar en workshop
            'coordenada_y': 2.0,
            'ubicacion_especial': [],
            'notas': 'Primera fila, fácil acceso',
            'activa': True
        },
        # ... T2-T16
        
        # Sala (17 posiciones)
        {
            'mesa_id': 'S1',
            'nombre_display': 'Sala 1',
            'zona': 'Sala',
            'capacidad_base': 4,
            'capacidad_maxima': 4,
            'tipo_mesa': 'Rectangular',
            'es_movible': False,
            'ubicacion_especial': ['Ventana'],
            'notas': 'Mesa premium con vista',
            'activa': True
        },
        # ... S2-S8, SOFA_1-4, B5, B8
    ]
    
    for mesa_data in mesas_reales:
        table.create(mesa_data)
        print(f"✅ Creada: {mesa_data['mesa_id']}")

if __name__ == "__main__":
    asyncio.run(migrate_all_tables())
```

#### Tabla 2: `CONFIGURACIONES_VALIDAS`

```javascript
Campos:
- config_id (Autonumber, Primary)
- mesas (Multiple select) - Ej: ["T1", "T2"]
- capacidad_total (Number, integer) - Suma capacidades
- zona (Single select) - Terraza, Sala, Barra
- requiere_juntar (Checkbox)
- tiempo_setup_minutos (Number, integer) - Ej: 3, 5
- es_comoda (Checkbox) - ¿Configuración confortable?
- notas (Long text)
- foto_configuracion (Attachment)
- aprobada_por_staff (Checkbox) - Validada en workshop
- fecha_creacion (Created time)
```

**Popular con resultados del workshop:**
```javascript
Ejemplos:
- config_1: mesas=["T1", "T2"], capacidad=8, requiere_juntar=true, tiempo_setup=3
- config_2: mesas=["T3", "T4"], capacidad=8, requiere_juntar=true, tiempo_setup=3
- config_3: mesas=["T5", "T6"], requiere_juntar=false, notas="BLOQUEADO por árbol"
- config_4: mesas=["S2"], capacidad=8, requiere_juntar=false, notas="Mesa grande individual"
```

#### Tabla 3: `RESTRICCIONES_FISICAS`

```javascript
Campos:
- restriccion_id (Autonumber, Primary)
- tipo (Single select) - Opciones: Obstáculo fijo, Climática, Espacial, Normativa
- mesas_afectadas (Multiple select) - Link a MESAS_FISICAS
- descripcion (Long text)
- activa (Checkbox)
- severidad (Single select) - Crítica, Alta, Media, Baja
- condicion_aplicacion (Long text) - Ej: "Si llueve", "Si viento > 30 km/h"
- fecha_creacion (Created time)
```

**Ejemplos:**
```javascript
restricciones = [
    {
        'tipo': 'Obstáculo fijo',
        'mesas_afectadas': ['T5', 'T6'],
        'descripcion': 'Árbol ubicado entre T5 y T6 impide juntarlas',
        'severidad': 'Crítica',
        'activa': True
    },
    {
        'tipo': 'Climática',
        'mesas_afectadas': ['T1', 'T2', 'T3'],
        'descripcion': 'Primeras mesas se mojan con lluvia ligera',
        'severidad': 'Alta',
        'condicion_aplicacion': 'Probabilidad lluvia > 40%',
        'activa': True
    },
    {
        'tipo': 'Climática',
        'mesas_afectadas': ['T10', 'T11', 'T12'],
        'descripcion': 'Sol directo 14:00-17:00 en verano, incómodo',
        'severidad': 'Media',
        'condicion_aplicacion': 'Hora 14-17 Y mes Jun-Sep',
        'activa': True
    }
]
```

#### Tabla 4: `ZONAS`

```javascript
Campos:
- zona_id (Single line text, Primary) - "terraza", "sala", "barra"
- nombre_display (Single line text) - "Terraza", "Sala Interior", "Barra"
- descripcion (Long text)
- capacidad_total_personas (Number) - Suma de todas las mesas
- numero_mesas (Number) - Cantidad de mesas
- prioridad_default (Number, 1-5) - 5=máxima prioridad
- requiere_clima_favorable (Checkbox) - True para terraza
- notas_operacionales (Long text)
- activa (Checkbox)
```

**Data:**
```javascript
zonas = [
    {
        'zona_id': 'terraza',
        'nombre_display': 'Terraza',
        'capacidad_total_personas': 64,  # 16 mesas × 4
        'numero_mesas': 16,
        'prioridad_default': 5,  # Preferida por clientes
        'requiere_clima_favorable': True,
        'notas_operacionales': 'Verificar clima siempre. Configuración dinámica.',
        'activa': True
    },
    {
        'zona_id': 'sala',
        'nombre_display': 'Sala Interior',
        'capacidad_total_personas': 78,  # S1-S8 + sofás + B5,B8
        'numero_mesas': 17,
        'prioridad_default': 4,
        'requiere_clima_favorable': False,
        'notas_operacionales': 'Ambiente controlado, siempre disponible.',
        'activa': True
    },
    {
        'zona_id': 'barra',
        'nombre_display': 'Barra',
        'capacidad_total_personas': 6,  # B1, B2 (2-3 cada una)
        'numero_mesas': 2,
        'prioridad_default': 2,  # Última opción
        'requiere_clima_favorable': False,
        'notas_operacionales': 'Solo overflow cuando terraza/sala llenas.',
        'activa': True
    }
]
```

### Día 5-6: Implementar TableRepository

**Actualizar repository para usar Airtable:**

```python
# src/infrastructure/repositories/table_repository.py

class TableRepository:
    """
    Repository actualizado para L3 (Airtable)
    Versión 2.0 con schema completo
    """
    
    def __init__(self):
        self.api = Api(settings.AIRTABLE_TOKEN)
        self.base_id = settings.AIRTABLE_BASE_ID
        
        # Referencias a tablas
        self.mesas_table = self.api.table(self.base_id, 'MESAS_FISICAS')
        self.configs_table = self.api.table(self.base_id, 'CONFIGURACIONES_VALIDAS')
        self.restrictions_table = self.api.table(self.base_id, 'RESTRICCIONES_FISICAS')
        self.zones_table = self.api.table(self.base_id, 'ZONAS')
    
    async def get_all_active_tables(self) -> List[Table]:
        """Obtener todas las mesas activas"""
        records = self.mesas_table.all(formula="{activa} = 1")
        return [self._record_to_table(r) for r in records]
    
    async def get_tables_by_zone(self, zone: str) -> List[Table]:
        """Obtener mesas de una zona específica"""
        formula = f"AND({{zona}} = '{zone}', {{activa}} = 1)"
        records = self.mesas_table.all(formula=formula)
        return [self._record_to_table(r) for r in records]
    
    async def get_valid_configurations(
        self, 
        min_capacity: int,
        zone: Optional[str] = None
    ) -> List[TableConfiguration]:
        """Obtener configuraciones válidas que cumplan capacidad mínima"""
        formula = f"AND({{capacidad_total}} >= {min_capacity}, {{aprobada_por_staff}} = 1)"
        if zone:
            formula = f"AND({formula}, {{zona}} = '{zone}')"
        
        records = self.configs_table.all(formula=formula)
        return [self._record_to_config(r) for r in records]
    
    async def get_active_restrictions(self) -> List[PhysicalRestriction]:
        """Obtener restricciones físicas activas"""
        records = self.restrictions_table.all(formula="{activa} = 1")
        return [self._record_to_restriction(r) for r in records]
    
    async def get_climatic_restrictions(
        self, 
        weather_condition: str
    ) -> List[PhysicalRestriction]:
        """Obtener restricciones climáticas aplicables"""
        formula = f"AND({{tipo}} = 'Climática', {{activa}} = 1)"
        records = self.restrictions_table.all(formula=formula)
        
        # Filtrar por condición específica
        applicable = []
        for r in records:
            restriction = self._record_to_restriction(r)
            if self._condition_applies(restriction.condicion_aplicacion, weather_condition):
                applicable.append(restriction)
        
        return applicable
    
    def _record_to_table(self, record) -> Table:
        """Convertir record de Airtable a entidad Table"""
        fields = record['fields']
        return Table(
            id=fields['mesa_id'],
            name=fields['nombre_display'],
            zone=fields['zona'],
            capacity=fields['capacidad_base'],
            max_capacity=fields.get('capacidad_maxima', fields['capacidad_base']),
            table_type=fields['tipo_mesa'],
            is_movable=fields.get('es_movible', False),
            position=(
                fields.get('coordenada_x'),
                fields.get('coordenada_y')
            ),
            special_location=fields.get('ubicacion_especial', []),
            notes=fields.get('notas', ''),
            is_active=fields.get('activa', True)
        )
```

### Día 7-8: Setup de Logging y Monitoring

**Implementar sistema de logging detallado:**

```python
# src/infrastructure/logging/decision_logger.py

from loguru import logger
import json
from datetime import datetime

class DecisionLogger:
    """
    Logger especializado para decisiones de asignación
    Critical para debugging y aprendizaje
    """
    
    def __init__(self):
        # Configurar logger con rotation
        logger.add(
            "logs/table_assignments_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # Nuevo archivo cada día
            retention="6 months",  # Guardar 6 meses
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
            level="INFO"
        )
        
        logger.add(
            "logs/table_assignments_detailed_{time:YYYY-MM-DD}.json",
            rotation="00:00",
            retention="6 months",
            serialize=True,  # JSON estructurado
            level="DEBUG"
        )
    
    async def log_assignment_decision(
        self,
        booking: Booking,
        candidates: List[TableConfiguration],
        scores: List[float],
        selected: TableConfiguration,
        context: dict,
        execution_time_ms: float
    ):
        """
        Log completo de una decisión de asignación
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'booking': {
                'id': booking.id,
                'personas': booking.numero_personas,
                'fecha': booking.fecha.isoformat(),
                'hora': booking.hora_inicio.isoformat(),
                'zona_preferida': booking.preferencias.zona_preferida,
                'cliente_id': booking.cliente_id
            },
            'context': {
                'clima': {
                    'temperatura': context.get('weather', {}).get('temp'),
                    'lloviendo': context.get('weather', {}).get('is_raining'),
                    'viento': context.get('weather', {}).get('wind_speed')
                },
                'ocupacion_actual': context.get('occupancy_rate'),
                'hora_servicio': context.get('service_period'),  # lunch/dinner
                'reservas_posteriores': len(context.get('next_bookings', []))
            },
            'candidates': [
                {
                    'mesas': [m.id for m in c.mesas],
                    'capacidad': c.capacidad_total,
                    'zona': c.zona,
                    'requiere_juntar': c.requiere_juntar,
                    'score': scores[i]
                }
                for i, c in enumerate(candidates)
            ],
            'selected': {
                'mesas': [m.id for m in selected.mesas],
                'capacidad': selected.capacidad_total,
                'zona': selected.zona,
                'score': max(scores),
                'rank': scores.index(max(scores)) + 1
            },
            'performance': {
                'execution_time_ms': execution_time_ms,
                'candidates_generated': len(candidates)
            }
        }
        
        logger.info(f"Assignment decision for booking {booking.id}: {selected.mesas[0].id}")
        logger.debug(json.dumps(log_entry, indent=2))
    
    async def log_assignment_outcome(
        self,
        booking_id: str,
        satisfaction_rating: float,
        duration_actual_minutes: int,
        duration_estimated_minutes: int,
        staff_comments: str,
        had_complaints: bool
    ):
        """
        Log del outcome real de una asignación
        Critical para aprendizaje
        """
        outcome = {
            'timestamp': datetime.now().isoformat(),
            'booking_id': booking_id,
            'outcome': {
                'satisfaction': satisfaction_rating,
                'duration_actual': duration_actual_minutes,
                'duration_estimated': duration_estimated_minutes,
                'duration_delta': duration_actual_minutes - duration_estimated_minutes,
                'had_complaints': had_complaints,
                'staff_comments': staff_comments
            }
        }
        
        logger.info(f"Assignment outcome for {booking_id}: satisfaction={satisfaction_rating}/5")
        logger.debug(json.dumps(outcome, indent=2))
```

### Día 9-10: Testing de Infraestructura

**Checklist de validación:**

- [ ] Airtable contiene 35 mesas reales
- [ ] Al menos 20 configuraciones válidas documentadas
- [ ] Al menos 10 restricciones físicas capturadas
- [ ] TableRepository puede leer todas las mesas
- [ ] TableRepository filtra por zona correctamente
- [ ] Logger genera archivos JSON estructurados
- [ ] Redis está configurado y accesible
- [ ] Weather service funciona (API key válida)

**Script de testing:**

```python
# tests/integration/test_l3_infrastructure.py

import pytest
from src.infrastructure.repositories.table_repository import TableRepository

@pytest.mark.asyncio
async def test_can_fetch_all_tables():
    repo = TableRepository()
    tables = await repo.get_all_active_tables()
    
    assert len(tables) >= 35, "Deben existir al menos 35 mesas"
    assert any(t.zone == 'terraza' for t in tables), "Debe haber mesas en terraza"
    assert any(t.zone == 'sala' for t in tables), "Debe haber mesas en sala"
    assert any(t.zone == 'barra' for t in tables), "Debe haber mesas en barra"

@pytest.mark.asyncio
async def test_can_fetch_valid_configurations():
    repo = TableRepository()
    configs = await repo.get_valid_configurations(min_capacity=6)
    
    assert len(configs) > 0, "Deben existir configuraciones para 6+ personas"
    assert all(c.capacidad_total >= 6 for c in configs)

@pytest.mark.asyncio
async def test_can_fetch_restrictions():
    repo = TableRepository()
    restrictions = await repo.get_active_restrictions()
    
    assert len(restrictions) >= 10, "Deben existir al menos 10 restricciones"
    
    # Verificar que existen restricciones climáticas
    climatic = [r for r in restrictions if r.tipo == 'Climática']
    assert len(climatic) > 0, "Deben existir restricciones climáticas"

# Ejecutar: pytest tests/integration/ -v
```

**Entregables Fase 0:**
- ✅ Airtable L3 completo (4 tablas pobladas)
- ✅ Workshop realizado con staff (planos anotados)
- ✅ TableRepository funcionando
- ✅ Logging system configurado
- ✅ Tests de infraestructura pasando

---

## 📋 FASE 1: ALGORITMO BASE (Semanas 3-4)

### Objetivo
Implementar algoritmo híbrido funcional sin ML, solo heurísticas fijas.

### Día 11-13: Implementar Generación de Candidatos (CSP + FFD)

```python
# src/application/services/candidate_generator.py

from typing import List, Optional
from itertools import combinations

class CandidateGenerator:
    """
    Genera candidatos válidos usando CSP + First-Fit Decreasing
    """
    
    def __init__(self, table_repo: TableRepository):
        self.table_repo = table_repo
    
    async def generate_candidates(
        self,
        booking: Booking,
        context: AssignmentContext
    ) -> List[TableConfiguration]:
        """
        Pipeline completo de generación
        """
        candidates = []
        personas = booking.numero_personas
        
        # PASO 1: Filtrar mesas disponibles (RESTRICCIONES DURAS)
        available_tables = await self._get_available_tables(booking, context)
        
        if not available_tables:
            return []  # No hay mesas disponibles
        
        # PASO 2: Aplicar restricciones climáticas
        if context.weather:
            available_tables = await self._filter_by_weather(
                available_tables, 
                context.weather
            )
        
        # PASO 3: Obtener restricciones físicas
        physical_restrictions = await self.table_repo.get_active_restrictions()
        
        # ESTRATEGIA 1: Match exacto (Best-Fit)
        exact_matches = self._find_exact_capacity_matches(
            available_tables, 
            personas
        )
        candidates.extend(exact_matches)
        
        # ESTRATEGIA 2: Mesa un poco más grande (hasta +2 personas)
        larger_tables = self._find_slightly_larger_tables(
            available_tables,
            personas,
            max_waste=2
        )
        candidates.extend(larger_tables)
        
        # ESTRATEGIA 3: Configuraciones pre-aprobadas (L3)
        approved_configs = await self._find_approved_combinations(
            personas,
            booking.preferencias.zona_preferida
        )
        # Filtrar solo las que tienen mesas disponibles
        approved_available = [
            c for c in approved_configs
            if all(self._is_available(m, available_tables) for m in c.mesas)
        ]
        candidates.extend(approved_available)
        
        # ESTRATEGIA 4: Combinaciones nuevas (FFD - Exploration)
        if len(candidates) < 5:  # Si tenemos pocos candidatos, explorar
            new_combos = await self._generate_ffd_combinations(
                available_tables,
                personas,
                physical_restrictions
            )
            candidates.extend(new_combos)
        
        # PASO 4: Validar restricciones físicas en todos
        valid_candidates = [
            c for c in candidates
            if self._validate_physical_restrictions(c, physical_restrictions)
        ]
        
        # PASO 5: Overflow a barra si necesario
        if not valid_candidates and personas <= 3:
            barra_tables = [t for t in available_tables if t.zone == 'barra']
            valid_candidates = [
                TableConfiguration([t], t.capacity, False, 0, 'barra')
                for t in barra_tables
            ]
        
        return valid_candidates
    
    async def _get_available_tables(
        self,
        booking: Booking,
        context: AssignmentContext
    ) -> List[Table]:
        """
        Obtener mesas disponibles en el horario de la reserva
        """
        all_tables = await self.table_repo.get_all_active_tables()
        
        # Consultar Redis por ocupación
        occupied = await context.redis.get_occupied_tables(
            start=booking.hora_inicio,
            end=booking.hora_fin
        )
        
        occupied_ids = set(occupied)
        available = [t for t in all_tables if t.id not in occupied_ids]
        
        return available
    
    async def _filter_by_weather(
        self,
        tables: List[Table],
        weather: WeatherCondition
    ) -> List[Table]:
        """
        Filtrar mesas según clima
        """
        # Si llueve o viento fuerte, bloquear terraza
        if weather.is_raining or weather.wind_speed > 40:
            return [t for t in tables if t.zone != 'terraza']
        
        # Si mucho sol (verano + mediodía), obtener restricciones
        if weather.is_sunny and 14 <= datetime.now().hour <= 17:
            sun_restrictions = await self.table_repo.get_climatic_restrictions(
                'sol_directo'
            )
            blocked_tables = set()
            for r in sun_restrictions:
                blocked_tables.update(r.mesas_afectadas)
            
            tables = [t for t in tables if t.id not in blocked_tables]
        
        return tables
    
    def _find_exact_capacity_matches(
        self,
        tables: List[Table],
        personas: int
    ) -> List[TableConfiguration]:
        """
        Buscar mesas con capacidad exacta
        """
        matches = []
        for table in tables:
            if table.capacity == personas:
                matches.append(TableConfiguration(
                    mesas=[table],
                    capacidad_total=table.capacity,
                    requiere_juntar=False,
                    minutos_setup=0,
                    zona=table.zone
                ))
        return matches
    
    async def _generate_ffd_combinations(
        self,
        tables: List[Table],
        personas: int,
        restrictions: List[PhysicalRestriction]
    ) -> List[TableConfiguration]:
        """
        First-Fit Decreasing: generar combinaciones de 2 mesas
        """
        # Ordenar por capacidad descendente (FFD)
        sorted_tables = sorted(tables, key=lambda t: t.capacity, reverse=True)
        
        combos = []
        # Limitar a primeras 12 mesas para evitar explosión combinatoria
        for t1, t2 in combinations(sorted_tables[:12], 2):
            total_capacity = t1.capacity + t2.capacity
            
            # Solo considerar si:
            # 1. Capacidad suficiente
            # 2. No desperdiciar mucho (máx +2 personas)
            # 3. Misma zona (no juntar terraza con sala)
            if personas <= total_capacity <= personas + 2:
                if t1.zone == t2.zone:
                    # Verificar si son juntables físicamente
                    if self._are_combinable(t1, t2, restrictions):
                        setup_time = self._estimate_setup_time(t1, t2)
                        combos.append(TableConfiguration(
                            mesas=[t1, t2],
                            capacidad_total=total_capacity,
                            requiere_juntar=True,
                            minutos_setup=setup_time,
                            zona=t1.zone
                        ))
        
        return combos
    
    def _are_combinable(
        self,
        t1: Table,
        t2: Table,
        restrictions: List[PhysicalRestriction]
    ) -> bool:
        """
        Verificar si dos mesas se pueden juntar físicamente
        """
        # Buscar restricciones que bloqueen esta combinación
        for r in restrictions:
            if r.tipo in ['Obstáculo fijo', 'Espacial']:
                if t1.id in r.mesas_afectadas and t2.id in r.mesas_afectadas:
                    # Hay restricción que las afecta a ambas
                    if 'no juntar' in r.descripcion.lower() or 'impide' in r.descripcion.lower():
                        return False
        
        # Si ambas son movibles y están en misma zona, asumimos juntables
        if t1.is_movable and t2.is_movable and t1.zone == t2.zone:
            return True
        
        # Si están físicamente cerca (distancia < 3 metros)
        if t1.position and t2.position:
            x1, y1 = t1.position
            x2, y2 = t2.position
            distance = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            return distance < 3.0
        
        # Default: no juntar si no tenemos info
        return False
```

### Día 14-16: Implementar Scoring Multi-Criterio

```python
# src/application/services/table_scorer.py

class TableScorer:
    """
    Calcula scores multi-criterio para candidatos
    Versión 1.0: Weights fijos (sin ML)
    """
    
    def __init__(self):
        # Weights basados en mejores prácticas de industria
        self.weights = {
            'fit_capacidad': 0.35,       # Minimizar desperdicio
            'experiencia_historica': 0.25,  # Satisfacción pasada
            'preferencias_cliente': 0.20,   # Indoor vs outdoor
            'facilidad_setup': 0.10,     # Tiempo configurar
            'impacto_futuro': 0.10,      # No bloquear después
        }
    
    async def score_candidate(
        self,
        candidato: TableConfiguration,
        booking: Booking,
        context: AssignmentContext
    ) -> float:
        """
        Calcular score final (0-1) para un candidato
        """
        scores = {}
        
        # CRITERIO 1: Fit de capacidad (35%)
        scores['fit_capacidad'] = self._score_capacity_fit(
            candidato.capacidad_total,
            booking.numero_personas
        )
        
        # CRITERIO 2: Experiencia histórica (25%)
        scores['experiencia_historica'] = await self._score_historical_experience(
            candidato,
            booking,
            context
        )
        
        # CRITERIO 3: Preferencias del cliente (20%)
        scores['preferencias_cliente'] = self._score_client_preferences(
            candidato,
            booking,
            context
        )
        
        # CRITERIO 4: Facilidad de setup (10%)
        scores['facilidad_setup'] = self._score_setup_ease(candidato)
        
        # CRITERIO 5: Impacto en futuras reservas (10%)
        scores['impacto_futuro'] = await self._score_future_impact(
            candidato,
            booking,
            context
        )
        
        # WEIGHTED SUM
        final_score = sum(scores[k] * self.weights[k] for k in scores)
        
        return final_score
    
    def _score_capacity_fit(self, capacidad_mesa: int, personas: int) -> float:
        """
        Score basado en ajuste de capacidad
        1.0 = perfect fit, <1.0 = desperdicio
        """
        if personas > capacidad_mesa:
            return 0.0  # No cabe
        
        if personas == capacidad_mesa:
            return 1.0  # Perfect fit
        
        # Penalizar desperdicio cuadráticamente
        ratio = personas / capacidad_mesa
        return ratio ** 2
    
    async def _score_historical_experience(
        self,
        candidato: TableConfiguration,
        booking: Booking,
        context: AssignmentContext
    ) -> float:
        """
        Score basado en satisfacción histórica (L2 Memory)
        Versión 1.0: Usar defaults si no hay historial
        """
        # Buscar en L2 (MCP Memory) satisfacción promedio
        historical_data = await context.l2_memory.get_satisfaction_for_config(
            config_id=candidato.get_id(),
            similar_size=booking.numero_personas
        )
        
        if historical_data and historical_data.count >= 3:
            # Tenemos datos históricos confiables
            return historical_data.avg_rating / 5.0
        
        # Default: asumir satisfacción media-alta para nuevas configs
        # Zona premium (terraza) = 0.85, sala = 0.80, barra = 0.65
        default_scores = {
            'terraza': 0.85,
            'sala': 0.80,
            'barra': 0.65
        }
        return default_scores.get(candidato.zona, 0.75)
    
    def _score_client_preferences(
        self,
        candidato: TableConfiguration,
        booking: Booking,
        context: AssignmentContext
    ) -> float:
        """
        Score basado en preferencias del cliente
        """
        # Si cliente especificó zona preferida
        if booking.preferencias.zona_preferida:
            if candidato.zona == booking.preferencias.zona_preferida:
                return 1.0  # Cumple preferencia
            else:
                return 0.3  # No cumple pero no descalifica
        
        # Sin preferencia explícita: usar patrones aprendidos
        # Versión 1.0: Usar heurística simple
        # - Terraza preferida en buen clima
        # - Sala preferida en mal clima o noche
        
        if context.weather and context.weather.is_good:
            if candidato.zona == 'terraza':
                return 0.9
            elif candidato.zona == 'sala':
                return 0.7
            else:  # barra
                return 0.4
        else:
            # Mal clima o noche
            if candidato.zona == 'sala':
                return 0.9
            elif candidato.zona == 'terraza':
                return 0.3  # Terraza con mal clima
            else:  # barra
                return 0.5
    
    def _score_setup_ease(self, candidato: TableConfiguration) -> float:
        """
        Score basado en facilidad de preparar la mesa
        """
        if not candidato.requiere_juntar:
            return 1.0  # Mesa lista para usar
        
        # Penalizar por tiempo de setup
        # 0 min = 1.0, 10 min = 0.0
        setup_time = candidato.minutos_setup
        return max(0.0, 1.0 - (setup_time / 10.0))
    
    async def _score_future_impact(
        self,
        candidato: TableConfiguration,
        booking: Booking,
        context: AssignmentContext
    ) -> float:
        """
        Score basado en impacto en reservas posteriores
        ¿Esta asignación bloquea buenas opciones después?
        """
        # Obtener próximas reservas en las siguientes 2 horas
        next_bookings = await context.redis.get_next_bookings(
            after=booking.hora_fin,
            hours=2
        )
        
        if not next_bookings:
            return 1.0  # Sin reservas posteriores, sin impacto
        
        # Simular: ¿Cuántas opciones quedan después de asignar esta mesa?
        remaining_capacity = await self._simulate_remaining_capacity(
            candidato,
            booking,
            next_bookings,
            context
        )
        
        # Si quedan muchas opciones, buen score
        # Normalizar: 5+ opciones = 1.0, 0 opciones = 0.0
        return min(1.0, remaining_capacity / 5.0)
```

### Día 17-18: Integración Completa del Algoritmo

```python
# src/application/services/intelligent_table_assignment_service.py

class IntelligentTableAssignmentService:
    """
    Servicio principal de asignación inteligente
    Versión 1.0: Algoritmo híbrido sin ML
    """
    
    def __init__(
        self,
        table_repo: TableRepository,
        candidate_generator: CandidateGenerator,
        scorer: TableScorer,
        decision_logger: DecisionLogger
    ):
        self.table_repo = table_repo
        self.generator = candidate_generator
        self.scorer = scorer
        self.logger = decision_logger
        self.redis = get_redis_client()
    
    async def assign_table(
        self,
        booking: Booking
    ) -> TableAssignment:
        """
        Pipeline completo de asignación inteligente
        """
        start_time = time.time()
        
        try:
            # FASE 1: Cargar contexto completo
            context = await self._build_context(booking)
            
            # FASE 2: Generar candidatos (CSP + FFD)
            candidates = await self.generator.generate_candidates(
                booking, 
                context
            )
            
            if not candidates:
                raise NoAvailableTablesError(
                    f"No hay mesas disponibles para {booking.numero_personas} personas"
                )
            
            # FASE 3: Calcular scores para todos los candidatos
            scored_candidates = []
            for candidato in candidates:
                score = await self.scorer.score_candidate(
                    candidato,
                    booking,
                    context
                )
                scored_candidates.append((candidato, score))
            
            # FASE 4: Seleccionar el mejor
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            best_candidate, best_score = scored_candidates[0]
            
            # FASE 5: Ejecutar asignación
            assignment = await self._execute_assignment(
                best_candidate,
                booking,
                best_score
            )
            
            # FASE 6: Registrar decisión para análisis posterior
            execution_time = (time.time() - start_time) * 1000  # ms
            await self.logger.log_assignment_decision(
                booking=booking,
                candidates=[c[0] for c in scored_candidates],
                scores=[c[1] for c in scored_candidates],
                selected=best_candidate,
                context=context.to_dict(),
                execution_time_ms=execution_time
            )
            
            # FASE 7: Programar feedback post-servicio
            await self._schedule_feedback_collection(
                assignment.id,
                booking.duracion_estimada
            )
            
            return assignment
            
        except Exception as e:
            logger.error(f"Error en asignación inteligente: {e}")
            # Fallback a asignación simple
            return await self._fallback_simple_assignment(booking)
    
    async def _build_context(self, booking: Booking) -> AssignmentContext:
        """
        Construir contexto completo para decisión
        """
        return AssignmentContext(
            weather=await self._get_weather(),
            occupancy_rate=await self._get_current_occupancy(),
            service_period=self._detect_service_period(booking.hora_inicio),
            next_bookings=await self._get_next_bookings(booking),
            l2_memory=MCP_Memory_Client(),
            redis=self.redis,
            l3_airtable=self.table_repo
        )
```

### Día 19-20: Testing de Algoritmo Base

**Casos de prueba:**

```python
# tests/integration/test_intelligent_assignment.py

@pytest.mark.asyncio
async def test_assigns_exact_match_when_available():
    """
    Caso simple: Mesa de capacidad exacta disponible
    """
    service = IntelligentTableAssignmentService(...)
    
    booking = create_test_booking(personas=4, zona_preferida='sala')
    assignment = await service.assign_table(booking)
    
    assert assignment is not None
    assert assignment.capacidad_total == 4  # Exact match
    assert assignment.zona == 'sala'

@pytest.mark.asyncio
async def test_combines_tables_for_large_group():
    """
    Grupo grande: Debe juntar 2 mesas
    """
    booking = create_test_booking(personas=8, zona_preferida='terraza')
    assignment = await service.assign_table(booking)
    
    assert assignment is not None
    assert len(assignment.mesas) == 2  # Dos mesas juntadas
    assert assignment.capacidad_total >= 8

@pytest.mark.asyncio
async def test_blocks_terraza_when_raining():
    """
    Lluvia: No debe asignar terraza
    """
    # Mock weather service para simular lluvia
    with mock_weather(is_raining=True):
        booking = create_test_booking(personas=4, zona_preferida='terraza')
        assignment = await service.assign_table(booking)
        
        # Debe asignar sala en lugar de terraza
        assert assignment.zona != 'terraza'

@pytest.mark.asyncio
async def test_prefers_better_scoring_option():
    """
    Múltiples opciones: Debe elegir la de mayor score
    """
    booking = create_test_booking(personas=4)
    
    # Forzar múltiples candidatos disponibles
    # Verificar que elige terraza (score más alto) sobre barra
    assignment = await service.assign_table(booking)
    
    assert assignment.zona in ['terraza', 'sala']  # No barra
```

**Entregables Fase 1:**
- ✅ Algoritmo híbrido completo implementado
- ✅ Generación de candidatos funcional (5-15 por reserva)
- ✅ Scoring multi-criterio funcionando
- ✅ Tests automatizados pasando (10+ test cases)
- ✅ Performance <200ms por asignación
- ✅ Logging detallado configurado

---

## 🧪 FASE 2: PRUEBAS HUMANAS (Semanas 5-8) 🔥

### Objetivo
**Validar sistema con operación real paralela, recopilar feedback masivo**

*(Contenido detallado ya está en el documento de investigación, sección "FASE 2: OPERACIÓN PARALELA CON HUMANOS")*

**Resumen ejecutivo:**
- 4 semanas de operación paralela
- Sistema AI sugiere, humano decide y registra feedback
- Target: 800+ decisiones con feedback completo
- Métricas: Agreement rate >70%, Satisfaction >4.2/5
- Output: Dataset robusto para entrenar ML

---

## 🤖 FASE 3: APRENDIZAJE ML (Semanas 9-10)

*(Contenido detallado en documento de investigación, sección "FASE 3: APRENDIZAJE SUPERVISADO")*

**Resumen:**
- Entrenar Gradient Boosting Regressor con 800+ decisiones
- Features: 15+ características (capacidad, clima, histórico, etc.)
- Target: Satisfacción del cliente (0-1)
- Validación: MAE <0.15, R² >0.60
- A/B testing interno: ML vs heurística

---

## 🚀 FASE 4: PRODUCCIÓN (Semanas 11-12)

*(Contenido detallado en documento de investigación, sección "FASE 4: PRODUCCIÓN GRADUAL")*

**Semana 11:** 30% reservas con AI (soft launch)  
**Semana 12:** 100% con AI (full production)  
**Kill-switch:** Disponible siempre  
**Staff override:** Permitido siempre  

---

## ✅ CHECKLIST FINAL DE ENTREGA

### Infraestructura
- [ ] Airtable L3: 4 tablas pobladas (35 mesas, 20+ configs, 10+ restricciones)
- [ ] Redis L1 configurado y funcionando
- [ ] NotebookLM L2 con primeros documentos
- [ ] MCP Memory con entidades iniciales
- [ ] Logging detallado operativo

### Código
- [ ] `IntelligentTableAssignmentService` completo
- [ ] `CandidateGenerator` con CSP + FFD
- [ ] `TableScorer` con multi-criterio
- [ ] `FeedbackCollector` para Fase 2
- [ ] `ContinuousLearningService` para Fase 5
- [ ] ML model training pipeline

### Testing
- [ ] 15+ tests unitarios pasando
- [ ] 10+ tests de integración pasando
- [ ] Performance <200ms verificado
- [ ] Load testing (50 reservas concurrentes)

### Operacional
- [ ] Staff capacitado (workshop + training)
- [ ] Tablet interface para feedback funcional
- [ ] Dashboard de monitoring en tiempo real
- [ ] Alertas configuradas (Slack/email)
- [ ] Runbook operacional documentado

### Métricas
- [ ] Sistema captura satisfaction ratings
- [ ] Sistema captura agreement rate
- [ ] Sistema captura table turnover time
- [ ] Dashboard muestra métricas en vivo

---

## 🎯 MÉTRICAS DE ÉXITO - RESUMEN

| Fase | Métrica Clave | Target | Validación |
|------|--------------|--------|------------|
| Fase 1 | Performance | <200ms | Load test |
| Fase 2 | Agreement Rate | >70% | Logs diarios |
| Fase 2 | Satisfaction | >4.2/5 | Feedback forms |
| Fase 3 | ML MAE | <0.15 | Train/test split |
| Fase 4 | Override Rate | <20% | Monitoring |
| Fase 5 | Revenue Improvement | +10% | Analytics mes 6 |

---

## 📞 PRÓXIMOS PASOS INMEDIATOS

**Para comenzar implementación:**

1. **Aprobar este plan** con gerente + staff clave
2. **Agendar workshop** (Día 1-2): 2 horas con equipo completo
3. **Iniciar Fase 0**: Migración a Airtable + mapeo físico
4. **Setup repo Git**: Branch `feature/intelligent-table-assignment`
5. **Comunicar a equipo**: Email explicando proyecto + timeline

**¿Listo para comenzar?** 🚀

---

**Documento generado**: 12 febrero 2026  
**Versión**: 1.0  
**Autor**: Sistema Verdent Assistant  
**Requiere**: Aprobación para iniciar Fase 0
