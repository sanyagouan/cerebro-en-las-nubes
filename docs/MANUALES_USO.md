# 📚 MANUALES DE USO - SISTEMA "EN LAS NUBES"

**Sistema integral de gestión para En Las Nubes Restobar**

---

## 📋 ÍNDICE

1. [Manual del Camarero](#1-manual-del-camarero)
2. [Manual del Cocinero](#2-manual-del-cocinero)
3. [Manual de la Encargada](#3-manual-de-la-encargada)
4. [Manual de la Dueña/Admin](#4-manual-de-la-dueñaadmin)
5. [Guía de Instalación APK](#5-guía-de-instalación-apk)
6. [Preguntas Frecuentes](#6-preguntas-frecuentes)

---

## 1. MANUAL DEL CAMARERO

### 1.1 Descripción del Rol

Como **camarero/a**, tu función principal es atender a los clientes en sala. El sistema te ayuda a:
- Ver las reservas del día
- Saber qué mesas están ocupadas
- Marcar cuando los clientes se sientan o se van
- Recibir alertas de nuevas reservas

### 1.2 Acceso al Sistema

#### App Android (Móvil/Tablet)

1. Abre la app **"En Las Nubes"**
2. Introduce tu email y contraseña
3. Pulsa **"Iniciar Sesión"**

**Credenciales de prueba:**
```
Email: camarero@enlasnubes.com
Password: camarero123
```

#### Dashboard Web (PC)

1. Abre el navegador y ve a: `https://dashboard.enlasnubes.com`
2. Introduce tus credenciales
3. Pulsa **"Entrar"**

### 1.3 Pantalla Principal

Al entrar verás:

```
┌─────────────────────────────────────┐
│  📊 DASHBOARD                       │
├─────────────────────────────────────┤
│  Reservas hoy: 12                   │
│  Pendientes: 3                      │
│  Confirmadas: 8                     │
│  Clientos sentados: 1               │
├─────────────────────────────────────┤
│  [RESERVAS] [MESAS]                 │
└─────────────────────────────────────┘
```

### 1.4 Gestión de Reservas

#### Ver lista de reservas

1. Pulsa en la pestaña **"RESERVAS"**
2. Verás una lista con todas las reservas del día:

```
┌──────────────────────────────────────┐
│ 14:00 - Mesa 3T                      │
│ Juan García - 4 personas             │
│ Estado: ✅ Confirmada                │
│ [SENTAR] [VER]                       │
├──────────────────────────────────────┤
│ 14:30 - Mesa 1I                      │
│ María López - 2 personas             │
│ Estado: ⏳ Pendiente                 │
│ [CONFIRMAR] [LLAMAR]                 │
└──────────────────────────────────────┘
```

#### Marcar cliente como "Sentado"

1. Busca la reserva en la lista
2. Pulsa el botón **[SENTAR]**
3. El estado cambiará a "🪑 Sentado"
4. El sistema notificará automáticamente a cocina

#### Marcar mesa como "Liberada"

1. Ve a la pestaña **"MESAS"**
2. Busca la mesa que se va a liberar
3. Pulsa **[LIBERAR]**
4. El sistema actualizará la disponibilidad

### 1.5 Vista de Mesas

La vista de mesas muestra el estado en tiempo real:

```
┌─────────────────────────────────────┐
│           TERRAZA                   │
│  ┌───┐ ┌───┐ ┌───┐                 │
│  │1T │ │2T │ │3T │                 │
│  │🔴 │ │🟢 │ │🟡 │                 │
│  └───┘ └───┘ └───┘                 │
│                                      │
│           INTERIOR                   │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐           │
│  │1I │ │2I │ │3I │ │4I │           │
│  │🟢 │ │🔴 │ │🟢 │ │🟡 │           │
│  └───┘ └───┘ └───┘ └───┘           │
└─────────────────────────────────────┘

LEYENDA:
🟢 Libre    🟡 Reservada    🔴 Ocupada
```

### 1.6 Notificaciones

Recibirás notificaciones push en tu móvil cuando:

| Evento | Sonido | Prioridad |
|--------|--------|-----------|
| Nueva reserva | 🔔 Campana | Alta |
| Cliente ha llegado | 🔔 Campana 2x | Alta |
| Mesa liberada | ✨ Suave | Normal |
| Cancelación | ⚠️ Alerta | Media |

### 1.7 Atención al Cliente

#### Cuando llega un cliente con reserva:

1. **Saluda**: "¡Hola! ¿Tiene reserva?"
2. **Busca** la reserva en la app (por nombre o teléfono)
3. **Confirma**: "¿Es usted [Nombre] para [X] personas?"
4. **Acompaña** a la mesa
5. **Pulsa [SENTAR]** en la app

#### Si el cliente NO tiene reserva:

1. Consulta la disponibilidad en **MESAS**
2. Si hay mesa libre: acompáñalo y crea reserva desde la app
3. Si no hay mesa: ofrece lista de espera

### 1.8 Preguntas Frecuentes del Camarero

**P: ¿Cómo sé si una mesa está libre?**
R: En la vista MESAS, las mesas verdes (🟢) están libres.

**P: ¿Qué hago si el cliente no viene?**
R: Después de 15 minutos, marca como "No-show" en la app. La mesa quedará libre.

**P: ¿Puedo ver reservas de otros días?**
R: Sí, usa el selector de fecha en la parte superior.

---

## 2. MANUAL DEL COCINERO

### 2.1 Descripción del Rol

Como **cocinero/a**, tu función es:
- Ver el flujo de comensales previsto
- Recibir alertas de nuevos clientes sentados
- Marcar platos como listos
- Gestionar tiempos de espera

### 2.2 Acceso al Sistema

**Credenciales:**
```
Email: cocina@enlasnubes.com
Password: cocina123
```

### 2.3 Pantalla Principal - Vista Cocina

```
┌─────────────────────────────────────────────────┐
│  🍳 VISTA COCINA                        14:30   │
├─────────────────────────────────────────────────┤
│  PRÓXIMOS CLIENTES                              │
│  ┌─────────────────────────────────────────┐   │
│  │ 14:30 - Mesa 3T - 4 personas            │   │
│  │ Nota: Uno es celíaco                    │   │
│  │ ⏱️ Esperando hace 5 min                  │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │ 14:45 - Mesa 1I - 2 personas            │   │
│  │ Sin notas especiales                    │   │
│  │ ⏱️ Esperando hace 2 min                  │   │
│  └─────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│  OCUPACIÓN ACTUAL                               │
│  Comensales: 12/60                              │
│  Próxima reserva: 15:00 (6 personas)            │
└─────────────────────────────────────────────────┘
```

### 2.4 Alertas que Recibirás

| Alerta | Cuándo | Prioridad |
|--------|--------|-----------|
| Cliente sentado | Cuando el camarero marca "sentado" | Alta |
| Grupo grande | Reservas >8 personas | Alta |
| Nota especial | Si hay alergias o preferencias | Alta |
| Mesa liberada | Cuando termina el servicio | Baja |

### 2.5 Acciones Disponibles

1. **Ver detalles de reserva**: Pulsa sobre una reserva
2. **Marcar platos listos**: No implementado aún
3. **Añadir nota a cocina**: Para comunicar con sala

### 2.6 Notas Especiales

El sistema te avisará automáticamente de:
- ⚠️ **Alergias**: Muestra icono de alerta rojo
- 🌾 **Sin gluten**: Muestra icono de trigo tachado
- 🐕 **Mascotas**: Cliente viene con perro (terraza obligatoria)
- 🎂 **Cumpleaños**: Ocasión especial

---

## 3. MANUAL DE LA ENCARGADA

### 3.1 Descripción del Rol

Como **encargada**, tienes acceso completo a:
- Gestión de reservas (crear, modificar, cancelar)
- Asignación de mesas
- Gestión de incidencias
- Supervisión del equipo
- Métricas del día

### 3.2 Acceso al Sistema

**Credenciales:**
```
Email: encargada@enlasnubes.com
Password: encargada123
```

### 3.3 Pantalla Principal - Dashboard

```
┌─────────────────────────────────────────────────┐
│  📊 DASHBOARD ENCARGADA                 14:30   │
├─────────────────────────────────────────────────┤
│  MÉTRICAS DEL DÍA                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Reservas│ │ Ocupación│ │ No-shows│           │
│  │   18    │ │   65%    │ │    2    │           │
│  └─────────┘ └─────────┘ └─────────┘           │
│                                                  │
│  PRÓXIMAS 1 HORA                                │
│  15:00 - García, 6p - Confirmada                │
│  15:00 - López, 4p - Pendiente de confirmar     │
│  15:30 - Martínez, 2p - Confirmada              │
├─────────────────────────────────────────────────┤
│  ALERTAS                                        │
│  ⚠️ 2 reservas pendientes de confirmar          │
│  ⚠️ 1 grupo grande hoy (15 personas, 21:00)     │
└─────────────────────────────────────────────────┘
```

### 3.4 Gestión de Reservas

#### Crear nueva reserva

1. Pulsa botón **[+ NUEVA RESERVA]**
2. Rellena el formulario:

```
┌─────────────────────────────────────┐
│  NUEVA RESERVA                      │
├─────────────────────────────────────┤
│ Nombre: [                    ]      │
│ Teléfono: [                  ]      │
│ Fecha: [📅 20/02/2026]             │
│ Hora: [🕐 21:00]                    │
│ Personas: [4▼]                      │
│ Mesa: [Automática▼]                 │
│ Notas: [                    ]       │
│                                     │
│ [CANCELAR]        [CREAR RESERVA]   │
└─────────────────────────────────────┘
```

3. Pulsa **[CREAR RESERVA]**
4. El sistema enviará WhatsApp de confirmación automáticamente

#### Modificar reserva

1. Busca la reserva en la lista
2. Pulsa **[EDITAR]**
3. Modifica los campos necesarios
4. Pulsa **[GUARDAR]**

#### Cancelar reserva

1. Busca la reserva
2. Pulsa **[CANCELAR]**
3. Selecciona motivo:
   - Cliente solicita
   - No-show (no vino)
   - Error de reserva
   - Otro
4. Confirma cancelación

### 3.5 Asignación de Mesas

#### Vista mapa de mesas

```
┌─────────────────────────────────────────────┐
│  ASIGNACIÓN DE MESAS               [GUARDAR]│
├─────────────────────────────────────────────┤
│  TERRAZA                                    │
│  ┌─────┐ ┌─────┐ ┌─────┐                   │
│  │ 1T  │ │ 2T  │ │ 3T  │                   │
│  │ 🟢  │ │ 🟡  │ │ 🔴  │                   │
│  │cap:4│ │cap:4│ │cap:6│                   │
│  └─────┘ └─────┘ └─────┘                   │
│                                              │
│  INTERIOR                                   │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐           │
│  │ 1I  │ │ 2I  │ │ 3I  │ │ 4I  │           │
│  │ 🟡  │ │ 🟢  │ │ 🟢  │ │ 🟢  │           │
│  └─────┘ └─────┘ └─────┘ └─────┘           │
│                                              │
│  Arrastra las reservas a las mesas          │
└─────────────────────────────────────────────┘
```

#### Arrastrar y soltar

1. Las reservas pendientes aparecen a la izquierda
2. Arrastra una reserva a una mesa disponible
3. El sistema valida la capacidad
4. Pulsa **[GUARDAR]** para confirmar

### 3.6 Gestión de Incidencias

#### Tipos de incidencias

| Tipo | Ejemplo | Acción |
|------|---------|--------|
| Cliente insatisfecho | Queja sobre servicio | Registrar y escalar |
| Problema técnico | App no funciona | Reportar a soporte |
| Mesa no disponible | Reserva sin mesa | Reasignar o cancelar |
| Overbooking | Más reservas que mesas | Gestionar lista de espera |

#### Registrar incidencia

1. Ve a **CONFIGURACIÓN > INCIDENCIAS**
2. Pulsa **[+ NUEVA]**
3. Describe el problema
4. Asigna prioridad
5. Guarda

### 3.7 Supervisión del Equipo

Puedes ver la actividad de cada camarero:
- Reservas atendidas
- Tiempos de respuesta
- Mesas gestionadas

### 3.8 Lista de Espera

Cuando no hay disponibilidad:

1. Ve a **LISTA DE ESPERA**
2. Pulsa **[+ AÑADIR]**
3. Registra: Nombre, Teléfono, Personas, Hora preferida
4. Cuando se libere una mesa, el sistema notificará automáticamente

---

## 4. MANUAL DE LA DUEÑA/ADMIN

### 4.1 Descripción del Rol

Como **dueña/administradora**, tienes control total sobre:
- Todas las funciones de encargada
- Gestión de usuarios
- Configuración del sistema
- Métricas y reportes
- Facturación y costes

### 4.2 Acceso al Sistema

**Credenciales:**
```
Email: admin@enlasnubes.com
Password: admin123
```

### 4.3 Panel de Administración

```
┌─────────────────────────────────────────────────┐
│  ⚙️ ADMINISTRACIÓN                     🔔 3    │
├─────────────────────────────────────────────────┤
│  [Usuarios] [Config] [Reportes] [Sistema]       │
├─────────────────────────────────────────────────┤
│  RESUMEN SEMANAL                                │
│  ┌─────────────────────────────────────────┐   │
│  │ Reservas totales: 156                   │   │
│  │ Ocupación media: 72%                    │   │
│  │ Ingresos estimados: 12.450€             │   │
│  │ No-shows: 8 (5.1%)                      │   │
│  └─────────────────────────────────────────┘   │
│                                                  │
│  GRÁFICO DE OCUPACIÓN                           │
│  [📊 Ver gráfico completo]                      │
└─────────────────────────────────────────────────┘
```

### 4.4 Gestión de Usuarios

#### Lista de usuarios

```
┌─────────────────────────────────────────────────┐
│  USUARIOS DEL SISTEMA                    [+NEW] │
├─────────────────────────────────────────────────┤
│  Nombre        Email              Rol    Activo │
│  ─────────────────────────────────────────────  │
│  Ana García    ana@enlasnubes    Camarero  ✅   │
│  Carlos Ruiz   carlos@enlasnubes Cocina   ✅   │
│  Laura Díaz    laura@enlasnubes  Encarg.  ✅   │
│  Susana López  susana@enlasnubes Admin    ✅   │
└─────────────────────────────────────────────────┘
```

#### Crear nuevo usuario

1. Pulsa **[+ NUEVO USUARIO]**
2. Rellena: Nombre, Email, Rol, Contraseña inicial
3. El usuario recibirá email de bienvenida
4. Deberá cambiar contraseña en primer login

#### Roles disponibles

| Rol | Permisos |
|-----|----------|
| **Camarero** | Ver reservas, marcar sentado/liberado |
| **Cocina** | Ver flujo, recibir alertas |
| **Encargada** | CRUD reservas, asignar mesas, supervisar |
| **Admin** | Control total |

### 4.5 Configuración del Sistema

#### Horarios

```
┌─────────────────────────────────────┐
│  HORARIOS DEL RESTAURANTE           │
├─────────────────────────────────────┤
│  COMIDAS                            │
│  Lunes:    Cerrado                  │
│  Mar-Dom: 13:00 - 17:00            │
│                                      │
│  CENAS                               │
│  Lunes:    Cerrado                  │
│  Mar-Mié:  Cerrado                  │
│  Jueves:   20:00 - 24:00            │
│  Vie-Sáb:  20:00 - 01:00            │
│  Domingo:  Cerrado                  │
│                                      │
│  [EDITAR HORARIOS]                  │
└─────────────────────────────────────┘
```

#### Mesas

Configura las mesas disponibles:
- Número de mesas por zona
- Capacidad de cada mesa
- Capacidad ampliada (con sillas extra)

#### Festivos

Añade días festivos cuando el restaurante:
- Cierra completamente
- Tiene horario especial

### 4.6 Reportes y Métricas

#### Reportes disponibles

| Reporte | Frecuencia | Contenido |
|---------|------------|-----------|
| Diario | Cada mañana | Reservas del día anterior |
| Semanal | Lunes | Resumen semana, ocupación |
| Mensual | Día 1 | Métricas completas, ingresos |
| Personalizado | On-demand | Período seleccionado |

#### Métricas principales

```
┌─────────────────────────────────────────────┐
│  MÉTRICAS FEBRERO 2026                     │
├─────────────────────────────────────────────┤
│  Reservas totales:     312                  │
│  Personas atendidas:   1.248                │
│  Ocupación media:      68%                  │
│  Ticket medio:         32€                  │
│  Ingresos estimados:   39.936€              │
│  No-shows:             12 (3.8%)            │
│  Cancelaciones:        24 (7.7%)            │
│  Clientes recurrentes: 45%                  │
└─────────────────────────────────────────────┘
```

### 4.7 Monitor del Sistema

Verifica el estado de todos los componentes:

```
┌─────────────────────────────────────────────┐
│  🖥️ MONITOR DEL SISTEMA                    │
├─────────────────────────────────────────────┤
│  Backend API:        🟢 Online              │
│  Base de datos:      🟢 Conectado           │
│  Redis Cache:        🟢 Funcionando         │
│  VAPI (llamadas):    🟢 Operativo           │
│  WhatsApp (Twilio):  🟢 Conectado           │
│  WebSockets:         🟢 3 conexiones activas│
│                                              │
│  Última llamada:     14:25 (2 min atrás)   │
│  Reservas hoy:       18                     │
│  Errores últimas 24h: 2 (menores)           │
└─────────────────────────────────────────────┘
```

### 4.8 Respaldos y Seguridad

- Los datos se respaldan automáticamente cada día
- Puedes exportar reservas a Excel/CSV
- Los logs se mantienen 30 días

---

## 5. GUÍA DE INSTALACIÓN APK

### 5.1 Requisitos Previos

| Requisito | Detalle |
|-----------|---------|
| **Dispositivo** | Android 8.0 o superior |
| **Espacio** | 50 MB libres |
| **Conexión** | WiFi o datos móviles |
| **Permisos** | Notificaciones, Cámara (opcional) |

### 5.2 Instalación en Móvil Android

#### Paso 1: Descargar APK

1. Abre el navegador en tu móvil
2. Ve a: `https://enlasnubes.com/descargar`
3. Pulsa **"Descargar APK"**
4. Espera a que termine la descarga

#### Paso 2: Permitir instalación

1. Abre **Ajustes** del móvil
2. Ve a **Seguridad** o **Aplicaciones**
3. Activa **"Permitir de fuentes desconocidas"**
4. O permite instalación desde el navegador usado

#### Paso 3: Instalar

1. Abre la notificación de descarga completada
2. O ve a **Descargas** y pulsa el APK
3. Pulsa **INSTALAR**
4. Espera a que termine

#### Paso 4: Abrir y configurar

1. Pulsa **ABRIR**
2. Acepta los permisos solicitados:
   - Notificaciones: ✅ Sí (importante)
   - Cámara: Opcional (para escanear QR)
3. Introduce tus credenciales
4. ¡Listo!

### 5.3 Instalación en Tablet

El proceso es idéntico al móvil. Recomendaciones para tablets:

| Tablet | Uso recomendado |
|--------|-----------------|
| **Hostelería** | Vista de reservas en recepción |
| **Cocina** | Vista de flujo de clientes |
| **Sala** | Mapa de mesas para camareros |

### 5.4 Configuración Inicial

Tras instalar, configura:

1. **Notificaciones**: Ve a Ajustes > Notificaciones > Activa todas
2. **Sonido**: Asegúrate de tener sonido activo
3. **Pantalla**: Desactiva "Bloqueo automático" en uso

### 5.5 Solución de Problemas

| Problema | Solución |
|----------|----------|
| "No se puede instalar" | Activa fuentes desconocidas |
| "Aplicación no funciona" | Cierra y vuelve a abrir |
| "No llegan notificaciones" | Revisa permisos y conexión |
| "Error de conexión" | Verifica que hay internet |
| "Login incorrecto" | Verifica email y contraseña |

### 5.6 Actualización de la App

Cuando haya una nueva versión:

1. Recibirás notificación en el móvil
2. O aparecerá aviso al abrir la app
3. Descarga la nueva APK
4. Instala sobre la versión anterior
5. Tus datos se conservarán

---

## 6. PREGUNTAS FRECUENTES

### Generales

**P: ¿El sistema funciona sin internet?**
R: No, requiere conexión permanente. Los datos se guardan en la nube.

**P: ¿Puedo usar el sistema en varios dispositivos a la vez?**
R: Sí, puedes tener la app en móvil, tablet y el dashboard en PC simultáneamente.

**P: ¿Los datos están seguros?**
R: Sí, usamos encriptación y respaldos automáticos diarios.

### VAPI (Llamadas)

**P: ¿Qué hace el asistente telefónico?**
R: Responde llamadas, toma reservas, consulta horarios y disponibilidad.

**P: ¿Qué pasa si VAPI falla?**
R: Las llamadas se desvían al teléfono del restaurante.

**P: ¿Puedo personalizar el saludo?**
R: Sí, contacta con soporte para cambios en el mensaje.

### Dashboard

**P: ¿Cómo cambio mi contraseña?**
R: Ve a Configuración > Mi cuenta > Cambiar contraseña

**P: ¿Puedo ver datos de días pasados?**
R: Sí, usa el selector de fecha para navegar entre días.

### App Android

**P: ¿La app gasta mucha batería?**
R: No, está optimizada. ~2-3% por hora de uso activo.

**P: ¿Funciona en iPhone?**
R: No actualmente. Solo Android.

**P: ¿Cómo reporto un error?**
R: Envía email a soporte@enlasnubes.com con captura de pantalla.

---

## 📞 SOPORTE TÉCNICO

| Canal | Contacto | Horario |
|-------|----------|---------|
| **Email** | soporte@enlasnubes.com | 24/7 |
| **Teléfono** | 941 57 84 51 | 13:00-17:00, 20:00-24:00 |
| **WhatsApp** | +34 941 57 84 51 | Horario del restaurante |

---

**Versión del documento:** 1.0  
**Última actualización:** Febrero 2026  
**Autor:** Sistema En Las Nubes
