# Notepad: App Android Completa

## Aprendizajes

### 2026-02-21 - Task 1: Tabla Usuarios en Airtable

**Tabla creada:**
- Base ID: `appQ2ZXAR68cqDmJt`
- Table ID: `tblGYelDJso5QkiXL`
- Nombre: `Usuarios`

**Campos creados vía API:**
| Campo | Tipo | ID |
|-------|------|-----|
| Usuario | singleLineText | fldv1ixrpH32ETmBz |
| Nombre | singleLineText | fldksOPKHBbnfHTaB |
| Password_Hash | singleLineText | fldWVA7Dyam5oGmJ9 |
| Rol | singleSelect | fldDIFksSE15AMyid |
| Teléfono | phoneNumber | fldyTatziNeblyPkY |
| Device_Token | singleLineText | fld7OiMTgLaqIAbrS |

**Limitaciones encontradas:**
- La API de Airtable NO permite crear campos `checkbox` sin opciones específicas
- La API de Airtable NO permite crear campos `dateTime` sin opciones de formato
- La API de Airtable NO permite crear campos `createdTime` ni `lastModifiedTime`
- **Solución:** Añadir manualmente desde UI de Airtable los campos: Activo, Último_Login, Creado, Modificado

**Roles definidos (en español):**
- `administradora` (redBright)
- `encargada` (blueBright)
- `camarero` (greenBright)
- `cocina` (orangeBright)

## Decisiones

### 2026-02-21 - Credenciales
- Usar **usuario** en lugar de **email** para login
- Usuarios: `administradora`, `encargada`, `camarero`, `cocina`
- Contraseñas iniciales: `{rol}123` (ej: `administradora123`)
- La administradora puede cambiar contraseñas de cualquier usuario

## Problemas Resueltos

### 2026-02-21 - Airtable API Limitations
- No se pueden crear ciertos tipos de campos vía API
- Workaround: Crear campos esenciales vía API, el resto manualmente

### 2026-02-21 - passlib incompatibilidad con bcrypt
**Problema:** `passlib.context.CryptContext` falla con error: `ValueError: password cannot be longer than 72 bytes`
**Solución:** Usar `bcrypt` directamente:
```python
import bcrypt
BCRYPT_ROUNDS = 12

def _hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def _verify_password(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
```

## Usuarios en Airtable (Actualizados)

| Usuario | Airtable ID | Contraseña | Hash bcrypt |
|---------|-------------|------------|-------------|
| administradora | recRNBFCvwmozGSW2 | administradora123 | `$2b$12$X7YF06...` |
| encargada | rec4Y6toOmpwXHiFi | encargada123 | `$2b$12$YY6UYJ...` |
| camarero | recAizVFnFJEZUrL9 | camarero123 | `$2b$12$r4bcwH...` |
| cocina | recSxVEEd5a8ICGH7 | cocina123 | `$2b$12$sISTnF...` |

## Verificaciones Completadas

### 2026-02-21 - Flujo de Autenticación Completo
- ✅ UserRepository lee usuarios de Airtable
- ✅ bcrypt genera hashes válidos (`$2b$12$...`)
- ✅ bcrypt verifica contraseñas correctamente
- ✅ JWT tokens se generan y decodifican
- ✅ RBAC implementado con matriz de permisos

### 2026-02-21 - Wave 2: Endpoints de Usuarios y Notificaciones
**Endpoints implementados (9 nuevos):**
| Endpoint | Método | Permiso | Descripción |
|----------|--------|---------|-------------|
| `/auth/yo` | GET | Cualquiera autenticado | Perfil del usuario actual |
| `/auth/password` | PUT | Cualquiera autenticado | Cambiar propia contraseña |
| `/usuarios` | GET | usuarios.ver | Listar usuarios (admin) |
| `/usuarios` | POST | usuarios.crear | Crear usuario (admin) |
| `/usuarios/{id}` | GET | usuarios.ver | Ver usuario específico |
| `/usuarios/{id}` | PUT | usuarios.editar | Editar usuario (admin) |
| `/usuarios/{id}/password` | PUT | usuarios.cambiar_password | Admin cambia contraseña |
| `/usuarios/{id}` | DELETE | usuarios.desactivar | Soft delete (admin) |
| `/notificaciones/enviar` | POST | notificaciones.enviar | Enviar avisos a roles |
| `/cocina/pedidos` | GET | cocina.ver | Ver pedidos del día (cocina/encargada/admin) |

**Archivos modificados:**
- `src/api/mobile/mobile_api.py` - Añadidos 9 endpoints nuevos + modelos Pydantic
- Import corregido: `from src.application.services.auth_service import auth_service, TokenData`

**Nota sobre FCM:** El envío de notificaciones push está preparado pero requiere configuración de Firebase Cloud Messaging (fcm_service). Por ahora cuenta los dispositivos con token.
