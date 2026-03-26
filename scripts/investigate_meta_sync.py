#!/usr/bin/env python3
"""
Script para investigar cómo recuperar/sincronizar plantillas de Meta hacia Twilio.

Este script:
1. Consulta el endpoint LegacyContent para ver plantillas migradas de Meta
2. Lista todas las plantillas en Content API
3. Investiga el estado de las plantillas y su origen

Autor: Sistema de Reservas En Las Nubes
Fecha: 2026-03-25
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env en el directorio del proyecto
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Cargando variables desde: {env_file}")
else:
    print(f"⚠️ No se encontró archivo .env en: {env_file}")


class TwilioMetaSyncInvestigator:
    """Investiga la sincronización de plantillas Meta → Twilio."""
    
    BASE_URL_CONTENT = "https://content.twilio.com/v1"
    BASE_URL_API = "https://api.twilio.com/2010-04-01"
    
    def __init__(self, account_sid: str, auth_token: str):
        """
        Inicializa el investigador.
        
        Args:
            account_sid: Account SID de Twilio (AC...)
            auth_token: Auth Token de Twilio
        """
        self.account_sid = account_sid
        self.auth = HTTPBasicAuth(account_sid, auth_token)
    
    def check_legacy_content(self) -> Dict[str, Any]:
        """
        Consulta el endpoint LegacyContent para ver plantillas migradas de Meta.
        
        Returns:
            dict con la respuesta del endpoint
        """
        print("\n" + "=" * 80)
        print("1. CONSULTANDO ENDPOINT LegacyContent")
        print("=" * 80)
        print("\nEste endpoint muestra plantillas de Meta migradas a Content API.")
        
        url = f"{self.BASE_URL_CONTENT}/LegacyContent"
        
        try:
            response = requests.get(url, auth=self.auth, params={"PageSize": 50})
            
            print(f"\n📡 URL: {url}")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                meta_info = data.get("meta", {})
                
                print(f"\n✅ Respuesta exitosa!")
                print(f"   Total de plantillas mapeadas: {len(results)}")
                print(f"   Página: {meta_info.get('page', 0)}")
                print(f"   Total resultados: {meta_info.get('total_results', 0)}")
                
                if results:
                    print("\n📋 PLANTILLAS DE META MAPEADAS:")
                    print("-" * 80)
                    for t in results:
                        name = t.get("legacy_template_name", "N/A")
                        content_sid = t.get("sid", "N/A")
                        status = t.get("status", "N/A")
                        legacy_id = t.get("legacy_template_id", "N/A")
                        language = t.get("language", "N/A")
                        variables = t.get("variables", [])
                        
                        print(f"\n  📌 {name}")
                        print(f"     Content SID: {content_sid}")
                        print(f"     Legacy ID (Meta): {legacy_id}")
                        print(f"     Estado: {status}")
                        print(f"     Idioma: {language}")
                        print(f"     Variables: {', '.join(variables) if variables else 'Ninguna'}")
                else:
                    print("\n⚠️  No hay plantillas mapeadas en LegacyContent.")
                    print("   Esto significa que:")
                    print("   1. Tu WABA no ha sido migrada automáticamente")
                    print("   2. Las plantillas fueron creadas después de la migración")
                    print("   3. Necesitas contactar a soporte de Twilio")
                
                return data
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"error": response.status_code, "message": response.text}
                
        except Exception as e:
            print(f"\n❌ Excepción: {e}")
            return {"error": str(e)}
    
    def list_content_templates(self) -> Dict[str, Any]:
        """
        Lista todas las plantillas en Content API.
        
        Returns:
            dict con la respuesta del endpoint
        """
        print("\n" + "=" * 80)
        print("2. LISTANDO PLANTILLAS EN CONTENT API")
        print("=" * 80)
        
        url = f"{self.BASE_URL_CONTENT}/Content"
        
        try:
            response = requests.get(url, auth=self.auth, params={"PageSize": 50})
            
            print(f"\n📡 URL: {url}")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("contents", [])
                
                print(f"\n✅ Respuesta exitosa!")
                print(f"   Total de plantillas en Content API: {len(results)}")
                
                if results:
                    print("\n📋 PLANTILLAS EN CONTENT API:")
                    print("-" * 80)
                    for t in results:
                        sid = t.get("sid", "N/A")
                        name = t.get("friendly_name", "N/A")
                        status = t.get("status", "N/A")
                        language = t.get("language", "N/A")
                        types = t.get("types", [])
                        
                        print(f"\n  📌 {name}")
                        print(f"     SID: {sid}")
                        print(f"     Estado: {status}")
                        print(f"     Idioma: {language}")
                        print(f"     Tipos: {types}")
                else:
                    print("\n⚠️  No hay plantillas en Content API.")
                
                return data
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"error": response.status_code, "message": response.text}
                
        except Exception as e:
            print(f"\n❌ Excepción: {e}")
            return {"error": str(e)}
    
    def check_whatsapp_templates_legacy(self) -> Dict[str, Any]:
        """
        Consulta las plantillas de WhatsApp usando el endpoint legacy.
        
        Returns:
            dict con la respuesta del endpoint
        """
        print("\n" + "=" * 80)
        print("3. CONSULTANDO PLANTILLAS WHATSAPP (LEGACY)")
        print("=" * 80)
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Content.json"
        
        try:
            response = requests.get(url, auth=self.auth)
            
            print(f"\n📡 URL: {url}")
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Respuesta exitosa!")
                print(f"   Response: {json.dumps(data, indent=2)[:500]}...")
                return data
            else:
                print(f"\n❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return {"error": response.status_code, "message": response.text}
                
        except Exception as e:
            print(f"\n❌ Excepción: {e}")
            return {"error": str(e)}
    
    def investigate_sync_options(self) -> None:
        """
        Imprime información sobre las opciones de sincronización.
        """
        print("\n" + "=" * 80)
        print("4. OPCIONES DE SINCRONIZACIÓN META → TWILIO")
        print("=" * 80)
        
        print("""
Basado en la investigación, estas son las opciones disponibles:

📌 OPCIÓN A: MIGRACIÓN AUTOMÁTICA (RECOMENDADA)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Twilio migra automáticamente las plantillas aprobadas de Meta
   2. El endpoint LegacyContent muestra el mapeo
   3. Si NO aparecen tus plantillas:
      → Contactar a soporte de Twilio: support@twilio.com
      → Solicitar migración manual de tu WABA
      → Tiempo estimado: 24-48 horas

   4. Una vez migradas, usar los ContentSid (HX...) directamente

📌 OPCIÓN B: CREAR PLANTILLAS EN TWILIO CON VINCULACIÓN
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Crear plantillas en Twilio con el MISMO NOMBRE que en Meta
   2. Usar la MISMA CATEGORÍA (UTILITY, AUTHENTICATION, MARKETING)
   3. Twilio intentará vincular automáticamente con la plantilla aprobada en Meta
   4. Si la vinculación funciona → Aprobación instantánea
   5. Si falla → Pasar por proceso de aprobación (1-24 horas)

📌 OPCIÓN C: USAR FORMATO LEGACY (NO RECOMENDADO)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. Usar el Template SID legacy (WH...) de Meta
   2. Funciona pero sin características avanzadas de Content API
   3. Twilio descontinuará soporte legacy eventualmente

⚠️  IMPORTANTE:
   - Twilio recomienda crear plantillas directamente en su plataforma
   - Mayor control del ciclo de vida
   - Mejor integración con Content API
   - Gestión de versiones más clara

📞 CONTACTAR SOPORTE TWILIO:
   - Email: support@twilio.com
   - Incluir: Account SID, WABA ID, nombres de plantillas
   - Solicitar: "Migración manual de plantillas WhatsApp Business"
""")
        
        print("\n" + "=" * 80)
        print("5. PRÓXIMOS PASOS RECOMENDADOS")
        print("=" * 80)
        print("""
1. ✅ Ejecutar este script para ver si tus plantillas ya fueron migradas
2. Si NO aparecen en LegacyContent:
   a. Contactar a soporte de Twilio (soporte@twilio.com)
   b. Incluir:
      - Account SID: ACd37052c7a26448d2e12e20c68ecdca09
      - WABA ID: (tu WhatsApp Business Account ID)
      - Nombres de plantillas: reserva_cancelada_nubes, mesa_disponible_nubes, etc.
   c. Solicitar migración manual
3. Si SÍ aparecen:
   a. Usar los ContentSid (HX...) en tu código
   b. Actualizar content_sids.py con los nuevos SIDs
4. Alternativamente:
   a. Crear plantillas en Twilio con los mismos nombres que en Meta
   b. Esperar vinculación automática o aprobación
""")


def main():
    """Función principal."""
    print("=" * 80)
    print("INVESTIGACIÓN DE SINCRONIZACIÓN META → TWILIO")
    print("=" * 80)
    print(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Obtener credenciales de variables de entorno
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("\n❌ Error: Debes configurar las variables de entorno:")
        print("   TWILIO_ACCOUNT_SID=your_account_sid")
        print("   TWILIO_AUTH_TOKEN=your_auth_token")
        return 1
    
    print(f"\n🔑 Account SID: {account_sid[:10]}...{account_sid[-4:]}")
    
    investigator = TwilioMetaSyncInvestigator(account_sid, auth_token)
    
    # 1. Consultar LegacyContent (plantillas de Meta migradas)
    legacy_data = investigator.check_legacy_content()
    
    # 2. Listar plantillas en Content API
    content_data = investigator.list_content_templates()
    
    # 3. Consultar plantillas WhatsApp legacy
    whatsapp_data = investigator.check_whatsapp_templates_legacy()
    
    # 4. Mostrar opciones de sincronización
    investigator.investigate_sync_options()
    
    # 5. Guardar resultados
    output = {
        "timestamp": datetime.now().isoformat(),
        "account_sid": account_sid,
        "legacy_content": legacy_data,
        "content_api": content_data,
        "whatsapp_legacy": whatsapp_data
    }
    
    filename = "meta_sync_investigation.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Resultados guardados en: {filename}")
    print("\n" + "=" * 80)
    print("INVESTIGACIÓN COMPLETADA")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
