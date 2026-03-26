#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo para recrear plantillas de WhatsApp y enviarlas a Meta.

PASOS:
1. Eliminar TODAS las plantillas existentes
2. Crear las 4 plantillas necesarias
3. Enviar cada plantilla a Meta para aprobación
4. Actualizar content_sids.py con los nuevos SIDs
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Configurar codificación para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Cargar variables de entorno
load_dotenv()

# Credenciales de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# URLs de la API
BASE_URL = "https://content.twilio.com/v1"
CONTENT_URL = f"{BASE_URL}/Content"
APPROVAL_URL = f"{BASE_URL}/Content/{{sid}}/ApprovalRequests/whatsapp"

# Autenticación
AUTH = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
HEADERS = {"Content-Type": "application/json"}


def get_all_templates():
    """Obtiene todas las plantillas existentes"""
    print("\n[INFO] Obteniendo plantillas existentes...")
    
    response = requests.get(CONTENT_URL, auth=AUTH, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        contents = data.get("contents", [])
        print(f"[INFO] Encontradas {len(contents)} plantillas")
        return contents
    else:
        print(f"[ERROR] No se pudieron obtener plantillas: {response.status_code}")
        return []


def delete_template(sid, name):
    """Elimina una plantilla por SID"""
    url = f"{CONTENT_URL}/{sid}"
    response = requests.delete(url, auth=AUTH, headers=HEADERS)
    
    if response.status_code == 204:
        print(f"  [OK] Eliminada: {name} ({sid})")
        return True
    else:
        print(f"  [ERROR] No se pudo eliminar {name}: {response.status_code}")
        return False


def delete_all_templates():
    """Elimina TODAS las plantillas existentes"""
    print("\n" + "=" * 70)
    print("[PASO 1] ELIMINANDO TODAS LAS PLANTILLAS EXISTENTES")
    print("=" * 70)
    
    templates = get_all_templates()
    
    if not templates:
        print("[INFO] No hay plantillas para eliminar")
        return True
    
    deleted = 0
    failed = 0
    
    for template in templates:
        sid = template.get("sid")
        name = template.get("friendly_name", "sin_nombre")
        
        if delete_template(sid, name):
            deleted += 1
        else:
            failed += 1
    
    print(f"\n[RESUMEN] {deleted} eliminadas, {failed} fallos")
    return failed == 0


def create_template(friendly_name, body, footer=None):
    """
    Crea una nueva plantilla en Twilio Content API
    
    Args:
        friendly_name: Nombre de la plantilla
        body: Texto del cuerpo
        footer: Texto del pie de página (opcional)
    
    Returns:
        dict con datos de la plantilla o None si falla
    """
    # Construir el body completo
    full_body = body
    if footer:
        full_body += f"\n\n{footer}"
    
    payload = {
        "friendly_name": friendly_name,
        "language": "es",
        "types": {
            "twilio/text": {
                "body": full_body
            }
        }
    }
    
    print(f"\n  [CREANDO] {friendly_name}")
    print(f"       Body: {body[:60]}...")
    
    response = requests.post(CONTENT_URL, json=payload, auth=AUTH, headers=HEADERS)
    
    if response.status_code in [200, 201]:
        data = response.json()
        sid = data.get("sid")
        print(f"       [OK] Creada! SID: {sid}")
        return data
    else:
        print(f"       [ERROR] Status: {response.status_code}")
        print(f"       Response: {response.text}")
        return None


def submit_for_approval(sid, name, category="UTILITY"):
    """
    Envía una plantilla a Meta para aprobación
    
    Args:
        sid: SID de la plantilla
        name: Nombre de la plantilla
        category: Categoría de Meta (UTILITY, AUTHENTICATION, MARKETING)
    
    Returns:
        bool: True si se envió correctamente
    """
    url = APPROVAL_URL.format(sid=sid)
    
    payload = {
        "name": name,
        "category": category
    }
    
    print(f"\n  [ENVIANDO A META] {name}")
    print(f"       SID: {sid}")
    print(f"       Category: {category}")
    
    response = requests.post(url, json=payload, auth=AUTH, headers=HEADERS)
    
    print(f"       Status: {response.status_code}")
    print(f"       Response: {response.text[:500] if response.text else 'Empty'}")
    
    if response.status_code in [200, 201, 202]:
        print(f"       [OK] Enviado a Meta!")
        return True
    else:
        print(f"       [ERROR] No se pudo enviar a Meta")
        return False


def create_all_templates():
    """Crea las 4 plantillas necesarias"""
    print("\n" + "=" * 70)
    print("[PASO 2] CREANDO LAS 4 PLANTILLAS NECESARIAS")
    print("=" * 70)
    
    # Definir las plantillas con contenido exacto
    templates = [
        {
            "name": "reserva_confirmacion_nubes",
            "body": "Estimado/a {{1}}, confirmamos tu reserva en Restaurante En Las Nubes. Fecha: {{2}}, hora: {{3}}. Te esperamos.",
            "footer": "Gracias por confiar en nosotros"
        },
        {
            "name": "reserva_recordatorio_nubes",
            "body": "Recordatorio de reserva para {{1}}: mesa para {{2}} personas el {{3}} a las {{4}} en Restaurante En Las Nubes. Responde SI para confirmar o NO para cancelar.",
            "footer": "Responde SI o NO para gestionar tu reserva"
        },
        {
            "name": "reserva_cancelada_nubes",
            "body": "Aviso para {{1}}: tu reserva del {{2}} a las {{3}} en Restaurante En Las Nubes ha sido cancelada. Para cualquier consulta contacta con nosotros.",
            "footer": "Lamentamos los inconvenientes causados"
        },
        {
            "name": "mesa_disponible_nubes",
            "body": "Disponibilidad de mesa para {{1}}: tenemos mesa para {{2}} personas el {{3}} a las {{4}} en Restaurante En Las Nubes. Contacta con nosotros para confirmar.",
            "footer": "Contacta con nosotros para reservar"
        }
    ]
    
    created = []
    
    for template in templates:
        result = create_template(
            friendly_name=template["name"],
            body=template["body"],
            footer=template["footer"]
        )
        
        if result:
            created.append({
                "name": template["name"],
                "sid": result.get("sid"),
                "body": template["body"],
                "footer": template["footer"]
            })
    
    print(f"\n[RESUMEN] {len(created)} de 4 plantillas creadas")
    return created


def submit_all_for_approval(templates):
    """Envía todas las plantillas a Meta para aprobación"""
    print("\n" + "=" * 70)
    print("[PASO 3] ENVIANDO PLANTILLAS A META PARA APROBACIÓN")
    print("=" * 70)
    
    submitted = 0
    
    for template in templates:
        if submit_for_approval(template["sid"], template["name"]):
            submitted += 1
    
    print(f"\n[RESUMEN] {submitted} de {len(templates)} enviadas a Meta")
    return submitted


def update_content_sids(templates):
    """Actualiza el archivo content_sids.py con los nuevos SIDs"""
    print("\n" + "=" * 70)
    print("[PASO 4] ACTUALIZANDO content_sids.py")
    print("=" * 70)
    
    if not templates:
        print("[ERROR] No hay plantillas para actualizar")
        return False
    
    # Leer el archivo actual
    file_path = "src/infrastructure/templates/content_sids.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Crear nuevo contenido
        new_content = '''"""
Mapeo de nombres de plantilla a Content SIDs de Twilio.
Actualizado automáticamente por recreate_templates_v3.py
"""

CONTENT_SIDS = {
'''
        
        for template in templates:
            new_content += f'    "{template["name"]}": "{template["sid"]}",\n'
        
        new_content += '''}

# Alias para compatibilidad
TEMPLATE_ALIASES = {
    "confirmacion": "reserva_confirmacion_nubes",
    "recordatorio": "reserva_recordatorio_nubes",
    "cancelacion": "reserva_cancelada_nubes",
    "mesa_disponible": "mesa_disponible_nubes",
}


def get_sid(template_name: str) -> str:
    """
    Obtiene el SID de una plantilla por su nombre o alias.
    
    Args:
        template_name: Nombre o alias de la plantilla
    
    Returns:
        Content SID de Twilio
    
    Raises:
        KeyError: Si la plantilla no existe
    """
    # Intentar con alias primero
    if template_name in TEMPLATE_ALIASES:
        template_name = TEMPLATE_ALIASES[template_name]
    
    if template_name not in CONTENT_SIDS:
        raise KeyError(f"Plantilla no encontrada: {template_name}")
    
    return CONTENT_SIDS[template_name]
'''
        
        # Escribir el nuevo contenido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"[OK] Archivo actualizado: {file_path}")
        print("\nNuevos SIDs:")
        for template in templates:
            print(f'    "{template["name"]}": "{template["sid"]}",')
        
        return True
        
    except Exception as e:
        print(f"[ERROR] No se pudo actualizar el archivo: {e}")
        return False


def main():
    """Ejecuta el proceso completo"""
    print("=" * 70)
    print("  RECREACIÓN COMPLETA DE PLANTILLAS WHATSAPP")
    print("=" * 70)
    print("\n[INFO] Este script realiza:")
    print("  1. Elimina TODAS las plantillas existentes")
    print("  2. Crea las 4 plantillas necesarias")
    print("  3. Envía cada plantilla a Meta para aprobación")
    print("  4. Actualiza content_sids.py con los nuevos SIDs")
    
    # Verificar credenciales
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("\n[ERROR] Credenciales de Twilio no configuradas")
        print("        Asegúrate de que TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN están en .env")
        return
    
    # PASO 1: Eliminar todas las plantillas
    delete_all_templates()
    
    # PASO 2: Crear las 4 plantillas
    created_templates = create_all_templates()
    
    if not created_templates:
        print("\n[ERROR] No se creó ninguna plantilla. Abortando.")
        return
    
    # PASO 3: Enviar a Meta para aprobación
    submitted = submit_all_for_approval(created_templates)
    
    # PASO 4: Actualizar content_sids.py
    if submitted > 0:
        update_content_sids(created_templates)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("  RESUMEN FINAL")
    print("=" * 70)
    print(f"\n  Plantillas creadas: {len(created_templates)}")
    print(f"  Enviadas a Meta: {submitted}")
    print(f"  Archivo actualizado: {'Sí' if created_templates else 'No'}")
    
    if created_templates:
        print("\n  NUEVOS SIDs:")
        for t in created_templates:
            print(f"    {t['name']}: {t['sid']}")
    
    print("\n[INFO] Las plantillas están pendientes de aprobación por Meta.")
    print("       El proceso de aprobación puede tardar hasta 24 horas.")
    print("       Ejecuta check_template_approval_simple.py para verificar el estado.")


if __name__ == "__main__":
    main()
