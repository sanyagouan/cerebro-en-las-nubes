#!/usr/bin/env python3
"""Diagnóstico completo de WhatsApp via Twilio."""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from twilio.rest import Client

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
whatsapp_from = os.getenv('TWILIO_WHATSAPP_FROM', '')

print("=" * 60)
print("DIAGNOSTICO WHATSAPP - TWILIO")
print("=" * 60)

print(f"\n--- CONFIGURACION ---")
print(f"Account SID: {account_sid[:10]}..." if account_sid else "Account SID: NO CONFIGURADO")
print(f"Auth Token: {auth_token[:5]}..." if auth_token else "Auth Token: NO CONFIGURADO")
print(f"WhatsApp From: {whatsapp_from}")

client = Client(account_sid, auth_token)

# 1. Buscar el mensaje específico
print(f"\n--- ESTADO DEL MENSAJE SM112f0aea7230835b443d2d63cba4a25e ---")
try:
    msg = client.messages('SM112f0aea7230835b443d2d63cba4a25e').fetch()
    print(f"SID: {msg.sid}")
    print(f"Status: {msg.status}")
    print(f"To: {msg.to}")
    print(f"From: {msg.from_}")
    print(f"Body: {msg.body[:100] if msg.body else '(vacio)'}")
    print(f"Error Code: {msg.error_code}")
    print(f"Error Message: {msg.error_message}")
    print(f"Date Created: {msg.date_created}")
    print(f"Date Sent: {msg.date_sent}")
    print(f"Date Updated: {msg.date_updated}")
    print(f"Direction: {msg.direction}")
    print(f"Price: {msg.price}")
except Exception as e:
    print(f"Error al buscar mensaje: {e}")

# 2. Listar los últimos 10 mensajes WhatsApp
print(f"\n--- ULTIMOS 10 MENSAJES ---")
try:
    messages = client.messages.list(limit=10)
    for i, m in enumerate(messages):
        print(f"\n  [{i+1}] SID: {m.sid}")
        print(f"      Status: {m.status}")
        print(f"      To: {m.to}")
        print(f"      From: {m.from_}")
        body_preview = (m.body[:80] + "...") if m.body and len(m.body) > 80 else (m.body or "(vacio)")
        print(f"      Body: {body_preview}")
        print(f"      Error Code: {m.error_code}")
        print(f"      Error Msg: {m.error_message}")
        print(f"      Date: {m.date_created}")
except Exception as e:
    print(f"Error al listar mensajes: {e}")

print(f"\n{'=' * 60}")
print("FIN DEL DIAGNOSTICO")
print(f"{'=' * 60}")
