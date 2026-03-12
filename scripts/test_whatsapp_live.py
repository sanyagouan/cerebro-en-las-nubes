#!/usr/bin/env python3
"""
Script de prueba para enviar mensajes WhatsApp via Twilio.

Uso:
    python scripts/test_whatsapp_live.py +34XXXXXXXXX
    python scripts/test_whatsapp_live.py +34600000000 --template reserva_confirmacion_nubes_hx7175f69e6fcd551065df13962b6d96c6

Variables de entorno requeridas:
    TWILIO_ACCOUNT_SID - SID de la cuenta Twilio
    TWILIO_AUTH_TOKEN - Token de autenticación
    TWILIO_WHATSAPP_NUMBER - Número de WhatsApp origen (ej: whatsapp:+358454910405)
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Añadir el directorio raíz al path para importar el servicio
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from loguru import logger

# Cargar variables de entorno desde .env si existe
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Variables cargadas desde {env_path}")
else:
    logger.warning("No se encontró archivo .env, usando variables del sistema")


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
            
            # Variables de ejemplo para la plantilla
            variables = {
                "1": "Cliente Prueba",
                "2": "15/03/2026",
                "3": "21:00",
                "4": "4"
            }
            
            # Intentar enviar con Content SID (nueva API de Twilio)
            try:
                message = client.messages.create(
                    from_=whatsapp_from,
                    to=to_formatted,
                    content_sid=template_sid,
                    content_variables=variables
                )
                logger.success(f"✅ Mensaje con plantilla enviado: SID {message.sid}")
                logger.info(f"   Status: {message.status}")
                logger.info(f"   Body: {message.body[:100] if message.body else 'N/A'}...")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Error con Content SID, intentando método alternativo: {e}")
                
                # Método alternativo: body formateado manualmente
                body = f"¡Hola {variables['1']}! Tu reserva en Restobar En Las Nubes para el {variables['2']} a las {variables['3']} para {variables['4']} personas ha sido confirmada. ¡Te esperamos!"
                
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
    python scripts/test_whatsapp_live.py +34600000000 --template reserva_confirmacion_nubes_hx7175f69e6fcd551065df13962b6d96c6
    python scripts/test_whatsapp_live.py +34600000000 --service
        """
    )
    
    parser.add_argument(
        "numero",
        help="Número de destino en formato internacional (ej: +34600000000)"
    )
    
    parser.add_argument(
        "--template",
        "-t",
        default=None,
        help="SID de la plantilla de WhatsApp a usar"
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
    
    if args.service:
        success = test_whatsapp_service(args.numero)
    else:
        success = test_whatsapp_direct(args.numero, args.template)
    
    logger.info("=" * 60)
    if success:
        logger.success("✅ TEST COMPLETADO CON ÉXITO")
    else:
        logger.error("❌ TEST FALLIDO")
    logger.info("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
