import sys
import os
import time

sys.path.append(r"C:\Users\yago\AppData\Roaming\Python\Python313\site-packages")
try:
    from notebooklm_mcp.api_client import NotebookLMClient
    from notebooklm_mcp.auth import load_cached_tokens
except ImportError: sys.exit(1)

NB6_ID = "0c89210d-8d36-424f-b98d-c7d717f74601"
BASE_DIR = r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY"

FILES = [
    ("src/application/agents/base_agent.py", "base_agent.py"),
    ("src/application/agents/human_agent.py", "human_agent.py"),
    ("src/application/agents/logic_agent.py", "logic_agent.py"),
    ("src/application/agents/router_agent.py", "router_agent.py"),
    ("src/application/orchestrator.py", "orchestrator.py"),
    ("inject_vapi_prompt.py", "inject_vapi_prompt.py"),
    ("tests/mocks/vapi.mock.js", "vapi.mock.js"),
]

def main():
    tokens = load_cached_tokens()
    if not tokens: return
    client = NotebookLMClient(cookies=tokens.cookies, csrf_token=tokens.csrf_token, session_id=tokens.session_id)
    print(f"Uploading files to Notebook 6 ({NB6_ID})...")
    for rel, title in FILES:
        path = os.path.join(BASE_DIR, rel)
        if not os.path.exists(path): continue
        with open(path, "r", encoding="utf-8") as f:
            client.add_text_source(NB6_ID, f.read(), title)
            print(f"  Uploaded {title}")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
