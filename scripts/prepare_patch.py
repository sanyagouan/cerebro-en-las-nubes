import json

with open("assistant.json", "r", encoding="utf-8") as f:
    assistant = json.load(f)

patch = {
    "firstMessage": "¡Hola! Soy Nube, la recepcionista de En Las Nubes Restobar en Logroño. ¿Quieres hacer una reserva o te ayudo con alguna pregunta?",
    "backgroundSound": "off",
    "transcriber": {
        "provider": "deepgram",
        "model": "nova-2",
        "language": "es"
    }
}

if "model" in assistant:
    patch["model"] = assistant["model"]
    for msg in patch["model"].get("messages", []):
        if msg.get("role") == "system":
             content = msg["content"]
             content = content.replace("Logrono", "Logroño")
             content = content.replace("Espana", "España")
             content = content.replace("espanol", "español")
             content = content.replace("informacion", "información")
             content = content.replace("dia", "día")
             content = content.replace("telefono", "teléfono")
             content = content.replace("direccion", "dirección")
             msg["content"] = content

with open("patch.json", "w", encoding="utf-8") as f:
    json.dump(patch, f, ensure_ascii=False, indent=2)
