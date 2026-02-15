"""
Servicio de Tareas Programadas (Scheduled Jobs)
Ejecuta tareas periódicas en background:
- Expirar notificaciones de waitlist antiguas (>15 minutos)
- Recordatorios de reserva 24h antes (WhatsApp)
- Futuro: Limpieza de caché Redis
"""
import asyncio
import logging
from datetime import datetime, timedelta, date
from typing import Optional

from src.application.services.waitlist_service import WaitlistService
from src.core.entities.waitlist import WaitlistStatus
from src.infrastructure.repositories.booking_repo import AirtableBookingRepository
from src.infrastructure.external.twilio_service import TwilioService
from src.infrastructure.templates.whatsapp_messages import recordatorio_24h_template

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Servicio para ejecutar tareas programadas en background.
    Usa asyncio para no bloquear el servidor FastAPI.
    """

    def __init__(self, interval_seconds: int = 60):
        """
        Args:
            interval_seconds: Intervalo entre ejecuciones (default: 60s = 1 minuto)
        """
        self.interval_seconds = interval_seconds
        self.waitlist_service = WaitlistService()
        self.booking_repository = AirtableBookingRepository()
        self.twilio_service = TwilioService()
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Inicia el scheduler en background."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"Scheduler started (interval: {self.interval_seconds}s)")

    async def stop(self):
        """Detiene el scheduler gracefully."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")

    async def _run_loop(self):
        """Loop principal que ejecuta las tareas periódicamente."""
        while self._running:
            try:
                await self._execute_jobs()
            except Exception as e:
                logger.error(f"Error executing scheduled jobs: {e}", exc_info=True)

            # Esperar hasta el próximo ciclo
            await asyncio.sleep(self.interval_seconds)

    async def _execute_jobs(self):
        """Ejecuta todas las tareas programadas."""
        # Job 1: Expirar notificaciones antiguas de waitlist
        await self._expire_old_notifications()

        # Job 2: Enviar recordatorios WhatsApp 24h antes
        await self._send_24h_reminders_whatsapp()

        # Futuro: Agregar más jobs aquí
        # await self._cleanup_redis_cache()

    async def _expire_old_notifications(self):
        """
        Expira notificaciones de waitlist que tienen >15 minutos sin confirmación.
        Cambia estado de NOTIFIED → EXPIRED.
        """
        try:
            # Obtener todas las entradas notificadas
            notified_entries = await self.waitlist_service.waitlist_repository.list_by_status(
                status=WaitlistStatus.NOTIFIED,
                fecha=None  # Buscar en todas las fechas
            )

            if not notified_entries:
                return  # No hay nada que expirar

            now = datetime.now()
            expiration_threshold = timedelta(minutes=15)
            expired_count = 0

            for entry in notified_entries:
                if not entry.notified_at:
                    continue

                # Calcular tiempo transcurrido desde notificación
                time_since_notification = now - entry.notified_at

                if time_since_notification > expiration_threshold:
                    # EXPIRAR: cambiar estado a EXPIRED
                    try:
                        await self.waitlist_service.waitlist_repository.update(
                            entry_id=entry.airtable_id,
                            estado=WaitlistStatus.EXPIRED
                        )
                        expired_count += 1
                        logger.info(
                            f"Expired waitlist entry {entry.airtable_id} "
                            f"({entry.nombre_cliente}) - notified {time_since_notification.total_seconds() / 60:.1f} min ago"
                        )

                        # Opcional: Notificar al próximo en la fila
                        # await self.waitlist_service.notify_next_in_queue(
                        #     fecha=entry.fecha,
                        #     hora=entry.hora,
                        #     pax=entry.num_personas
                        # )

                    except Exception as e:
                        logger.error(
                            f"Error expiring waitlist entry {entry.airtable_id}: {e}",
                            exc_info=True
                        )

            if expired_count > 0:
                logger.info(f"Expired {expired_count} waitlist notification(s)")

        except Exception as e:
            logger.error(f"Error in _expire_old_notifications: {e}", exc_info=True)

    async def _send_24h_reminders_whatsapp(self):
        """
        Envía recordatorios WhatsApp 24 horas antes de cada reserva.

        Proceso:
        1. Obtiene reservas para mañana (fecha actual + 1 día)
        2. Filtra las que NO han recibido recordatorio
        3. Envía WhatsApp usando template recordatorio_24h_template()
        4. Marca como enviado en Airtable
        """
        try:
            # Calcular fecha de mañana
            tomorrow = date.today() + timedelta(days=1)

            # Obtener todas las reservas de mañana (no canceladas)
            bookings = self.booking_repository.list_by_date(fecha=tomorrow)

            if not bookings:
                logger.debug(f"No hay reservas para {tomorrow.strftime('%Y-%m-%d')}")
                return

            # Filtrar solo las que NO han recibido recordatorio
            pending_reminders = [
                booking for booking in bookings
                if not booking.recordatorio_enviado
            ]

            if not pending_reminders:
                logger.debug(f"Todas las reservas de {tomorrow} ya tienen recordatorio enviado")
                return

            sent_count = 0
            failed_count = 0

            for booking in pending_reminders:
                try:
                    # Generar mensaje usando template
                    mensaje = recordatorio_24h_template(
                        nombre_cliente=booking.nombre,
                        fecha=booking.fecha,
                        hora=booking.hora,
                        num_personas=booking.pax,
                        mesa_asignada=booking.mesa_asignada  # Puede ser None
                    )

                    # Enviar WhatsApp via Twilio
                    success = self.twilio_service.send_whatsapp(
                        to=booking.telefono,
                        message=mensaje
                    )

                    if success:
                        # Marcar como enviado en Airtable
                        update_success = self.booking_repository.update_booking_reminder_sent(
                            booking_id=booking.id
                        )

                        if update_success:
                            sent_count += 1
                            logger.info(
                                f"✅ Recordatorio enviado: {booking.nombre} "
                                f"({booking.telefono}) para {booking.fecha} {booking.hora}"
                            )
                        else:
                            failed_count += 1
                            logger.warning(
                                f"⚠️ WhatsApp enviado pero no se pudo marcar en DB: {booking.id}"
                            )
                    else:
                        failed_count += 1
                        logger.error(
                            f"❌ Fallo enviando WhatsApp a {booking.telefono} "
                            f"(reserva: {booking.id})"
                        )

                except Exception as e:
                    failed_count += 1
                    logger.error(
                        f"❌ Error enviando recordatorio para booking {booking.id}: {e}",
                        exc_info=True
                    )

            # Resumen final
            if sent_count > 0 or failed_count > 0:
                logger.info(
                    f"📊 Recordatorios 24h: {sent_count} enviados, "
                    f"{failed_count} fallidos (total: {len(pending_reminders)} pendientes)"
                )

        except Exception as e:
            logger.error(f"Error in _send_24h_reminders_whatsapp: {e}", exc_info=True)


# Singleton global
_scheduler: Optional[SchedulerService] = None


def get_scheduler() -> SchedulerService:
    """Devuelve la instancia singleton del scheduler."""
    global _scheduler
    if _scheduler is None:
        _scheduler = SchedulerService(interval_seconds=60)  # Revisar cada minuto
    return _scheduler
