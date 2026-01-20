# Cerebro En Las Nubes 🧠☁️

AI-powered booking and customer service system for **En Las Nubes Restobar** (Logroño).

## 🏗️ Architecture

Multi-agent AI system built with Python, FastAPI, and OpenAI/DeepSeek:

```
┌─────────────────┐     ┌─────────────────┐
│   VAPI (Voice)  │────▶│                 │
└─────────────────┘     │   Orchestrator  │
                        │                 │
┌─────────────────┐     │  ┌───────────┐  │     ┌─────────────┐
│ WhatsApp/Twilio │────▶│  │  Router   │  │────▶│  Airtable   │
└─────────────────┘     │  │ Agent     │  │     │  (Database) │
                        │  └───────────┘  │     └─────────────┘
                        │  ┌───────────┐  │
                        │  │  Logic    │  │
                        │  │ Agent     │  │
                        │  └───────────┘  │
                        │  ┌───────────┐  │
                        │  │  Human    │  │
                        │  │ Agent     │  │
                        │  └───────────┘  │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run locally
python -m uvicorn src.main:app --reload
```

### Docker Deployment

```bash
docker-compose up -d
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/vapi/webhook` | POST | VAPI voice calls |
| `/whatsapp/webhook` | POST | WhatsApp messages |

## 🤖 Agents

- **Router Agent** (`gpt-4o-mini`): Intent classification
- **Logic Agent** (`deepseek-chat`): Availability reasoning
- **Human Agent** (`gpt-4o`): Natural language generation

## 📁 Project Structure

```
src/
├── api/                 # FastAPI routers
│   ├── vapi_router.py
│   └── whatsapp_router.py
├── application/         # Business logic
│   ├── agents/          # AI Agents
│   ├── services/        # Team alerts, etc.
│   └── orchestrator.py
├── core/                # Domain layer
│   ├── entities/        # Pydantic models
│   ├── logic/           # Booking engine
│   └── ports/           # Interfaces
├── infrastructure/      # External services
│   └── repositories/    # Airtable adapter
└── main.py              # FastAPI app
```

## 🔧 Environment Variables

```env
# OpenAI
OPENAI_API_KEY=sk-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# VAPI
VAPI_API_KEY=...

# Airtable
AIRTABLE_API_KEY=pat...
AIRTABLE_BASE_ID=app...

# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=+...
```

## 📝 License

Private - En Las Nubes Restobar
