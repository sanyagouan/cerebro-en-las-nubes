import sys
import os
import time

# Add site-packages to path
sys.path.append(r"C:\Users\yago\AppData\Roaming\Python\Python313\site-packages")

try:
    from notebooklm_mcp.api_client import NotebookLMClient
    from notebooklm_mcp.auth import load_cached_tokens
except ImportError:
    print("Error: Could not import notebooklm_mcp. Check sys.path.")
    sys.exit(1)

# Notebook IDs
NB1_ID = "16f76e16-6a7d-4390-a8c1-8f408ae496ee"

# Files to upload to NB1
FILES = [
    (r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY\README.md", "README.md"),
    (r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY\src\main.py", "src/main.py"),
    (r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY\docker-compose.yml", "docker-compose.yml"),
    (r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY\DEPLOYMENT.md", "DEPLOYMENT.md"),
    (r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY\API.md", "API.md"),
    (r"C:\Users\yago\Desktop\COPIA ASISTENTE VOZ EN LAS NUBES-ANTIGRAVITY\.env.example", ".env.example"),
]

def main():
    print("Loading auth tokens...")
    tokens = load_cached_tokens()
    if not tokens:
        print("Error: No authentication tokens found. Please run notebooklm-mcp-auth.")
        return

    print("Initializing client...")
    client = NotebookLMClient(cookies=tokens.cookies, csrf_token=tokens.csrf_token, session_id=tokens.session_id)
    
    print(f"Uploading {len(FILES)} files to Notebook 1 ({NB1_ID})...")
    
    for file_path, title in FILES:
        if not os.path.exists(file_path):
            print(f"Skipping missing file: {file_path}")
            continue
            
        print(f"Uploading {title}...")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Using add_text_source
            result = client.add_text_source(NB1_ID, content, title)
            if result:
                print(f"  Success! Source ID: {result.get('id')}")
            else:
                print(f"  Failed: No result returned.")
            
            # Sleep slightly to avoid rate limits
            time.sleep(2)
            
        except Exception as e:
            print(f"  Error uploading {title}: {e}")

if __name__ == "__main__":
    main()
