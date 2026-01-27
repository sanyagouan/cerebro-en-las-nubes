import sys
import os
import time

sys.path.append(r"C:\Users\yago\AppData\Roaming\Python\Python313\site-packages")

try:
    from notebooklm_mcp.api_client import NotebookLMClient
    from notebooklm_mcp.auth import load_cached_tokens
except ImportError:
    sys.exit(1)

NB3_ID = "6a526f76-16b6-423c-9b88-68a42ca8516a"
BASE_DIR = r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY"

FILES = [
    ("DATOS RESTOBAR EN LAS NUBES/FAQS_RESTOBAR.md", "FAQS_RESTOBAR.md"),
    ("src/application/agents/base_agent.py", "base_agent.py"),
    ("src/application/agents/human_agent.py", "human_agent.py"),
    ("src/application/agents/logic_agent.py", "logic_agent.py"),
    ("src/application/agents/router_agent.py", "router_agent.py"),
]

def main():
    tokens = load_cached_tokens()
    if not tokens: return
    client = NotebookLMClient(cookies=tokens.cookies, csrf_token=tokens.csrf_token, session_id=tokens.session_id)
    
    print(f"Uploading {len(FILES)} files to Notebook 3 ({NB3_ID})...")
    for rel_path, title in FILES:
        full_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(full_path): continue
        try:
            with open(full_path, "r", encoding="utf-8") as f: content = f.read()
            result = client.add_text_source(NB3_ID, content, title)
            if result: print(f"  Success: {title}")
            time.sleep(2)
        except Exception as e: print(f"  Error {title}: {e}")

if __name__ == "__main__":
    main()
