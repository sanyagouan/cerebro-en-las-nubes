import sys
import os
import time

sys.path.append(r"C:\Users\yago\AppData\Roaming\Python\Python313\site-packages")
try:
    from notebooklm_mcp.api_client import NotebookLMClient
    from notebooklm_mcp.auth import load_cached_tokens
except ImportError: sys.exit(1)

NB4_ID = "cc90b5d5-8ee9-438d-9af9-fd057ff229ae"
BASE_DIR = r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY"

FILES = [
    ("src/infrastructure/external/airtable_service.py", "airtable_service.py"),
    ("src/infrastructure/external/twilio_service.py", "twilio_service.py"),
    ("src/infrastructure/services/whatsapp_service.py", "whatsapp_service.py"),
    ("src/infrastructure/services/weather_service.py", "weather_service.py"),
    ("src/infrastructure/repositories/booking_repo.py", "booking_repo.py"),
    ("src/api/vapi_router.py", "vapi_router.py"),
    ("src/api/whatsapp_router.py", "whatsapp_router.py"),
]

def main():
    tokens = load_cached_tokens()
    if not tokens: return
    client = NotebookLMClient(cookies=tokens.cookies, csrf_token=tokens.csrf_token, session_id=tokens.session_id)
    print(f"Uploading files to Notebook 4 ({NB4_ID})...")
    for rel, title in FILES:
        path = os.path.join(BASE_DIR, rel)
        if not os.path.exists(path): continue
        with open(path, "r", encoding="utf-8") as f:
            client.add_text_source(NB4_ID, f.read(), title)
            print(f"  Uploaded {title}")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
