# Progreso - App Android Completa

## Completado

### Wave 1: Backend - Usuarios en Airtable ✅
- [x] Task 1: Crear tabla Usuarios en Airtable
- [x] Task 2: Crear UserRepository en Python
- [x] Task 3: Implementar bcrypt en AuthService
- [x] Task 4: Migrar AuthService para usar UserRepository
- [x] Task 5: Crear usuarios iniciales (4 roles)
- [x] Task 6: Implementar matriz de permisos RBAC
- [x] Task 7: Añadir endpoint cambiar contraseña

### Wave 2: Backend - Endpoints de Usuarios ✅
- [x] Task 8-17: Todos los endpoints de usuarios y notificaciones

### Wave 3: Backend - Despliegue Coolify ✅
- [x] Task 18-23: Backend desplegado y funcionando

### Wave 4: Android - Autenticación Completa ✅
- [x] Task 24-30: Login con usuario (no email), persistencia

### Wave 5: Android - Navegación por Rol ✅
- [x] Task 31-36: Navegación dinámica implementada

### Wave 6: Android - Gestión de Usuarios ✅
- [x] Task 37: UserManagementScreen existe
- [x] Task 38: Lista de usuarios con filtros
- [x] Task 39: Diálogo nuevo usuario
- [x] Task 40: Editar usuario
- [x] Task 41: Desactivar usuario (soft delete)
- [x] Task 42: Cambiar contraseña de usuario
- [x] Conexión con backend real (RestobarRepository)

### Wave 7: Android - Completar Funcionalidades ✅
- [x] Task 44: KitchenScreen - Conectado a API real
- [x] Task 46: ProfileScreen creado
- [x] Task 47: Cambio de propia contraseña implementado

### Wave 8: Android - Notificaciones Push FCM ✅
- [x] Task 52: FCM configurado
- [x] Task 53: FcmService implementado
- [x] Task 54: Registro de device token en login
- [x] Task 56: Notificaciones entrantes mostradas

### Wave 9: Documentación ✅
- [x] Progreso documentado
- [x] Issues documentados

---

## Commits Realizados

| Commit | Wave | Descripción |
|--------|------|-------------|
| `69574d4` | Wave 6 | Gestión de usuarios completa |
| `64842cb` | Wave 7 | KitchenScreen API real + ProfileScreen |
| `c1ad90e` | Wave 8 | FCM notificaciones push integradas |

---

## Archivos Creados/Modificados

### Nuevos
- `presentation/admin/UserManagementScreen.kt`
- `presentation/profile/ProfileScreen.kt`
- `presentation/profile/ProfileViewModel.kt`

### Modificados
- `data/remote/RestobarApi.kt` - endpoints usuarios + changeOwnPassword
- `data/repository/RestobarRepository.kt` - funciones usuarios + perfil
- `data/repository/AuthRepository.kt` - getCurrentUser
- `presentation/admin/AdminScreen.kt` - navegación
- `presentation/admin/AdminViewModel.kt` - UserManagementState
- `presentation/dashboard/DashboardScreen.kt` - navegación perfil
- `presentation/kitchen/KitchenViewModel.kt` - API real
- `presentation/auth/LoginViewModel.kt` - token FCM
- `service/FcmService.kt` - token storage

---

**Última actualización:** 2026-02-21
**Estado:** ✅ COMPLETADO (Wave 1-8)
**Pendiente:** Generación APK release (manual)
