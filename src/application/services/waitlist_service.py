"""
Servicio de lógica de negocio para Waitlist.
Gestiona la cola de espera y notificaciones automáticas.
"""

from datetime import datetime, date, time
from typing import Optional, List
import logging

from src.core.entities.waitlist import WaitlistEntry, WaitlistStatus
from src.infrastructure.repositories.waitlist_repository import waitlist_repository
from src.infrastructure.external.twilio_service import TwilioService
from src.infrastructure.templates.content_sids import MESA_DISPONIBLE_NUBES_SID

logger = logging.getLogger(__name__)


class WaitlistService:
    """
    Servicio de Waitlist con lógica de negocio.
    
    Responsabilidades:
    - Añadir clientes a la lista de espera
    - Notificar cuando hay mesa disponible
    - Gestionar expiración de notificaciones
    - Confirmar reservas desde waitlist
    """
    
    def __init__(
        self,
        waitlist_repo=None,
        twilio_service: Optional[TwilioService] = None
    ):
        self.waitlist_repo = waitlist_repo or waitlist_repository
        self.twilio_service = twilio_service or TwilioService()
    
    async def add_to_waitlist(
        self,
        nombre: str,
        telefono: str,
        fecha: date,
        hora: time,
        pax: int,
        zona_preferida: Optional[str] = None,
        notas: Optional[str] = None,
        origen: str = "VAPI_VOICE"
    ) -> WaitlistEntry:
        """
        Añade un cliente a la lista de espera.
        
        Returns:
            WaitlistEntry creada con posición asignada
        """
        try:
            # Calcular posición (último + 1)
            waiting_entries = await self.waitlist_repo.list_by_status(
                WaitlistStatus.WAITING,
                fecha=fecha
            )
            
            nueva_posicion = len(waiting_entries) + 1
            
            # Crear entrada
            entry = WaitlistEntry(
                nombre_cliente=nombre,
                telefono_cliente=telefono,
                fecha=fecha,
                hora=hora,
                num_personas=pax,
                zona_preferida=zona_preferida,
                estado=WaitlistStatus.WAITING,
                posicion=nueva_posicion,
                notas=notas,
                origen=origen
            )
            
            # Guardar en Airtable
            created_entry = await self.waitlist_repo.create(entry)
            
            logger.info(
                f"Cliente añadido a waitlist: {nombre} (posición {nueva_posicion}) "
                f"para {fecha} {hora} - {pax} pax"
            )
            
            return created_entry
            
        except Exception as e:
            logger.error(f"Error añadiendo a waitlist: {e}")
            raise
    
    async def notify_availability(
        self,
        fecha: date,
        hora: time,
        pax: int
    ) -> Optional[WaitlistEntry]:
        """
        Notifica al próximo cliente en waitlist que hay mesa disponible.
        
        Args:
            fecha: Fecha de la reserva
            hora: Hora de la reserva
            pax: Capacidad disponible
        
        Returns:
            WaitlistEntry notificada, o None si no hay nadie esperando
        """
        try:
            # Buscar próximo cliente waiting que pueda usar esta mesa
            entry = await self.waitlist_repo.get_next_waiting(fecha, hora, pax)
            
            if not entry:
                logger.info("No hay entradas waiting compatibles para notificar")
                return None
            
            # Enviar WhatsApp usando plantilla aprobada (Content API)
            fecha_str = fecha.strftime("%d/%m/%Y")
            hora_str = hora.strftime("%H:%M")
            
            # Variables para la plantilla mesa_disponible_nubes
            # {{1}} = nombre_cliente, {{2}} = num_personas, {{3}} = fecha, {{4}} = hora
            template_variables = {
                "1": entry.nombre_cliente,
                "2": str(entry.num_personas),
                "3": fecha_str,
                "4": hora_str
            }
            
            whatsapp_sid = self.twilio_service.send_whatsapp_template(
                to_number=entry.telefono_cliente,
                template_sid=MESA_DISPONIBLE_NUBES_SID,
                variables=template_variables
            )
            
            if not whatsapp_sid:
                logger.error(f"Falló envío de WhatsApp a {entry.telefono_cliente}")
                return None
            
            # Actualizar estado a NOTIFIED
            entry.marcar_como_notificado(whatsapp_sid)
            
            await self.waitlist_repo.update(
                entry_id=entry.airtable_id,
                updates={
                    "estado": WaitlistStatus.NOTIFIED,
                    "notified_at": entry.notified_at,
                    "notificacion_sid": whatsapp_sid
                }
            )
            
            logger.info(
                f"Cliente notificado de disponibilidad: {entry.nombre_cliente} "
                f"(WhatsApp SID: {whatsapp_sid})"
            )
            
            return entry
            
        except Exception as e:
            logger.error(f"Error notificando disponibilidad: {e}")
            return None
    
    def _build_availability_message(
        self,
        entry: WaitlistEntry,
        fecha: date,
        hora: time
    ) -> str:
        """Construye el mensaje WhatsApp de disponibilidad."""
        fecha_str = fecha.strftime("%d/%m/%Y")
        hora_str = hora.strftime("%H:%M")
        
        mensaje = f"""🎉 ¡Mesa Disponible! - En Las Nubes

Hola {entry.nombre_cliente}, tenemos una mesa disponible para {entry.num_personas} personas el {fecha_str} a las {hora_str}.

¿La quieres? Responde:
• SÍ para confirmar
• NO si ya no la necesitas

⏰ Reserva disponible por 15 minutos.

📍 C/ Mª Teresa Gil de Gárate 16, Logroño
☎️ 941 57 84 51

- En Las Nubes Resto Bar ☁️"""
        
        return mensaje
    
    async def confirm_from_waitlist(self, entry_id: str) -> bool:
        """
        Marca una entrada como confirmada.
        El sistema debe crear la reserva real después de esto.
        
        Returns:
            True si se confirmó correctamente
        """
        try:
            entry = await self.waitlist_repo.get_by_id(entry_id)
            
            if not entry:
                logger.error(f"No se encontró waitlist entry: {entry_id}")
                return False
            
            if entry.estado != WaitlistStatus.NOTIFIED:
                logger.warning(
                    f"No se puede confirmar entry {entry_id}: estado es {entry.estado}"
                )
                return False
            
            # Marcar como confirmada
            entry.marcar_como_confirmada()
            
            await self.waitlist_repo.update(
                entry_id=entry_id,
                updates={
                    "estado": WaitlistStatus.CONFIRMED,
                    "confirmed_at": entry.confirmed_at
                }
            )
            
            logger.info(f"Waitlist entry confirmada: {entry_id} - {entry.nombre_cliente}")
            return True
            
        except Exception as e:
            logger.error(f"Error confirmando waitlist entry: {e}")
            return False
    
    async def cancel_from_waitlist(self, entry_id: str) -> bool:
        """
        Cancela una entrada de la waitlist (cliente rechazó o ya no necesita).
        
        Returns:
            True si se canceló correctamente
        """
        try:
            entry = await self.waitlist_repo.get_by_id(entry_id)
            
            if not entry:
                logger.error(f"No se encontró waitlist entry: {entry_id}")
                return False
            
            # Marcar como cancelada
            entry.marcar_como_cancelada()
            
            await self.waitlist_repo.update(
                entry_id=entry_id,
                updates={
                    "estado": WaitlistStatus.CANCELLED,
                    "cancelled_at": entry.cancelled_at
                }
            )
            
            logger.info(f"Waitlist entry cancelada: {entry_id} - {entry.nombre_cliente}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelando waitlist entry: {e}")
            return False
    
    async def check_and_expire_old_notifications(self) -> int:
        """
        Revisa todas las entradas NOTIFIED y expira las que pasaron 15 minutos.
        
        Returns:
            Número de entradas expiradas
        """
        try:
            notified_entries = await self.waitlist_repo.list_by_status(
                WaitlistStatus.NOTIFIED
            )
            
            expired_count = 0
            
            for entry in notified_entries:
                if entry.ha_expirado():
                    # Marcar como expirada
                    entry.marcar_como_expirada()
                    
                    await self.waitlist_repo.update(
                        entry_id=entry.airtable_id,
                        updates={
                            "estado": WaitlistStatus.EXPIRED,
                            "expired_at": entry.expired_at
                        }
                    )
                    
                    logger.info(f"Waitlist entry expirada: {entry.airtable_id}")
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Total de entradas expiradas: {expired_count}")
            
            return expired_count
            
        except Exception as e:
            logger.error(f"Error revisando expiraciones: {e}")
            return 0
    
    async def get_waitlist_position(
        self,
        telefono: str,
        fecha: date
    ) -> Optional[tuple[int, int]]:
        """
        Obtiene la posición de un cliente en la waitlist.
        
        Args:
            telefono: Teléfono del cliente
            fecha: Fecha de la reserva
        
        Returns:
            Tupla (posición, total) o None si no está en waitlist
        """
        try:
            waiting_entries = await self.waitlist_repo.list_by_status(
                WaitlistStatus.WAITING,
                fecha=fecha
            )
            
            for entry in waiting_entries:
                if entry.telefono_cliente == telefono:
                    return (entry.posicion, len(waiting_entries))
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo posición en waitlist: {e}")
            return None


# Instancia global del servicio
waitlist_service = WaitlistService()
