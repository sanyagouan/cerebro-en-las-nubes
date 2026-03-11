"""
Servicio de gestión de reservas.

Este servicio centraliza toda la lógica de negocio relacionada con reservas,
incluyendo creación, actualización, cancelación y confirmación multi-canal.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from loguru import logger

# Importaciones internas
from src.core.entities.reservation import (
    Reservation,
    ReservationState,
    TipoTelefono,
    TipoConfirmacion
)
from src.core.utils.phone_utils import detectar_tipo_telefono
from pyairtable import Api


class ReservationService:
    """
    Servicio para gestionar el ciclo de vida completo de las reservas.
    
    Responsabilidades:
    - Crear reservas con detección automática de tipo de teléfono
    - Actualizar estados de reservas con validación de transiciones
    - Gestionar confirmaciones multi-canal (WhatsApp/verbal)
    - Cancelar reservas con registro de motivos
    """
    
    def __init__(self):
        """Inicializa el servicio con conexión a Airtable."""
        self.base_id = os.getenv("AIRTABLE_BASE_ID", "appQ2ZXAR68cqDmJt")
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        
        if not self.api_key:
            logger.error("AIRTABLE_API_KEY no configurada")
            self.api = None
            return
        
        self.api = Api(self.api_key)
        self.reservas_table = self.api.table(self.base_id, "Reservas")
        logger.info("ReservationService inicializado correctamente")
    
    async def create_reservation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea una nueva reserva con detección automática de tipo de teléfono.
        
        Args:
            data: Diccionario con campos de la reserva:
                - nombre: str - Nombre del cliente
                - telefono: str - Teléfono en formato E.164 (+34XXXXXXXXX)
                - fecha: str - Fecha en formato YYYY-MM-DD
                - hora: str - Hora en formato ISO 8601
                - personas: int - Número de comensales
                - notas: str (opcional) - Peticiones especiales
        
        Returns:
            Dict con la reserva creada y metadatos:
                - success: bool
                - reservation_id: str
                - tipo_telefono: str (movil/fijo/desconocido)
                - requires_whatsapp_confirmation: bool
                - requires_verbal_confirmation: bool
                - message: str
        
        Raises:
            ValueError: Si faltan campos obligatorios
            Exception: Si falla la creación en Airtable
        """
        try:
            # Validar campos obligatorios
            required_fields = ["nombre", "telefono", "fecha", "hora", "personas"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Campo obligatorio faltante: {field}")
            
            telefono = data["telefono"]
            
            # Detectar tipo de teléfono (móvil/fijo/desconocido)
            tipo_telefono = detectar_tipo_telefono(telefono)
            logger.info(f"Teléfono {telefono} detectado como: {tipo_telefono}")
            
            # Determinar tipo de confirmación según el canal
            tipo_confirmacion = "pendiente"
            requiere_recordatorio = False
            
            if tipo_telefono == "movil":
                # Móviles: confirmación por WhatsApp
                tipo_confirmacion = "pendiente"  # Se confirmará vía WhatsApp
                requiere_recordatorio = False
            elif tipo_telefono == "fijo":
                # Fijos: confirmación verbal durante la llamada VAPI
                tipo_confirmacion = "pendiente"  # Se confirmará verbalmente
                requiere_recordatorio = True  # Necesitan recordatorio manual
            else:
                # Desconocido: por defecto esperamos confirmación
                tipo_confirmacion = "pendiente"
                requiere_recordatorio = True
            
            # Preparar datos para Airtable
            airtable_data = {
                "Nombre del Cliente": data["nombre"],
                "Teléfono": telefono,
                "Fecha de Reserva": data["fecha"],
                "Hora": data["hora"],
                "Cantidad de Personas": int(data["personas"]),
                "Notas": data.get("notas", ""),
                "Estado": "Pre-reserva",  # Estado inicial unificado
                "Tipo_Telefono": tipo_telefono,
                "Tipo_Confirmacion": tipo_confirmacion,
                "Requiere_Recordatorio": requiere_recordatorio,
                "Notas_Confirmacion": ""  # Se llenará al confirmar
            }
            
            # Crear registro en Airtable
            record = self.reservas_table.create(airtable_data)
            record_id = record["id"]
            
            logger.info(f"Reserva creada exitosamente: {record_id} para {telefono}")
            
            # Retornar respuesta diferenciada según tipo de teléfono
            response = {
                "success": True,
                "reservation_id": record_id,
                "tipo_telefono": tipo_telefono,
                "requires_whatsapp_confirmation": tipo_telefono == "movil",
                "requires_verbal_confirmation": tipo_telefono == "fijo",
            }
            
            if tipo_telefono == "movil":
                response["message"] = "Reserva creada. Se enviará WhatsApp de confirmación."
            elif tipo_telefono == "fijo":
                response["message"] = "Reserva creada. Pedir confirmación verbal ahora."
            else:
                response["message"] = "Reserva creada. Tipo de teléfono desconocido, verificar manualmente."
            
            return response
            
        except ValueError as e:
            logger.error(f"Error de validación al crear reserva: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error de validación: {e}"
            }
        except Exception as e:
            logger.error(f"Error al crear reserva en Airtable: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Error al crear reserva: {e}"
            }
    
    async def get_by_phone(self, telefono: str) -> Optional[Dict[str, Any]]:
        """
        Busca la reserva más reciente de un cliente por su teléfono.
        
        Args:
            telefono: Número de teléfono en formato E.164
        
        Returns:
            Dict con los datos de la reserva o None si no existe
        """
        try:
            # Buscar reservas con este teléfono, ordenadas por fecha de creación (más reciente primero)
            formula = f"{{Teléfono}} = '{telefono}'"
            records = self.reservas_table.all(formula=formula, sort=["-Creado"])
            
            if not records:
                logger.warning(f"No se encontró reserva para teléfono: {telefono}")
                return None
            
            # Retornar la más reciente
            record = records[0]
            logger.info(f"Reserva encontrada para {telefono}: {record['id']}")
            
            return {
                "id": record["id"],
                "fields": record["fields"]
            }
            
        except Exception as e:
            logger.error(f"Error al buscar reserva por teléfono {telefono}: {e}")
            return None
    
    async def update(
        self,
        reservation_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza una reserva existente con validación de transiciones de estado.
        
        Args:
            reservation_id: ID de Airtable de la reserva
            updates: Diccionario con campos a actualizar
        
        Returns:
            Dict con resultado de la actualización:
                - success: bool
                - message: str
                - reservation_id: str
        """
        try:
            # Si se actualiza el estado, validar la transición
            if "Estado" in updates:
                # Primero obtener el estado actual
                current_record = self.reservas_table.get(reservation_id)
                current_state = current_record["fields"].get("Estado", "Pre-reserva")
                new_state = updates["Estado"]
                
                # Validar transición usando el modelo Pydantic
                from src.core.entities.reservation import ReservationState
                
                try:
                    current_enum = ReservationState(current_state)
                    new_enum = ReservationState(new_state)
                    
                    # Validar transición (lógica simplificada, los estados finales no pueden cambiar)
                    final_states = [
                        ReservationState.COMPLETADA,
                        ReservationState.CANCELADA,
                        ReservationState.NO_SHOW
                    ]
                    
                    if current_enum in final_states:
                        logger.warning(
                            f"Intento de cambiar estado final {current_state} a {new_state}"
                        )
                        return {
                            "success": False,
                            "message": f"No se puede cambiar un estado final ({current_state})"
                        }
                    
                    logger.info(f"Transición de estado válida: {current_state} → {new_state}")
                    
                except ValueError as e:
                    logger.error(f"Estado inválido: {e}")
                    return {
                        "success": False,
                        "message": f"Estado inválido: {e}"
                    }
            
            # Realizar la actualización en Airtable
            updated_record = self.reservas_table.update(reservation_id, updates)
            
            logger.info(f"Reserva {reservation_id} actualizada exitosamente")
            
            return {
                "success": True,
                "message": "Reserva actualizada correctamente",
                "reservation_id": reservation_id,
                "fields": updated_record["fields"]
            }
            
        except Exception as e:
            logger.error(f"Error al actualizar reserva {reservation_id}: {e}")
            return {
                "success": False,
                "message": f"Error al actualizar: {e}"
            }
    
    async def cancel_by_phone(
        self,
        telefono: str,
        reason: str = "Cancelada por cliente"
    ) -> Dict[str, Any]:
        """
        Cancela la reserva más reciente de un cliente.
        
        Args:
            telefono: Número de teléfono del cliente
            reason: Motivo de la cancelación
        
        Returns:
            Dict con resultado de la cancelación
        """
        try:
            # Buscar la reserva
            reservation = await self.get_by_phone(telefono)
            
            if not reservation:
                return {
                    "success": False,
                    "message": f"No se encontró reserva activa para {telefono}"
                }
            
            reservation_id = reservation["id"]
            current_state = reservation["fields"].get("Estado", "Pre-reserva")
            
            # Verificar que no esté ya cancelada o completada
            if current_state in ["Cancelada", "Completada", "No Show"]:
                return {
                    "success": False,
                    "message": f"La reserva ya está en estado: {current_state}"
                }
            
            # Actualizar a estado Cancelada
            result = await self.update(
                reservation_id,
                {
                    "Estado": "Cancelada",
                    "Notas_Confirmacion": f"{reason}. Cancelada el {datetime.now().isoformat()}"
                }
            )
            
            if result["success"]:
                logger.info(f"Reserva {reservation_id} cancelada: {reason}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error al cancelar reserva de {telefono}: {e}")
            return {
                "success": False,
                "message": f"Error al cancelar: {e}"
            }
    
    async def confirm_verbal(
        self,
        telefono: str,
        confirmed: bool,
        notas: str = ""
    ) -> Dict[str, Any]:
        """
        Confirma o rechaza una reserva verbalmente (teléfonos fijos).
        
        Args:
            telefono: Número de teléfono del cliente
            confirmed: True si el cliente confirmó, False si no
            notas: Notas adicionales de la confirmación
        
        Returns:
            Dict con resultado de la confirmación
        """
        try:
            if not confirmed:
                # Cliente no confirmó - cancelar reserva
                return await self.cancel_by_phone(
                    telefono,
                    reason="Cliente no confirmó verbalmente"
                )
            
            # Cliente confirmó - actualizar estado
            reservation = await self.get_by_phone(telefono)
            
            if not reservation:
                return {
                    "success": False,
                    "message": f"No se encontró reserva para confirmar: {telefono}"
                }
            
            reservation_id = reservation["id"]
            timestamp = datetime.now().isoformat()
            
            result = await self.update(
                reservation_id,
                {
                    "Estado": "Confirmada",
                    "Tipo_Confirmacion": "verbal",
                    "Notas_Confirmacion": f"Confirmada verbalmente el {timestamp}. {notas}".strip()
                }
            )
            
            if result["success"]:
                logger.info(f"Reserva {reservation_id} confirmada verbalmente")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en confirmación verbal de {telefono}: {e}")
            return {
                "success": False,
                "message": f"Error en confirmación: {e}"
            }


# Instancia singleton del servicio
reservation_service = ReservationService()
