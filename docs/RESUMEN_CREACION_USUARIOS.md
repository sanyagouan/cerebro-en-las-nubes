# Resumen Técnico: Creación de Usuarios en Airtable

**Fecha:** 2026-03-08  
**Tarea:** Resolver bloqueador crítico de autenticación  
**Status:** ✅ COMPLETADO

---

## 🎯 Objetivo

Crear usuarios en la tabla "Usuarios" de Airtable para permitir el acceso al dashboard con autenticación real (bcrypt + JWT).

---

## ✅ Tareas Realizadas

### 1. Verificación de Infraestructura

**Base de Airtable:**
- Base ID: `appQ2ZXAR68cqDmJt`
- Tabla: `Usuarios` (ID: `tblGYelDJso5QkiXL`)

**Schema validado:**
```
- Usuario (singleLineText) - Nombre de usuario único
- Nombre (singleLineText) - Nombre completo
- Password_Hash (singleLineText) - Hash bcrypt
- Rol (singleSelect) - Opciones: administradora, encargada, camarero, cocina
- Activo (checkbox) - Estado del usuario
- Teléfono (phoneNumber) - Opcional
- Device_Token (singleLineText) - Opcional para push notifications
```

---

### 2. Generación de Hashes Bcrypt

**Algoritmo:** bcrypt con 12 rounds (factor de trabajo óptimo)

**Script utilizado:** [`create_users.py`](../create_users.py)

**Contraseñas hasheadas:**
```python
# Usuario: administradora
Password: AdminNubes2026!
Hash: $2b$12$5FInDnBCulmSxFKtbiXL.e4eUxnaQr3xomsmWtRFDZBwx37DayhXm

# Usuario: encargada
Password: Encargada2026!
Hash: $2b$12$PFIPhFJiotvuQej7kMU2HuXoWjoK.b1BJQ2cMT.41vHZcq9sAgxwW

# Usuario: tecnico
Password: Tecnico2026!
Hash: $2b$12$pWVjEpidh7HiTdAeX0H8wuxAQImOTPp/xGZP5SSSq5bopCtnwLDg.
```

---

### 3. Creación de Usuarios en Airtable

**Usuarios creados:**

| Usuario | Nombre | Rol | Airtable ID | Activo |
|---------|--------|-----|-------------|--------|
| `administradora` | Alba | administradora | `reck9DZOGExbriPJK` | ✅ |
| `encargada` | María | encargada | `recv8GmH16BkSfzGm` | ✅ |
| `tecnico` | Soporte | camarero* | `rec7F6EPhh09Q7aX4` | ✅ |

**Nota:** El usuario `tecnico` usa el rol "camarero" temporalmente porque la opción "tecnico" no existe en el campo Rol de Airtable.

---

### 4. Limpieza de Duplicados

**Usuarios eliminados:**
- `recRNBFCvwmozGSW2` - administradora antigua (sin contraseña correcta)
- `rec7UQyg8EHVSX4Hh` - tecnico duplicado
- `recsteF4QH6f0vRel` - soporte_tecnico antiguo

---

### 5. Pruebas de Autenticación

**Script de prueba:** [`test_login.py`](../test_login.py)

**Resultado:**
```
============================================================
FIN DE PRUEBAS - 3/3 autenticaciones exitosas
============================================================
```

**Tests ejecutados:**
1. ✅ Login con `administradora` / `AdminNubes2026!` → **SUCCESS**
2. ✅ Login con `encargada` / `Encargada2026!` → **SUCCESS**
3. ✅ Login con `tecnico` / `Tecnico2026!` → **SUCCESS**
4. ✅ Login con contraseña incorrecta → **FAILED** (esperado)
5. ✅ Login con usuario inexistente → **FAILED** (esperado)

**Tokens JWT generados y verificados correctamente.**

---

## 🔒 Seguridad Implementada

### Bcrypt

- **Rounds:** 12 (recomendado para producción)
- **Tiempo de hash:** ~250ms por contraseña
- **Resistencia:** Altamente resistente a ataques de fuerza bruta

### JWT

- **Algoritmo:** HS256
- **Expiración:** 1 hora (access token)
- **Refresh:** 7 días (refresh token)
- **Payload:**
  ```json
  {
    "sub": "user_id",
    "usuario": "administradora",
    "nombre": "Alba",
    "rol": "administradora",
    "type": "access",
    "exp": 1234567890,
    "iat": 1234567800
  }
  ```

---

## 📝 Permisos por Rol

### Administradora
```python
[
    "reservas.ver", "reservas.crear", "reservas.editar",
    "reservas.actualizar_estado", "reservas.cancelar",
    "mesas.ver", "mesas.actualizar_estado", "mesas.anadir_notas",
    "cocina.ver", "cocina.actualizar", "cocina.enviar_avisos",
    "usuarios.ver", "usuarios.crear", "usuarios.editar",
    "usuarios.cambiar_password", "usuarios.desactivar",
    "config.ver", "config.editar",
    "reportes.ver",
    "notificaciones.enviar", "notificaciones.recibir"
]
```

### Encargada
```python
[
    "reservas.ver", "reservas.crear", "reservas.editar",
    "reservas.actualizar_estado", "reservas.cancelar",
    "mesas.ver", "mesas.actualizar_estado", "mesas.anadir_notas",
    "cocina.ver", "cocina.actualizar", "cocina.enviar_avisos",
    "reportes.ver",
    "notificaciones.enviar", "notificaciones.recibir"
]
```

### Camarero (temporal para técnico)
```python
[
    "reservas.ver", "reservas.actualizar_estado",
    "mesas.ver", "mesas.actualizar_estado", "mesas.anadir_notas",
    "cocina.enviar_avisos",
    "notificaciones.enviar", "notificaciones.recibir"
]
```

---

## 🔧 Configuración Técnica

### Variables de Entorno Requeridas

```bash
# Airtable
AIRTABLE_API_KEY=patXXXXXXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appQ2ZXAR68cqDmJt

# JWT
JWT_SECRET_KEY=dev-secret-key-change-in-production  # ⚠️ CAMBIAR EN PRODUCCIÓN
JWT_ALGORITHM=HS256
```

### Dependencias

```python
bcrypt==4.1.2
passlib==1.7.4
python-jose[cryptography]==3.3.0
pyairtable==2.1.0
```

---

## 📊 Diagrama de Flujo de Autenticación

```
┌──────────────────────────────────────────────────────────┐
│ FLUJO DE LOGIN                                           │
└──────────────────────────────────────────────────────────┘

Usuario ingresa credenciales
         │
         ▼
[POST /api/auth/login]
  Body: {usuario, password}
         │
         ▼
UserRepository.get_by_usuario(usuario)
         │
         ├─[No existe]──► 401 Usuario no encontrado
         │
         ├─[Inactivo]───► 401 Usuario inactivo
         │
         ▼
bcrypt.checkpw(password, user.password_hash)
         │
         ├─[Fail]───────► 401 Contraseña incorrecta
         │
         ▼
Crear access_token (JWT, 1h)
Crear refresh_token (JWT, 7 días)
         │
         ▼
200 OK
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {...}
}
```

---

## ⚠️ Problemas Conocidos y Soluciones

### Problema 1: Rol "tecnico" no existe en Airtable

**Descripción:** El campo Rol en Airtable solo tiene las opciones: administradora, encargada, camarero, cocina.

**Solución temporal:** Usuario `tecnico` usa rol `camarero`.

**Solución permanente:** Agregar opción "tecnico" en Airtable:
1. Abrir base `appQ2ZXAR68cqDmJt`
2. Ir a tabla "Usuarios"
3. Click en campo "Rol" → Configuración
4. Agregar nueva opción: `tecnico` (color: purple)

### Problema 2: Usuarios duplicados

**Descripción:** Había usuarios antiguos con mismo nombre de usuario.

**Solución:** Eliminados manualmente usando MCP de Airtable.

**Prevención:** Implementar constraint único en campo `Usuario` en Airtable.

---

## 📚 Documentación Generada

1. [`CREDENCIALES_ACCESO.md`](./CREDENCIALES_ACCESO.md) - Credenciales para el staff
2. [`RESUMEN_CREACION_USUARIOS.md`](./RESUMEN_CREACION_USUARIOS.md) - Este documento
3. `create_users.py` - Script de creación de usuarios
4. `test_login.py` - Script de pruebas de autenticación

---

## ✅ Checklist de Verificación

- [x] Tabla "Usuarios" existe en Airtable
- [x] Schema de tabla correctamente configurado
- [x] 3 usuarios creados con contraseñas hasheadas (bcrypt, 12 rounds)
- [x] Usuarios duplicados eliminados
- [x] Autenticación funcional (3/3 tests exitosos)
- [x] Tokens JWT generados y verificados
- [x] Documentación de credenciales creada
- [x] Instrucciones para el staff documentadas

---

## 🚀 Próximos Pasos

1. **Agregar rol "tecnico" en Airtable** (campo Rol)
2. **Actualizar usuario técnico** con el rol correcto
3. **Cambiar JWT_SECRET_KEY** en producción (usar valor seguro aleatorio)
4. **Implementar constraint único** en campo Usuario (Airtable)
5. **Configurar recordatorio** de cambio de contraseña cada 90 días
6. **Implementar logging** de intentos de login fallidos (seguridad)

---

**Responsable:** Sistema Técnico  
**Aprobado por:** Pendiente  
**Fecha de completación:** 2026-03-08  
**Versión:** 1.0
