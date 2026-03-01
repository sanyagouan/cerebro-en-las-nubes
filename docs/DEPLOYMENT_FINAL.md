# GUIA DE DEPLOYMENT FINAL

## Estado Actual: LISTO PARA DEPLOY

---

## 1. DASHBOARD - Despliegue en Coolify

### Archivos Preparados:
- `dashboard/Dockerfile` - Multi-stage build con nginx
- `dashboard/nginx.conf` - Configuracion de proxy para API
- `dashboard/.dockerignore` - Exclusiones para build
- `dashboard/dist/` - Build de produccion listo

### Pasos para desplegar:

1. **En Coolify Dashboard:**
   - Crear nuevo recurso "Static Site" o "Docker Compose"
   - Conectar repositorio de GitHub
   - Seleccionar directorio: `/dashboard`
   - Puerto: `80`

2. **O alternativamente, subir build manual:**
   ```bash
   # El build ya esta listo en dashboard/dist/
   # Subir esa carpeta como sitio estatico en Coolify
   ```

3. **Variables de entorno (si se necesita):**
   ```
   VITE_API_URL=https://go84sgscs4ckcs08wog84o0o.app.generaia.site
   ```

---

## 2. APK ANDROID - Compilacion

### Archivos Preparados:
- `android-app/app/google-services.json` - Firebase configurado
- `android-app/app/build.gradle.kts` - API URL actualizada
- `android-app/gradle/wrapper/gradle-wrapper.properties` - Gradle 8.2
- `android-app/gradlew.bat` - Wrapper script Windows

### Opcion A: Desde Android Studio (RECOMENDADO)

1. Abrir Android Studio
2. File > Open > Seleccionar carpeta `android-app`
3. Esperar a que Gradle sincronice
4. Build > Build Bundle(s) / APK(s) > Build APK(s)
5. El APK estara en: `app/build/outputs/apk/release/app-release.apk`

### Opcion B: Desde linea de comandos

```powershell
cd android-app

# Descargar Gradle Wrapper JAR (primera vez)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/gradle/gradle/master/gradle/wrapper/gradle-wrapper.jar" -OutFile "gradle/wrapper/gradle-wrapper.jar"

# Compilar APK de release
.\gradlew.bat assembleRelease
```

### Opcion C: Usar Gradle global

Si tienes Gradle instalado globalmente:
```powershell
cd android-app
gradle assembleRelease
```

---

## 3. INSTALACION APK

### Metodo 1: USB (ADB)
```powershell
adb install app/build/outputs/apk/release/app-release.apk
```

### Metodo 2: Transferencia directa
1. Copiar APK al movil
2. Abrir desde el movil
3. Si sale error "Instalacion bloqueada":
   - Ajustes > Seguridad > Origenes desconocidos > Permitir

---

## 4. CREDENCIALES DE PRUEBA

### Dashboard Web:
```
Email: admin@enlasnubes.com
Password: admin123
```

### App Android:
```
Email: camarero@enlasnubes.com
Password: camarero123

Email: encargada@enlasnubes.com
Password: encargada123

Email: admin@enlasnubes.com
Password: admin123
```

---

## 5. URLS DEL SISTEMA

| Servicio | URL |
|----------|-----|
| Backend API | https://go84sgscs4ckcs08wog84o0o.app.generaia.site |
| Health Check | https://go84sgscs4ckcs08wog84o0o.app.generaia.site/health |
| API Docs | https://go84sgscs4ckcs08wog84o0o.app.generaia.site/docs |
| Dashboard | (pendiente deploy en Coolify) |

---

## 6. RESUMEN DE LO COMPLETADO

- [x] VAPI Assistant configurado con 4 tools
- [x] Backend desplegado y funcional
- [x] Airtable conectado
- [x] Redis cache configurado
- [x] Dashboard redisenado con UI profesional
- [x] Dashboard build de produccion listo
- [x] Dockerfile para Coolify listo
- [x] Firebase configurado (google-services.json)
- [x] API URL configurada en Android
- [x] Gradle Wrapper configurado
- [x] Manuales de uso creados
- [x] Documentacion Firebase creada

### Pendiente de accion manual:
- [ ] Desplegar Dashboard en Coolify
- [ ] Compilar APK con Android Studio o Gradle

---

**Fecha:** 2026-02-19
**Version:** 1.0.0
