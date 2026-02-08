import requests
import os
import json

# Configuration
VAPI_API_KEY = "c1b0d8be-239c-4dc5-b07c-0cee8dcfba94"
ASSISTANT_ID = "9a1f2df2-1c2d-4061-b11c-bdde7568c85d" # Nube V3
PHONE_ID_1 = "f12ce288-000f-4016-9553-f1798c5f2d11"
PHONE_ID_2 = "ac351bb2-6b49-483e-a48a-c35c1502542d"
SERVER_URL = "https://ykkksgc84sw80g8s8wg0ws40.app.generaia.site/vapi/assistant"

headers = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json"
}

def update_assistant():
    url = f"https://api.vapi.ai/assistant/{ASSISTANT_ID}"
    payload = {
        "serverUrl": SERVER_URL
    }
    print(f"Updating Assistant {ASSISTANT_ID} with Server URL: {SERVER_URL}")
    try:
        resp = requests.patch(url, json=payload, headers=headers)
        if resp.status_code == 200:
            print("Assistant Updated Successfully!")
            print(resp.json())
        else:
            print(f"Failed to update assistant: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error updating assistant: {e}")

def link_assistant_to_phone(phone_id):
    url = f"https://api.vapi.ai/phone-number/{phone_id}"
    payload = {
        "assistantId": ASSISTANT_ID
    }
    print(f"Linking Assistant to Phone {phone_id}...")
    try:
        resp = requests.patch(url, json=payload, headers=headers)
        if resp.status_code == 200:
            print(f"Phone {phone_id} updated successfully!")
        else:
             print(f"Failed to update phone {phone_id}: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Error updating phone: {e}")

if __name__ == "__main__":
    update_assistant()
    # Link to both numbers just in case
    link_assistant_to_phone(PHONE_ID_1)
    link_assistant_to_phone(PHONE_ID_2)
