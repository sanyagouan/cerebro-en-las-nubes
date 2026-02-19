# Firebase Setup para App Android

## Resumen

La app Android de En Las Nubes Restobar usa Firebase Cloud Messaging (FCM) para enviar notificaciones push a los empleados. Sin Firebase, la app compilará pero NO recibirá notificaciones.

---

## Opciones

### Opción A: Con Firebase (Recomendado - Notificaciones Push)

Ventajas:
- Notificaciones push en tiempo real
- Alertas de nuevas reservas
- Avisos de grupos grandes
- Comunicación instantánea con el equipo

### Opción B: Sin Firebase (Solo WebSocket)

Ventajas:
- No requiere configuración adicional
- Funciona con WebSocket para tiempo real
- Más rápido de implementar

Desventajas:
- NO hay notificaciones cuando la app está cerrada
- Solo recibe datos cuando la app está abierta

---

## Configuración Firebase (Opción A)

### Paso 1: Crear Proyecto en Firebase Console

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Haz clic en "Añadir proyecto"
3. Nombre del proyecto: `enlasnubes-restobar`
4. Desactiva Google Analytics (no necesario para FCM)
5. Haz clic en "Crear proyecto"

### Paso 2: Añadir App Android

1. En el panel del proyecto, haz clic en el icono de Android
2. **Nombre del paquete:** `com.enlasnubes.restobar`
3. **Apodo de la app:** En Las Nubes Restobar
4. **Certificado SHA-1:** (Opcional, solo para Google Sign-In)

### Paso 3: Descargar google-services.json

1. Firebase generará el archivo `google-services.json`
2. Descárgalo
3. Colócalo en: `android-app/app/google-services.json`

### Paso 4: Habilitar Cloud Messaging

1. En Firebase Console, ve a **Engage > Cloud Messaging**
2. Copia la **Server Key** (clave del servidor)
3. Añádela a tu `.env` del backend:
   ```
   FCM_SERVER_KEY=tu_clave_del_servidor_aqui
   ```

### Paso 5: Descomentar el plugin

En `android-app/app/build.gradle.kts`, cambia:

```kotlin
// ANTES:
// alias(libs.plugins.google.services)

// DESPUÉS:
alias(libs.plugins.google.services)
```

### Paso 6: Compilar APK

```bash
cd android-app
./gradlew assembleRelease
```

El APK estará en: `android-app/app/build/outputs/apk/release/`

---

## Compilar SIN Firebase (Opción B)

Si prefieres compilar sin Firebase por ahora:

1. **Eliminar dependencia FCM:**

   En `android-app/app/build.gradle.kts`, comenta o elimina:
   ```kotlin
   // implementation(libs.firebase.messaging)
   ```

2. **Eliminar FcmService:**

   Borra o comenta el archivo: `android-app/app/src/main/java/com/enlasnubes/restobar/service/FcmService.kt`

3. **Compilar APK:**

   ```bash
   cd android-app
   ./gradlew assembleRelease
   ```

---

## Requisitos Previos

### Para compilar el APK necesitas:

1. **Android Studio** (recomendado) o JDK 17+
2. **Android SDK** API 34
3. **Gradle** 8.2+

### Verificar entorno:

```bash
# Verificar Java
java -version  # Debe ser 17+

# Verificar Gradle
cd android-app
./gradlew --version
```

---

## Comandos de Compilación

### Debug APK (desarrollo)

```bash
cd android-app
./gradlew assembleDebug
```

Ubicación: `app/build/outputs/apk/debug/app-debug.apk`

### Release APK (producción)

```bash
cd android-app
./gradlew assembleRelease
```

Ubicación: `app/build/outputs/apk/release/app-release.apk`

### Con firma (para distribución)

1. Crear keystore:
   ```bash
   keytool -genkey -v -keystore enlasnubes.keystore -alias enlasnubes -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Configurar en `app/build.gradle.kts`:
   ```kotlin
   signingConfigs {
       create("release") {
           storeFile = file("../enlasnubes.keystore")
           storePassword = "tu_password"
           keyAlias = "enlasnubes"
           keyPassword = "tu_password"
       }
   }
   ```

3. Compilar:
   ```bash
   ./gradlew assembleRelease
   ```

---

## Instalación del APK

### Método 1: USB (ADB)

```bash
adb install app/build/outputs/apk/release/app-release.apk
```

### Método 2: Descarga directa

1. Sube el APK a un servidor o Google Drive
2. Comparte el enlace con los empleados
3. En el móvil: Descargar > Abrir > Instalar
4. Si sale error "Instalación bloqueada":
   - Ajustes > Seguridad > Orígenes desconocidos > Permitir

### Método 3: Android Studio

1. Conecta el dispositivo por USB
2. Android Studio > Run > Select Device

---

## Credenciales de Prueba

Una vez instalada la app:

```
Email: camarero@enlasnubes.com
Password: camarero123
```

```
Email: encargada@enlasnubes.com
Password: encargada123
```

---

## Troubleshooting

### Error: "google-services.json not found"

**Solución:** Añade el archivo descargado de Firebase en `android-app/app/`

### Error: "Failed to resolve: com.google.firebase"

**Solución:** Asegúrate de tener Google Play Services actualizado en el SDK Manager

### Error: "API_BASE_URL not accessible"

**Solución:** Verifica que el backend está corriendo en:
`https://go84sgscs4ckcs08wog84o0o.app.generaia.site`

### La app no conecta al backend

1. Verifica conexión a internet
2. Comprueba que el backend está healthy:
   ```bash
   curl https://go84sgscs4ckcs08wog84o0o.app.generaia.site/health
   ```
3. Revisa logs de la app en Logcat

---

## Próximos Pasos

1. [ ] Crear proyecto en Firebase Console
2. [ ] Descargar google-services.json
3. [ ] Configurar FCM Server Key en backend
4. [ ] Compilar APK
5. [ ] Distribuir a empleados
6. [ ] Probar notificaciones push

---

**Fecha:** 2026-02-19  
**Autor:** Verdent Agent
