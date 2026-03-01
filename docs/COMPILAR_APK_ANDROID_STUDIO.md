# GUÍA DEFINITIVA: Compilar APK con Android Studio

## TIEMPO ESTIMADO: 15-30 minutos

---

## PASO 1: ABRIR PROYECTO (2 min)

1. Abre **Android Studio**
2. **File → Open**
3. Selecciona esta carpeta:
   ```
   C:\Users\yago\Desktop\EN LAS NUBES-PROYECTOS\OPENCODE-COPIA-ASISTENTE-VOZ-EN LAS NUBES\android-app
   ```
4. Clic en **OK**

---

## PASO 2: SINCRONIZAR (3-5 min)

Android Studio descargará dependencias. Espera.

**Si sale un popup de "Gradle Sync Needed"** → Clic en **"Sync Now"**

**Si pide actualizar Gradle** → Acepta

---

## PASO 3: VER ERRORES (1 min)

1. Mira la pestaña **Build** en la parte inferior
2. Si hay errores, aparecerán en ROJO
3. **COPIA TODOS LOS ERRORES** y pégalos en el chat

**Ejemplo de cómo se ven los errores:**
```
e: file:///.../TablesScreen.kt:271:13 Unresolved reference: RowScope
```

---

## PASO 4: ARREGLAR ERRORES (yo lo haré)

Cuando me pegues los errores, los arreglo AL INSTANTE.
Probablemente sean 3-5 errores de imports o APIs experimentales.

---

## PASO 5: COMPILAR APK (2 min)

Una vez sin errores:

1. **Build → Build Bundle(s) / APK(s) → Build APK(s)**
2. Espera a que termine
3. Aparecerá un popup **"APK(s) generated successfully"**
4. Clic en **"locate"** para abrir la carpeta

---

## PASO 6: INSTALAR APK

El APK estará en:
```
android-app\app\build\outputs\apk\release\app-release.apk
```

**Para instalar:**
1. Copia el APK a tu móvil
2. Ábrelo desde el móvil
3. Si dice "Instalación bloqueada":
   - Ajustes → Seguridad → Orígenes desconocidos → Permitir

---

## CREDENCIALES DE PRUEBA

```
Email: camarero@enlasnubes.com
Password: camarero123
```

```
Email: encargada@enlasnubes.com
Password: encargada123
```

---

## SI ANDROID STUDIO NO LO TIENES

Descárgalo de: https://developer.android.com/studio

Instalación: 10-15 minutos

---

## RESUMEN

1. **Abre** el proyecto en Android Studio
2. **Espera** sincronización
3. **Copia** los errores que salgan
4. **Pégalos aquí** → Los arreglo
5. **Compila** → Tienes el APK

---

**¿Empezamos? Abre Android Studio y dime qué pasa.**
