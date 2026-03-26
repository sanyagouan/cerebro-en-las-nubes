# Sincronización de Plantillas WhatsApp: Meta → Twilio Content API

> **Documento técnico detallado sobre cómo sincronizar plantillas de WhatsApp Business creadas en Meta Business Manager (Meta) hacia Twilio Content API para su uso en el sistema de mensajería Twilio.

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura de Plantillas](#arquitectura-de-plantillas)
3. [Endpoint LegacyContent](#endpoint-legacycontent)
4. [Flujo de Trabajo Recomendado](#flujo-de-trabajo-recomendado)
5. [Script de Ejemplo en Python](#script-de-ejemplo-en-python)
6. [Mejores Prácticas](#mejores-prácticas)
7. [Preguntas Frecuentes](#preguntas-frecuentes)
8. [Referencias](#referencias)

---

## 1. Introducción

Este documento explica el proceso para sincronizar plantillas de WhatsApp creadas en Meta Business Manager hacia Twilio Content API, permitiendo utilizarlas desde aplicaciones Python que enviar mensajes de WhatsApp.

### Contexto

Twilio está migrando su sistema de plantillas de WhatsApp a una nueva arquitectura llamada **Content API**. Este cambio afecta a las plantillas creadas en Meta (plataforma nativa de Meta) y las plantillas creadas directamente en Twilio (plataforma heredada).

### Objetivos

1. **Mapear plantillas existentes** de Meta a Content API de Twilio
2. **Evitar recrear plantillas** ya aprobadas en Meta
3. **Mantener consistencia** entre ambos sistemas

---

## 2. Arquitectura de Plantillas

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE PLANTILLAS                                        │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────┐
                    │   META BM      │
                    │  (Aprobación)   │
                    └────────┬──────┬┘
                                  │
              ┌─────────────────┴─────────────────┐
              │  Opción A:        │   Opción B:        │
              │  Migración        │   Creación Nueva   │
              │  Automática        │   en Twilio       │
              └─────────────────┴─────────────────┘
                                  │
                                  ▼
                    ┌─────────────────┐
                    │ Content API     │
                    │  (HX...)         │
                    └─────────────────┘
```

### Identificadores Clave

| Sistema | Identificador | Formato | Ejemplo |
|--------|---------------|-------|---------|
| **Meta** | Template ID | Numérico | `123456789` |
| **Twilio Legacy** | Template SID | `WHxxxx` | `WH123abc456def` |
| **Twilio Content API** | Content SID | `HXxxxx` | `HX987654321abc` |

---

## 3. Endpoint LegacyContent

El endpoint clave para la sincronización es:

```
GET https://content.twilio.com/v1/LegacyContent
```

### Qué devuelve este endpoint?

Devuelve un **mapeo** entre las plantillas "legacy" de WhatsApp (creadas en Meta) y sus identificadores de Content API (`ContentSid` que empiezan por `HX...`).

### Ejemplo de respuesta

```json
{
  "meta": {
    "page": 0,
    "page_size": 50,
    "total_results": 3
  },
  "results": [
    {
    "sid": "HX123abc456def",
    "account_sid": "ACxxxxxxxx",
    "legacy_template_name": "confirmacion_reserva",
    "legacy_template_id": "123456789",
    "date_created": "2026-03-24T10:00:00Z",
    "date_updated": "2026-03-24T10:00:00Z",
    "types": ["twilio/text", "twilio/media"],
    "language": "es",
    "variables": ["nombre", "fecha", "hora"],
    "status": "approved"
  }
  ]
}
```

### Campos importantes

| Campo | Descripción |
|-------|-------------|
| `sid` | **ContentSid** de Content API (formato `HX...`) |
| `legacy_template_name` | Nombre de la plantilla en Meta |
| `legacy_template_id` | ID de la plantilla en Meta |
| `status` | Estado de la plantilla (`approved`, `pending`, `rejected`) |
| `variables` | Variables de la plantilla |

---

## 4. Flujo de Trabajo Recomendado

### Escenario A: Plantillas ya migradas automáticamente

Si Twilio ya migró las plantillas de tu WABA:

```python
# 1. Consultar LegacyContent
response = requests.get(
    "https://content.twilio.com/v1/LegacyContent",
    auth=(account_sid, auth_token)
)

# 2. Verificar si aparecen tus plantillas
for template in response.json()["results"]:
    print(f"Plantilla: {template['legacy_template_name']}")
    print(f"  ContentSid: {template['sid']}")
    print(f"  Estado: {template['status']}")
```

✅ **Acción:** Usar los `ContentSid` (`HX...`) directamente en tu código.

### Escenario B: Plantillas NO migradas

Si las plantillas no aparecen en LegacyContent:

```python
# Opción 1: Contactar soporte de Twilio
# Solicitar migración manual de tu WABA

# Opción 2: Recrear plantillas en Twilio
# (Ver sección 5)
```

⚠️ **Importante:** Twilio recomienda crear plantillas directamente en su plataforma para tener control total del ciclo de vida.

### Escenario C: Recrear plantillas con vinculación automática

Si decides recrear las plantillas en Twilio:

1. **Usar el mismo nombre exacto** que en Meta
2. **Usar la misma categoría** (AUTHENTICATION, MARKETING, UTILITY, etc.)
3. Twilio intentará vincular automáticamente con la plantilla aprobada en Meta

```python
# Crear plantilla en Twilio con mismo nombre que en Meta
content_sid = create_twilio_template(
    name="confirmacion_reserva",  # Mismo nombre que en Meta
    category="UTILITY",
    language="es",
    body="Hola {{1}}, tu reserva está confirmada para el {{2}} a las {{3}}."
)
```

---

## 5. Script de Ejemplo en Python

```python
#!/usr/bin/env python3
"""
Script para consultar el endpoint LegacyContent de Twilio
y obtener el mapeo de plantillas Meta → Content API.

Autor: Sistema de Reservas En Las Nubes
Fecha: 2026-03-24
"""

import os
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime


class TwilioLegacyContentChecker:
    """Consulta el mapeo de plantillas Meta → Twilio Content API."""
    
    BASE_URL = "https://content.twilio.com/v1"
    
    def __init__(self, account_sid: str, auth_token: str):
        """
        Inicializa el checker.
        
        Args:
            account_sid: Account SID de Twilio (AC...)
            auth_token: Auth Token de Twilio
        """
        self.account_sid = account_sid
        self.auth = HTTPBasicAuth(account_sid, auth_token)
    
    def get_legacy_content(self, page_size: int = 50) -> dict:
        """
        Consulta el endpoint LegacyContent.
        
        Args:
            page_size: Número de resultados por página
            
        Returns:
            dict con la respuesta completa del endpoint
        """
        url = f"{self.BASE_URL}/LegacyContent"
        params = {
            "PageSize": page_size
        }
        
        response = requests.get(url, auth=self.auth, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_all_legacy_templates(self) -> list:
        """
        Obtiene todas las plantillas legacy paginando si es necesario.
        
        Returns:
            list: Lista de todas las plantillas mapeadas
        """
        all_templates = []
        page = 0
        
        while True:
            result = self.get_legacy_content()
            all_templates.extend(result.get("results", []))
            
            meta = result.get("meta", {})
            if page >= meta.get("total_pages", 1) - 1:
                break
            page += 1
        
        return all_templates
    
    def print_template_mapping(self, templates: list) -> None:
        """
        Imprime el mapeo de plantillas de forma legible.
        
        Args:
            templates: Lista de plantillas del endpoint
        """
        print("\n" + "=" * 80)
        print("MAPEO DE PLANTILLAS META → TWILIO CONTENT API")
        print("=" * 80 + "\n")
        
        if not templates:
            print("⚠️  No se encontraron plantillas mapeadas.")
            print("   Esto puede significar:")
            print("   1. Tu WABA no ha sido migrada a Content API")
            print("   2. No tienes plantillas aprobadas en Meta")
            print("   3. Necesitas contactar a soporte de Twilio")
            return
        
        print(f"{'Nombre Meta':<30} {'ContentSid':<20} {'Estado':<15}")
        print("-" * 80)
        
        for template in templates:
            name = template.get("legacy_template_name", "N/A")
            content_sid = template.get("sid", "N/A")
            status = template.get("status", "N/A")
            legacy_id = template.get("legacy_template_id", "N/A")
            language = template.get("language", "N/A")
            variables = template.get("variables", [])
            
            print(f"{name:<30} {content_sid:<20} {status:<15}")
            print(f"   Legacy ID: {legacy_id}")
            print(f"   Idioma: {language}")
            print(f"   Variables: {', '.join(variables) if variables else 'Ninguna'}")
            print()
        
        print("=" * 80)
        print(f"Total de plantillas mapeadas: {len(templates)}")
        print("=" * 80)
    
    def export_to_json(self, templates: list, filename: str = "legacy_content_mapping.json") -> None:
        """
        Exporta el mapeo a un archivo JSON.
        
        Args:
            templates: Lista de plantillas
            filename: Nombre del archivo de salida
        """
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_templates": len(templates),
            "templates": templates
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Mapeo exportado a: {filename}")


def main():
    """Función principal."""
    # Obtener credenciales de variables de entorno
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("❌ Error: Debes configurar las variables de entorno:")
        print("   TWILIO_ACCOUNT_SID=your_account_sid")
        print("   TWILIO_AUTH_TOKEN=your_auth_token")
        return
    
    print("🔍 Consultando endpoint LegacyContent...")
    
    checker = TwilioLegacyContentChecker(account_sid, auth_token)
    
    try:
        # Obtener todas las plantillas
        templates = checker.get_all_legacy_templates()
        
        # Imprimir resultados
        checker.print_template_mapping(templates)
        
        # Exportar a JSON
        checker.export_to_json(templates)
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Error HTTP: {e}")
        print(f"   Status Code: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
```

### Uso del script

```bash
# 1. Configurar variables de entorno
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_auth_token_here"

# 2. Ejecutar el script
python scripts/check_legacy_content.py

# 3. Revisar la salida
# - Se imprimirá el mapeo en consola
# - Se creará archivo legacy_content_mapping.json
```

---

## 6. Mejores Prácticas

### ✅ Recomendado

1. **Crear plantillas en Twilio directamente**
   - Mayor control sobre el ciclo de vida
   - Mejor integración con Content API
   - Gestión de versiones más clara

2. **Usar los ContentSid (`HX...`) en tu código**
   ```python
   # En lugar de:
   message = client.messages.create(
       from_="whatsapp:+14155238886",
       body="Tu mensaje",
       to="whatsapp:+34600000000",
       content_sid="HXabc123..."  # ❌ Legacy
   )
   
   # Usar:
   message = client.messages.create(
       from_="whatsapp:+14155238886",
       content_sid="HXabc123...",  # ✅ Content API
       content_variables={"nombre": "Juan", "fecha": "15/03"},
       to="whatsapp:+34600000000"
   )
   ```

3. **Mantener nombres consistentes**
   - Si recreas plantillas, usa los mismos nombres que en Meta
   - Facilita la vinculación automática

### ❌ Evitar

1. **Mezclar sistemas legacy y Content API**
   - Puede causar inconsistencias
   - Difícil de mantener

2. **Ignorar el estado de aprobación**
   - Siempre verificar `status` antes de usar una plantilla
   - Las plantillas rechazadas no se pueden enviar

3. **Hardcodear IDs de plantillas**
   - Usar variables de entorno o configuración
   - Los IDs pueden cambiar entre entornos

---

## 7. Preguntas Frecuentes

### P: ¿Por qué no veo mis plantillas en LegacyContent?

**R:** Posibles causas:
1. Tu WABA (WhatsApp Business Account) no ha sido migrada a Content API
2. Las plantillas fueron creadas después de la migración automática
3. Necesitas contactar a soporte de Twilio para forzar la migración

### P: ¿Puedo usar mis plantillas de Meta directamente?

**R:** Sí, pero con limitaciones:
- Debes usar el formato legacy (`content_sid` que empieza por `WH...`)
- No tendrás acceso a las características avanzadas de Content API
- Twilio recomienda migrar a Content API

### P: ¿Cuánto tarda la migración automática?

**R:** Depende de Twilio:
- Normalmente 24-48 horas después de solicitarla
- Para cuentas nuevas, puede ser inmediato
- Contacta a soporte si lleva más de 48 horas

### P: ¿Pierdo las aprobaciones de Meta si recreo en Twilio?

**R:** No necesariamente:
- Si usas el **mismo nombre y categoría**, Twilio intentará vincular con la plantilla aprobada en Meta
- Si la vinculación falla, tendrás que pasar por aprobación de nuevo
- Tiempo de aprobación típico: 1-24 horas

---

## 8. Referencias

- [Twilio Content API Documentation](https://www.twilio.com/docs/content)
- [LegacyContent Endpoint Reference](https://www.twilio.com/docs/content/legacycontent)
- [WhatsApp Business API via Twilio](https://www.twilio.com/docs/whatsapp)
- [Content API Templates](https://www.twilio.com/docs/content/content-api-templates)

---

## 9. Vinculación Exacta de Plantillas (Actualización 2026-03-25)

### Proceso de Vinculación

Para vincular plantillas de Meta con Twilio Content API, es necesario:

1. **Usar nombres idénticos** en ambos sistemas (Meta y Twilio)
2. **Usar contenido idéntico** (cuerpo del mensaje)
3. **Usar la misma categoría** (UTILITY, MARKETING, AUTHENTICATION)

### Plantillas Vinculadas Exitosamente

| Nombre en Meta | Nombre en Twilio | Content SID | Estado |
|-----------------|------------------|-------------|--------|
| `mesa_disponibilidad_enlasnubes_es` | `mesa_disponibilidad_enlasnubes_es` | `HX2bbf4bf865ac57eafe90051a41c42c3e` | ✅ Approved |
| `reserva_cancelacion_enlasnubes_es` | `reserva_cancelacion_enlasnubes_es` | `HXa09aef98872394b339fdb50bf8ec72e` | ✅ Approved |
| `reserva_recordatorio_enlasnubes_es` | `reserva_recordatorio_enlasnubes_es` | `HX2cc2087501d3f98701961631697c0b37` | ✅ Approved |
| `reserva_confirmacion_enlasnubes_es` | `reserva_confirmacion_enlasnubes_es` | `HXa529c4953d53a2cbb9ff5b5699ee3c3f` | ✅ Approved |

### Código Actualizado

El archivo [`src/infrastructure/templates/content_sids.py`](src/infrastructure/templates/content_sids.py) ha sido actualizado con estos nuevos SIDs:

```python
CONTENT_SIDS = {
    "mesa_disponibilidad": "HX2bbf4bf865ac57eafe90051a41c42c3e",
    "reserva_cancelacion": "HXa09aef98872394b339fdb50bf8ec72e",
    "reserva_recordatorio": "HX2cc2087501d3f98701961631697c0b37",
    "reserva_confirmacion": "HXa529c4953d53a2cbb9ff5b5699ee3c3f",
}
```

### Limpieza de Plantillas Obsoletas

Durante el proceso de sincronización, se identificaron plantillas duplicadas y obsoletas que deben ser eliminadas:

- Plantillas con nombres genéricos (sin el sufijo `_enlasnubes_es`)
- Plantillas rechazadas por Meta
- Plantillas pendientes de aprobación por más de 7 días

Para eliminar estas plantillas, ejecutar:
```bash
python scripts/delete_obsolete_templates.py
```

---

**Documento generado:** 2026-03-24  
**Última actualización:** 2026-03-25  
**Autor:** Sistema de Reservas En Las Nubes  
**Versión:** 1.1
