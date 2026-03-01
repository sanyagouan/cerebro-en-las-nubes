# 📱 APP ANDROID - EN LAS NUBES RESTOBAR

**Tecnología:** Kotlin + Jetpack Compose + Hilt + Retrofit + WebSocket  
**Arquitectura:** MVVM + Clean Architecture  
**Estado:** Base implementada, listo para features específicas

---

## ✅ IMPLEMENTADO

### Backend (Python FastAPI)

| Componente | Archivo | Descripción |
|------------|---------|-------------|
| WebSocket Manager | `src/api/websocket/connection_manager.py` | Gestión de conexiones por rol |
| WebSocket Endpoint | `src/api/websocket/reservations_ws.py` | `/ws/reservations` con auth JWT |
| Auth Service | `src/services/auth_service.py` | JWT + RBAC (4 roles) |
| Push Notifications | `src/services/push_notification_service.py` | FCM para Android |
| Mobile API | `src/api/mobile/mobile_api.py` | Endpoints REST para app |

### Android App

| Componente | Descripción |
|------------|-------------|
| **Auth** | Login con JWT, token storage con DataStore |
| **Navegación** | Bottom navigation adaptativa por rol |
| **Reservas** | Lista de reservas del día con estados |
| **Mesas** | Vista de mesas con estado en tiempo real |
| **Roles** | 4 perfiles: Camarero, Cocinero, Encargada, Admin |
| **FCM** | Servicio de notificaciones push configurado |
| **DI** | Hilt para inyección de dependencias |
| **Networking** | Retrofit + OkHttp con logging |

---

## 📁 ESTRUCTURA DEL PROYECTO

```
android-app/
├── app/
│   ├── src/main/java/com/enlasnubes/restobar/
│   │   ├── data/
│   │   │   ├── model/           # User, Reservation, Table, etc.
│   │   │   ├── remote/          # RestobarApi (Retrofit)
│   │   │   └── repository/      # AuthRepository, RestobarRepository
│   │   ├── di/
│   │   │   └── NetworkModule.kt # Hilt providers
│   │   ├── presentation/
│   │   │   ├── auth/            # LoginScreen + ViewModel
│   │   │   ├── dashboard/       # DashboardScreen (contenedor)
│   │   │   ├── reservations/    # Lista de reservas
│   │   │   ├── tables/          # Mapa de mesas
│   │   │   ├── navigation/      # Rutas de navegación
│   │   │   └── theme/           # Colors, Theme, Typography
│   │   ├── service/
│   │   │   └── FcmService.kt    # Firebase Cloud Messaging
│   │   ├── MainActivity.kt
│   │   └── RestobarApplication.kt
│   └── build.gradle.kts
├── gradle/libs.versions.toml    # Version catalog
└── build.gradle.kts
```

---

## 🔐 ROLES Y PERMISOS

| Rol | Tabs | Permisos |
|-----|------|----------|
| **Camarero** | Reservas, Mesas | Ver reservas, marcar sentado/liberado, añadir notas |
| **Cocinero** | Cocina | Ver flujo de trabajo, recibir alertas, marcar platos listos |
| **Encargada** | Reservas, Mesas, Cocina | CRUD reservas, asignar mesas, gestionar incidencias |
| **Admin** | Todas las tabs | Acceso total, estadísticas, gestión de usuarios |

---

## 🔔 EVENTOS PUSH CONFIGURADOS

| Evento | Roles | Prioridad |
|--------|-------|-----------|
| Nueva reserva | Camarero, Encargada, Admin | Alta |
| Reserva confirmada | Camarero, Encargada, Admin | Normal |
| Cliente sentado | Todos | Alta |
| Mesa liberada | Todos | Normal |
| No-show | Camarero, Encargada, Admin | Normal |
| Grupo grande (>10) | Encargada, Admin | Alta |
| Alerta cocina | Todos | Alta |

---

## 🌐 API ENDPOINTS

```
POST /api/mobile/auth/login          # Login con email/password
POST /api/mobile/auth/logout         # Cerrar sesión
POST /api/mobile/auth/refresh        # Refrescar token

GET  /api/mobile/reservations        # Lista de reservas
GET  /api/mobile/reservations/{id}   # Detalle de reserva
PUT  /api/mobile/reservations/{id}/status  # Cambiar estado
POST /api/mobile/reservations        # Crear reserva

GET  /api/mobile/tables              # Lista de mesas
PUT  /api/mobile/tables/{id}/status  # Cambiar estado mesa

GET  /api/mobile/dashboard/stats     # Estadísticas del día

WS   /ws/reservations?token=JWT      # WebSocket para tiempo real
```

---

## 🚀 PRÓXIMOS PASOS

### Alto Prioridad
1. **WebSocket Client en Android** - Conectar con backend para tiempo real
2. **UI de Reservas** - Tarjetas con acciones rápidas (sentar, cancelar)
3. **Mapa de Mesas** - Vista visual drag-and-drop para encargada
4. **Vista Cocina** - Flujo de trabajo por hora con alertas

### Medio Prioridad
5. **Sincronización offline básica** - Cache local con Room
6. **Notificaciones push** - Completar integración FCM
7. **Estadísticas Admin** - Dashboard con gráficos

---

## 📋 CONFIGURACIÓN

### 1. Variables de entorno backend (.env)
```bash
JWT_SECRET_KEY=your-secret-key-min-32-chars
FCM_SERVER_KEY=your-firebase-server-key
```

### 2. Configurar API URL (android-app/app/build.gradle.kts)
```kotlin
buildConfigField("String", "API_BASE_URL", "\"https://your-api.com\"")
buildConfigField("String", "WS_BASE_URL", "\"wss://your-api.com\"")
```

### 3. Firebase Setup
- Agregar `google-services.json` en `android-app/app/`
- Habilitar Cloud Messaging en Firebase Console

---

## 🧪 CREDENCIALES DE PRUEBA

```
Email: test@enlasnubes.com
Password: test123
Rol: Camarero
```

---

## 📚 DEPENDENCIAS PRINCIPALES

| Librería | Versión | Uso |
|----------|---------|-----|
| Jetpack Compose | BOM 2023.10 | UI moderna declarativa |
| Hilt | 2.48 | Inyección de dependencias |
| Retrofit | 2.9.0 | HTTP client |
| Scarlet | 0.1.12 | WebSocket client |
| Coroutines | 1.7.3 | Async programming |
| DataStore | 1.0.0 | Local storage |
| FCM | 23.4.0 | Push notifications |

---

## 📝 NOTAS

- **Arquitectura:** Online-only (sin offline) como se solicitó
- **Distribución:** APK directo (sin Play Store)
- **Versión mínima Android:** API 26 (Android 8.0)
- **Estado actual:** Base funcional, listo para iterar features

---

**Documentación completa del contexto de negocio:**  
Ver `NOTEBOOKLM_CONTEXT_APP.md` en directorio raíz

**Autor:** Verdent Agent  
**Fecha:** 2026-02-08
