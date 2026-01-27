import sys
import os
import time

sys.path.append(r"C:\Users\yago\AppData\Roaming\Python\Python313\site-packages")
from notebooklm_mcp.api_client import NotebookLMClient
from notebooklm_mcp.auth import load_cached_tokens

NB5_ID = "2e4f8352-25fb-4d56-b46d-6ab5b82a3f64"
BASE_DIR = r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY"

FILES = [
    ("src/infrastructure/cache/redis_cache.py", "redis_cache.py"),
    ("RESUMEN_REDIS_OPTIMIZADO.md", "RESUMEN_REDIS_OPTIMIZADO.md"),
    ("test_redis_performance.py", "test_redis_performance.py"),
    ("comprehensive_redis_test.py", "comprehensive_redis_test.py"),
    ("redis.conf", "redis.conf"),
]

def main():
    tokens = load_cached_tokens()
    if not tokens: return
    client = NotebookLMClient(cookies=tokens.cookies, csrf_token=tokens.csrf_token, session_id=tokens.session_id)
    print(f"Uploading files to Notebook 5 ({NB5_ID})...")
    for rel, title in FILES:
        path = os.path.join(BASE_DIR, rel)
        if not os.path.exists(path): continue
        with open(path, "r", encoding="utf-8") as f:
            client.add_text_source(NB5_ID, f.read(), title)
            print(f"  Uploaded {title}")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
