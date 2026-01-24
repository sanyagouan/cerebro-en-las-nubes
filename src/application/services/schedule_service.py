from datetime import date, time, datetime
from typing import Tuple, List, Optional
import logging

from src.domain.services.holiday_service import HolidayService

logger = logging.getLogger(__name__)

class ScheduleService:
    """
    Servicio de dominio para gestionar horarios y aperturas.
    Contiene la lógica de negocio sobre cuándo abre el restaurante.
    """
    
    def __init__(self, holiday_service: Optional[HolidayService] = None):
        self.holiday_service = holiday_service or HolidayService()

    def es_horario_apertura(self, fecha: date, hora: time) -> Tuple[bool, str]:
        """
        Determina si el restaurante está abierto en una fecha y hora dadas.
        Retorna (True/False, Mensaje explicativo).
        Reglas basadas en la información proporcionada:
        - Lunes: CERRADO (salvo festivo/víspera, a revisar). Asumimos cerrado por defecto.
        - Martes, Miércoles: Solo COMIDAS (13:00 - 17:00). CENA CERRADO.
        - Jueves: COMIDAS (13:00 - 17:00) y CENAS (20:00 - 00:00).
        - Viernes: COMIDAS (13:00 - 17:00) y CENAS (20:00 - 00:30/01:00).
        - Sábado: COMIDAS (13:00 - 17:00) y CENAS (20:00 - 01:00).
        - Domingo: Solo COMIDAS (13:00 - 17:00). DOMINGO NOCHE CERRADO.
        """
        
        dia_semana = fecha.weekday() # 0=Lunes, 6=Domingo
        
        # 1. Verificar Lunes Cerrado
        if dia_semana == 0:
            # Podríamos añadir lógica de excepción por festivos aquí
            return False, "Los lunes descansamos en las nubes."

        # Definir rangos generales
        # Comidas: 13:00 a 16:30 (admitimos reservas hasta esa hora, cierre 17:00)
        inicio_comida = time(13, 0)
        fin_comida_reserva = time(16, 30) # Límite para reservar
        fin_comida_cierre = time(17, 0)
        
        # Cenas
        inicio_cena = time(20, 0)
        fin_cena_reserva = time(23, 0) # Límite estándar
        if dia_semana in [4, 5]: # V y S
            fin_cena_reserva = time(23, 30)
            
        # Determinar si es petición de COMIDA o CENA
        es_comida = inicio_comida <= hora <= fin_comida_cierre
        es_cena = inicio_cena <= hora <= time(23, 59) or (time(0,0) <= hora <= time(1, 30)) # Madrugada
        
        if not (es_comida or es_cena):
            return False, "Estamos cerrados a esa hora. Nuestro horario es de 13:00 a 17:00 y noches de Jueves a Sábado a partir de las 20:00."

        # 2. Reglas específicas por día
        if es_cena:
            # Martes (1), Miércoles (2), Domingo (6) -> CERRADO NOCHE
            if dia_semana in [1, 2, 6]:
                # Verificar víspera de festivo si fuera necesario
                # if not self.holiday_service.es_vispera_festivo(fecha):
                return False, "Las noches de domingo, martes y miércoles descansamos."
            
            # Jueves (3) -> ABIERTO NOCHE (Corregido: Antes decía cerrado)
            # Viernes (4), Sábado (5) -> ABIERTO NOCHE
            
        # 3. Validar hora límite de reserva
        if es_comida and hora > fin_comida_reserva:
             return False, f"La cocina cierra pronto a mediodía. La última hora de reserva es a las {fin_comida_reserva.strftime('%H:%M')}."
             
        if es_cena:
             if dia_semana == 3 and hora > time(23,0): # Jueves cierra antes
                  return False, "Los jueves cerramos un poquito antes, cocina hasta las 23:00."
             elif hora > fin_cena_reserva:
                  return False, f"Para cenar, la cocina cierra a eso de las {fin_cena_reserva.strftime('%H:%M')}."

        return True, "Abierto"

    def obtener_turnos(self, fecha: date, servicio: str) -> List[str]:
        """
        Devuelve los turnos disponibles si aplican.
        """
        # Lógica simplificada de turnos para Fines de Semana
        dia_semana = fecha.weekday()
        if dia_semana in [4, 5, 6]: # V, S, D
            if servicio == "COMIDA":
                return ["13:30", "15:15"]
            elif servicio == "CENA" and dia_semana in [4, 5]:
                return ["20:30", "22:30"]
        
        return [] # Sin turnos fijos (reservas libres)
