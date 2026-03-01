# Schema PostgreSQL - En Las Nubes Restobar

## Descripción
Este documento contiene el esquema completo de PostgreSQL para el sistema de reservas de En Las Nubes Restobar.

## Tablas

### 1. Tabla: `restaurants`
Información del restaurante (preparado para multi-tenant futuro)

| Campo | Tipo | Descripción |
|---------|-----------|-------------|
| restaurant_id | UUID (PK) | Identificador único del restaurante |
| name | VARCHAR(100) | Nombre del restaurante |
| address | TEXT | Dirección física |
| phone | VARCHAR(20) | Número de teléfono |
| email | VARCHAR(100) | Email de contacto |
| hours_config | JSONB | Configuración de horarios |
| turn_config | JSONB | Configuración de turnos |
| restrictions | JSONB | Restricciones de negocio |
| created_at | TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP | Fecha de última actualización |

### 2. Tabla: `customers`
Información de clientes (CRM)

| Campo | Tipo | Descripción |
|---------|-----------|-------------|
| customer_id | UUID (PK) | Identificador único del cliente |
| restaurant_id | UUID (FK) | Referencia al restaurante |
| name | VARCHAR(100) | Nombre del cliente |
| phone | VARCHAR(20) | Teléfono (único) |
| whatsapp | VARCHAR(20) | Número de WhatsApp |
| email | VARCHAR(100) | Email del cliente |
| preferences | JSONB | Preferencias del cliente |
| total_reservations | INTEGER | Total de reservas |
| loyalty_points | INTEGER | Puntos de lealtad |
| last_visit_date | DATE | Última visita |
| data_consent | BOOLEAN | Consentimiento GDPR |
| consent_date | TIMESTAMP | Fecha de consentimiento |
| created_at | TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP | Fecha de última actualización |

### 3. Tabla: `tables`
Inventario físico de mesas (21 mesas en total)

| Campo | Tipo | Descripción |
|---------|-----------|-------------|
| table_id | VARCHAR(10) (PK) | Identificador de mesa (ej: 'A1', 'B2') |
| restaurant_id | UUID (FK) | Referencia al restaurante |
| capacity_min | INTEGER | Capacidad mínima |
| capacity_max | INTEGER | Capacidad máxima |
| zone | ENUM | Zona (interior/terraza) |
| notes | TEXT | Notas (ej: 'JUNTO AL BAÑO') |
| is_auxiliary | BOOLEAN | Mesa auxiliar/combinable |
| priority | INTEGER | Prioridad de asignación |
| coordinates_x | DECIMAL(8,2) | Coordenada X |
| coordinates_y | DECIMAL(8,2) | Coordenada Y |
| features | JSONB | Características adicionales |
| is_active | BOOLEAN | Mesa activa |
| created_at | TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP | Fecha de última actualización |

### 4. Tabla: `reservations`
Registro de reservas y CRM

| Campo | Tipo | Descripción |
|---------|-----------|-------------|
| id | UUID (PK) | Identificador único de reserva |
| restaurant_id | UUID (FK) | Referencia al restaurante |
| customer_id | UUID (FK) | Referencia al cliente |
| table_id | VARCHAR(10) (FK) | Referencia a mesa |
| customer_name | VARCHAR(100) | Nombre del cliente (redundancia) |
| customer_phone | VARCHAR(20) | Teléfono del cliente (redundancia) |
| guest_count | INTEGER | Número de personas (PAX) |
| service_date | DATE | Fecha de servicio |
| service_time | TIME | Hora de servicio |
| status | ENUM | Estado (pendiente/confirmada/cancelada/no_show/completada) |
| confirmation_code | VARCHAR(8) | Código de confirmación (único) |
| confirmation_sent_at | TIMESTAMP | Fecha de envío de confirmación |
| confirmed_at | TIMESTAMP | Fecha de confirmación |
| special_requests | JSONB | Solicitudes especiales |
| source | VARCHAR(20) | Origen (VAPI/manual/web/whatsapp) |
| created_by | VARCHAR(50) | Creado por |
| origin_system | VARCHAR(20) | Sistema de origen |
| created_at | TIMESTAMP | Fecha de creación |
| updated_at | TIMESTAMP | Fecha de última actualización |

### 5. Tabla: `availability_slots`
Control granular de disponibilidad

| Campo | Tipo | Descripción |
|---------|-----------|-------------|
| id | UUID (PK) | Identificador único de slot |
| table_id | VARCHAR(10) (FK) | Referencia a mesa |
| service_date | DATE | Fecha de servicio |
| service_time | TIME | Hora de servicio |
| available | BOOLEAN | Disponible |
| locked_by_reservation_id | UUID (FK) | Reserva que bloquea el slot |
| created_at | TIMESTAMP | Fecha de creación |

### 6. Tabla: `audit_log`
Trazabilidad completa de acciones

| Campo | Tipo | Descripción |
|---------|-----------|-------------|
| id | UUID (PK) | Identificador único de log |
| restaurant_id | UUID (FK) | Referencia al restaurante |
| entity_type | ENUM | Tipo de entidad (reservation/table/slot/customer) |
| entity_id | UUID | ID de la entidad |
| action | ENUM | Acción (create/confirm/cancel/lock/unlock/update/delete) |
| details | JSONB | Detalles de la acción |
| old_values | JSONB | Valores anteriores |
| new_values | JSONB | Nuevos valores |
| performed_by | VARCHAR(50) | Realizado por (system/staff/customer) |
| ip_address | INET | Dirección IP |
| user_agent | TEXT | User agent |
| system_source | VARCHAR(20) | Sistema fuente (n8n) |
| workflow_id | VARCHAR(50) | ID del workflow |
| created_at | TIMESTAMP | Fecha de creación |

### 7. Tabla: `restaurant_info`
Información del restaurante (horarios, políticas)

| Campo | Tipo | Descripción |
|---------|-----------|-------------|
| key | VARCHAR(50) (PK) | Clave única |
| value | TEXT | Valor |
| value_type | VARCHAR(20) | Tipo (text/json/number/boolean) |
| description | TEXT | Descripción |
| updated_at | TIMESTAMP | Fecha de actualización |

## Tipos ENUM

### reservation_status
- `pendiente`: Reserva creada pero no confirmada
- `confirmada`: Reserva confirmada por cliente
- `cancelada`: Reserva cancelada
- `no_show`: Cliente no se presentó
- `completada`: Servicio completado

### table_zone
- `interior`: Zona interior del restaurante
- `terraza`: Zona terraza

### audit_action
- `create`: Creación de entidad
- `confirm`: Confirmación de reserva
- `cancel`: Cancelación
- `lock`: Bloqueo de slot
- `unlock`: Desbloqueo de slot
- `update`: Actualización
- `delete`: Eliminación

### entity_type
- `reservation`: Entidad reserva
- `table`: Entidad mesa
- `slot`: Entidad slot de disponibilidad
- `customer`: Entidad cliente

## Índices

### Índices críticos para rendimiento
- `idx_reservations_date_time`: (service_date, service_time)
- `idx_reservations_customer`: (customer_id)
- `idx_reservations_restaurant`: (restaurant_id)
- `idx_reservations_table`: (table_id)
- `idx_reservations_status`: (status)
- `idx_reservations_phone`: (customer_phone)
- `idx_reservations_confirmation_code`: (confirmation_code)
- `idx_availability_table_date`: (table_id, service_date)
- `idx_availability_available`: (available)
- `idx_audit_timestamp`: (created_at DESC)
- `idx_audit_entity`: (entity_type, entity_id)

## Vistas Útiles

### daily_availability
Vista de disponibilidad diaria por zona

### customer_reservation_summary
Vista de resumen de reservas por cliente

## Funciones Útiles

### verificar_disponibilidad()
Función para verificar disponibilidad de mesas según fecha, hora, personas y zona.

### generar_codigo_confirmacion()
Función para generar códigos de confirmación únicos (4 letras + 4 números).

## Triggers

### update_timestamp()
Trigger automático para actualizar `updated_at` en todas las tablas.

## Datos Iniciales

### restaurant_info
Configuración inicial del restaurante:
- `phone_number`: +34 941 57 84 51
- `address`: Dirección del restaurante
- `opening_hours`: Horarios de apertura
- `exception_days`: Días de excepción/cierre
- `max_reservation_days`: 30 días máximos
- `cancellation_policy`: 24 horas
- `confirmation_timeout`: 2 horas
- `no_show_policy`: 15 minutos

## Código SQL Completo

```sql
-- ============================================================================
-- SCHEMA POSTGRESQL - EN LAS NUBES RESTOBAR
-- Sistema de Reservas y Gestión de Mesas
-- ============================================================================
-- Autor: Kilo Code
-- Fecha: 2025-12-24
-- Versión: 1.0
-- ============================================================================

-- Habilitar extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TIPOS ENUMERADOS
-- ============================================================================

-- Estados de reserva
CREATE TYPE reservation_status AS ENUM (
    'pendiente',
    'confirmada',
    'cancelada',
    'no_show',
    'completada'
);

-- Zonas del restaurante
CREATE TYPE table_zone AS ENUM (
    'interior',
    'terraza'
);

-- Tipos de acciones de auditoría
CREATE TYPE audit_action AS ENUM (
    'create',
    'confirm',
    'cancel',
    'lock',
    'unlock',
    'update',
    'delete'
);

-- Tipos de entidades para auditoría
CREATE TYPE entity_type AS ENUM (
    'reservation',
    'table',
    'slot',
    'customer'
);

-- ============================================================================
-- TABLA: restaurants
-- Información del restaurante (preparado para multi-tenant futuro)
-- ============================================================================
CREATE TABLE restaurants (
    restaurant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    
    -- Configuración de horarios (JSONB para flexibilidad)
    hours_config JSONB NOT NULL DEFAULT '{
        "lunes_vespertino": {"inicio": "19:30", "fin": "23:00"},
        "martes_vespertino": {"inicio": "19:30", "fin": "23:00"},
        "miercoles_vespertino": {"inicio": "19:30", "fin": "23:00"},
        "jueves_vespertino": {"inicio": "19:30", "fin": "23:00"},
        "viernes_vespertino": {"inicio": "19:30", "fin": "23:00"},
        "sabado_completo": {"inicio": "12:30", "fin": "16:00"},
        "domingo_completo": {"inicio": "12:30", "fin": "16:00"}
    }'::jsonb,
    
    -- Configuración de turnos
    turn_config JSONB NOT NULL DEFAULT '{
        "almuerzo": {"duracion": 90, "ultimo_turno": "14:00"},
        "cena": {"duracion": 120, "ultimo_turno": "22:00"}
    }'::jsonb,
    
    -- Configuración de restricciones
    restrictions JSONB NOT NULL DEFAULT '{
        "mesas_especiales": ["C2", "C3"],
        "politica_mascotas": "no_permitidas",
        "opciones_sin_gluten": true,
        "tiempo_cancelacion": 24,
        "tiempo_confirmacion": 2
    }'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para restaurants
CREATE INDEX idx_restaurants_name ON restaurants(name);
CREATE INDEX idx_restaurants_active ON restaurants(created_at);

-- ============================================================================
-- TABLA: customers
-- Información de clientes (CRM)
-- ============================================================================
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    
    -- Datos básicos del cliente
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    whatsapp VARCHAR(20),
    email VARCHAR(100),
    
    -- Preferencias del cliente (JSONB para flexibilidad)
    preferences JSONB DEFAULT '{
        "zona_preferida": null,
        "mesa_preferida": null,
        "alergias": [],
        "ocasiones_especiales": [],
        "frecuencia_visita": "ocasional",
        "notificaciones_recordatorios": true
    }'::jsonb,
    
    -- Historial y lealtad
    total_reservations INTEGER DEFAULT 0,
    loyalty_points INTEGER DEFAULT 0,
    last_visit_date DATE,
    
    -- GDPR
    data_consent BOOLEAN DEFAULT false,
    consent_date TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_customer_phone UNIQUE(phone)
);

-- Índices para customers
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_whatsapp ON customers(whatsapp);
CREATE INDEX idx_customers_restaurant ON customers(restaurant_id);

-- ============================================================================
-- TABLA: tables
-- Inventario físico de mesas (21 mesas en total)
-- ============================================================================
CREATE TABLE tables (
    table_id VARCHAR(10) PRIMARY KEY,  -- ej: 'A1', 'B2', 'C2-C'
    restaurant_id UUID NOT NULL REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    
    -- Capacidad de la mesa
    capacity_min INTEGER NOT NULL CHECK (capacity_min > 0),
    capacity_max INTEGER NOT NULL CHECK (capacity_max >= capacity_min),
    
    -- Ubicación y tipo
    zone table_zone NOT NULL,
    notes TEXT,  -- ej: 'JUNTO AL BAÑO'
    
    -- Configuración especial
    is_auxiliary BOOLEAN DEFAULT false,  -- para mesas auxiliares/combinables
    priority INTEGER DEFAULT 0,  -- para orden de asignación
    
    -- Mesas auxiliares se usan para:
    -- 1. Combinación de mesas para grupos grandes (>10 personas)
    -- 2. Mesas de emergencia/backup cuando las principales están ocupadas
    -- 3. Mesas que se pueden dividir (ej: C2-C indica combinación de C2 y C3)
    -- 4. Mesas con prioridad baja que solo se asignan cuando no hay otra opción
    
    -- Coordenadas para asignación inteligente (opcional)
    coordinates_x DECIMAL(8,2),
    coordinates_y DECIMAL(8,2),
    
    -- Características adicionales (JSONB para flexibilidad)
    features JSONB DEFAULT '{
        "sillas_nino": 0,
        "accesibilidad_ruedas": false,
        "cerca_ventana": false,
        "preferencia_grupos": false
    }'::jsonb,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_restaurant_table UNIQUE(restaurant_id, table_id)
);

-- Índices para tables
CREATE INDEX idx_tables_restaurant ON tables(restaurant_id);
CREATE INDEX idx_tables_zone_capacity ON tables(zone, capacity_max);
CREATE INDEX idx_tables_active ON tables(is_active);
CREATE INDEX idx_tables_priority ON tables(priority DESC);

-- ============================================================================
-- TABLA: reservations
-- Registro de reservas y CRM
-- ============================================================================
CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID NOT NULL REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    table_id VARCHAR(10) REFERENCES tables(table_id) ON DELETE SET NULL,
    
    -- Datos del cliente (redundancia para queries rápidas)
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    
    -- Datos de la reserva
    guest_count INTEGER NOT NULL CHECK (guest_count > 0),
    service_date DATE NOT NULL,
    service_time TIME NOT NULL,
    
    -- Estados y tracking
    status reservation_status NOT NULL DEFAULT 'pendiente',
    confirmation_code VARCHAR(8) UNIQUE,
    confirmation_sent_at TIMESTAMP WITH TIME ZONE,
    confirmed_at TIMESTAMP WITH TIME ZONE,
    
    -- Solicitudes especiales (JSONB para flexibilidad)
    special_requests JSONB DEFAULT '{
        "trona": false,
        "descorche": false,
        "cerca_ventana": false,
        "accesibilidad": false,
        "notas_adicionales": ""
    }'::jsonb,
    
    -- Origen de la reserva
    source VARCHAR(20) DEFAULT 'VAPI' CHECK (source IN ('VAPI', 'manual', 'web', 'whatsapp')),
    
    -- Campos de auditoría
    created_by VARCHAR(50),
    origin_system VARCHAR(20) DEFAULT 'VAPI',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices críticos para reservations
CREATE INDEX idx_reservations_date_time ON reservations(service_date, service_time);
CREATE INDEX idx_reservations_customer ON reservations(customer_id);
CREATE INDEX idx_reservations_restaurant ON reservations(restaurant_id);
CREATE INDEX idx_reservations_table ON reservations(table_id);
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_phone ON reservations(customer_phone);
CREATE INDEX idx_reservations_confirmation_code ON reservations(confirmation_code);

-- ============================================================================
-- TABLA: availability_slots
-- Control granular de disponibilidad
-- ============================================================================
CREATE TABLE availability_slots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_id VARCHAR(10) NOT NULL REFERENCES tables(table_id) ON DELETE CASCADE,
    service_date DATE NOT NULL,
    service_time TIME NOT NULL,
    
    -- Estado del slot
    available BOOLEAN NOT NULL DEFAULT true,
    locked_by_reservation_id UUID REFERENCES reservations(id) ON DELETE SET NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_table_slot UNIQUE(table_id, service_date, service_time)
);

-- Índices para rendimiento
CREATE INDEX idx_availability_table_date ON availability_slots(table_id, service_date);
CREATE INDEX idx_availability_available ON availability_slots(available);
CREATE INDEX idx_availability_time ON availability_slots(service_time);
CREATE INDEX idx_availability_reservation ON availability_slots(locked_by_reservation_id);

-- ============================================================================
-- TABLA: audit_log
-- Trazabilidad completa de acciones
-- ============================================================================
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    restaurant_id UUID REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    
    -- Acción y entidad
    entity_type entity_type NOT NULL,
    entity_id UUID,
    action audit_action NOT NULL,
    
    -- Detalles
    details JSONB,
    old_values JSONB,
    new_values JSONB,
    
    -- Origen
    performed_by VARCHAR(50) NOT NULL CHECK (performed_by IN ('system', 'staff', 'customer')),
    ip_address INET,
    user_agent TEXT,
    
    -- Sistema
    system_source VARCHAR(20) DEFAULT 'VAPI',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para audit_log
CREATE INDEX idx_audit_timestamp ON audit_log(created_at DESC);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_restaurant ON audit_log(restaurant_id);

-- ============================================================================
-- TABLA: restaurant_info
-- Información del restaurante (horarios, políticas)
-- ============================================================================
CREATE TABLE restaurant_info (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    value_type VARCHAR(20) DEFAULT 'text' CHECK (value_type IN ('text', 'json', 'number', 'boolean')),
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para restaurant_info
CREATE INDEX idx_info_key ON restaurant_info(key);

-- ============================================================================
-- VISTAS ÚTILES
-- ============================================================================

-- Vista: disponibilidad diaria por zona
CREATE VIEW daily_availability AS
SELECT 
    r.restaurant_id,
    r.service_date,
    t.zone,
    COUNT(CASE WHEN a.available = true THEN 1 END) as mesas_disponibles,
    COUNT(CASE WHEN a.available = false THEN 1 END) as mesas_ocupadas,
    SUM(CASE WHEN a.available = true THEN t.capacity_max ELSE 0 END) as capacidad_disponible,
    SUM(CASE WHEN a.available = false THEN t.capacity_max ELSE 0 END) as capacidad_ocupada
FROM reservations r
CROSS JOIN tables t ON r.restaurant_id = t.restaurant_id
LEFT JOIN availability_slots a ON t.table_id = a.table_id AND a.service_date = r.service_date
WHERE t.is_active = true
GROUP BY r.restaurant_id, r.service_date, t.zone;

-- Vista: resumen de reservas por cliente
CREATE VIEW customer_reservation_summary AS
SELECT 
    c.customer_id,
    c.name,
    c.phone,
    c.whatsapp,
    COUNT(r.id) as total_reservas,
    COUNT(CASE WHEN r.status = 'confirmada' THEN 1 END) as reservas_confirmadas,
    COUNT(CASE WHEN r.status = 'cancelada' THEN 1 END) as reservas_canceladas,
    MAX(r.service_date) as ultima_visita,
    SUM(r.guest_count) as total_personas
FROM customers c
LEFT JOIN reservations r ON c.customer_id = r.customer_id
GROUP BY c.customer_id, c.name, c.phone, c.whatsapp;

-- ============================================================================
-- FUNCIONES ÚTILES
-- ============================================================================

-- Función: verificar disponibilidad
CREATE OR REPLACE FUNCTION verificar_disponibilidad(
    p_restaurant_id UUID,
    p_fecha DATE,
    p_hora TIME,
    p_num_personas INTEGER,
    p_zona table_zone DEFAULT NULL
) RETURNS JSON AS $$
DECLARE
    resultado JSON;
    mesas_disponibles INTEGER;
BEGIN
    SELECT COUNT(DISTINCT t.table_id)
    INTO mesas_disponibles
    FROM tables t
    JOIN availability_slots a ON t.table_id = a.table_id
    WHERE t.restaurant_id = p_restaurant_id
        AND t.is_active = true
        AND (p_zona IS NULL OR t.zone = p_zona)
        AND a.service_date = p_fecha
        AND a.available = true
        AND t.capacity_max >= p_num_personas
        AND NOT EXISTS (
            SELECT 1 FROM reservations r 
            WHERE r.table_id = t.table_id 
                AND r.service_date = p_fecha
                AND r.status IN ('confirmada', 'pendiente')
                AND ABS(EXTRACT(EPOCH FROM (r.service_time - p_hora))) < 3600
        );
    
    resultado := json_build_object(
        'disponible', mesas_disponibles > 0,
        'mesas_disponibles', mesas_disponibles,
        'capacidad_total', (SELECT SUM(capacity_max) FROM tables WHERE restaurant_id = p_restaurant_id AND is_active = true)
    );
    
    RETURN resultado;
END;
$$ LANGUAGE plpgsql;

-- Función: generar código de confirmación único
CREATE OR REPLACE FUNCTION generar_codigo_confirmacion()
RETURNS VARCHAR(8) AS $$
DECLARE
    codigo VARCHAR(8);
    existe BOOLEAN;
BEGIN
    LOOP
        -- Generar código: 4 letras + 4 números
        codigo := upper(substring(md5(random()::text), 1, 4)) || 
                   lpad(floor(random() * 10000)::text, 4, '0');
        
        -- Verificar unicidad
        SELECT EXISTS(SELECT 1 FROM reservations WHERE confirmation_code = codigo)
        INTO existe;
        
        EXIT WHEN NOT existe;
    END LOOP;
    
    RETURN codigo;
END;
$$ LANGUAGE plpgsql;

-- Función: trigger para updated_at automático
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger para updated_at automático en todas las tablas
CREATE TRIGGER trigger_restaurants_updated
    BEFORE UPDATE ON restaurants
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_customers_updated
    BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_tables_updated
    BEFORE UPDATE ON tables
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_reservations_updated
    BEFORE UPDATE ON reservations
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trigger_restaurant_info_updated
    BEFORE UPDATE ON restaurant_info
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- DATOS INICIALES (restaurant_info)
-- ============================================================================

INSERT INTO restaurant_info (key, value, value_type, description) VALUES
    ('phone_number', '+34 941 57 84 51', 'text', 'Número de teléfono del restaurante'),
    ('address', 'Dirección del restaurante', 'text', 'Dirección física del restaurante'),
    ('opening_hours', '{
        "lunes": {"inicio": "19:30", "fin": "23:00"},
        "martes": {"inicio": "19:30", "fin": "23:00"},
        "miercoles": {"inicio": "19:30", "fin": "23:00"},
        "jueves": {"inicio": "19:30", "fin": "23:00"},
        "viernes": {"inicio": "19:30", "fin": "23:00"},
        "sabado": {"inicio": "12:30", "fin": "16:00"},
        "domingo": {"inicio": "12:30", "fin": "16:00"}
    }', 'json', 'Horarios de apertura'),
    ('exception_days', '[]', 'json', 'Días de excepción/cierre'),
    ('max_reservation_days', '30', 'number', 'Días máximos para reservar con antelación'),
    ('cancellation_policy', '24', 'number', 'Horas de antelación para cancelación gratuita'),
    ('confirmation_timeout', '2', 'number', 'Horas para confirmar una prereserva'),
    ('no_show_policy', '15', 'number', 'Minutos de tolerancia para no-show');

-- ============================================================================
-- COMENTARIOS FINALES
-- ============================================================================
-- Este esquema está diseñado para:
-- 1. Soportar el flujo completo de reservas por voz (VAPI)
-- 2. Permitir confirmaciones por WhatsApp
-- 3. Facilitar recordatorios automáticos
-- 4. Proporcionar trazabilidad completa (audit_log)
-- 5. Ser escalable a multi-tenant futuro
-- 6. Permitir migración desde Airtable sin dependencias específicas
-- ============================================================================
```
