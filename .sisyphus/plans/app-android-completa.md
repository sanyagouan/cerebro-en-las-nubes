# Plan: App Android Completa - En Las Nubes Restobar

## TL;DR

> **Objetivo**: Sistema completo de autenticación y funcionalidades por rol para el restaurante.
> 
> **Entregables**:
> - Login funcional con 4 roles (todo en español)
> - Usuarios en Airtable (no hardcodeados)
> - Gestión de usuarios (solo Administradora)
> - Navegación dinámica por permisos
> - Notificaciones push entre personal
> - Despliegue completo en Coolify
> 
> **Esfuerzo estimado**: Grande (2-3 semanas)
> **Ejecución paralela**: SÍ - Backend y Frontend pueden avanzar en paralelo

---

## 1. DIAGNÓSTICO COMPLETO

### 1.1 Credenciales Oficiales (Español de España)

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| **Administradora** | `administradora` | `administradora123` |
| **Encargada** | `encargada` | `encargada123` |
| **Camarero** | `camarero` | `camarero123` |
| **Cocina** | `cocina` | `cocina123` |

> ⚠️ **Importante**: La Administradora puede cambiar contraseñas de cualquier usuario.

### 1.2 Tabla Usuarios en Airtable

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID | Auto | Identificador único |
| Usuario | Text | Único, sin espacios (ej: "administradora") |
| Nombre | Text | Nombre completo para mostrar |
| Password_Hash | Text | bcrypt |
| Rol | Single Select | administradora, encargada, camarero, cocina |
| Activo | Checkbox | Default: true (soft delete) |
| Telefono | Phone | Opcional, para contacto |
| Device_Token | Text | Token FCM para notificaciones push |
| Ultimo_Login | DateTime | Auto-update |
| Creado | Created time | Auto |
| Modificado | Last modified | Auto |

### 1.3 Backend - Estado Actual

| Componente | Archivo | Estado |
|------------|---------|--------|
| Login móvil | `src/api/mobile/mobile_api.py` | ⚠️ Hardcodeado, usar emails |
| Auth Service | `src/application/services/auth_service.py` | ⚠️ Sin bcrypt |
| JWT Tokens | Ambos archivos | ✅ Funciona |
| Permisos RBAC | `check_permission()` | ⚠️ Básico |
| Gestión usuarios | - | ❌ No existe |
| Notificaciones push | - | ❌ No existe |

### 1.4 App Android - Estado Actual

| Pantalla | Funcionalidad | Estado |
|----------|---------------|--------|
| **LoginScreen** | UI + llamada API | ⚠️ Credenciales incorrectas |
| **ReservationsScreen** | Lista + filtros + estados | ✅ Funciona |
| **TablesScreen** | Mapa mesas + cambiar estado | ✅ Funciona |
| **KitchenScreen** | Vista flujo | ⚠️ Datos mock |
| **AdminScreen** | Stats + gestión usuarios | ❌ TODO mock |
| **ConfigScreen** | Cambiar URL servidor | ❌ No existe |
| **Navegación por rol** | Ocultar tabs | ❌ No implementado |

---

## 2. FUNCIONALIDADES POR ROL

### 2.1 Rol CAMARERO

**Tabs visibles:** Reservas, Mesas

**Funcionalidades:**
- ✅ Ver lista de reservas del día
- ✅ Filtrar por fecha/estado
- ✅ Marcar cliente como "Sentado"
- ✅ Marcar mesa como "Liberada"
- ✅ Ver mapa de mesas en tiempo real
- ✅ Ver pedidos especiales por mesa
- ✅ Ver peticiones extras de clientes
- ✅ Buscar reserva por nombre/teléfono
- ✅ Marcar "No-show" si cliente no viene
- ✅ Enviar avisos a Cocina
- ✅ Añadir notas en mesas
- ✅ Comunicarse con el backend/asistente
- ✅ Recibir notificaciones push

**NO puede:**
- ❌ Crear reservas
- ❌ Editar reservas
- ❌ Cancelar reservas
- ❌ Ver cocina (vista cocina)
- ❌ Ver estadísticas
- ❌ Gestionar usuarios

### 2.2 Rol COCINA

**Tabs visibles:** Solo Cocina

**Funcionalidades:**
- ✅ Ver flujo de clientes previsto
- ✅ Ver reservas con hora de llegada
- ✅ Recibir alertas de clientes sentados
- ✅ Ver notas especiales (alergias, sin gluten)
- ✅ Ver alertas de grupos grandes
- ✅ Ver pedidos especiales de cada mesa
- ✅ Marcar platos como listos
- ✅ Añadir notas para sala (camareros)
- ✅ Enviar avisos a Camareros
- ✅ Recibir notificaciones push

**NO puede:**
- ❌ Ver reservas (lista completa)
- ❌ Ver mesas
- ❌ Cualquier gestión

### 2.3 Rol ENCARGADA

**Tabs visibles:** Inicio, Reservas, Mesas, Cocina

**Funcionalidades:**
- ✅ Todo lo de Camarero
- ✅ Crear nueva reserva
- ✅ Editar reserva existente
- ✅ Cancelar reserva (con motivo)
- ✅ Asignar mesas (drag & drop)
- ✅ Gestionar lista de espera
- ✅ Registrar incidencias
- ✅ Ver métricas del día
- ✅ Supervisar actividad del equipo
- ✅ Ver alertas de reservas pendientes
- ✅ Enviar avisos a cualquier rol
- ✅ Recibir notificaciones push

**NO puede:**
- ❌ Gestionar usuarios
- ❌ Cambiar contraseñas
- ❌ Cambiar configuración del sistema
- ❌ Ver reportes históricos completos

### 2.4 Rol ADMINISTRADORA

**Tabs visibles:** Todo + Panel Administración

**Funcionalidades:**
- ✅ Todo lo de Encargada
- ✅ Gestionar usuarios (crear/editar/eliminar)
- ✅ Cambiar contraseñas de usuarios
- ✅ Asignar roles
- ✅ Configurar horarios del restaurante
- ✅ Configurar mesas (número, capacidades)
- ✅ Configurar festivos
- ✅ Ver reportes diarios/semanales/mensuales
- ✅ Ver métricas completas
- ✅ Exportar datos a Excel/CSV
- ✅ Monitor del sistema (estado servicios)
- ✅ Ver logs del sistema

---

## 3. MATRIZ DE PERMISOS (RBAC)

| Permiso | administradora | encargada | camarero | cocina |
|---------|:--------------:|:---------:|:--------:|:------:|
| `reservas.ver` | ✅ | ✅ | ✅ | ❌ |
| `reservas.crear` | ✅ | ✅ | ❌ | ❌ |
| `reservas.editar` | ✅ | ✅ | ❌ | ❌ |
| `reservas.actualizar_estado` | ✅ | ✅ | ✅ | ❌ |
| `reservas.cancelar` | ✅ | ✅ | ❌ | ❌ |
| `mesas.ver` | ✅ | ✅ | ✅ | ❌ |
| `mesas.actualizar_estado` | ✅ | ✅ | ✅ | ❌ |
| `mesas.anadir_notas` | ✅ | ✅ | ✅ | ❌ |
| `cocina.ver` | ✅ | ✅ | ❌ | ✅ |
| `cocina.actualizar` | ✅ | ✅ | ❌ | ✅ |
| `cocina.enviar_avisos` | ✅ | ✅ | ✅ | ✅ |
| `usuarios.ver` | ✅ | ❌ | ❌ | ❌ |
| `usuarios.crear` | ✅ | ❌ | ❌ | ❌ |
| `usuarios.editar` | ✅ | ❌ | ❌ | ❌ |
| `usuarios.cambiar_password` | ✅ | ❌ | ❌ | ❌ |
| `usuarios.desactivar` | ✅ | ❌ | ❌ | ❌ |
| `config.ver` | ✅ | ❌ | ❌ | ❌ |
| `config.editar` | ✅ | ❌ | ❌ | ❌ |
| `reportes.ver` | ✅ | ✅ | ❌ | ❌ |
| `notificaciones.enviar` | ✅ | ✅ | ✅ | ✅ |
| `notificaciones.recibir` | ✅ | ✅ | ✅ | ✅ |

---

## 4. NOTIFICACIONES PUSH (FCM)

### 4.1 Tipos de Notificación

| Tipo | Origen | Destino | Ejemplo |
|------|--------|---------|---------|
| **Cliente sentado** | Camarero | Cocina | "Mesa 3 sentada - 4 personas" |
| **Plato listo** | Cocina | Camarero | "Mesa 5 - Entrantes listos" |
| **Nota en mesa** | Camarero | Cocina | "Mesa 2 - Sin gluten" |
| **Alerta reserva** | Backend | Todos | "Grupo de 10 en 30 min" |
| **Incidencia** | Encargada | Todos | "Terraza cerrada por lluvia" |

### 4.2 Implementación

**Backend (Firebase Admin SDK):**
```python
import firebase_admin
from firebase_admin import messaging

def enviar_notificacion(token: str, titulo: str, cuerpo: str, data: dict = None):
    message = messaging.Message(
        notification=messaging.Notification(
            title=titulo,
            body=cuerpo
        ),
        data=data or {},
        token=token
    )
    response = messaging.send(message)
    return response
```

**Android (FCM):**
```kotlin
class FCMService : FirebaseMessagingService() {
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        // Mostrar notificación
        mostrarNotificacion(
            titulo = remoteMessage.notification?.title,
            cuerpo = remoteMessage.notification?.body,
            data = remoteMessage.data
        )
    }
    
    override fun onNewToken(token: String) {
        // Enviar token al backend
        viewModelScope.launch {
            authRepository.registrarDeviceToken(token)
        }
    }
}
```

---

## 5. ONDAS DE EJECUCIÓN

### Wave 1: Backend - Usuarios en Airtable

```
├── Task 1: Crear tabla Usuarios en Airtable (via airtable-mcp)
├── Task 2: Crear UserRepository en Python (CRUD Airtable)
├── Task 3: Implementar bcrypt en AuthService (passlib)
├── Task 4: Migrar AuthService para usar UserRepository
├── Task 5: Crear usuarios iniciales (4 roles con credenciales oficiales)
├── Task 6: Implementar matriz de permisos RBAC completa
└── Task 7: Añadir endpoint para cambiar contraseña (solo administradora)
```

### Wave 2: Backend - Endpoints de Usuarios y Notificaciones

```
├── Task 8: GET /api/movil/auth/yo (datos usuario actual)
├── Task 9: PUT /api/movil/auth/password (cambiar propia contraseña)
├── Task 10: PUT /api/movil/usuarios/{id}/password (admin cambia cualquier contraseña)
├── Task 11: GET /api/movil/usuarios (listar, solo administradora)
├── Task 12: POST /api/movil/usuarios (crear, solo administradora)
├── Task 13: PUT /api/movil/usuarios/{id} (editar, solo administradora)
├── Task 14: DELETE /api/movil/usuarios/{id} (soft delete, solo administradora)
├── Task 15: POST /api/movil/dispositivo/token (registrar FCM token)
├── Task 16: POST /api/movil/notificaciones/enviar (enviar aviso)
└── Task 17: GET /api/movil/cocina/pedidos (para cocina)
```

### Wave 3: Backend - Despliegue Coolify

```
├── Task 18: Verificar configuración Coolify existente
├── Task 19: Añadir variables de entorno Firebase (FCM)
├── Task 20: Actualizar requirements.txt con nuevas dependencias
├── Task 21: Verificar health check endpoint
├── Task 22: Deploy a Coolify
└── Task 23: Verificar endpoints en producción
```

### Wave 4: Android - Autenticación Completa

```
├── Task 24: Crear ConfigScreen (cambiar URL servidor)
├── Task 25: Actualizar LoginScreen con credenciales oficiales
├── Task 26: Implementar EncryptedSharedPreferences para tokens
├── Task 27: Implementar persistencia de sesión (auto-login)
├── Task 28: Implementar logout real (invalidar token)
├── Task 29: Mejorar manejo de errores en login
└── Task 30: Guardar rol en sesión para futuras cargas
```

### Wave 5: Android - Navegación por Rol

```
├── Task 31: Implementar navegación dinámica (ocultar tabs por rol)
├── Task 32: Administradora: mostrar todas las tabs
├── Task 33: Cocina: mostrar solo tab Cocina
├── Task 34: Camarero: mostrar Reservas + Mesas
├── Task 35: Encargada: mostrar Inicio + Reservas + Mesas + Cocina
└── Task 36: Verificar permisos antes de cada navegación
```

### Wave 6: Android - Gestión de Usuarios (Administradora)

```
├── Task 37: Crear UserManagementScreen
├── Task 38: Implementar lista de usuarios con filtros
├── Task 39: Crear diálogo de nuevo usuario
├── Task 40: Implementar editar usuario
├── Task 41: Implementar desactivar usuario (soft delete)
├── Task 42: Implementar cambiar contraseña de usuario
└── Task 43: Validar que no se desactive la última administradora
```

### Wave 7: Android - Completar Funcionalidades

```
├── Task 44: KitchenScreen - Conectar con API real
├── Task 45: AdminScreen - Conectar estadísticas reales
├── Task 46: Crear ProfileScreen (ver perfil propio)
├── Task 47: Implementar cambio de propia contraseña
├── Task 48: Añadir indicador de conexión WebSocket
├── Task 49: Implementar pull-to-refresh global
├── Task 50: Implementar envío de notas/avisos en mesas
└── Task 51: Implementar comunicación con cocina
```

### Wave 8: Android - Notificaciones Push

```
├── Task 52: Configurar Firebase Cloud Messaging
├── Task 53: Crear FCMService para recibir notificaciones
├── Task 54: Implementar registro de device token
├── Task 55: Crear UI para enviar avisos
├── Task 56: Mostrar notificaciones entrantes
└── Task 57: Manejar tap en notificación (navegar a pantalla)
```

### Wave 9: Tests y Verificación

```
├── Task 58: Test login con cada rol
├── Task 59: Test permisos bloquean acciones no autorizadas
├── Task 60: Test navegación por rol
├── Task 61: Test gestión de usuarios (administradora)
├── Task 62: Test notificaciones push
├── Task 63: Test persistencia de sesión
├── Task 64: Generar APK release final
└── Task 65: Documentar cambios en README
```

---

## 6. ENDPOINTS API FINALES (todo en español)

### Autenticación
```
POST /api/movil/auth/login           ✅ Modificar (usuario en lugar de email)
POST /api/movil/auth/logout          ✅ Existe
POST /api/movil/auth/refresh         ✅ Existe
GET  /api/movil/auth/yo              ❌ Crear
PUT  /api/movil/auth/password        ❌ Crear (cambiar propia)
```

### Usuarios (solo administradora)
```
GET    /api/movil/usuarios           ❌ Crear
POST   /api/movil/usuarios           ❌ Crear
PUT    /api/movil/usuarios/{id}      ❌ Crear
DELETE /api/movil/usuarios/{id}      ❌ Crear (soft delete)
PUT    /api/movil/usuarios/{id}/password  ❌ Crear (admin cambia)
```

### Notificaciones
```
POST /api/movil/dispositivo/token    ❌ Crear (registrar FCM)
POST /api/movil/notificaciones/enviar ❌ Crear
```

### Cocina
```
GET  /api/movil/cocina/pedidos       ❌ Crear
PUT  /api/movil/cocina/pedidos/{id}  ❌ Crear
```

### Ya existen
```
GET/POST/PUT /api/movil/reservas/*   ✅
GET/PUT /api/movil/mesas/*           ✅
GET /api/movil/inicio/estadisticas   ✅
WS  /ws/reservas                     ✅
```

---

## 7. CRITERIOS DE ACEPTACIÓN

### Login y Sesión
- [ ] Login funciona con los 4 roles usando credenciales oficiales (usuario, no email)
- [ ] Sesión persiste al cerrar la app
- [ ] Logout limpia todo
- [ ] Refresh token funciona automáticamente

### Permisos
- [ ] Cocina solo ve tab Cocina
- [ ] Camarero ve Reservas + Mesas, NO Inicio ni Cocina ni Admin
- [ ] Encargada ve Inicio + Reservas + Mesas + Cocina, NO Admin
- [ ] Administradora ve todo incluyendo gestión usuarios

### Gestión Usuarios (Administradora)
- [ ] Puede crear usuarios con cualquier rol
- [ ] Puede cambiar rol de usuario existente
- [ ] Puede cambiar contraseña de cualquier usuario
- [ ] Puede desactivar usuario (soft delete)
- [ ] No puede desactivar la última administradora
- [ ] Contraseñas hasheadas con bcrypt

### Notificaciones Push
- [ ] Camarero puede enviar avisos a Cocina
- [ ] Cocina puede enviar avisos a Camareros
- [ ] Backend puede enviar avisos a todos
- [ ] Notificaciones se muestran en Android
- [ ] Tap en notificación navega a pantalla correcta

### UI/UX (Todo en español de España)
- [ ] Pantalla de configuración permite cambiar URL
- [ ] Indicador visible de conexión WebSocket
- [ ] Pull-to-refresh en todas las listas
- [ ] Estados vacíos claros
- [ ] Sin términos en inglés (no "waiter", "manager", etc.)

---

## 8. DESPLIEGUE COOLIFY

### Variables de Entorno Requeridas

```env
# Ya existentes
AIRTABLE_API_KEY=***
AIRTABLE_BASE_ID=appcUoRqLVqxQm7K2
OPENAI_API_KEY=***
DEEPSEEK_API_KEY=***
TWILIO_ACCOUNT_SID=***
TWILIO_AUTH_TOKEN=***
REDIS_URL=***

# Nuevas para FCM
FIREBASE_PROJECT_ID=en-las-nubes-restobar
FIREBASE_PRIVATE_KEY=***
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@***
```

### Health Check
```
GET /health → {"status": "ok", "version": "1.1.0"}
```

---

## 9. FUTURO: MIGRACIÓN DE AIRTABLE

**Objetivo a medio plazo**: Eliminar Airtable y migrar todo a Supabase/PostgreSQL dentro de Coolify.

**Beneficios**:
- Sin límites de rate (5 QPS de Airtable)
- Control total de datos
- Sin costes de Airtable
- Todo en un único sistema

**Plan futuro** (no en este proyecto):
1. Crear tablas en Supabase replicando Airtable
2. Migrar datos existentes
3. Actualizar repositorios Python
4. Eliminar dependencia de Airtable

---

**Fecha:** 2026-02-21
**Versión:** 2.0
**Idioma:** Español de España
**Basado en:** Investigación profunda + feedback del usuario
