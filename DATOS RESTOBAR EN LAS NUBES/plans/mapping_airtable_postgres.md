# Mapeo de Campos - Airtable ↔ PostgreSQL

## Descripción
Este documento define la equivalencia entre campos de Airtable y PostgreSQL para facilitar la sincronización entre ambos sistemas.

## Tablas Equivalentes

### 1. Tabla: Clientes (Airtable) ↔ customers (PostgreSQL)

| Campo Airtable | Campo PostgreSQL | Tipo PostgreSQL | Notas |
|---------------|------------------|------------------|-------|
| ID (Record ID) | customer_id | UUID | ID único del cliente |
| Nombre | name | VARCHAR(100) | Nombre completo |
| Teléfono | phone | VARCHAR(20) | Único, formato +34 XXX XXX XXX |
| WhatsApp | whatsapp | VARCHAR(20) | Número de WhatsApp |
| Email | email | VARCHAR(100) | Email de contacto |
| Preferencias | preferences | JSONB | Zona preferida, alergias, etc. |
| Total Reservas | total_reservations | INTEGER | Contador de reservas |
| Puntos Lealtad | loyalty_points | INTEGER | Sistema de lealtad |
| Última Visita | last_visit_date | DATE | Fecha última visita |
| Consentimiento GDPR | data_consent | BOOLEAN | Consentimiento datos |
| Fecha Consentimiento | consent_date | TIMESTAMP | Fecha de aceptación |
| Creado el | created_at | TIMESTAMP | Fecha de creación |
| Actualizado el | updated_at | TIMESTAMP | Fecha última actualización |

**Notas de sincronización:**
- El `Record ID` de Airtable se mapea a `customer_id` de PostgreSQL
- Los campos JSONB en PostgreSQL (`preferences`) se deserializan en Airtable como campos separados o campos de fórmula
- Para migración: crear primero en Airtable, luego sincronizar a PostgreSQL usando el Record ID como referencia

---

### 2. Tabla: Reservas (Airtable) ↔ reservations (PostgreSQL)

| Campo Airtable | Campo PostgreSQL | Tipo PostgreSQL | Notas |
|---------------|------------------|------------------|-------|
| ID (Record ID) | id | UUID | ID único de reserva |
| Cliente (Linked) | customer_id | UUID (FK) | Referencia a customers |
| Mesa (Linked) | table_id | VARCHAR(10) (FK) | Referencia a tables |
| Nombre Cliente | customer_name | VARCHAR(100) | Redundancia para queries rápidas |
| Teléfono Cliente | customer_phone | VARCHAR(20) | Redundancia para queries rápidas |
| Personas (PAX) | guest_count | INTEGER | Número de personas |
| Fecha | service_date | DATE | Fecha de servicio |
| Hora | service_time | TIME | Hora de servicio |
| Estado | status | ENUM | pendiente/confirmada/cancelada/no_show/completada |
| Código Confirmación | confirmation_code | VARCHAR(8) | Código único (8 caracteres) |
| Enviado el | confirmation_sent_at | TIMESTAMP | Fecha envío WhatsApp |
| Confirmado el | confirmed_at | TIMESTAMP | Fecha confirmación |
| Solicitudes Especiales | special_requests | JSONB | Trona, descorche, etc. |
| Origen | source | VARCHAR(20) | VAPI/manual/web/whatsapp |
| Creado por | created_by | VARCHAR(50) | Usuario/sistema |
| Sistema Origen | origin_system | VARCHAR(20) | VAPI/n8n/manual |
| Creado el | created_at | TIMESTAMP | Fecha de creación |
| Actualizado el | updated_at | TIMESTAMP | Fecha última actualización |

**Notas de sincronización:**
- Los campos `customer_name` y `customer_phone` en PostgreSQL son redundantes pero necesarios para queries rápidas sin JOIN
- El campo `special_requests` (JSONB) en PostgreSQL se mapea a múltiples campos en Airtable:
  - `Trona` (Checkbox)
  - `Descorche` (Checkbox)
  - `Cerca Ventana` (Checkbox)
  - `Accesibilidad` (Checkbox)
  - `Notas Adicionales` (Text)
- El estado en Airtable puede ser un Single Select con opciones: Pendiente, Confirmada, Cancelada, No Show, Completada

---

### 3. Tabla: Mesas (Airtable) ↔ tables (PostgreSQL)

| Campo Airtable | Campo PostgreSQL | Tipo PostgreSQL | Notas |
|---------------|------------------|------------------|-------|
| ID (Record ID) | table_id | VARCHAR(10) | Identificador (ej: A1, B2, C2-C) |
| Capacidad Mínima | capacity_min | INTEGER | Personas mínimas |
| Capacidad Máxima | capacity_max | INTEGER | Personas máximas |
| Zona | zone | ENUM | interior/terraza |
| Notas | notes | TEXT | Ej: JUNTO AL BAÑO |
| Mesa Auxiliar | is_auxiliary | BOOLEAN | Para combinación de grupos |
| Prioridad | priority | INTEGER | Orden de asignación |
| Coordenada X | coordinates_x | DECIMAL(8,2) | Posición X |
| Coordenada Y | coordinates_y | DECIMAL(8,2) | Posición Y |
| Sillas Niño | features.sillas_nino | JSONB | Número de sillas infantiles |
| Accesibilidad Ruedas | features.accesibilidad_ruedas | JSONB | Accesible en silla de ruedas |
| Cerca Ventana | features.cerca_ventana | JSONB | Preferencia ventana |
| Preferencia Grupos | features.preferencia_grupos | JSONB | Adecuada para grupos |
| Activa | is_active | BOOLEAN | Mesa disponible |
| Creado el | created_at | TIMESTAMP | Fecha de creación |
| Actualizado el | updated_at | TIMESTAMP | Fecha última actualización |

**Notas de sincronización:**
- El `table_id` en PostgreSQL es VARCHAR(10) para permitir identificadores como "A1", "B2", "C2-C" (mesas combinables)
- Los campos anidados en `features` (JSONB) se mapean a campos separados en Airtable
- Para mesas combinables (ej: C2-C), el `table_id` en Airtable puede ser una fórmula que concatena dos mesas

---

### 4. Tabla: Disponibilidad (Airtable) ↔ availability_slots (PostgreSQL)

| Campo Airtable | Campo PostgreSQL | Tipo PostgreSQL | Notas |
|---------------|------------------|------------------|-------|
| ID (Record ID) | id | UUID | ID único de slot |
| Mesa (Linked) | table_id | VARCHAR(10) (FK) | Referencia a tables |
| Fecha | service_date | DATE | Fecha de servicio |
| Hora | service_time | TIME | Hora de servicio |
| Disponible | available | BOOLEAN | true/false |
| Bloqueado por | locked_by_reservation_id | UUID (FK) | Referencia a reservations |
| Creado el | created_at | TIMESTAMP | Fecha de creación |

**Notas de sincronización:**
- Los slots de disponibilidad se generan automáticamente en PostgreSQL basados en:
  - Horarios del restaurante (restaurant_info)
  - Turnos configurados (restaurants.turn_config)
  - Mesas activas (tables.is_active)
- En Airtable, esta tabla puede ser de solo lectura o generada por vistas
- La combinación única `(table_id, service_date, service_time)` evita duplicados

---

### 5. Tabla: Logs de Auditoría (Airtable) ↔ audit_log (PostgreSQL)

| Campo Airtable | Campo PostgreSQL | Tipo PostgreSQL | Notas |
|---------------|------------------|------------------|-------|
| ID (Record ID) | id | UUID | ID único de log |
| Tipo Entidad | entity_type | ENUM | reservation/table/slot/customer |
| ID Entidad | entity_id | UUID | ID de la entidad afectada |
| Acción | action | ENUM | create/confirm/cancel/lock/unlock/update/delete |
| Detalles | details | JSONB | Información adicional |
| Valores Anteriores | old_values | JSONB | Estado antes del cambio |
| Nuevos Valores | new_values | JSONB | Estado después del cambio |
| Realizado por | performed_by | VARCHAR(50) | system/staff/customer |
| Dirección IP | ip_address | INET | IP del origen |
| User Agent | user_agent | TEXT | Navegador/dispositivo |
| Sistema Fuente | system_source | VARCHAR(20) | n8n/VAPI/manual |
| Workflow ID | workflow_id | VARCHAR(50) | ID del workflow n8n |
| Creado el | created_at | TIMESTAMP | Fecha de creación |

**Notas de sincronización:**
- Los campos JSONB (`details`, `old_values`, `new_values`) se deserializan en Airtable como campos separados
- El campo `entity_type` en Airtable puede ser un Single Select
- El campo `action` en Airtable puede ser un Single Select con las opciones listadas

---

### 6. Tabla: Información Restaurante (Airtable) ↔ restaurant_info (PostgreSQL)

| Campo Airtable | Campo PostgreSQL | Tipo PostgreSQL | Notas |
|---------------|------------------|------------------|-------|
| Clave | key | VARCHAR(50) (PK) | Identificador único |
| Valor | value | TEXT | Valor de la configuración |
| Tipo Valor | value_type | VARCHAR(20) | text/json/number/boolean |
| Descripción | description | TEXT | Descripción del campo |
| Actualizado el | updated_at | TIMESTAMP | Fecha última actualización |

**Notas de sincronización:**
- Esta tabla contiene configuración global del restaurante
- Ejemplos de registros:
  - `phone_number`: +34 941 57 84 51
  - `address`: Dirección física
  - `opening_hours`: JSON con horarios
  - `max_reservation_days`: 30
  - `cancellation_policy`: 24 (horas)
  - `confirmation_timeout`: 2 (horas)

---

## Consideraciones para Sincronización

### Estrategia de Sincronización Bidireccional

#### Dirección Airtable → PostgreSQL (Fase 1)
1. **Airtable como fuente de verdad inicial**
   - Los workflows de n8n escriben directamente en Airtable
   - Un workflow de sincronización lee cambios de Airtable y replica en PostgreSQL
   - Prioridad: latencia mínima para el usuario

2. **Mapeo de IDs**
   - Usar `Record ID` de Airtable como `customer_id`/`id` en PostgreSQL
   - Mantener un campo `airtable_record_id` en PostgreSQL si es necesario para trazabilidad

3. **Manejo de JSONB**
   - Los campos JSONB en PostgreSQL se deserializan en campos separados de Airtable
   - Ejemplo: `preferences` (JSONB) → `Zona Preferida`, `Alergias`, `Ocasiones Especiales`

#### Dirección PostgreSQL → Airtable (Fase 2 - Futura)
1. **PostgreSQL como fuente de verdad**
   - Los workflows de n8n escriben directamente en PostgreSQL
   - Un workflow de sincronización replica cambios en Airtable (dashboard)
   - Airtable se convierte en dashboard de solo lectura

2. **Migración de datos**
   - Script de migración para mover datos de Airtable a PostgreSQL
   - Validar integridad referencial antes de activar PostgreSQL como fuente principal

### Reglas de Transformación de Datos

#### Fechas y Horas
- **Airtable**: Usa campos Date y Time separados
- **PostgreSQL**: Usa `DATE` y `TIME` separados
- **Transformación**: Directa, sin conversión necesaria

#### Enums
- **Airtable**: Usa Single Select con opciones predefinidas
- **PostgreSQL**: Usa tipos ENUM
- **Transformación**: Mapeo directo de valor a valor ENUM

#### JSONB
- **Airtable**: Campos separados o campos de fórmula
- **PostgreSQL**: JSONB con estructura definida
- **Transformación**: 
  - Al leer de Airtable: serializar campos en JSONB
  - Al escribir en Airtable: deserializar JSONB en campos separados

#### UUIDs
- **Airtable**: Usa `Record ID` (string generado por Airtable)
- **PostgreSQL**: Usa `UUID` generado por `uuid_generate_v4()`
- **Transformación**: 
  - Al migrar: usar `Record ID` de Airtable como `customer_id`
  - Al crear nuevo: generar UUID en PostgreSQL y sincronizar a Airtable

### Campos Calculados en Airtable

Algunos campos en Airtable pueden ser fórmulas que no existen en PostgreSQL:

| Campo Airtable | Fórmula | Equivalente PostgreSQL |
|---------------|---------|----------------------|
| Duración Reserva | `Hora Fin - Hora Inicio` | Calculado en workflow |
| Estado Formateado | `IF(Estado="pendiente", "⏳ Pendiente", ...)` | Formateado en frontend |
| Nombre Completo | `Nombre & " (" & Teléfono & ")")` | Concatenación en query |
| Días hasta Reserva | `DATETIME_DIFF(Fecha, TODAY())` | Calculado en workflow |

**Nota**: Estos campos calculados NO se almacenan en PostgreSQL, se calculan en tiempo real en los workflows o frontend.

---

## Estrategia de Migración

### Fase 1: Preparación
1. Crear todas las tablas en PostgreSQL con el esquema definido
2. Crear índices necesarios para rendimiento
3. Crear vistas y funciones útiles
4. Insertar datos iniciales en `restaurant_info`

### Fase 2: Migración de Datos
1. **Exportar datos de Airtable**
   - Usar API de Airtable para exportar todas las tablas
   - Incluir `Record ID` para mapeo

2. **Transformar y cargar en PostgreSQL**
   - Mapear `Record ID` → `customer_id`/`id`
   - Transformar campos JSONB apropiadamente
   - Validar constraints (UNIQUE, NOT NULL, CHECK)

3. **Validar integridad**
   - Verificar que todos los registros de Airtable están en PostgreSQL
   - Verificar que las relaciones (FKs) son correctas
   - Ejecutar queries de validación

### Fase 3: Sincronización Activa
1. **Configurar webhooks de Airtable**
   - Webhook en `customers` para detectar cambios
   - Webhook en `reservations` para detectar cambios
   - Webhook en `tables` para detectar cambios

2. **Implementar workflow de sincronización en n8n**
   - Trigger: Webhook de Airtable
   - Acción: Leer cambio → Actualizar PostgreSQL
   - Logging: Registrar en `audit_log`

3. **Monitorear sincronización**
   - Verificar que no hay registros huérfanos
   - Verificar que no hay duplicados
   - Alertar en caso de fallo de sincronización

---

## Consideraciones de Rendimiento

### Índices Críticos
Los siguientes índices en PostgreSQL son esenciales para queries frecuentes:

```sql
-- Queries de disponibilidad (más frecuentes)
CREATE INDEX idx_reservations_date_time ON reservations(service_date, service_time);
CREATE INDEX idx_availability_table_date ON availability_slots(table_id, service_date);

-- Queries de cliente
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_reservations_phone ON reservations(customer_phone);

-- Queries de estado
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_availability_available ON availability_slots(available);

-- Queries de auditoría
CREATE INDEX idx_audit_timestamp ON audit_log(created_at DESC);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
```

### Partitioning (Futuro)
Para escalabilidad, considerar partitioning por fecha en tablas grandes:

```sql
-- Ejemplo: Partitioning de reservations por mes
CREATE TABLE reservations (
    -- ... campos ...
) PARTITION BY RANGE (service_date);

-- Crear particiones para cada mes
CREATE TABLE reservations_2025_01 PARTITION OF reservations
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

---

## Validación de Integridad

### Queries de Validación

#### 1. Verificar clientes huérfanos en PostgreSQL
```sql
SELECT c.phone, c.name
FROM customers c
WHERE c.phone NOT IN (
    SELECT DISTINCT customer_phone 
    FROM reservations r 
    WHERE r.customer_id IS NULL
);
```

#### 2. Verificar reservas sin cliente válido
```sql
SELECT r.id, r.customer_phone
FROM reservations r
LEFT JOIN customers c ON r.customer_id = c.customer_id
WHERE r.customer_id IS NOT NULL AND c.customer_id IS NULL;
```

#### 3. Verificar slots de disponibilidad inconsistentes
```sql
SELECT a.table_id, a.service_date, a.service_time
FROM availability_slots a
LEFT JOIN reservations r ON a.locked_by_reservation_id = r.id
WHERE a.available = false AND r.id IS NULL;
```

#### 4. Verificar duplicados de confirmation_code
```sql
SELECT confirmation_code, COUNT(*)
FROM reservations
WHERE confirmation_code IS NOT NULL
GROUP BY confirmation_code
HAVING COUNT(*) > 1;
```

---

## Resumen de Mapeo

| Tabla Airtable | Tabla PostgreSQL | Registros Estimados | Complejidad |
|----------------|------------------|-------------------|-------------|
| Clientes | customers | ~500 | Media |
| Reservas | reservations | ~50/día | Alta |
| Mesas | tables | 21 | Baja |
| Disponibilidad | availability_slots | ~1000/día | Alta |
| Logs Auditoría | audit_log | ~1000/día | Alta |
| Info Restaurante | restaurant_info | ~10 | Baja |

**Notas finales:**
- El modelo de PostgreSQL está diseñado para ser la fuente de verdad definitiva
- Airtable actúa como dashboard operativo y fase inicial
- La sincronización debe ser bidireccional y en tiempo real
- Todos los campos JSONB en PostgreSQL tienen estructura definida para facilitar mapeo
- Los índices están optimizados para los patrones de query del sistema de reservas
