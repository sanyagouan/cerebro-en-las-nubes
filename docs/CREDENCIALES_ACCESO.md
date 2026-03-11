# 🔐 Credenciales de Acceso al Sistema

**Fecha de creación:** 2026-03-08  
**Sistema:** Dashboard de Gestión - En Las Nubes Restobar

---

## 📋 Usuarios Creados

### 1. Administradora (Alba)

**Propósito:** Acceso total al sistema con permisos de administración

```
Usuario: administradora
Password: AdminNubes2026!
Rol: administradora
Airtable ID: reck9DZOGExbriPJK
```

**Permisos:**
- ✅ Ver, crear, editar y cancelar reservas
- ✅ Gestionar mesas (ver, actualizar estado, añadir notas)
- ✅ Ver y gestionar cocina
- ✅ Gestionar usuarios (crear, editar, cambiar contraseñas, desactivar)
- ✅ Ver y editar configuración del sistema
- ✅ Ver reportes
- ✅ Enviar y recibir notificaciones

---

### 2. Encargada (María)

**Propósito:** Gestión operativa del restaurante

```
Usuario: encargada
Password: Encargada2026!
Rol: encargada
Airtable ID: recv8GmH16BkSfzGm
```

**Permisos:**
- ✅ Ver, crear, editar y cancelar reservas
- ✅ Gestionar mesas
- ✅ Ver y actualizar cocina
- ✅ Enviar avisos a cocina
- ✅ Ver reportes
- ✅ Enviar y recibir notificaciones

---

### 3. Técnico (Soporte)

**Propósito:** Soporte técnico y pruebas del sistema

```
Usuario: tecnico
Password: Tecnico2026!
Rol: camarero (temporal)
Airtable ID: rec7F6EPhh09Q7aX4
```

**Permisos actuales (como camarero):**
- ✅ Ver reservas
- ✅ Actualizar estado de reservas
- ✅ Ver mesas
- ✅ Actualizar estado de mesas
- ✅ Añadir notas a mesas
- ✅ Enviar avisos a cocina

**⚠️ NOTA:** El rol "tecnico" completo con todos los permisos está pendiente de configurar en Airtable. Actualmente usa el rol "camarero" como temporal.

---

## 🔒 Seguridad de Contraseñas

Las contraseñas están hasheadas con **bcrypt** usando 12 rounds (factor de trabajo óptimo):

```
- Administradora: $2b$12$5FInDnBCulmSxFKtbiXL.e...
- Encargada: $2b$12$PFIPhFJiotvuQej7kMU2Hu...
- Técnico: $2b$12$pWVjEpidh7HiTdAeX0H8wu...
```

### Requisitos de contraseña:
- Mínimo 8 caracteres
- Contiene mayúsculas y minúsculas
- Contiene números
- Contiene caracteres especiales

---

## 📱 Cómo Acceder al Dashboard

### Desde Navegador Web:

1. Abrir navegador (Chrome, Firefox, Safari, Edge)
2. Ir a la URL del dashboard: `https://[URL-DEL-SERVIDOR]/dashboard`
3. Ingresar las credenciales:
   - **Usuario:** `administradora`, `encargada`, o `tecnico`
   - **Password:** (ver arriba)
4. Hacer clic en "Iniciar Sesión"

### Desde App Móvil Android (próximamente):

1. Abrir la app "En Las Nubes - Gestión"
2. Ingresar usuario y contraseña
3. Tocar "Iniciar Sesión"
4. (Opcional) Activar "Recordar sesión"

---

## ⚙️ Cambiar Contraseña

### Para usuarios con acceso:

1. Iniciar sesión en el dashboard
2. Ir a **Perfil** (ícono de usuario, esquina superior derecha)
3. Seleccionar "Cambiar Contraseña"
4. Ingresar:
   - Contraseña actual
   - Nueva contraseña
   - Confirmar nueva contraseña
5. Hacer clic en "Guardar"

### Para administradores (cambiar contraseña de otros usuarios):

1. Iniciar sesión como **administradora**
2. Ir a **Configuración** → **Usuarios**
3. Buscar el usuario
4. Hacer clic en el menú (⋮) → "Cambiar Contraseña"
5. Ingresar la nueva contraseña
6. Confirmar

---

## 🔧 Verificación Técnica

### Script de verificación (para técnicos):

```bash
# Ejecutar en el directorio del proyecto
python test_login.py
```

**Resultado esperado:**
```
============================================================
FIN DE PRUEBAS - 3/3 autenticaciones exitosas
============================================================
```

### Verificación manual con bcrypt:

```python
import bcrypt

# Verificar contraseña
password = "AdminNubes2026!"
hash = "$2b$12$5FInDnBCulmSxFKtbiXL.e4eUxnaQr3xomsmWtRFDZBwx37DayhXm"

result = bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
print(f"Verificación: {result}")  # Debe imprimir: True
```

---

## 🚨 Problemas Comunes

### "Usuario o contraseña incorrectos"

**Soluciones:**
1. Verificar que el usuario esté escrito **exactamente** como se muestra (sin espacios)
2. Verificar que la contraseña incluya mayúsculas, números y símbolos
3. Verificar que el usuario esté **activo** en Airtable
4. Si persiste el error, contactar al administrador del sistema

### "Error de conexión"

**Soluciones:**
1. Verificar conexión a internet
2. Verificar que el servidor backend esté corriendo
3. Verificar que Airtable API esté configurada correctamente
4. Contactar a soporte técnico

### Token expirado

Los tokens de acceso expiran después de **1 hora** por seguridad. Simplemente vuelve a iniciar sesión.

---

## 📞 Soporte

**Para problemas de acceso:**
- Email: soporte@enlasnubes.com (provisional)
- Teléfono: 941 XXX XXX (provisional)
- Usuario técnico en sistema: `tecnico`

---

## ⚠️ IMPORTANTE

1. **NO compartir** las contraseñas con personas no autorizadas
2. **Cambiar la contraseña** periódicamente (recomendado cada 90 días)
3. **NO anotar** las contraseñas en lugares visibles
4. **Cerrar sesión** al terminar de usar el sistema
5. **Reportar** cualquier actividad sospechosa inmediatamente

---

**Última actualización:** 2026-03-08  
**Responsable:** Sistema Técnico  
**Versión:** 1.0
