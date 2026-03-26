# Informe: Opciones para Integrar Teléfono Fijo con VAPI

> **Restobar "En Las Nubes" - Logroño, España**  
> Fecha: 2026-03-21  
> Autor: Arquitecto del Sistema

---

## 📋 Resumen Ejecutivo

**Problema:** El restobar "En Las Nubes" tiene un teléfono fijo (941 57 84 51) que los clientes ya conocen. Se necesita que las llamadas a este número sean atendidas por el agente de voz "Nube" (VAPI).

**Soluciones analizadas:**
1. Desvío de llamadas (Call Forwarding)
2. Portabilidad SIP/VoIP
3. Centralita Virtual (PBX)

**Recomendación:** Desvío de llamadas como solución inmediata + Portabilidad SIP a medio plazo.

---

## 🎯 Contexto del Problema

### Situación Actual

| Elemento | Valor |
|----------|-------|
| **Teléfono fijo del restobar** | 941 57 84 51 |
| **Número VAPI actual** | +358 454 910 405 (Finlandia) |
| **Proveedor VAPI** | Twilio (con limitaciones en España) |
| **Problema con Twilio** | No vende números españoles por restricciones regulatorias EU |

### Restricciones Identificadas

Según [`docs/INVESTIGACION_NUMEROS_ESPANOLES_TWILIO.md`](INVESTIGACION_NUMEROS_ESPANOLES_TWILIO.md):

> **Twilio NO puede vender números españoles** debido a:
> - Directiva EU E-Privacy (2009/136/EC)
> - Regulaciones eIDAS (EU 910/2014)
> - Requisitos de identificación local en España

---

## 🔍 Opciones Analizadas

### Opción 1: Desvío de Llamadas (Call Forwarding)

#### Descripción
Configurar el teléfono fijo para desviar todas las llamadas al número de VAPI (+358 454 910 405).

#### Cómo Funciona en España

| Operador | Código Activación | Código Desactivación | Coste |
|----------|-------------------|---------------------|-------|
| **Movistar** | `*21*+358454910405#` | `#21#` | ~0.05€/min + cuota de establecimiento |
| **Vodafone** | `*21*+358454910405#` | `#21#` | ~0.04€/min |
| **Orange** | `*21*+358454910405#` | `#21#` | ~0.03-0.05€/min |
| **MásMóvil** | `*21*+358454910405#` | `#21#` | Variable (consultar) |

> **Nota:** Los códigos pueden variar según la región y tipo de línea. Verificar con el operador actual del restobar.

#### Proceso de Implementación

```
┌─────────────────────────────────────────────────────────────┐
│ FLUJO: DESVÍO DE LLAMADAS                                   │
└─────────────────────────────────────────────────────────────┘

1. Cliente llama al 941 57 84 51
   └─> Línea fija recibe llamada

2. Desvío automático (configurado en centralita)
   └─> Llamada redirigida a +358 454 910 405

3. VAPI recibe llamada
   └─> Agente Nube contesta

4. Conversación normal
   └─> Reserva gestionada por IA
```

#### Pros y Contras

| Ventajas | Desventajas |
|----------|-------------|
| ✅ Implementación inmediata (5 minutos) | ❌ Coste por minuto de llamada desviada |
| ✅ No requiere cambios en VAPI | ❌ Número VAPI aparece en identificador de llamadas (puede confundir) |
| ✅ Mantiene número original visible | ❌ Dependencia de la línea fija física |
| ✅ Reversible en cualquier momento | ❌ Si la línea fía falla, no hay respaldo |
| ✅ Sin contratos nuevos | ❌ Calidad de audio depende de dos redes |

#### Estimación de Costes

**Suponiendo 50 llamadas/mes x 3 min promedio:**

| Concepto | Coste Mensual |
|----------|---------------|
| Cuota establecimiento (una vez) | ~5-10€ |
| Coste llamadas desviadas (150 min) | ~6-8€ |
| **Total primer mes** | ~11-18€ |
| **Total meses siguientes** | ~6-8€/mes |

---

### Opción 2: Portabilidad SIP/VoIP

#### Descripción
Portar el número fijo 941 57 84 51 a un proveedor VoIP que soporte SIP trunking con VAPI.

#### Proveedores VoIP para España

Según investigación previa, los proveedores que **SÍ** ofrecen números españoles:

| Proveedor | Números Fijos | SIP Trunking | WhatsApp API | Coste/Mes |
|-----------|---------------|--------------|--------------|-----------|
| **Vonage** | ✅ Sí | ✅ Sí | ✅ Sí | ~5€ |
| **Telnyx** | ✅ Sí | ✅ Sí | ⚠️ Limitado | ~3€ |
| **MessageBird** | ✅ Sí | ✅ Sí | ✅ Sí | ~4€ |
| **Sinch** | ✅ Sí | ✅ Sí | ✅ Sí | ~6€ |

> **Twilio NO ofrece números españoles** - descartado para esta opción.

#### Arquitectura con Portabilidad SIP

```
┌─────────────────────────────────────────────────────────────┐
│ ARQUITECTURA: PORTABILIDAD SIP/VoIP                         │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │   Cliente llama  │
                    │   941 57 84 51   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Proveedor VoIP  │
                    │  (Vonage/Telnyx) │
                    └────────┬─────────┘
                             │ SIP Trunking
                             ▼
                    ┌──────────────────┐
                    │      VAPI        │
                    │  (BYO-SIP-Trunk) │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Agente Nube    │
                    │   contesta       │
                    └──────────────────┘
```

#### Configuración VAPI para SIP Externo

Según documentación de VAPI, se requiere:

**1. Crear Credenciales SIP Trunk:**
```json
POST /credential
{
  "provider": "byo-sip-trunk",
  "name": "Vonage España - En Las Nubes",
  "gateways": [
    {
      "ip": "GATEWAY_IP_VONAGE",
      "port": 5060,
      "inboundEnabled": true
    }
  ],
  "outboundLeadingPlusEnabled": true
}
```

**2. Registrar Número con SIP Trunk:**
```json
POST /phone-number
{
  "provider": "byo-phone-number",
  "name": "Fijo Restobar En Las Nubes",
  "number": "34941578451",
  "numberE164CheckEnabled": false,
  "credentialId": "CREDENTIAL_ID_CREADO"
}
```

#### Proceso de Portabilidad en España

1. **Solicitar portabilidad** al proveedor VoIP elegido
   - Documentación requerida:
     - Contrato de servicios con el operador actual
     - Última factura del teléfono fijo
     - DNI del titular de la línea
   - Plazo: 1-3 días hábiles

2. **Configurar SIP trunking** con VAPI
   - Obtener credenciales SIP del proveedor
   - Crear credencial en VAPI
   - Registrar número

3. **Probar llamadas** entrantes y salientes

#### Pros y Contras

| Ventajas | Desventajas |
|----------|-------------|
| ✅ Número original mantenido | ❌ Proceso de portabilidad (1-3 días) |
| ✅ Sin coste por minuto de desvío | ❌ Requiere configuración técnica SIP |
| ✅ Identificador de llamadas correcto | ❌ Posible downtime durante portabilidad |
| ✅ Más flexible y escalable | ❌ Dependencia de un nuevo proveedor |
| ✅ Posible integrar WhatsApp API | ❌ Curva de aprendizaje inicial |
| ✅ Sin línea física requerida | ❌ Contrato nuevo con proveedor VoIP |

#### Estimación de Costes

| Concepto | Coste |
|----------|-------|
| Portabilidad | Gratis (normalmente) |
| Número VoIP/mes | 3-6€ |
| Llamadas entrantes | 0€ |
| Llamadas salientes | ~0.01-0.03€/min |
| **Total mensual estimado** | **5-10€/mes** |

---

### Opción 3: Centralita Virtual (PBX)

#### Descripción
Usar una centralita virtual que reciba las llamadas del fijo y las enrute a VAPI vía SIP.

#### Proveedores PBX en España

| Proveedor | Tipo | Coste/Mes | SIP Trunking | Integración VAPI |
|-----------|------|-----------|--------------|------------------|
| **RingCentral** | Cloud PBX | 15-30€ | ✅ | Via API/Webhook |
| **3CX** | Software PBX | 10-25€ | ✅ | Via SIP trunk |
| **FonYou** | Virtual PBX España | 8-20€ | ✅ | Via API |
| **Centralita.com** | Cloud PBX España | 5-15€ | ✅ | Via SIP |
| **MiCentralita** | Cloud PBX | 10-20€ | ✅ | Via SIP |

#### Arquitectura con Centralita Virtual

```
┌─────────────────────────────────────────────────────────────┐
│ ARQUITECTURA: CENTRALITA VIRTUAL                            │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │   Cliente llama  │
                    │   941 57 84 51   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Centralita    │
                    │    Virtual PBX   │
                    │  (RingCentral)   │
                    └────────┬─────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
             ┌──────────────┐  ┌──────────────┐
             │  VAPI Agent  │  │   Teléfono   │
             │  (SIP trunk) │  │   Físico     │
             └──────────────┘  │  (Backup)    │
                               └──────────────┘
```

#### Casos de Uso de Centralita

1. **Horario comercial:** Llamadas → VAPI
2. **Fuera de horario:** Llamadas → Buzón de voz
3. **Overflow:** Si VAPI no disponible → Teléfono físico
4. **Handoff:** Si cliente pide humano → Transferir a físico

#### Pros y Contras

| Ventajas | Desventajas |
|----------|-------------|
| ✅ Máxima flexibilidad | ❌ Coste más alto (doble proveedor) |
| ✅ Posible backup a teléfono físico | ❌ Complejidad de configuración |
| ✅ Horarios y reglas avanzadas | ❌ Latencia adicional posible |
| ✅ Múltiples destinos | ❌ Otro sistema a mantener |
| ✅ Reporting unificado | ❌ Curva de aprendizaje alta |

#### Estimación de Costes

| Concepto | Coste/Mes |
|----------|-----------|
| Centralita virtual | 10-30€ |
| Número VoIP (si aplica) | 3-6€ |
| Llamadas | Variable |
| **Total mensual** | **15-40€/mes** |

---

## 📊 Comparativa Final

| Criterio | Desvío | Portabilidad SIP | Centralita PBX |
|----------|--------|------------------|----------------|
| **Coste inicial** | ⭐⭐⭐⭐⭐ 0€ | ⭐⭐⭐⭐ ~0€ | ⭐⭐ ~50€ |
| **Coste mensual** | ⭐⭐⭐ 6-8€ | ⭐⭐⭐⭐⭐ 5-10€ | ⭐⭐ 15-40€ |
| **Tiempo implementación** | ⭐⭐⭐⭐⭐ 5 min | ⭐⭐⭐ 1-3 días | ⭐⭐ 1-2 semanas |
| **Complejidad técnica** | ⭐⭐⭐⭐⭐ Baja | ⭐⭐⭐ Media | ⭐⭐ Alta |
| **Fiabilidad** | ⭐⭐⭐ Media | ⭐⭐⭐⭐ Alta | ⭐⭐⭐⭐ Alta |
| **Flexibilidad** | ⭐⭐ Baja | ⭐⭐⭐⭐ Alta | ⭐⭐⭐⭐⭐ Muy alta |
| **Experiencia usuario** | ⭐⭐⭐ Buena | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐⭐ Buena |
| **Escalabilidad** | ⭐⭐ Baja | ⭐⭐⭐⭐⭐ Alta | ⭐⭐⭐⭐ Alta |

---

## 🎯 Recomendación Final

### Estrategia Recomendada: Enfoque Híbrido

```
┌─────────────────────────────────────────────────────────────┐
│ PLAN DE IMPLEMENTACIÓN RECOMENDADO                          │
└─────────────────────────────────────────────────────────────┘

FASE 1 (HOY - Inmediato)
├─ Configurar desvío de llamadas en teléfono fijo
├─ Código: *21*+358454910405# (verificar con operador)
├─ Probar que VAPI recibe llamadas correctamente
└─ Coste: 0€ setup + ~6-8€/mes

FASE 2 (1-2 Semanas - Evaluación)
├─ Monitorear volumen de llamadas y costes
├─ Evaluar experiencia del cliente
├─ Investigar proveedor VoIP preferido (Vonage o Telnyx)
└─ Preparar documentación para portabilidad

FASE 3 (1-3 Meses - Migración)
├─ Solicitar portabilidad a proveedor VoIP elegido
├─ Configurar SIP trunking con VAPI
├─ Probar en paralelo antes de cutover
└─ Migrar definitivamente
```

### Justificación

1. **Desvío como solución inmediata:**
   - Permite empezar HOY mismo
   - Sin contratos ni procesos burocráticos
   - Reversible si no funciona

2. **Portabilidad SIP como solución definitiva:**
   - Elimina coste por minuto de desvío
   - Mejor experiencia de usuario (caller ID correcto)
   - Más robusto y profesional
   - Permite integrar WhatsApp API con el mismo número

3. **Centralita PBX descartada para ahora:**
   - Complejidad innecesaria para las necesidades actuales
   - Coste elevado para el volumen esperado
   - Considerar solo si se requiere handoff a humano frecuente

---

## 📝 Pasos de Implementación Inmediata

### Paso 1: Verificar Operador Actual

```bash
# Preguntar al negocio:
- ¿Quién es el operador del teléfono fijo? (Movistar, Vodafone, Orange, otro)
- ¿Es línea particular o empresa?
- ¿Hay contrato de permanencia?
```

### Paso 2: Configurar Desvío

**Para Movistar (más común en España):**
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

### Paso 3: Probar Llamada

1. Llamar al 941 57 84 51 desde un móvil
2. Verificar que VAPI recibe la llamada
3. Verificar que el agente Nube contesta correctamente
4. Probar una reserva completa

### Paso 4: Monitorear

- Revisar primera semana de llamadas
- Evaluar costes reales vs estimados
- Recoger feedback de clientes

---

## ⚠️ Consideraciones Importantes

### Sobre el Número VAPI Actual (+358)

El número finlandés actual tiene limitaciones:
- **Identificador de llamadas:** Aparece como Finlandia (puede confundir)
- **WhatsApp:** No puede usarse para WhatsApp Business (requiere verificación)
- **Costes:** Clientes pueden tener recelos al ver número extranjero

### Sobre la Portabilidad

**Requisitos en España:**
- La línea debe estar activa y al día de pago
- El titular debe coincidir con quien solicita portabilidad
- Proceso tarda 1-3 días hábiles (máximo 2 días según normativa)

**Durante la portabilidad:**
- Puede haber un periodo breve (minutos) sin servicio
- Recomendable hacer en horario de cierre del restaurante

### Sobre Proveedores VoIP Recomendados

**Vonage:**
- ✅ Presencia establecida en España
- ✅ Soporte en español
- ✅ WhatsApp API integrado
- ⚠️ Ligeramente más caro

**Telnyx:**
- ✅ Más económico
- ✅ Buena documentación técnica
- ⚠️ Soporte principalmente en inglés
- ⚠️ WhatsApp API limitado

---

## 📚 Referencias

- [VAPI BYOC Documentation](https://docs.vapi.ai/phone-numbers/bring-your-own-carrier)
- [Twilio Spanish Numbers Investigation](./INVESTIGACION_NUMEROS_ESPANOLES_TWILIO.md)
- [Vonage España](https://www.vonage.es)
- [Telnyx Phone Numbers](https://telnyx.com/products/phone-numbers)
- [Portabilidad Móvil en España - CNMC](https://www.cnmc.es/)

---

**Documento preparado por:** Arquitecto del Sistema  
**Para:** Restobar "En Las Nubes" - Logroño  
**Estado:** ✅ Listo para revisión
