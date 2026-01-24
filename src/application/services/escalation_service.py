"""
Servicio de Escalado a Humano - En Las Nubes Restobar
Determina cuándo una reserva debe ser gestionada por personal humano.
"""

from datetime import date
from typing import Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum

from src.application.services.holiday_service import get_holiday_service


class EscalationReason(str, Enum):
    GRUPO_GRANDE = "grupo_grande"
    ALTA_DEMANDA = "alta_demanda"
    EVENTO_PRIVADO = "evento_privado"
    SIN_DISPONIBILIDAD = "sin_disponibilidad"
    SOLICITUD_COMPLEJA = "solicitud_compleja"
    DUDA_CLIENTE = "duda_cliente"
    PETICION_EXPLICITA = "peticion_explicita"


@dataclass
class EscalationResult:
    """Resultado de la evaluación de escalado."""
    debe_escalar: bool
    motivos: List[EscalationReason]
    mensaje_cliente: str
    prioridad: int = 1  # 1=Alta, 2=Media, 3=Baja


class EscalationService:
    """
    Servicio que determina cuándo una reserva debe ser escalada
    a personal humano (maître, encargado, etc.)
    """
    
    # Umbrales
    MAX_PAX_AUTOMATICO = 10
    
    # Fechas de alta demanda conocidas (además de las del HolidayService)
    FECHAS_ALTA_DEMANDA_FIJAS = [
        # Añadir manualmente fechas especiales que no son festivos
        # (14, 2),  # San Valentín - ejemplo
    ]
    
    def __init__(self):
        self.holiday_service = get_holiday_service()
    
    def evaluar_escalado(
        self,
        pax: int,
        fecha: date,
        solicitudes: List[str] = None,
        sin_disponibilidad: bool = False,
        cliente_solicita_humano: bool = False
    ) -> EscalationResult:
        """
        Evalúa si una reserva debe ser escalada a humano.
        """
        solicitudes = solicitudes or []
        motivos = []
        mensajes = []
        prioridad = 3  # Baja por defecto
        
        # ========== 1. GRUPOS GRANDES ==========
        if pax > self.MAX_PAX_AUTOMATICO:
            motivos.append(EscalationReason.GRUPO_GRANDE)
            mensajes.append(f"Para grupos de más de {self.MAX_PAX_AUTOMATICO} personas necesitamos confirmar disponibilidad con nuestro equipo")
            prioridad = min(prioridad, 1)
        
        # ========== 2. FECHAS DE ALTA DEMANDA ==========
        if self.holiday_service.es_alta_demanda(fecha):
            motivos.append(EscalationReason.ALTA_DEMANDA)
            festivo = self.holiday_service.get_festivo(fecha)
            nombre = festivo.nombre if festivo else "fecha especial"
            mensajes.append(f"El {fecha.strftime('%d/%m')} es {nombre}, un día de alta demanda. Necesitamos verificar disponibilidad")
            prioridad = min(prioridad, 1)
        
        # Fechas fijas de alta demanda
        if (fecha.month, fecha.day) in [(m, d) for m, d in self.FECHAS_ALTA_DEMANDA_FIJAS]:
            motivos.append(EscalationReason.ALTA_DEMANDA)
        
        # ========== 3. EVENTOS PRIVADOS ==========
        if "evento_privado" in solicitudes or "celebracion" in solicitudes:
            motivos.append(EscalationReason.EVENTO_PRIVADO)
            mensajes.append("Para eventos privados o celebraciones especiales, le pasamos con nuestro equipo de reservas")
            prioridad = min(prioridad, 2)
        
        # ========== 4. SIN DISPONIBILIDAD ==========
        if sin_disponibilidad:
            motivos.append(EscalationReason.SIN_DISPONIBILIDAD)
            mensajes.append("En este momento no veo disponibilidad automática. Le paso con mi compañero para verificar opciones alternativas")
            prioridad = min(prioridad, 2)
        
        # ========== 5. SOLICITUDES COMPLEJAS ==========
        solicitudes_complejas = ["menu_personalizado", "alergia_multiple", "decoracion_especial"]
        if any(s in solicitudes for s in solicitudes_complejas):
            motivos.append(EscalationReason.SOLICITUD_COMPLEJA)
            mensajes.append("Para solicitudes especiales, le paso con nuestro equipo")
            prioridad = min(prioridad, 2)
        
        # ========== 6. PETICIÓN EXPLÍCITA ==========
        if cliente_solicita_humano:
            motivos.append(EscalationReason.PETICION_EXPLICITA)
            mensajes.append("Por supuesto, le paso con mi compañero ahora mismo")
            prioridad = min(prioridad, 1)
        
        # ========== RESULTADO ==========
        if motivos:
            mensaje = mensajes[0] if mensajes else "Le paso con nuestro equipo de reservas"
            return EscalationResult(
                debe_escalar=True,
                motivos=motivos,
                mensaje_cliente=mensaje,
                prioridad=prioridad
            )
        
        return EscalationResult(
            debe_escalar=False,
            motivos=[],
            mensaje_cliente="",
            prioridad=3
        )
    
    def get_mensaje_transferencia(
        self,
        motivo: EscalationReason
    ) -> str:
        """
        Genera el mensaje que el asistente debe decir antes de transferir.
        """
        mensajes = {
            EscalationReason.GRUPO_GRANDE: 
                "Para grupos grandes necesitamos verificar la disponibilidad de nuestro salón. Le paso con mi compañero que le atenderá encantado.",
            EscalationReason.ALTA_DEMANDA:
                "Esta fecha tiene mucha demanda. Le paso con nuestro equipo para confirmar disponibilidad y ofrecerle la mejor opción.",
            EscalationReason.EVENTO_PRIVADO:
                "Para eventos especiales tenemos opciones que pueden interesarle. Le paso con nuestro encargado.",
            EscalationReason.SIN_DISPONIBILIDAD:
                "Déjeme pasarle con mi compañero, él podrá ver opciones alternativas para su reserva.",
            EscalationReason.SOLICITUD_COMPLEJA:
                "Para atender su solicitud especial correctamente, le paso con nuestro equipo.",
            EscalationReason.DUDA_CLIENTE:
                "Entiendo que tiene algunas dudas. Le paso con mi compañero que podrá resolverlas mejor.",
            EscalationReason.PETICION_EXPLICITA:
                "Por supuesto, le paso con mi compañero ahora mismo. Un momento, por favor."
        }
        return mensajes.get(motivo, "Le paso con nuestro equipo. Un momento, por favor.")


# Singleton global
_escalation_service: Optional[EscalationService] = None


def get_escalation_service() -> EscalationService:
    """Devuelve la instancia singleton del servicio de escalado."""
    global _escalation_service
    if _escalation_service is None:
        _escalation_service = EscalationService()
    return _escalation_service
