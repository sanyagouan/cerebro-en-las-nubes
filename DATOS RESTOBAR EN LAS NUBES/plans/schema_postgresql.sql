-- ============================================================================
-- SCHEMA POSTGRESQL PARA EN LAS NUBES RESTOBAR
-- Sistema Integral de Recepcionista Virtual
-- ============================================================================

-- ============================================================================
-- TIPOS ENUM
-- ============================================================================

-- Estados de reserva
CREATE TYPE reservation_status AS ENUM (
    'pendiente',
    'confirmada',
    'cancelada',
    'no_show',
    'completada'
);

-- Zonas de mesas
CREATE TYPE table_zone AS ENUM (
    'interior',
    'terraza'
);

-- Acciones de auditoría
CREATE TYPE audit_action AS ENUM (
    'create',
    'confirm',
    'cancel',
    'lock',
    'unlock',
    'update'
);

-- Tipos de entidad para auditoría
CREATE TYPE entity_type AS ENUM (
    'reservation',
    'table',
    'slot'
);

-- ============================================================================
-- TABLA: restaurants
-- Propósito: Almacenar información del restaurante, preparado para multi-tenant
-- ============================================================================
CREATE TABLE restaurants (
    restaurant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    hours_config JSONB DEFAULT '{}',
    turn_config JSONB DEFAULT '{}',
    restrictions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLA: customers
-- Propósito: CRM de clientes, historial de visitas y preferencias
-- ============================================================================
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    whatsapp VARCHAR(20),
    email VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    total_reservations INTEGER DEFAULT 0,
    loyalty_points INTEGER DEFAULT 0,
    last_visit_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_restaurant ON customers(restaurant_id);
CREATE INDEX idx_customers_whatsapp ON customers(whatsapp) WHERE whatsapp IS NOT NULL;

-- ============================================================================
-- TABLA: tables
-- Propósito: Inventario físico de mesas (21 mesas en total)
-- ============================================================================
CREATE TABLE tables (
    table_id VARCHAR(10) PRIMARY KEY,
    restaurant_id UUID REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    capacity_min INTEGER NOT NULL CHECK (capacity_min > 0),
    capacity_max INTEGER NOT NULL CHECK (capacity_max >= capacity_min),
    zone table_zone NOT NULL,
    notes TEXT,
    is_auxiliary BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 0 CHECK (priority >= 0),
    coordinates_x DECIMAL(10, 2),
    coordinates_y DECIMAL(10, 2),
    features JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes
CREATE INDEX idx_tables_restaurant ON tables(restaurant_id);
CREATE INDEX idx_tables_zone ON tables(zone);
CREATE INDEX idx_tables_capacity ON tables(capacity_min, capacity_max);
CREATE INDEX idx_tables_priority ON tables(priority);

-- ============================================================================
-- TABLA: reservations
-- Propósito: Registro de reservas y CRM
-- ============================================================================
CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(customer_id) ON DELETE SET NULL,
    table_id VARCHAR(10) REFERENCES tables(table_id) ON DELETE SET NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    guest_count INTEGER NOT NULL CHECK (guest_count > 0),
    status reservation_status NOT NULL DEFAULT 'pendiente',
    confirmation_code VARCHAR(10) UNIQUE NOT NULL,
    service_date DATE NOT NULL,
    service_time TIME NOT NULL,
    special_requests JSONB DEFAULT '{}',
    source VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes
CREATE INDEX idx_reservations_date ON reservations(service_date);
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_phone ON reservations(customer_phone);
CREATE INDEX idx_reservations_code ON reservations(confirmation_code);
CREATE INDEX idx_reservations_restaurant ON reservations(restaurant_id);
CREATE INDEX idx_reservations_customer ON reservations(customer_id);
CREATE INDEX idx_reservations_table ON reservations(table_id);

-- ============================================================================
-- TABLA: availability_slots
-- Propósito: Control granular de disponibilidad
-- ============================================================================
CREATE TABLE availability_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_id VARCHAR(10) REFERENCES tables(table_id) ON DELETE CASCADE,
    service_date DATE NOT NULL,
    service_time TIME NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    locked_by_reservation_id UUID REFERENCES reservations(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes
CREATE INDEX idx_slots_table ON availability_slots(table_id);
CREATE INDEX idx_slots_date_time ON availability_slots(service_date, service_time);
CREATE INDEX idx_slots_available ON availability_slots(available);
CREATE INDEX idx_slots_reservation ON availability_slots(locked_by_reservation_id);

-- Constraint único para evitar slots duplicados
CREATE UNIQUE INDEX idx_slots_unique ON availability_slots(table_id, service_date, service_time);

-- ============================================================================
-- TABLA: audit_log
-- Propósito: Trazabilidad completa de acciones
-- ============================================================================
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID REFERENCES restaurants(restaurant_id) ON DELETE CASCADE,
    entity_type entity_type NOT NULL,
    entity_id UUID NOT NULL,
    action audit_action NOT NULL,
    performed_by VARCHAR(50) NOT NULL,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsquedas frecuentes
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_restaurant ON audit_log(restaurant_id);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);

-- ============================================================================
-- TABLA: restaurant_info
-- Propósito: Información del restaurante (horarios, políticas)
-- ============================================================================
CREATE TABLE restaurant_info (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT
);

-- ============================================================================
-- VISTAS ÚTILES
-- ============================================================================

-- Vista de disponibilidad diaria
CREATE VIEW daily_availability AS
SELECT 
    t.table_id,
    t.capacity_min,
    t.capacity_max,
    t.zone,
    t.is_auxiliary,
    t.priority,
    s.service_date,
    s.service_time,
    s.available,
    s.locked_by_reservation_id
FROM tables t
LEFT JOIN availability_slots s ON t.table_id = s.table_id
ORDER BY t.priority, s.service_date, s.service_time;

-- Vista de resumen de reservas por cliente
CREATE VIEW customer_reservation_summary AS
SELECT 
    c.customer_id,
    c.name,
    c.phone,
    c.whatsapp,
    COUNT(r.id) as total_reservations,
    MAX(r.service_date) as last_reservation_date,
    SUM(CASE WHEN r.status = 'no_show' THEN 1 ELSE 0 END) as no_show_count
FROM customers c
LEFT JOIN reservations r ON c.customer_id = r.customer_id
GROUP BY c.customer_id, c.name, c.phone, c.whatsapp;

-- ============================================================================
-- FUNCIONES
-- ============================================================================

-- Función para verificar disponibilidad
CREATE OR REPLACE FUNCTION verificar_disponibilidad(
    p_date DATE,
    p_time TIME,
    p_guest_count INTEGER,
    p_zone table_zone DEFAULT NULL
)
RETURNS TABLE (
    table_id VARCHAR(10),
    capacity_min INTEGER,
    capacity_max INTEGER,
    zone table_zone,
    priority INTEGER,
    is_available BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.table_id,
        t.capacity_min,
        t.capacity_max,
        t.zone,
        t.priority,
        CASE 
            WHEN s.available IS NULL THEN TRUE
            WHEN s.available = TRUE THEN TRUE
            ELSE FALSE
        END as is_available
    FROM tables t
    LEFT JOIN availability_slots s ON t.table_id = s.table_id 
        AND s.service_date = p_date 
        AND s.service_time = p_time
    WHERE t.capacity_max >= p_guest_count
        AND (p_zone IS NULL OR t.zone = p_zone)
    ORDER BY t.priority, t.is_auxiliary, t.capacity_min;
END;
$$ LANGUAGE plpgsql;

-- Función para generar código de confirmación único
CREATE OR REPLACE FUNCTION generar_codigo_confirmacion()
RETURNS VARCHAR(10) AS $$
DECLARE
    chars TEXT := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    result VARCHAR(10) := '';
    i INTEGER;
BEGIN
    FOR i IN 1..6 LOOP
        result := result || substr(chars, floor(random() * length(chars) + 1)::INTEGER, 1);
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Función para actualizar timestamp automáticamente
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

-- Trigger para actualizar updated_at en restaurants
CREATE TRIGGER trigger_restaurants_updated_at
    BEFORE UPDATE ON restaurants
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Trigger para actualizar updated_at en customers
CREATE TRIGGER trigger_customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Trigger para actualizar updated_at en tables
CREATE TRIGGER trigger_tables_updated_at
    BEFORE UPDATE ON tables
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Trigger para actualizar updated_at en reservations
CREATE TRIGGER trigger_reservations_updated_at
    BEFORE UPDATE ON reservations
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- ============================================================================
-- DATOS INICIALES
-- ============================================================================

-- Información del restaurante
INSERT INTO restaurant_info (key, value, description) VALUES
    ('phone_number', '"987654321"', 'Número de teléfono del restaurante'),
    ('address', '"Calle Principal 123, Madrid"', 'Dirección del restaurante'),
    ('opening_hours', '{"monday": {"open": "12:00", "close": "16:00", "dinner_open": "20:00", "dinner_close": "00:00"}, "tuesday": {"open": "12:00", "close": "16:00", "dinner_open": "20:00", "dinner_close": "00:00"}, "wednesday": {"open": "12:00", "close": "16:00", "dinner_open": "20:00", "dinner_close": "00:00"}, "thursday": {"open": "12:00", "close": "16:00", "dinner_open": "20:00", "dinner_close": "00:00"}, "friday": {"open": "12:00", "close": "16:00", "dinner_open": "20:00", "dinner_close": "01:00"}, "saturday": {"open": "12:00", "close": "16:00", "dinner_open": "20:00", "dinner_close": "01:00"}, "sunday": {"open": "12:00", "close": "16:00", "dinner_open": "20:00", "dinner_close": "00:00"}}', 'Horarios de apertura por día'),
    ('exception_days', '[]', 'Días especiales con horarios diferentes'),
    ('max_reservation_days', '30', 'Días máximos de antelación para reservar'),
    ('min_reservation_hours', '2', 'Horas mínimas de antelación para reservar'),
    ('cancellation_hours', '24', 'Horas mínimas para cancelar sin penalización'),
    ('no_show_penalty', 'true', 'Aplicar penalización por no-show');

-- ============================================================================
-- COMENTARIOS
-- ============================================================================

COMMENT ON TABLE restaurants IS 'Almacena información del restaurante, preparado para soporte multi-tenant futuro';
COMMENT ON TABLE customers IS 'CRM de clientes, historial de visitas y preferencias';
COMMENT ON TABLE tables IS 'Inventario físico de mesas (21 mesas en total). is_auxiliary=true indica mesas que se usan para combinación, emergencia o prioridad baja';
COMMENT ON TABLE reservations IS 'Registro de reservas y CRM. source indica el origen: VAPI, manual, web, etc.';
COMMENT ON TABLE availability_slots IS 'Control granular de disponibilidad por mesa, fecha y hora';
COMMENT ON TABLE audit_log IS 'Trazabilidad completa de acciones sobre reservas, mesas y slots';
COMMENT ON TABLE restaurant_info IS 'Información del restaurante (horarios, políticas, configuración)';

COMMENT ON COLUMN tables.is_auxiliary IS 'Mesas auxiliares se usan para: 1) Combinación de mesas para grupos grandes (>10 personas), 2) Mesas de emergencia/backup cuando las principales están ocupadas, 3) Mesas que se pueden dividir (ej: C2-C indica combinación de C2 y C3), 4) Mesas con prioridad baja que solo se asignan cuando no hay otra opción';
COMMENT ON COLUMN tables.priority IS 'Orden de asignación: menor valor = mayor prioridad';
COMMENT ON COLUMN reservations.special_requests IS 'JSONB con peticiones especiales: cachopo_sg, tronas, descorche, alergias, etc.';
COMMENT ON COLUMN reservations.source IS 'Origen de la reserva: VAPI, manual, web, whatsapp, etc.';

-- ============================================================================
-- FIN DEL SCHEMA
-- ============================================================================
