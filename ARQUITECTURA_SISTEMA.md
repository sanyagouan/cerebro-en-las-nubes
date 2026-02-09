# ARQUITECTURA DEL SISTEMA - Cerebro En Las Nubes

## Resumen Ejecutivo

**Cerebro En Las Nubes** es un sistema integral de gestión de reservas para el restaurante "En Las Nubes Restobar" que consta de 3 componentes principales, TODOS en un único repositorio (`cerebro-en-las-nubes`).

---

## Componentes del Sistema

### 1. ASISTENTE DE VOZ (VAPI) + Backend
**Ubicación:** `src/` (Python/FastAPI)

**Función:**
- Recibe llamadas telefónicas de clientes
- Procesa la conversación con IA (RouterAgent → LogicAgent → HumanAgent)
- Gestiona reservas en Airtable
- Envía confirmaciones por WhatsApp (Twilio)

**Tecnologías:**
- Python 3.11 + FastAPI
- VAPI (Voice AI)
- Twilio (WhatsApp)
- Airtable (Base de datos principal)
- Redis (Caché)

---

### 2. DASHBOARD WEB (Administración)
**Ubicación:** `dashboard/` (React + TypeScript + Vite)

**Función:**
- Interfaz web para administradores/encargados
- Gestión visual de reservas, mesas, personal
- Reportes y analytics
- Configuración del sistema

**Usuarios:**
- Administradora/Dueña
- Encargada del restaurante

**Tecnologías:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- WebSocket client (tiempo real)

---

### 3. APP ANDROID (Personal del restaurante)
**Ubicación:** `android-app/` (Kotlin + Jetpack Compose)

**Función:**
- App móvil para camareros, cocineros, encargada
- Comunicación en tiempo real con el sistema
- Actualización de estado de mesas y reservas
- Notificaciones push

**Usuarios:**
- Camareros (ver reservas, actualizar estado mesas)
- Cocineros (vista de ocupación por hora)
- Encargada (gestión completa)
- Administradora (todos los permisos)

**Tecnologías:**
- Kotlin
- Jetpack Compose (UI moderna)
- WebSocket (Scarlet)
- Firebase Cloud Messaging (notificaciones)

---

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CEREBRO EN LAS NUBES                             │
│                    (Repositorio único: cerebro-en-las-nubes)             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   ASISTENTE   │          │   DASHBOARD   │          │  APP ANDROID  │
│    DE VOZ     │          │     WEB       │          │   (Personal)  │
│   (Backend)   │          │  (Admin Web)  │          │  (Camareros)  │
└───────┬───────┘          └───────┬───────┘          └───────┬───────┘
        │                          │                          │
        │                    ┌─────┴─────┐                    │
        │                    │           │                    │
        ▼                    ▼           ▼                    ▼
   ┌─────────┐         ┌─────────┐  ┌─────────┐         ┌─────────┐
   │ Cliente │         │  Admin  │  │Encargada│         │Camarero │
   │  Llama  │         │  Dueña  │  │         │         │Cocinero │
   └─────────┘         └─────────┘  └─────────┘         └─────────┘
        │                                               
        ▼                                               
   ┌─────────┐                                         
   │  VAPI   │                                         
   │(Voz AI) │                                         
   └────┬────┘                                         
        │                                               
        ▼                                               
┌─────────────────────────────────────────────────────┐
│              BACKEND (Python/FastAPI)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Router    │  │    Logic    │  │   Human     │  │
│  │    Agent    │→ │    Agent    │→ │    Agent    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│         │                │                │          │
│         └────────────────┼────────────────┘          │
│                          ▼                           │
│              ┌───────────────────────┐               │
│              │     Airtable (BD)     │               │
│              └───────────────────────┘               │
│                          │                           │
│         ┌────────────────┼────────────────┐          │
│         ▼                ▼                ▼          │
│    ┌─────────┐      ┌─────────┐      ┌─────────┐    │
│    │  Redis  │      │Supabase │      │ Twilio  │    │
│    │ (Caché) │      │  (Auth) │      │(WhatsApp│    │
│    └─────────┘      └─────────┘      └─────────┘    │
└─────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │   Dashboard │  │ App Android │  │   WebSocket  │
   │    (React)  │  │   (Kotlin)  │  │ (Tiempo Real)│
   └─────────────┘  └─────────────┘  └─────────────┘
```

---

## Estructura del Repositorio (Monorepo)

```
cerebro-en-las-nubes/
│
├── src/                          # BACKEND (Python/FastAPI)
│   ├── api/
│   │   ├── vapi_router.py        # Webhook llamadas VAPI
│   │   ├── whatsapp_router.py    # Webhook WhatsApp Twilio
│   │   ├── mobile/
│   │   │   └── mobile_api.py     # API para app Android
│   │   ├── websocket/
│   │   │   └── reservations_ws.py # WebSocket tiempo real
│   │   └── sync/
│   │       └── sync_api.py       # Sincronización Airtable↔Supabase
│   ├── application/
│   │   ├── orchestrator.py       # Orquestador principal
│   │   └── agents/
│   │       ├── router_agent.py   # Clasifica intenciones
│   │       ├── logic_agent.py    # Lógica de negocio
│   │       └── human_agent.py    # Respuestas naturales
│   ├── services/
│   │   ├── auth_service.py       # Autenticación JWT
│   │   ├── sync_service.py       # Sincronización BD
│   │   └── push_notification_service.py # Notificaciones FCM
│   └── core/
│       └── config/
│           └── settings.py       # Configuración centralizada
│
├── dashboard/                    # DASHBOARD WEB (React)
│   ├── src/
│   │   ├── components/           # Componentes UI
│   │   │   ├── Reservas.tsx
│   │   │   ├── Mesas.tsx
│   │   │   └── Dashboard.tsx
│   │   ├── types.ts              # Tipos TypeScript
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── android-app/                  # APP ANDROID (Kotlin)
│   └── app/src/main/java/com/enlasnubes/restobar/
│       ├── MainActivity.kt
│       ├── data/
│       │   ├── websocket/        # WebSocket Manager
│       │   ├── repository/       # Repositorios
│       │   └── remote/           # API client
│       └── presentation/
│           ├── auth/             # Login
│           ├── reservations/     # Pantalla reservas
│           ├── tables/           # Pantalla mesas
│           ├── kitchen/          # Pantalla cocina
│           └── admin/            # Pantalla admin
│
├── scripts/                      # Scripts utilidad
│   ├── deploy.sh                 # Deploy a Coolify
│   └── load_mcp_secrets.ps1      # Cargar secrets
│
├── Dockerfile                    # Contenedor backend
├── coolify.yaml                  # Config Coolify
├── requirements.txt              # Dependencias Python
└── README.md
```

---

## Flujo de Datos

### 1. Cliente hace reserva por teléfono:
```
Cliente → VAPI → Backend (RouterAgent) → LogicAgent → Airtable
                                        ↓
                                    WhatsApp (confirmación)
                                        ↓
                                    App Android (notificación push)
```

### 2. Encargada gestiona desde Dashboard:
```
Dashboard Web → Backend API → Airtable
                   ↓
              WebSocket → App Android (actualización tiempo real)
```

### 3. Camarero actualiza desde App:
```
App Android → Backend API → Airtable
                 ↓
            WebSocket → Dashboard (sincronización)
                 ↓
            Push FCM → Otros dispositivos
```

---

## Tecnologías Clave

| Componente | Stack | Propósito |
|------------|-------|-----------|
| **Backend** | Python + FastAPI | API REST, WebSocket, lógica de negocio |
| **Base de Datos** | Airtable | Datos operativos (reservas, mesas) |
| **Autenticación** | Supabase Auth | JWT para app móvil |
| **Caché** | Redis | Sesiones, disponibilidad en tiempo real |
| **Voz** | VAPI | Asistente de voz telefónico |
| **WhatsApp** | Twilio | Confirmaciones y comunicaciones |
| **Dashboard** | React + Vite | Interfaz de administración web |
| **App Móvil** | Kotlin + Compose | App Android para personal |
| **Tiempo Real** | WebSocket | Sincronización entre sistemas |
| **Notificaciones** | Firebase FCM | Push a móviles del personal |
| **Hosting** | Coolify VPS | Deploy de todo el sistema |

---

## URLs del Sistema (Después del deploy)

| Servicio | URL Ejemplo |
|----------|---------------|
| Backend API | `https://api.enlasnubes.com` |
| WebSocket | `wss://api.enlasnubes.com/ws` |
| Dashboard | `https://admin.enlasnubes.com` |
| App Android | APK instalado en dispositivos |

---

## Próximos Pasos para Poner en Producción

1. **Configurar dominio** en Coolify
2. **Actualizar URL del API** en `android-app/app/build.gradle.kts`
3. **Configurar AIRTABLE_WEBHOOK_SECRET** en `.env.mcp`
4. **Implementar login real** con Supabase Auth
5. **Deploy a Coolify** con `scripts/deploy.sh`
6. **Compilar APK** de Android y distribuir al personal

---

## Nota sobre los Repositorios

Actualmente existen 3 repos en GitHub por confusiones previas:
- ✅ **`cerebro-en-las-nubes`** (CORRECTO - usar este)
- ❌ `asistente-voz-en-las-nubes` (obsoleto)
- ❌ `NUEVO-ASISTENTE-EN-LAS-NUBES` (obsoleto)

**Recomendación:** Archivar o eliminar los repos obsoletos y trabajar únicamente con `cerebro-en-las-nubes`.
