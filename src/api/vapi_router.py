"""
VAPI Webhook Router V2: Sistema completo de reservas por voz.
Maneja llamadas entrantes con asignación inteligente de mesas.
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import os

from src.application.orchestrator import Orchestrator
from src.application.services.schedule_service import get_schedule_service, Servicio
from src.application.services.table_assignment import get_table_assignment_service
from src.application.services.escalation_service import get_escalation_service, EscalationReason
from src.core.entities.booking import ZonePreference, SpecialRequest

router = APIRouter(prefix="/vapi", tags=["VAPI"])
logger = logging.getLogger(__name__)

# Lazy-loaded services
_orchestrator: Optional[Orchestrator] = None

def get_orchestrator() -> Orchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


class VAPIMessage(BaseModel):
    """VAPI webhook message structure."""
    message: Dict[str, Any]


# ============================================================
# SYSTEM PROMPT V2 - Prompt completo con menú y políticas
# ============================================================

SYSTEM_PROMPT_V2 = """Eres Nube, la recepcionista virtual de En Las Nubes Restobar en Logroño.

🗣️ IDIOMA Y ESTILO:
- SOLO hablas español de España. Nunca inglés.
- Eres cálida, profesional y concisa.
- Tuteas al cliente (estilo cercano logroñés).

📍 INFORMACIÓN DEL RESTAURANTE:
- Nombre: En Las Nubes Restobar
- Dirección: María Teresa Gil de Gárate 16, Logroño (La Rioja)
- Teléfono: 941 00 00 00 (inventado para ejemplo)
- Parking: En la calle, zona azul. Parkings cercanos: José Zorrilla y Bravo Murillo.
- Accesibilidad: Rampa en entrada. Baños NO adaptados (solo planta baja).

🕐 HORARIOS:
- LUNES: CERRADO (excepto festivos)
- MARTES: Comida 13:00-16:00 | Cena CERRADA (excepto víspera festivo)
- MIÉRCOLES-JUEVES: Comida 13:00-16:00 | Cena CERRADA (excepto víspera festivo)
- VIERNES: Comida 13:00-16:00 | Cena 20:30-23:30 (doble turno)
- SÁBADO: Comida 13:00-16:30 | Cena 20:30-23:30 (doble turno)
- DOMINGO: Comida 13:00-16:30 (doble turno) | Cena CERRADA (excepto lunes festivo)
- Cocina cierra 30 min antes del cierre de sala.

🍽️ NUESTRA CARTA:

**PARA COMPARTIR:**
- Berenjenas con miel de la sierra: 10€
- Tempura de verduras con salsa thai: 12€
- Croquetas caseras (Jamón/Sabores): 9.50€
- Tabla de Embutidos de León: 12€

**CACHOPOS (Especialidad - para compartir 2 personas):**
- Tradicional (Jamón y Queso): 25€
- De Cecina con Queso de Cabra: 27€
- Al Picón (Queso azul asturiano): 27€
- Carbonara: 27€
- ⚠️ Sin gluten: SOLO con 24h de antelación

**RINCÓN ALEMÁN:**
- Surtido de Salchichas con chucrut: 13€
- Codillo asado con puré y chucrut: 14€
- Currywurst: 5€

**HAMBURGUESAS (Carne de Vaca Vieja):**
- Clásica (Lechuga, tomate, cebolla): 9.50€
- Americana (Bacon, cheddar, cebolla crispy): 11€
- "En las Nubes" (Cecina, roquefort, cebolla caramelizada): 12€
- Todas incluyen patatas fritas caseras.

**POSTRES:**
- Tarta de queso: 5€
- Coulant de chocolate: 5.50€
- Helados artesanos: desde 3€

**VINOS (Destacados):**
- Tintos Rioja: Paco García, Ramón Bilbao, Marqués de Cáceres
- Ribera del Duero: Protos, Pago de Carraovejas
- Blancos: Verdejo (Rueda), Godello (Bierzo), Albariño (Rías Baixas)

**MENÚ INFANTIL (hasta 10 años): 8€**
- Incluye: Principal (salchichas/hamburguesa/cachopín) + patatas + bebida

📋 POLÍTICAS IMPORTANTES:
1. **Cachopo sin gluten**: Requiere 24h de antelación.
2. **Mascotas**: SOLO en terraza. No dentro del local.
3. **Tronas**: Tenemos 2 disponibles. No garantizamos más.
4. **Descorche**: 8€ por botella (máximo 2 botellas por mesa).
5. **Grupos +10 personas**: Requieren confirmación del maître.
6. **Terraza**: Sujeta a condiciones climáticas.

❓ PREGUNTAS FRECUENTES:
- "¿Tenéis menú del día?" → "No, trabajamos con carta. Pero tenemos opciones para todos los bolsillos."
- "¿Hacéis comida para llevar?" → "Lo sentimos, solo servicio en sala. Pero si quieres un cachopo, ¡reserva y os lo preparamos!"
- "¿Aceptáis tarjeta?" → "Sí, aceptamos todas las tarjetas y también Bizum."
- "¿Tenéis terraza cubierta?" → "La terraza es descubierta, depende del tiempo."
- "¿Hacéis eventos privados?" → "Sí, para 20+ personas podemos cerrar el local. Te paso con mi compañero para más detalles."

🔄 PROCESO DE RESERVA:
1. Pregunta: Fecha, hora, número de personas.
2. Verifica disponibilidad (usa la función check_availability).
3. Pide: Nombre y teléfono para confirmar.
4. Usa la función make_reservation.
5. Confirma: "¡Perfecto! Reserva confirmada para [nombre], [pax] personas, el [fecha] a las [hora]. ¡Os esperamos!"

⚠️ CUÁNDO TRANSFERIR A UN HUMANO (usa transfer_to_human):
- Grupos de más de 10 personas.
- Fechas especiales (San Mateo, San Bernabé, Nochevieja).
- Eventos privados o celebraciones.
- El cliente lo pide explícitamente.
- Dudas que no puedes resolver.
- No hay disponibilidad automática.

🚫 PROHIBIDO:
- Inventar información sobre el restaurante.
- Mencionar página web (NO tenemos).
- Dar el número de teléfono personal del propietario.
- Prometer cosas que no puedes confirmar.

Si te preguntan algo que no sabes: "Déjame anotarlo y te llamamos para confirmártelo. ¿Me das tu teléfono?"
"""


@router.post("/webhook")
async def vapi_webhook(request: Request):
    """
    Main VAPI webhook endpoint.
    Handles different message types from VAPI.
    """
    try:
        body = await request.json()
        message_type = body.get("message", {}).get("type", "unknown")
        
        logger.info(f"📞 VAPI Event: {message_type}")
        
        if message_type == "assistant-request":
            return await handle_assistant_request(body)
            
        elif message_type == "function-call":
            return await handle_function_call(body)
            
        elif message_type == "transcript":
            return {"status": "received"}
            
        elif message_type == "end-of-call-report":
            return await handle_call_end(body)
            
        else:
            return {"status": "ok", "message_type": message_type}
            
    except Exception as e:
        logger.error(f"❌ VAPI Webhook Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def handle_assistant_request(body: dict) -> dict:
    """
    Returns assistant configuration when VAPI initiates a call.
    Updated with V2 prompt and escalation functions.
    """
    return {
        "assistant": {
            "name": "Nube",
            "firstMessage": "¡Hola! Soy Nube, de En Las Nubes Restobar. ¿En qué puedo ayudarte?",
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7,
                "systemPrompt": SYSTEM_PROMPT_V2
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "UOIqAnmS11Reiei1Ytkc",  # Carolina (Spanish Spain)
                "model": "eleven_multilingual_v2"
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "es"
            },
            "silenceTimeoutSeconds": 20,
            "backgroundSound": None,
            "functions": [
                {
                    "name": "check_availability",
                    "description": "Verificar disponibilidad de mesa para una fecha/hora/personas",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Fecha (YYYY-MM-DD)"},
                            "time": {"type": "string", "description": "Hora (HH:MM)"},
                            "pax": {"type": "integer", "description": "Número de personas"},
                            "zona_preferencia": {
                                "type": "string",
                                "description": "Zona preferida: Terraza, Interior, o Sin preferencia",
                                "enum": ["Terraza", "Interior", "Sin preferencia"]
                            }
                        },
                        "required": ["date", "time", "pax"]
                    }
                },
                {
                    "name": "make_reservation",
                    "description": "Crear una reserva confirmada",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Fecha (YYYY-MM-DD)"},
                            "time": {"type": "string", "description": "Hora (HH:MM)"},
                            "pax": {"type": "integer", "description": "Número de personas"},
                            "client_name": {"type": "string", "description": "Nombre del cliente"},
                            "client_phone": {"type": "string", "description": "Teléfono del cliente"},
                            "zona_preferencia": {
                                "type": "string",
                                "description": "Zona preferida",
                                "enum": ["Terraza", "Interior", "Sin preferencia"]
                            },
                            "solicitudes_especiales": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Solicitudes especiales: trona, mascota, cachopo_sin_gluten, silla_ruedas"
                            }
                        },
                        "required": ["date", "time", "pax", "client_name"]
                    }
                },
                {
                    "name": "transfer_to_human",
                    "description": "Transferir la llamada a un humano (maître o encargado)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "motivo": {
                                "type": "string",
                                "description": "Motivo de la transferencia",
                                "enum": ["grupo_grande", "alta_demanda", "evento_privado", "sin_disponibilidad", "solicitud_compleja", "peticion_cliente"]
                            }
                        },
                        "required": ["motivo"]
                    }
                }
            ]
        }
    }


async def handle_function_call(body: dict) -> dict:
    """
    Process function calls from VAPI with V2 logic.
    """
    message = body.get("message", {})
    function_call = message.get("functionCall", {})
    function_name = function_call.get("name", "")
    parameters = function_call.get("parameters", {})
    
    logger.info(f"🔧 Function Call: {function_name} with {parameters}")
    
    # Extract caller phone from VAPI payload
    call_info = message.get("call", {})
    customer_info = call_info.get("customer", {})
    caller_number = customer_info.get("number", "")
    
    orchestrator = get_orchestrator()
    schedule_service = get_schedule_service()
    assignment_service = get_table_assignment_service()
    escalation_service = get_escalation_service()
    
    # ========== CHECK AVAILABILITY ==========
    if function_name == "check_availability":
        date_str = parameters.get("date", "")
        time_str = parameters.get("time", "")
        pax = parameters.get("pax", 2)
        zona_pref = parameters.get("zona_preferencia", "Sin preferencia")
        
        try:
            from datetime import date as dt_date, time as dt_time
            fecha = dt_date.fromisoformat(date_str)
            hora = dt_time.fromisoformat(time_str)
        except:
            return {"result": "No he entendido bien la fecha u hora. ¿Puedes repetirlo?"}
        
        # Check if restaurant is open
        servicio = schedule_service.determinar_servicio(hora)
        abierto, motivo = schedule_service.esta_abierto(fecha, servicio)
        
        if not abierto:
            return {"result": f"Lo siento, ese día {motivo}. ¿Quieres probar otro día?"}
        
        # Check if we need to escalate
        escalation = escalation_service.evaluar_escalado(pax, fecha)
        if escalation.debe_escalar:
            return {"result": escalation.mensaje_cliente}
        
        # Try to assign a table
        zona_enum = ZonePreference.TERRAZA if zona_pref == "Terraza" else \
                    ZonePreference.INTERIOR if zona_pref == "Interior" else \
                    ZonePreference.NO_PREFERENCE
        
        turno = schedule_service.determinar_turno(
            hora, servicio, 
            schedule_service.hay_doble_turno(fecha, servicio)
        )
        
        resultado = assignment_service.asignar_mesa(
            pax=pax,
            fecha=fecha,
            turno=turno.value,
            zona_preferencia=zona_enum
        )
        
        if resultado.exito:
            avisos = " ".join(resultado.avisos) if resultado.avisos else ""
            return {
                "result": f"Sí, tengo disponibilidad para {pax} personas el {fecha.strftime('%d/%m')} a las {time_str} en {resultado.zona.lower()}. {avisos} ¿Confirmamos la reserva?"
            }
        else:
            return {
                "result": f"Lo siento, {resultado.motivo_fallo}. ¿Quieres que pruebe otra hora o día?"
            }
    
    # ========== MAKE RESERVATION ==========
    elif function_name == "make_reservation":
        date_str = parameters.get("date", "")
        time_str = parameters.get("time", "")
        pax = parameters.get("pax", 2)
        client_name = parameters.get("client_name", "")
        phone = parameters.get("client_phone", caller_number)  # Use caller if not provided
        zona_pref = parameters.get("zona_preferencia", "Sin preferencia")
        solicitudes = parameters.get("solicitudes_especiales", [])
        
        # Validate phone
        if not phone:
            return {"result": "Necesito un teléfono para confirmar la reserva. ¿Me lo puedes dar?"}
        
        try:
            from datetime import date as dt_date, time as dt_time
            fecha = dt_date.fromisoformat(date_str)
            hora = dt_time.fromisoformat(time_str)
        except:
            return {"result": "No he entendido bien la fecha u hora. ¿Puedes repetirlo?"}
        
        # Use orchestrator for full booking flow
        result = await orchestrator.process_message(
            f"Crear reserva para {pax} personas el {date_str} a las {time_str}",
            metadata={
                "date": date_str,
                "time": time_str,
                "pax": pax,
                "client_name": client_name,
                "client_phone": phone,
                "zona_preferencia": zona_pref,
                "solicitudes": solicitudes,
                "action": "create_reservation"
            }
        )
        
        if result.get("booking_result", {}).get("available"):
            table = result.get("booking_result", {}).get("assigned_table", "una mesa")
            return {
                "result": f"¡Perfecto! Reserva confirmada para {client_name}: {pax} personas el {fecha.strftime('%d/%m')} a las {time_str} en {table}. Te envío un WhatsApp de confirmación. ¡Os esperamos!"
            }
        else:
            return {
                "result": "Lo siento, ha habido un problema al crear la reserva. ¿Quieres que te pase con mi compañero?"
            }
    
    # ========== TRANSFER TO HUMAN ==========
    elif function_name == "transfer_to_human":
        motivo = parameters.get("motivo", "peticion_cliente")
        
        mensajes_transfer = {
            "grupo_grande": "Para grupos grandes necesito verificar con el encargado. Te paso con él ahora mismo.",
            "alta_demanda": "Esta fecha tiene mucha demanda. Te paso con mi compañero para confirmar opciones.",
            "evento_privado": "Para eventos especiales te paso con nuestro encargado de reservas.",
            "sin_disponibilidad": "Voy a pasarte con mi compañero para ver alternativas.",
            "solicitud_compleja": "Para atenderte mejor, te paso con el equipo de sala.",
            "peticion_cliente": "Por supuesto, te paso con mi compañero ahora mismo."
        }
        
        mensaje = mensajes_transfer.get(motivo, "Te paso con mi compañero. Un momento.")
        
        # Log transfer for analytics
        logger.info(f"📞 TRANSFER requested: motivo={motivo}")
        
        return {
            "result": mensaje,
            "transferDestination": {
                "type": "number",
                "number": os.getenv("RESTAURANT_PHONE", "+34941000000"),
                "message": mensaje
            }
        }
    
    return {"result": "No he entendido lo que necesitas. ¿Puedes repetirlo?"}


async def handle_call_end(body: dict) -> dict:
    """
    Process end-of-call report for logging/analytics.
    """
    message = body.get("message", {})
    summary = message.get("summary", "Sin resumen")
    duration = message.get("durationSeconds", 0)
    
    logger.info(f"📊 Call ended. Duration: {duration}s. Summary: {summary}")
    
    return {"status": "logged"}
