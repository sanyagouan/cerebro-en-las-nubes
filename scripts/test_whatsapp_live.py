#!/usr/bin/env python3
"""
Script de prueba para enviar mensajes WhatsApp via Twilio.

Uso:
    python scripts/test_whatsapp_live.py +34XXXXXXXXX
    python scripts/test_whatsapp_live.py +34600000000 --tipo confirmacion
    python scripts/test_whatsapp_live.py +34600000000 --template HX5352b9aa7f916c818e2407dccb671a74

Variables de entorno requeridas:
    TWILIO_ACCOUNT_SID - SID de la cuenta Twilio
    TWILIO_AUTH_TOKEN - Token de autenticación
    TWILIO_WHATSAPP_NUMBER - Número de WhatsApp origen (ej: whatsapp:+358454910405)

SIDs de plantillas (gestionados en src/infrastructure/templates/content_sids.py):
    - recordatorio: reserva_recordatorio_nubes
    - confirmacion: reserva_confirmacion_nubes
    - cancelacion: reserva_cancelada_nubes
    - mesa_disponible: mesa_disponible_nubes
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Añadir el directorio raíz al path para importar el servicio
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar SIDs desde la fuente única (después de configurar sys.path)
from src.infrastructure.templates.content_sids import CONTENT_SIDS

from dotenv import load_dotenv
from loguru import logger

# Cargar variables de entorno desde .env si existe
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Variables cargadas desde {env_path}")
else:
    logger.warning("No se encontró archivo .env, usando variables del sistema")


# SIDs de las plantillas WhatsApp - importados desde content_sids.py
# Actualizado: 2026-03-26 - Corregido para usar CONTENT_SIDS con claves correctas
PLANTILLAS_WHATSAPP = {
    "recordatorio": CONTENT_SIDS["reserva_recordatorio"],
    "confirmacion": CONTENT_SIDS["reserva_confirmacion"],
    "cancelacion": CONTENT_SIDS["reserva_cancelada"],
    "mesa_disponible": CONTENT_SIDS["mesa_disponible"],
}


def get_next_friday_formatted() -> str:
    """Obtiene el próximo viernes en formato largo español."""
    dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    
    today = datetime.now()
    days_until_friday = (4 - today.weekday()) % 7  # 4 = viernes
    if days_until_friday == 0:
        days_until_friday = 7  # Si hoy es viernes, usar el siguiente
    next_friday = today + timedelta(days=days_until_friday)
    
    return f"{dias_semana[next_friday.weekday()]} {next_friday.day} de {meses[next_friday.month - 1]}"


def test_whatsapp_direct(to_number: str, template_sid: str = None):
    """
    Prueba el envío de WhatsApp usando directamente la API de Twilio.
    
    Args:
        to_number: Número de destino en formato internacional (+34XXXXXXXXX)
        template_sid: SID de la plantilla de WhatsApp (opcional)
    """
    from twilio.rest import Client
    
    # Credenciales
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_from = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+358454910405")
    
    if not account_sid or not auth_token:
        logger.error("❌ TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN son requeridos")
        logger.info("Configura las variables de entorno o crea un archivo .env")
        return False
    
    logger.info(f"📱 Configuración:")
    logger.info(f"   Account SID: {account_sid[:10]}...")
    logger.info(f"   WhatsApp From: {whatsapp_from}")
    logger.info(f"   To: {to_number}")
    
    # Formatear número de destino
    if not to_number.startswith("whatsapp:"):
        to_formatted = f"whatsapp:{to_number}"
    else:
        to_formatted = to_number
    
    try:
        client = Client(account_sid, auth_token)
        
        # Si hay plantilla, intentar usar Content API
        if template_sid:
            logger.info(f"📋 Usando plantilla: {template_sid}")
            
            # Variables de ejemplo para la plantilla (4 variables según template completo)
            # Template: "Hola {{1}}, tienes reserva en En Las Nubes para el {{2}} a las {{3}}h para {{4}} personas."
            
            variables = {
                "1": "Juan",                              # Nombre del cliente
                "2": get_next_friday_formatted(),         # Fecha dinámica en formato largo español (ej: "viernes 28 de marzo")
                "3": "21:00",                             # Hora de la reserva
                "4": "4"                                  # Número de personas
            }
            
            # Intentar enviar con Content SID (nueva API de Twilio)
            try:
                message = client.messages.create(
                    from_=whatsapp_from,
                    to=to_formatted,
                    content_sid=template_sid,
                    content_variables=json.dumps(variables)
                )
                logger.success(f"✅ Mensaje con plantilla enviado: SID {message.sid}")
                logger.info(f"   Status: {message.status}")
                logger.info(f"   Body: {message.body[:100] if message.body else 'N/A'}...")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Error con Content SID, intentando método alternativo: {e}")
                
                # Método alternativo: body formateado manualmente (4 variables)
                body = f"¡Hola {variables['1']}! Tienes reserva en En Las Nubes para el {variables['2']} a las {variables['3']}h para {variables['4']} personas. ¿CONFIRMAS? Responde SÍ o NO. Gracias!"
                
                message = client.messages.create(
                    from_=whatsapp_from,
                    to=to_formatted,
                    body=body
                )
                logger.success(f"✅ Mensaje enviado (método alternativo): SID {message.sid}")
                logger.info(f"   Status: {message.status}")
                return True
        else:
            # Mensaje simple sin plantilla
            logger.info("📝 Enviando mensaje simple (sin plantilla)")
            
            body = f"🧪 Mensaje de prueba desde En Las Nubes Restobar - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            message = client.messages.create(
                from_=whatsapp_from,
                to=to_formatted,
                body=body
            )
            logger.success(f"✅ Mensaje enviado: SID {message.sid}")
            logger.info(f"   Status: {message.status}")
            logger.info(f"   Body: {message.body}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error enviando WhatsApp: {e}")
        return False


def test_whatsapp_service(to_number: str):
    """
    Prueba el envío usando el servicio TwilioService del proyecto.
    
    Args:
        to_number: Número de destino en formato internacional
    """
    from src.infrastructure.external.twilio_service import TwilioService
    
    logger.info("🔧 Probando TwilioService del proyecto...")
    
    service = TwilioService()
    
    if not service.client:
        logger.error("❌ Cliente de Twilio no inicializado. Revisa las credenciales.")
        return False
    
    # Mensaje de prueba
    body = f"🧪 Prueba desde TwilioService - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    
    result = service.send_whatsapp(to_number, body)
    
    if result:
        logger.success(f"✅ TwilioService envió mensaje: SID {result}")
        return True
    else:
        logger.error("❌ TwilioService falló al enviar")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Prueba de envío de WhatsApp via Twilio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
    python scripts/test_whatsapp_live.py +34600000000
    python scripts/test_whatsapp_live.py +34600000000 --tipo confirmacion
    python scripts/test_whatsapp_live.py +34600000000 --template HX5352b9aa7f916c818e2407dccb671a74
    python scripts/test_whatsapp_live.py +34600000000 --service

Plantillas disponibles (usar --tipo) - SIDs gestionados en content_sids.py:
    - recordatorio: reserva_recordatorio_nubes
    - confirmacion: reserva_confirmacion_nubes
    - cancelacion: reserva_cancelada_nubes
    - mesa_disponible: mesa_disponible_nubes
        """
    )
    
    parser.add_argument(
        "numero",
        help="Número de destino en formato internacional (ej: +34600000000)"
    )
    
    parser.add_argument(
        "--tipo",
        choices=list(PLANTILLAS_WHATSAPP.keys()),
        default=None,
        help="Tipo de plantilla a usar: recordatorio, confirmacion, cancelacion, mesa_disponible"
    )
    
    parser.add_argument(
        "--template",
        "-t",
        default=None,
        help="SID de la plantilla de WhatsApp a usar (alternativa a --tipo)"
    )
    
    parser.add_argument(
        "--service",
        "-s",
        action="store_true",
        help="Usar el TwilioService del proyecto en lugar de la API directa"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("🚀 TEST DE WHATSAPP VIA TWILIO")
    logger.info("=" * 60)
    
    # Determinar el SID de la plantilla
    template_sid = None
    if args.tipo:
        template_sid = PLANTILLAS_WHATSAPP.get(args.tipo)
        logger.info(f"📋 Usando plantilla '{args.tipo}': {template_sid}")
    elif args.template:
        template_sid = args.template
        logger.info(f"📋 Usando SID directo: {template_sid}")
    
    if args.service:
        success = test_whatsapp_service(args.numero)
    else:
        success = test_whatsapp_direct(args.numero, template_sid)
    
    logger.info("=" * 60)
    if success:
        logger.success("✅ TEST COMPLETADO CON ÉXITO")
    else:
        logger.error("❌ TEST FALLIDO")
    logger.info("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
