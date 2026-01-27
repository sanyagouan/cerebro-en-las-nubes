import sys
import os
import time

sys.path.append(r"C:\Users\yago\AppData\Roaming\Python\Python313\site-packages")
from notebooklm_mcp.api_client import NotebookLMClient
from notebooklm_mcp.auth import load_cached_tokens

NB7_ID = "7f2d7f3f-ca33-4fb4-9dca-950d74586af2"
BASE_DIR = r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY"

FILES = [
    ("src/core/logging.py", "logging.py"),
    ("docker-compose.yml", "docker-compose.yml"),
    ("Dockerfile", "Dockerfile"),
    ("DEPLOYMENT.md", "DEPLOYMENT.md"),
    ("tests/README.md", "tests/README.md"),
    ("find_coolify_app.py", "find_coolify_app.py"),
    ("coolify.yaml", "coolify.yaml"), # Opcional si existe
]

def main():
    tokens = load_cached_tokens()
    if not tokens: return
    client = NotebookLMClient(cookies=tokens.cookies, csrf_token=tokens.csrf_token, session_id=tokens.session_id)
    print(f"Uploading files to Notebook 7 ({NB7_ID})...")
    for rel, title in FILES:
        path = os.path.join(BASE_DIR, rel)
        if not os.path.exists(path): continue
        with open(path, "r", encoding="utf-8") as f:
            client.add_text_source(NB7_ID, f.read(), title)
            print(f"  Uploaded {title}")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
