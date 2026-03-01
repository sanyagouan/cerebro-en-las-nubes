"""
Servicio de Horarios - En Las Nubes Restobar
Gestiona horarios de apertura, turnos y reglas de disponibilidad.
"""

from datetime import date, time, datetime, timedelta
from typing import Tuple, List, Optional, Literal
from dataclasses import dataclass
from enum import Enum

from src.application.services.holiday_service import get_holiday_service


class Servicio(str, Enum):
    COMIDA = "Comida"
    CENA = "Cena"


class Turno(str, Enum):
    T1 = "T1"  # Primer turno
    T2 = "T2"  # Segundo turno


@dataclass
class HorarioServicio:
    """Representa un servicio con sus horarios."""
    servicio: Servicio
    hora_apertura: time
    hora_ultimo_turno: time  # Última hora para reservar
    hora_cierre_cocina: time
    hora_cierre_sala: time
    tiene_doble_turno: bool = False


@dataclass
class InfoTurno:
    """Información completa de un turno disponible."""
    turno: Turno
    hora_inicio: time
    hora_fin: time
    es_ultimo: bool = False


class ScheduleService:
    """
    Servicio de gestión de horarios del restaurante.
    Implementa todas las reglas de apertura, cierre y turnos.
    """
    
    # Horarios base
    HORARIOS_COMIDA = HorarioServicio(
        servicio=Servicio.COMIDA,
        hora_apertura=time(13, 0),
        hora_ultimo_turno=time(15, 30),
        hora_cierre_cocina=time(16, 0),
        hora_cierre_sala=time(17, 0),
        tiene_doble_turno=False  # Se activa en días especiales
    )
    
    HORARIOS_CENA = HorarioServicio(
        servicio=Servicio.CENA,
        hora_apertura=time(20, 30),
        hora_ultimo_turno=time(22, 30),
        hora_cierre_cocina=time(23, 00),
        hora_cierre_sala=time(23, 30),
        tiene_doble_turno=False  # Se activa en días especiales
    )
    
    # Horarios con doble turno (viernes noche, sábado, domingo comida)
    HORARIOS_COMIDA_DOBLE = HorarioServicio(
        servicio=Servicio.COMIDA,
        hora_apertura=time(13, 0),
        hora_ultimo_turno=time(15, 30),
        hora_cierre_cocina=time(16, 30),
        hora_cierre_sala=time(17, 30),
        tiene_doble_turno=True
    )
    
    HORARIOS_CENA_DOBLE = HorarioServicio(
        servicio=Servicio.CENA,
        hora_apertura=time(20, 30),
        hora_ultimo_turno=time(23, 00),
        hora_cierre_cocina=time(23, 30),
        hora_cierre_sala=time(00, 30),  # Del día siguiente
        tiene_doble_turno=True
    )
    
    def __init__(self):
        self.holiday_service = get_holiday_service()
    
    # ========== REGLAS DE APERTURA ==========
    
    def esta_abierto(self, fecha: date, servicio: Servicio) -> Tuple[bool, str]:
        """
        Verifica si el restaurante está abierto para un servicio en una fecha.
        Retorna (está_abierto, motivo).
        """
        dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
        
        # ========== LUNES: CERRADO (excepto festivo) ==========
        if dia_semana == 0:  # Lunes
            if not self.holiday_service.es_festivo(fecha):
                return False, "Lunes cerrado"
            # Si es festivo, abrimos
        
        # ========== MARTES-MIÉRCOLES NOCHE: CERRADO (excepto víspera festivo) ==========
        if dia_semana in [1, 2] and servicio == Servicio.CENA:  # M-X
            if not self.holiday_service.es_vispera_festivo(fecha):
                return False, "Entre semana no hay cenas (solo jueves, viernes y sábado)"
        
        # ========== DOMINGO NOCHE: CERRADO (excepto lunes festivo) ==========
        if dia_semana == 6 and servicio == Servicio.CENA:  # Domingo
            lunes = fecha + timedelta(days=1)
            if not self.holiday_service.es_festivo(lunes):
                return False, "Domingo noche cerrado"
        
        return True, "Abierto"
    
    def hay_doble_turno(self, fecha: date, servicio: Servicio) -> bool:
        """
        Verifica si hay doble turno (T1 y T2) para una fecha y servicio.
        Doble turno en:
        - Viernes noche
        - Sábado (comida y cena)
        - Domingo comida
        - Festivos y vísperas
        """
        dia_semana = fecha.weekday()
        
        # Viernes noche
        if dia_semana == 4 and servicio == Servicio.CENA:
            return True
        
        # Sábado (todo el día)
        if dia_semana == 5:
            return True
        
        # Domingo comida
        if dia_semana == 6 and servicio == Servicio.COMIDA:
            return True
        
        # Festivos (todo el día)
        if self.holiday_service.es_festivo(fecha):
            return True
        
        # Víspera de festivo (cena)
        if servicio == Servicio.CENA and self.holiday_service.es_vispera_festivo(fecha):
            return True
        
        return False
    
    # ========== OBTENCIÓN DE HORARIOS ==========
    
    def get_horario(self, fecha: date, servicio: Servicio) -> Optional[HorarioServicio]:
        """
        Devuelve el horario aplicable para una fecha y servicio.
        """
        abierto, _ = self.esta_abierto(fecha, servicio)
        if not abierto:
            return None
        
        doble = self.hay_doble_turno(fecha, servicio)
        
        if servicio == Servicio.COMIDA:
            return self.HORARIOS_COMIDA_DOBLE if doble else self.HORARIOS_COMIDA
        else:
            return self.HORARIOS_CENA_DOBLE if doble else self.HORARIOS_CENA
    
    def get_turnos_disponibles(self, fecha: date, servicio: Servicio) -> List[InfoTurno]:
        """
        Devuelve los turnos disponibles para una fecha y servicio.
        """
        horario = self.get_horario(fecha, servicio)
        if horario is None:
            return []
        
        turnos = []
        
        if servicio == Servicio.COMIDA:
            # Turno 1: 13:00 - 15:00
            turnos.append(InfoTurno(
                turno=Turno.T1,
                hora_inicio=time(13, 0),
                hora_fin=time(15, 0),
                es_ultimo=not horario.tiene_doble_turno
            ))
            
            if horario.tiene_doble_turno:
                # Turno 2: 15:00 - 16:30
                turnos.append(InfoTurno(
                    turno=Turno.T2,
                    hora_inicio=time(15, 0),
                    hora_fin=time(16, 30),
                    es_ultimo=True
                ))
        else:
            # Cena
            # Turno 1: 20:30 - 22:00
            turnos.append(InfoTurno(
                turno=Turno.T1,
                hora_inicio=time(20, 30),
                hora_fin=time(22, 0),
                es_ultimo=not horario.tiene_doble_turno
            ))
            
            if horario.tiene_doble_turno:
                # Turno 2: 22:00 - 23:30
                turnos.append(InfoTurno(
                    turno=Turno.T2,
                    hora_inicio=time(22, 0),
                    hora_fin=time(23, 30),
                    es_ultimo=True
                ))
        
        return turnos
    
    def determinar_turno(self, hora: time, servicio: Servicio, doble_turno: bool) -> Turno:
        """
        Determina el turno correspondiente a una hora.
        """
        if servicio == Servicio.COMIDA:
            if hora < time(15, 0):
                return Turno.T1
            return Turno.T2 if doble_turno else Turno.T1
        else:
            if hora < time(22, 0):
                return Turno.T1
            return Turno.T2 if doble_turno else Turno.T1
    
    def determinar_servicio(self, hora: time) -> Servicio:
        """
        Determina si una hora corresponde a comida o cena.
        """
        if time(12, 0) <= hora < time(18, 0):
            return Servicio.COMIDA
        return Servicio.CENA
    
    # ========== VALIDACIONES ==========
    
    def validar_hora_reserva(self, fecha: date, hora: time) -> Tuple[bool, str]:
        """
        Valida si una hora es válida para reservar.
        Retorna (válida, mensaje).
        """
        servicio = self.determinar_servicio(hora)
        abierto, motivo = self.esta_abierto(fecha, servicio)
        
        if not abierto:
            return False, motivo
        
        horario = self.get_horario(fecha, servicio)
        if horario is None:
            return False, "Servicio no disponible"
        
        # Verificar que la hora esté dentro del rango de reservas
        if hora < horario.hora_apertura:
            return False, f"Abrimos a las {horario.hora_apertura.strftime('%H:%M')}"
        
        if hora > horario.hora_ultimo_turno:
            return False, f"Última hora de reserva: {horario.hora_ultimo_turno.strftime('%H:%M')}"
        
        return True, "OK"
    
    def es_alta_demanda(self, fecha: date) -> bool:
        """
        Verifica si es un día de alta demanda que requiere escalado especial.
        """
        # Días de alta demanda conocidos (San Mateo, San Bernabé)
        if self.holiday_service.es_alta_demanda(fecha):
            return True
        
        # Sábados siempre son alta demanda
        if fecha.weekday() == 5:
            return True
        
        return False


# Singleton global
_schedule_service: Optional[ScheduleService] = None


def get_schedule_service() -> ScheduleService:
    """Devuelve la instancia singleton del servicio de horarios."""
    global _schedule_service
    if _schedule_service is None:
        _schedule_service = ScheduleService()
    return _schedule_service
