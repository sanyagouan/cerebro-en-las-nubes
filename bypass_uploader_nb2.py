import sys
import os
import time

sys.path.append(r"C:\Users\yago\AppData\Roaming\Python\Python313\site-packages")

try:
    from notebooklm_mcp.api_client import NotebookLMClient
    from notebooklm_mcp.auth import load_cached_tokens
except ImportError:
    print("Error: Could not import notebooklm_mcp.")
    sys.exit(1)

NB2_ID = "5baa2a13-feff-431f-8ec8-69cc3fead9ca"

BASE_DIR = r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY"

FILES = [
    ("src/core/logic/booking_engine.py", "booking_engine.py"),
    ("src/application/services/schedule_service.py", "schedule_service.py"),
    ("src/application/services/table_assignment.py", "table_assignment.py"),
    ("src/application/services/holiday_service.py", "holiday_service.py"),
    ("src/application/services/escalation_service.py", "escalation_service.py"),
    ("src/application/services/team_alerts.py", "team_alerts.py"),
    ("src/application/orchestrator.py", "orchestrator.py"),
    ("DATOS RESTOBAR EN LAS NUBES/CASOS_USO_RESTOBAR.md", "CASOS_USO_RESTOBAR.md"),
]

def main():
    print("Loading auth tokens...")
    tokens = load_cached_tokens()
    if not tokens:
        return

    print("Initializing client...")
    client = NotebookLMClient(cookies=tokens.cookies, csrf_token=tokens.csrf_token, session_id=tokens.session_id)
    
    print(f"Uploading {len(FILES)} files to Notebook 2 ({NB2_ID})...")
    
    for rel_path, title in FILES:
        full_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(full_path):
            print(f"Skipping missing file: {full_path}")
            continue
            
        print(f"Uploading {title}...")
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            result = client.add_text_source(NB2_ID, content, title)
            if result:
                print(f"  Success! Source ID: {result.get('id')}")
            else:
                print(f"  Failed.")
            time.sleep(2)
        except Exception as e:
            print(f"  Error uploading {title}: {e}")

if __name__ == "__main__":
    main()
