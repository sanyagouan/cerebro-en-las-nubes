import os
import sys
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def update_vapi_urls(new_base_url: str):
    new_base_url = new_base_url.rstrip("/")
    api_key = os.getenv("VAPI_API_KEY")
    assistant_id = os.getenv("VAPI_ASSISTANT_ID", "9a1f2df2-1c2d-4061-b11c-bdde7568c85d")
    
    if not api_key:
        print("Error: VAPI_API_KEY no encontrada en el .env")
        sys.exit(1)
        
    url = f"https://api.vapi.ai/assistant/{assistant_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "serverUrl": f"{new_base_url}/vapi/webhook",
        "server": {
            "url": f"{new_base_url}/vapi/assistant"
        }
    }
    
    print(f"Actualizando Asistente VAPI ({assistant_id}) a la URL: {new_base_url}")
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        print("Configuracion de VAPI actualizada correctamente en la nube.")
    except Exception as e:
        print(f"Error actualizando VAPI:")
        if hasattr(e, 'response') and e.response is not None:
            print(e.response.text)
        else:
            print(str(e))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = os.getenv("PUBLIC_URL")
        if not target_url:
            print("Uso: python set_vapi_url.py <https://tu-url.com>")
            sys.exit(1)
            
    update_vapi_urls(target_url)
