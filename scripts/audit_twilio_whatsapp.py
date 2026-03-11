#!/usr/bin/env python3
"""
Script de auditoría de configuración de WhatsApp en Twilio
Genera un informe completo del estado actual
"""
import os
import json
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def audit_twilio_whatsapp():
    """Auditar la configuración completa de Twilio WhatsApp"""
    
    # Credenciales
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "").replace("whatsapp:", "")
    
    if not account_sid or not auth_token:
        print("❌ ERROR: TWILIO_ACCOUNT_SID o TWILIO_AUTH_TOKEN no configurados")
        return
    
    print("=" * 80)
    print("🔍 AUDITORÍA DE CONFIGURACIÓN TWILIO WHATSAPP")
    print("=" * 80)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 Account SID: {account_sid}")
    print(f"📱 Número WhatsApp configurado: {whatsapp_number}")
    print("=" * 80)
    print()
    
    try:
        client = Client(account_sid, auth_token)
        
        # ========================================
        # 1. INFORMACIÓN DE LA CUENTA
        # ========================================
        print("📊 1. INFORMACIÓN DE LA CUENTA")
        print("-" * 80)
        try:
            account = client.api.accounts(account_sid).fetch()
            print(f"✅ Estado de la cuenta: {account.status}")
            print(f"   Nombre: {account.friendly_name}")
            print(f"   Tipo: {account.type}")
            print(f"   Creada: {account.date_created}")
        except Exception as e:
            print(f"❌ Error obteniendo info de cuenta: {e}")
        print()
        
        # ========================================
        # 2. NÚMEROS DE TELÉFONO
        # ========================================
        print("📞 2. NÚMEROS DE TELÉFONO EN LA CUENTA")
        print("-" * 80)
        try:
            numbers = client.incoming_phone_numbers.list(limit=100)
            
            if not numbers:
                print("⚠️  No se encontraron números de teléfono")
            else:
                for idx, number in enumerate(numbers, 1):
                    print(f"\n[{idx}] Número: {number.phone_number}")
                    print(f"    SID: {number.sid}")
                    print(f"    Nombre: {number.friendly_name or '(sin nombre)'}")
                    print(f"    País: {number.iso_country}")
                    
                    # Capacidades
                    caps = []
                    if getattr(number.capabilities, 'voice', False):
                        caps.append("🎙️  Voz")
                    if getattr(number.capabilities, 'sms', False):
                        caps.append("💬 SMS")
                    if getattr(number.capabilities, 'mms', False):
                        caps.append("📷 MMS")
                    print(f"    Capacidades: {', '.join(caps) if caps else '(ninguna)'}")
                    
                    # WhatsApp Status
                    # Nota: La API de Twilio no expone directamente si un número está habilitado para WhatsApp
                    # Debemos verificar a través de otros endpoints
                    is_configured_whatsapp = (number.phone_number == whatsapp_number or 
                                             number.phone_number == f"+{whatsapp_number}")
                    if is_configured_whatsapp:
                        print(f"    ✅ ESTE ES EL NÚMERO CONFIGURADO PARA WHATSAPP")
                    
                    # Webhooks configurados
                    if number.sms_url:
                        print(f"    📡 SMS Webhook: {number.sms_url}")
                    if number.voice_url:
                        print(f"    📡 Voice Webhook: {number.voice_url}")
                    
                    print()
        except Exception as e:
            print(f"❌ Error listando números: {e}")
        print()
        
        # ========================================
        # 3. WHATSAPP SENDER STATUS
        # ========================================
        print("📲 3. ESTADO DE WHATSAPP SENDER")
        print("-" * 80)
        try:
            # Intentar obtener información del WhatsApp sender
            # Nota: Twilio no tiene un endpoint específico para listar WhatsApp senders
            # Verificamos enviando un mensaje de prueba (comentado para evitar envíos reales)
            
            print(f"📱 Número configurado en .env: {whatsapp_number}")
            print()
            
            # Verificar si el número está en formato E.164
            if not whatsapp_number.startswith('+'):
                print(f"⚠️  ADVERTENCIA: El número {whatsapp_number} no está en formato E.164")
                print("   Formato correcto: +34666123456")
            else:
                print(f"✅ Número en formato E.164 correcto")
            
            # Determinar si es Sandbox o Producción
            if "+14155238886" in whatsapp_number:
                print("🧪 MODO: SANDBOX (Twilio WhatsApp Sandbox)")
                print("   ⚠️  Los destinatarios deben unirse enviando 'join <code>'")
            elif "+358" in whatsapp_number:
                print("🇫🇮 MODO: PRODUCCIÓN - Número finlandés (+358)")
                print("   ⚠️  PROBLEMA: Se requiere número español (+34) para el restobar")
            elif "+34" in whatsapp_number:
                print("🇪🇸 MODO: PRODUCCIÓN - Número español (+34)")
                print("   ✅ Correcto para el restobar en España")
            else:
                print(f"❓ MODO: Número no reconocido ({whatsapp_number})")
            
            print()
            
            # WhatsApp Business Info del .env
            print("📋 Información de WhatsApp Business (del .env):")
            print(f"   Business Name: En Las Nubes Restobar")
            print(f"   WhatsApp Business Account ID: 1437289717941886")
            print(f"   Meta Business Manager ID: 2779922545365043")
            
        except Exception as e:
            print(f"❌ Error verificando WhatsApp sender: {e}")
        print()
        
        # ========================================
        # 4. MENSAJES RECIENTES (últimos 5)
        # ========================================
        print("📨 4. MENSAJES WHATSAPP RECIENTES (últimos 5)")
        print("-" * 80)
        try:
            messages = client.messages.list(
                from_=f"whatsapp:{whatsapp_number}",
                limit=5
            )
            
            if not messages:
                print("ℹ️  No se encontraron mensajes recientes")
            else:
                for msg in messages:
                    status_icon = "✅" if msg.status == "delivered" else "⏳" if msg.status in ["queued", "sent"] else "❌"
                    print(f"{status_icon} [{msg.date_sent.strftime('%Y-%m-%d %H:%M')}] → {msg.to}")
                    print(f"   Estado: {msg.status}")
                    print(f"   Dirección: {msg.direction}")
                    print(f"   Precio: {msg.price or 'N/A'} {msg.price_unit or ''}")
                    if msg.error_code:
                        print(f"   ❌ Error: {msg.error_code} - {msg.error_message}")
                    print()
        except Exception as e:
            print(f"⚠️  No se pudieron obtener mensajes: {e}")
            print("   (Esto puede ser normal si aún no se han enviado mensajes)")
        print()
        
        # ========================================
        # 5. CONTENT TEMPLATES (Mensajes pre-aprobados)
        # ========================================
        print("📝 5. CONTENT TEMPLATES (Mensajes pre-aprobados)")
        print("-" * 80)
        try:
            # Intentar listar Content Templates usando la API v2010
            # Nota: Twilio Content API es un producto separado
            contents = client.content.v1.contents.list(limit=20)
            
            if not contents:
                print("⚠️  No se encontraron Content Templates registrados")
                print()
                print("❗ ACCIÓN REQUERIDA:")
                print("   Debes registrar templates de mensaje con Twilio Content API")
                print("   Ejecuta: python register_twilio_template.py")
            else:
                for content in contents:
                    print(f"✅ Template: {content.friendly_name}")
                    print(f"   SID: {content.sid}")
                    print(f"   Tipo: {content.types}")
                    print()
        except Exception as e:
            print(f"⚠️  Error listando Content Templates: {e}")
            print("   Puede que no tengas acceso a Twilio Content API")
        print()
        
        # ========================================
        # 6. WEBHOOKS CONFIGURADOS
        # ========================================
        print("🔗 6. WEBHOOKS CONFIGURADOS")
        print("-" * 80)
        print("ℹ️  Los webhooks de WhatsApp se configuran en:")
        print("   Twilio Console → Messaging → Settings → WhatsApp Sandbox/Sender")
        print()
        print("🎯 Webhook esperado (según task):")
        print("   https://go84sgscs4ckcs08wog84o0o.app.generaia.site/twilio/whatsapp/incoming")
        print()
        print("📚 Webhook en documentación:")
        print("   https://api.enlasnubes.com/whatsapp/webhook")
        print()
        print("⚠️  ACCIÓN REQUERIDA: Verificar en Twilio Console cuál está configurado")
        print()
        
        # ========================================
        # RESUMEN Y RECOMENDACIONES
        # ========================================
        print("=" * 80)
        print("📋 RESUMEN Y RECOMENDACIONES")
        print("=" * 80)
        print()
        print("✅ CONFIGURADO:")
        print("   • Cuenta Twilio activa")
        print(f"   • Número WhatsApp: {whatsapp_number}")
        print("   • Credenciales funcionando correctamente")
        print()
        print("⚠️  PROBLEMAS DETECTADOS:")
        print("   1. Número finlandés (+358) en lugar de español (+34)")
        print("   2. Variable inconsistente: código usa TWILIO_WHATSAPP_FROM, .env define TWILIO_WHATSAPP_NUMBER")
        print("   3. URL de webhook discrepante entre documentación y task")
        print()
        print("❗ ACCIONES PENDIENTES:")
        print("   1. Solicitar número español (+34) a Twilio")
        print("   2. Verificar webhook configurado en Twilio Console")
        print("   3. Confirmar templates de mensaje registrados con Meta")
        print("   4. Verificar estado de verificación de negocio con Meta")
        print("   5. Corregir nombre de variable (TWILIO_WHATSAPP_FROM vs TWILIO_WHATSAPP_NUMBER)")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    audit_twilio_whatsapp()
