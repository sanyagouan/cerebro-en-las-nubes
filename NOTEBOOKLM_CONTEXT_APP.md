# NotebookLM Business Context - En Las Nubes Restobar

**Fecha de extracción:** 2026-02-08  
**Cuadernos consultados:** Cerebro - Reservas & Lógica, Cerebro - Integraciones & APIs

---

## 1. REGLAS DE NEGOCIO - RESERVAS

### Horarios de Apertura
| Día | Estado | Horario Comidas | Horario Cenas |
|-----|--------|-----------------|---------------|
| Lunes | CERRADO (excepto festivos) | - | - |
| Martes | ABIERTO | 13:30 - 17:30 | Cerrado (excepto vísperas) |
| Miércoles | ABIERTO | 13:30 - 17:30 | Cerrado (excepto vísperas) |
| Jueves | ABIERTO | 13:30 - 17:30 | 20:00 - 24:00 |
| Viernes | ABIERTO | 13:30 - 17:30 | Hasta 00:30 (2 turnos) |
| Sábado | ABIERTO | 13:30 - 17:30 | Hasta 01:00 (2 turnos) |
| Domingo | ABIERTO (solo comida) | 13:30 - 17:30 | CERRADO |

**Nota:** Si el lunes es festivo, el cierre semanal se traslada al martes noche.

### Capacidad del Restaurante
- **Capacidad total:** 123 personas
- **Zona Interior:** 59 pax (mesas 2-6 pax, combinables)
- **Zona Terraza:** 64 pax (mesas grandes hasta 12 pax)

### Estados de Reserva
1. **Pendiente** - Creada, esperando confirmación WhatsApp
2. **Confirmada** - Cliente confirmó (código 8 caracteres)
3. **Cancelada** - Anulada por cliente o sistema
4. **No-show** - Cliente no apareció (15 min tolerancia)

### Política de Grupos Grandes
| Tamaño | Regla |
|--------|-------|
| >10 personas | Escalado automático a gestión humana |
| ≥7 personas | Solo Turno 1 en días de alta demanda |
| 12-15 pax | Combinación mesas terraza (C1+T3) |
| 16-20 pax | Combinación exclusiva terraza (C1+C2) |
| >20 pax | Coordinación manual obligatoria |

### Restricciones Especiales
- **Cachopo sin gluten:** 24h aviso previo obligatorio
- **Mascotas:** Solo en terraza (prohibido interior)
- **Tronas:** Stock limitado a 2 unidades
- **Accesibilidad:** Mesas prioritarias PMR disponibles (baño no adaptado)

### Tiempos Clave
- **Confirmación:** 2 horas para responder código
- **Tolerancia no-show:** 15 minutos
- **Cancelación:** 24h antelación solicitada

---

## 2. ARQUITECTURA DE INTEGRACIONES

### Flujo de Datos Actual
```
Cliente (Teléfono)
    ↓
Twilio (Voz)
    ↓
VAPI (Procesamiento IA)
    ↓
Backend FastAPI
    ↓ (Consulta)
Airtable (Datos) + OpenWeatherMap (Clima)
    ↓ (Guarda)
Twilio (WhatsApp/SMS Confirmación)
```

### Integraciones Activas
| Servicio | Propósito | Comunicación |
|----------|-----------|--------------|
| **VAPI** | Asistente de voz IA | Webhooks HTTP POST |
| **Twilio** | Telefonía + WhatsApp/SMS | Cliente REST + Webhooks |
| **Airtable** | Base de datos principal | API REST (pyairtable) |
| **OpenWeatherMap** | Validación clima terraza | HTTP GET (httpx) |
| **Redis** | Caché (rate limiting Airtable) | Cache |

### Nota Crítica sobre Supabase
**Supabase NO está implementado actualmente** en el código fuente. El sistema usa:
- `AirtableService` como persistencia real
- `MockReservationRepository` para operaciones simuladas

Para la app móvil, necesitamos implementar Supabase como backend de autenticación y datos en tiempo real.

---

## 3. CAMPOS DE RESERVA EN AIRTABLE

```python
{
    "Nombre del Cliente": str,
    "Teléfono": str,  # Formato: +34XXXXXXXXX
    "Fecha de Reserva": str,  # YYYY-MM-DD
    "Hora": str,  # ISO 8601
    "Cantidad de Personas": int,
    "Estado de Reserva": str,  # Enum: Pendiente/Confirmada/Cancelada
    "Mesa": list,  # Referencia a tabla Mesas
    "Notas": str,  # Peticiones especiales
    "Creado": timestamp,
    "Modificado": timestamp
}
```

---

## 4. REQUERIMIENTOS PARA APP MÓVIL

### Eventos Push Aprobados (por rol)

| Evento | Camarero | Cocinero | Encargada | Admin |
|--------|:--------:|:--------:|:---------:|:-----:|
| Nueva reserva | ✅ | ❌ | ✅ | ✅ |
| Reserva confirmada | ✅ | ❌ | ✅ | ✅ |
| Reserva cancelada | ✅ | ❌ | ✅ | ✅ |
| Cliente sentado | ✅ | ✅ | ✅ | ✅ |
| Mesa liberada | ✅ | ✅ | ✅ | ✅ |
| No-show | ✅ | ❌ | ✅ | ✅ |
| Grupo >10 pax | ❌ | ❌ | ✅ | ✅ |
| Alerta cocina | ✅ | ✅ | ✅ | ✅ |
| Incidencia | ❌ | ❌ | ✅ | ✅ |
| Overbooking | ❌ | ❌ | ✅ | ✅ |

### Permisos por Rol

**Camarero:**
- Ver reservas del día
- Marcar mesas como "sentado" / "liberado"
- Ver notas de clientes
- Añadir notas rápidas

**Cocinero:**
- Ver reservas con detalles de menú/pax
- Recibir alertas de entradas
- Ver preferencias especiales (alergias)
- Marcar "plato listo"

**Encargada:**
- Todo lo anterior +
- Crear/editar/cancelar reservas
- Asignar mesas (drag & drop)
- Gestionar lista de espera
- Registrar incidencias

**Admin:**
- Acceso total
- Ver estadísticas y KPIs
- Gestionar usuarios y roles
- Configurar horarios especiales

---

## 5. DECISIONES TÉCNICAS PENDIENTES

### Stack Aprobado
- **UI:** Jetpack Compose (Kotlin)
- **Arquitectura:** Online-only (sin offline)
- **Distribución:** APK directo
- **Backend:** WebSocket + REST API
- **Auth:** JWT con roles (RBAC)

### Implementación Requerida en Backend
1. WebSocket endpoint para tiempo real
2. JWT authentication con roles
3. API endpoints móviles específicos
4. Push notifications (Firebase Cloud Messaging)
5. Integración Supabase para auth y datos

### Estructura de Datos para App
```kotlin
data class Reservation(
    val id: String,
    val customerName: String,
    val phone: String,
    val date: LocalDate,
    val time: LocalTime,
    val pax: Int,
    val status: ReservationStatus,  // PENDING, CONFIRMED, CANCELLED, SEATED
    val tableId: String?,
    val tableName: String?,
    val notes: String?,
    val specialRequests: List<String>,
    val createdAt: Instant
)

data class Table(
    val id: String,
    val name: String,  // "Mesa 1T", "Mesa 2I"
    val capacity: Int,
    val maxCapacity: Int,  // Con sillas extra
    val location: Location,  // TERRACE, INTERIOR
    val status: TableStatus,  // FREE, OCCUPIED, RESERVED, MAINTENANCE
    val isActive: Boolean
)
```

---

## 6. OBSERVACIONES IMPORTANTES

### Diferencias con Implementación Actual
1. El sistema actual usa Airtable como única BD
2. Para la app móvil necesitamos:
   - Supabase para auth (JWT + roles)
   - Sincronización Airtable ↔ Supabase
   - WebSocket para tiempo real

### Datos Críticos a Sincronizar
- Tabla Reservas (Airtable ↔ Supabase)
- Tabla Mesas (Airtable ↔ Supabase)
- Estados de reserva en tiempo real
- Asignaciones de mesa

### Seguridad
- JWT tokens con expiración corta (15 min)
- Refresh tokens
- Role-based access control (RBAC)
- HTTPS obligatorio
- Rate limiting

---

**Documento generado automáticamente desde consultas NotebookLM**  
**Próximo paso:** Implementar backend WebSocket + auth + endpoints móviles
