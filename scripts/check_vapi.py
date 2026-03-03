import os
import requests
import json

api_key = "c5eefe50-cd80-41ac-9d64-fb7cccc2d5f6"
url = "https://api.vapi.ai/assistant"

headers = {
    "Authorization": f"Bearer {api_key}"
}

try:
    response = requests.get(url, headers=headers)
    assistants = response.json()
    print(json.dumps(assistants, indent=2))
except Exception as e:
    print(f"Error: {e}")
