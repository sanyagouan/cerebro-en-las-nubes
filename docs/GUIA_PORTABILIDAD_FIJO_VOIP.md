# Guía de Portabilidad VoIP para Teléfono Fijo

> **Restobar "En Las Nubes" - Logroño, España**  
> Número a portar: **941 57 84 51**  
> Fecha: 2026-03-21  
> Estado: ✅ Listo para imprimir

---

## 📋 Resumen Ejecutivo

### ¿Por qué portar el número fijo a VoIP?

Actualmente, el restobar utiliza un número de Finlandia (+358 454 910 405) con VAPI para el agente de voz "Nube". Esto genera varios problemas:

| Problema | Impacto |
|----------|---------|
| **Costes internacionales** | Cada llamada entrante tiene sobrecoste por routing internacional |
| **Identificador de llamadas** | Los clientes ven un número finlandés al recibir callbacks |
| **Confusión del cliente** | Número extranjero puede generar desconfianza |
| **Limitaciones WhatsApp** | No se puede usar para WhatsApp Business API |

### Beneficios de la Portabilidad VoIP

| Beneficio | Descripción |
|-----------|-------------|
| 💰 **Ahorro de costes** | Eliminación de costes de desvío internacional (~6-8€/mes) |
| 📞 **Número local** | Los clientes siguen llamando al 941 57 84 51 |
| 🔗 **Integración directa** | Conexión SIP nativa con VAPI |
| 📱 **WhatsApp Business** | Posibilidad de usar el mismo número para WhatsApp |
| ✅ **Experiencia mejorada** | Identificador de llamadas correcto |

### Inversión Estimada

| Concepto | Coste |
|----------|-------|
| Portabilidad | **Gratis** (la mayoría de proveedores) |
| Cuota mensual número VoIP | **3-6€/mes** |
| Llamadas entrantes | **0€** (incluidas) |
| Llamadas salientes | **~0.01-0.03€/min** |
| **Total mensual estimado** | **5-10€/mes** |

---

## 🏢 Proveedores VoIP Recomendados en España

### Comparativa de Proveedores

| Proveedor | Cuota/Mes | Min Entrante | SIP Trunking | WhatsApp API | Soporte ES | Recomendación |
|-----------|-----------|--------------|--------------|--------------|------------|---------------|
| **Zadarma** | ~3€ | Gratis | ✅ | ❌ | ✅ Chat/Email | ⭐⭐⭐⭐ Económico |
| **Netelip** | ~4€ | Gratis | ✅ | ❌ | ✅ Teléfono/Email | ⭐⭐⭐⭐ Español |
| **Telsome** | ~5€ | Gratis | ✅ | ❌ | ✅ Teléfono | ⭐⭐⭐⭐ Simple |
| **Vonage** | ~5€ | Gratis | ✅ | ✅ | ✅ Teléfono | ⭐⭐⭐⭐⭐ Completo |
| **Telnyx** | ~3€ | Gratis | ✅ | ⚠️ Limitado | ❌ Inglés | ⭐⭐⭐ Técnico |
| **MessageBird** | ~4€ | Gratis | ✅ | ✅ | ⚠️ Inglés | ⭐⭐⭐⭐ API |

### Recomendación Principal: Vonage

**¿Por qué Vonage?**

1. ✅ **Presencia establecida en España** - Oficina en Madrid
2. ✅ **Soporte en español** - Teléfono y email
3. ✅ **WhatsApp Business API integrado** - Un proveedor para todo
4. ✅ **Documentación SIP completa** - Fácil integración con VAPI
5. ✅ **Reputación consolidada** - Empresa cotizada en NASDAQ

**Web:** https://www.vonage.es

### Alternativa Económica: Zadarma

**¿Por qué Zadarma?**

1. ✅ **Más económico** - Desde 3€/mes
2. ✅ **Soporte en español** - Chat y email
3. ✅ **Interfaz sencilla** - Fácil de configurar
4. ✅ **Números españoles disponibles** - Fijos y móviles
5. ⚠️ **Sin WhatsApp API** - Solo telefonía

**Web:** https://zadarma.com/es/

### Alternativa Local: Netelip

**¿Por qué Netelip?**

1. ✅ **Empresa española** - Base en España
2. ✅ **Soporte telefónico local** - 900 xxx xxx
3. ✅ **Precios competitivos** - ~4€/mes
4. ✅ **Centralita virtual incluida** - Funciones extra
5. ⚠️ **Sin WhatsApp API** - Solo telefonía

**Web:** https://www.netelip.com

---

## 📋 Requisitos Previos

### Documentación Necesaria

Antes de iniciar la portabilidad, prepara estos documentos:

| Documento | Dónde conseguirlo | Notas |
|-----------|-------------------|-------|
| **Última factura del teléfono fijo** | Operador actual (Movistar/Vodafone/Orange) | Debe tener menos de 30 días |
| **Contrato de servicios** | Operador actual | Muestra el titular de la línea |
| **DNI del titular** | - | Debe coincidir con el contrato |
| **Formulario de portabilidad** | Lo proporciona el nuevo proveedor | Rellenar online |

### Información que Debes Conocer

```
┌─────────────────────────────────────────────────────────────┐
│ DATOS QUE NECESITARÁS AL RELLENAR EL FORMULARIO             │
└─────────────────────────────────────────────────────────────┘

✓ Número a portar: 941 57 84 51
✓ Operador actual: [Movistar / Vodafone / Orange / Otro]
✓ Tipo de línea: [Particular / Empresa]
✓ Nombre del titular: [Tal como aparece en la factura]
✓ NIF/CIF del titular: [DNI de la persona o empresa]
✓ Dirección de instalación: [Dirección del restobar]
✓ Código de operador (CSP): [Lo da el operador actual]
```

### Verificaciones Antes de Empezar

- [ ] La línea está **activa** y al día de pago
- [ ] No hay **permanencia activa** con el operador actual
- [ ] El titular de la línea es quien solicita la portabilidad
- [ ] Tienes una **factura reciente** (menos de 30 días)
- [ ] El número es de la **misma provincia** donde se dará el servicio

---

## 📝 Paso a Paso de la Portabilidad

### Timeline Estimado

```
┌─────────────────────────────────────────────────────────────┐
│ CRONOGRAMA DE PORTABILIDAD                                  │
└─────────────────────────────────────────────────────────────┘

DÍA 0        DÍA 1-2         DÍA 3-5          DÍA 5-7
  │            │               │                │
  ▼            ▼               ▼                ▼
┌─────┐    ┌─────────┐    ┌─────────┐    ┌─────────────┐
│Solic│───▶│Validación│───▶│Procesado│───▶│Portabilidad │
│itar │    │documentos│    │operador │    │completada   │
└─────┘    └─────────┘    └─────────┘    └─────────────┘
  │            │               │                │
  5 min       24-48h          24-72h           ✅ Listo
```

### Paso 1: Elegir Proveedor y Crear Cuenta

**Tiempo estimado:** 10-15 minutos

1. **Visitar la web del proveedor elegido** (ej. vonage.es)
2. **Crear una cuenta nueva** con email y contraseña
3. **Verificar el email** (click en enlace de confirmación)
4. **Completar el perfil de empresa:**
   - Nombre: "En Las Nubes Restobar"
   - NIF/CIF: [El del negocio]
   - Dirección: [Dirección del restobar]
   - Teléfono contacto: [Móvil del responsable]

### Paso 2: Solicitar la Portabilidad

**Tiempo estimado:** 15-20 minutos

1. **Acceder a la sección "Números" o "Portabilidad"**
2. **Seleccionar "Portar número existente"**
3. **Rellenar el formulario:**

```
┌─────────────────────────────────────────────────────────────┐
│ FORMULARIO DE PORTABILIDAD (Ejemplo)                        │
└─────────────────────────────────────────────────────────────┘

Número a portar:     [941 57 84 51]
Operador actual:     [Movistar / Vodafone / Orange / Otro]
Tipo de línea:       [X] Fijo  [ ] Móvil
Titular:             [Nombre completo como en factura]
NIF/CIF:             [12345678A]
Dirección:           [Calle Mayor 123, Logroño]
Código postal:       [26001]
Provincia:           [La Rioja]

Documentos adjuntos:
- [ ] Factura reciente (PDF)
- [ ] DNI del titular (anverso y reverso)
```

4. **Subir los documentos escaneados:**
   - Factura del teléfono fijo (PDF o foto clara)
   - DNI del titular (ambos lados en buena calidad)

5. **Firmar electrónicamente** el formulario
6. **Confirmar la solicitud**

### Paso 3: Esperar Validación

**Tiempo estimado:** 24-48 horas

Durante este periodo:

| Qué pasa | Qué debes hacer |
|----------|-----------------|
| El proveedor revisa los documentos | Estar atento al email |
| Verifican que el titular coincide | Responder si piden aclaraciones |
| Contactan con el operador actual | No es necesario hacer nada |
| Recibes confirmación de fecha de portabilidad | Anotar la fecha |

**Email típico de confirmación:**

```
Asunto: Portabilidad confirmada - 941 57 84 51

Estimado cliente,

Su solicitud de portabilidad ha sido validada.

Fecha programada: 26/03/2026
Hora estimada: Entre las 00:00 y las 06:00
Número: 941 57 84 51

Durante el proceso puede haber un corte breve del servicio
(máximo 2 horas).

Atentamente,
Equipo de Portabilidad
```

### Paso 4: Durante la Portabilidad

**Tiempo estimado:** 1-4 horas (normalmente de madrugada)

| Momento | Qué pasa | Impacto |
|---------|----------|---------|
| **Inicio** | El operador antiguo libera el número | Llamadas pueden no entrar |
| **Proceso** | El número se transfiere al nuevo proveedor | Corte de servicio |
| **Final** | El número está activo en el nuevo proveedor | Servicio restaurado |

**⚠️ Importante:** El corte suele ser de madrugada (00:00-06:00) para minimizar impacto.

### Paso 5: Verificar que Funciona

**Tiempo estimado:** 10 minutos

1. **Llamar al 941 57 84 51** desde otro teléfono
2. **Verificar que la llamada entra** en el panel del proveedor
3. **Probar la identificación de llamadas** (debe mostrar el número correcto)
4. **Hacer una llamada saliente** de prueba

---

## 🔗 Integración con VAPI (SIP Trunking)

### ¿Qué es SIP Trunking?

**Explicación sencilla:**

SIP Trunking es como un "tubo virtual" que conecta tu proveedor de teléfono (Vonage, Zadarma, etc.) con VAPI. Cuando alguien llama al 941 57 84 51:

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO DE LLAMADA CON SIP TRUNKING                           │
└─────────────────────────────────────────────────────────────┘

Cliente llama al 941 57 84 51
         │
         ▼
┌─────────────────┐
│  Proveedor VoIP │  ← Vonage, Zadarma, Netelip...
│  (tu número)    │
└────────┬────────┘
         │ SIP Trunking (tubo virtual)
         ▼
┌─────────────────┐
│      VAPI       │  ← Tu agente de voz
│   (conexión)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agente "Nube"  │  ← Contestación automática
│   responde      │
└─────────────────┘
```

### Datos que Necesitarás del Proveedor VoIP

Una vez completada la portabilidad, el proveedor te dará:

| Dato | Ejemplo | Dónde encontrarlo |
|------|---------|-------------------|
| **SIP Gateway / Proxy** | `sip.vonage.es` | Panel de control → Configuración SIP |
| **Puerto SIP** | `5060` (UDP) o `5061` (TLS) | Documentación del proveedor |
| **IP del Gateway** | `81.201.82.50` | Panel de control → SIP Trunking |
| **Usuario SIP** | `941578451` | Credenciales SIP |
| **Contraseña SIP** | `abc123xyz` | Credenciales SIP |

### Configuración en VAPI (Nosotros lo Hacemos)

**No te preocupes por esta parte técnica.** Una vez tengas los datos SIP del proveedor, nosotros configuraremos VAPI.

El proceso técnico sería:

**1. Crear credenciales SIP en VAPI:**
```json
POST https://api.vapi.ai/credential
{
  "provider": "byo-sip-trunk",
  "name": "Vonage España - En Las Nubes",
  "gateways": [
    {
      "ip": "IP_DEL_GATEWAY",
      "port": 5060,
      "inboundEnabled": true
    }
  ]
}
```

**2. Registrar el número en VAPI:**
```json
POST https://api.vapi.ai/phone-number
{
  "provider": "byo-phone-number",
  "name": "Fijo Restobar En Las Nubes",
  "number": "34941578451",
  "credentialId": "ID_CREDENCIAL_CREADA"
}
```

### Checklist de Integración

Una vez tengas el proveedor VoIP configurado:

- [ ] Obtener IP del gateway SIP del proveedor
- [ ] Obtener puerto SIP (normalmente 5060)
- [ ] Compartir credenciales con el equipo técnico
- [ ] Esperar configuración en VAPI
- [ ] Probar llamada entrante
- [ ] Verificar que el agente "Nube" contesta
- [ ] Probar identificación de llamadas

---

## 🛡️ Plan de Transición Seguro

### Estrategia Recomendada: Mantener Servicio Continuo

```
┌─────────────────────────────────────────────────────────────┐
│ PLAN DE TRANSICIÓN SIN CORTE DE SERVICIO                    │
└─────────────────────────────────────────────────────────────┘

FASE 1: AHORA (Inmediato)
├─ Configurar desvío de llamadas al número Finlandia
├─ Código: *21*+358454910405# (verificar con operador)
├─ El agente Nube ya puede recibir llamadas
└─ Coste: ~6-8€/mes en desvíos

FASE 2: PREPARACIÓN (Esta semana)
├─ Elegir proveedor VoIP (recomendado: Vonage)
├─ Recopilar documentación necesaria
├─ Crear cuenta en el proveedor
└─ Sin coste adicional

FASE 3: PORTABILIDAD (1-2 semanas)
├─ Solicitar portabilidad al proveedor VoIP
├─ Mantener desvío activo durante el proceso
├─ El desvío actúa como "red de seguridad"
└─ Posible corte breve (1-4 horas de madrugada)

FASE 4: INTEGRACIÓN (1-2 días después)
├─ Recibir credenciales SIP del proveedor
├─ Configurar SIP trunking en VAPI (nosotros)
├─ Probar llamadas entrantes y salientes
└─ Eliminar desvío antiguo
```

### Por Qué Mantener el Desvío Durante la Portabilidad

| Razón | Explicación |
|-------|-------------|
| **Red de seguridad** | Si algo falla, las llamadas siguen llegando |
| **Sin pérdida de clientes** | El restaurante no pierde ninguna reserva |
| **Tranquilidad** | El negocio no nota la transición |
| **Rollback fácil** | Si hay problemas, volver atrás es simple |

### Configuración del Desvío (Solución Temporal)

**Para Movistar (más común):**
```
Activar:   *21*+358454910405#
Desactivar: #21#
Verificar:  *#21#
```

**Para Vodafone:**
```
Activar:   *21*+358454910405#
Desactivar: #21#
```

**Para Orange:**
```
Activar:   *21*+358454910405#
Desactivar: #21#
```

> **Nota:** Verifica con tu operador actual los códigos exactos. Algunos operadores requieren llamar al servicio de atención al cliente para activar desvíos internacionales.

---

## ❓ Preguntas Frecuentes

### ¿Pierdo el número si algo sale mal?

**No.** El número 941 57 84 51 es tuyo y tienes derecho a portarlo. Si el proceso falla, el número se queda con el operador original. Siempre puedes intentarlo de nuevo.

### ¿Cuánto tiempo estoy sin teléfono?

Normalmente **1-4 horas**, y siempre de madrugada (00:00-06:00). El proveedor te avisará de la fecha y hora exactas.

### ¿Puedo seguir usando el teléfono físico?

**Depende.** Con VoIP, el número "vive" en la nube. Tienes dos opciones:

1. **Usar solo VAPI:** El número va directo al agente de voz
2. **Usar teléfono IP:** Comprar un teléfono VoIP físico para el local

### ¿Qué pasa con las llamadas salientes?

Con SIP trunking configurado, VAPI puede hacer llamadas salientes mostrando el 941 57 84 51 como identificador. Perfecto para callbacks de confirmación.

### ¿Puedo usar el número para WhatsApp Business?

**Sí, con algunos proveedores** (Vonage, MessageBird). El proceso de verificación de WhatsApp es independiente y requiere documentación adicional.

### ¿Necesito cambiar algo en el local?

**No necesariamente.** El número funciona en la nube. Si quieres un teléfono físico en el local, necesitarías un teléfono IP o una app de VoIP en el móvil.

---

## 📞 Contactos Útiles

### Proveedores VoIP Recomendados

| Proveedor | Web | Teléfono España |
|-----------|-----|-----------------|
| **Vonage** | vonage.es | 900 123 456 |
| **Zadarma** | zadarma.com/es | - (Chat/Email) |
| **Netelip** | netelip.com | 900 838 838 |
| **Telsome** | telsome.es | 900 838 838 |

### Operadores Actuales (para consultar)

| Operador | Teléfono | Web |
|----------|----------|-----|
| **Movistar** | 1004 | movistar.es |
| **Vodafone** | 22123 | vodafone.es |
| **Orange** | 1470 | orange.es |
| **MásMóvil** | 2373 | masmovil.es |

---

## ✅ Checklist Final

### Antes de Empezar

- [ ] Tengo la última factura del teléfono fijo
- [ ] Sé quién es el operador actual
- [ ] El titular de la línea está disponible para firmar
- [ ] He elegido el proveedor VoIP (recomendado: Vonage)
- [ ] He configurado el desvío temporal al número Finlandia

### Durante el Proceso

- [ ] He creado cuenta en el proveedor VoIP
- [ ] He enviado la solicitud de portabilidad
- [ ] He subido los documentos requeridos
- [ ] He recibido confirmación de fecha de portabilidad
- [ ] El desvío sigue activo como respaldo

### Después de la Portabilidad

- [ ] He verificado que las llamadas entran
- [ ] He recibido las credenciales SIP del proveedor
- [ ] He compartido las credenciales con el equipo técnico
- [ ] Se ha configurado la integración con VAPI
- [ ] He probado una llamada completa con el agente Nube
- [ ] He desactivado el desvío temporal

---

## 📚 Documentación Relacionada

- [`INFORME_TELEFONO_FIJO_VAPI.md`](INFORME_TELEFONO_FIJO_VAPI.md) - Análisis completo de opciones
- [`INVESTIGACION_NUMEROS_ESPANOLES_TWILIO.md`](INVESTIGACION_NUMEROS_ESPANOLES_TWILIO.md) - Por qué Twilio no sirve
- [VAPI BYOC Documentation](https://docs.vapi.ai/phone-numbers/bring-your-own-carrier) - Traer tu propio carrier

---

**Documento preparado por:** Equipo de Documentación  
**Para:** Restobar "En Las Nubes" - Logroño  
**Estado:** ✅ Listo para imprimir  
**Próxima revisión:** Tras completar la portabilidad
