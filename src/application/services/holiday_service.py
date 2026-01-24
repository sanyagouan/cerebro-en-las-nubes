"""
Servicio de Festivos - La Rioja / Logroño
Gestiona festivos nacionales, autonómicos y locales con soporte para actualización anual.
"""

from datetime import date, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class HolidayType(str, Enum):
    NACIONAL = "Nacional"
    AUTONOMICO = "Autonómico"
    LOCAL = "Local"


@dataclass
class Holiday:
    fecha: date
    nombre: str
    tipo: HolidayType
    es_alta_demanda: bool = False  # San Mateo, San Bernabé, etc.


class HolidayService:
    """
    Servicio de gestión de festivos para La Rioja y Logroño.
    Los festivos se definen por año y se pueden actualizar fácilmente.
    """
    
    def __init__(self, year: int = None):
        self.year = year or date.today().year
        self._holidays: Dict[int, List[Holiday]] = {}
        self._load_holidays()
    
    def _load_holidays(self):
        """Carga los festivos del año actual y siguiente."""
        for y in [self.year, self.year + 1]:
            self._holidays[y] = self._get_holidays_for_year(y)
    
    def _get_holidays_for_year(self, year: int) -> List[Holiday]:
        """
        Devuelve los festivos para un año específico.
        Esta es la función a actualizar anualmente.
        """
        
        # ========== FESTIVOS FIJOS (No cambian de fecha) ==========
        festivos_fijos = [
            Holiday(date(year, 1, 1), "Año Nuevo", HolidayType.NACIONAL),
            Holiday(date(year, 1, 6), "Epifanía del Señor (Reyes)", HolidayType.NACIONAL),
            Holiday(date(year, 5, 1), "Fiesta del Trabajo", HolidayType.NACIONAL),
            Holiday(date(year, 6, 9), "Día de La Rioja", HolidayType.AUTONOMICO),
            Holiday(date(year, 6, 11), "San Bernabé", HolidayType.LOCAL, es_alta_demanda=True),
            Holiday(date(year, 8, 15), "Asunción de la Virgen", HolidayType.NACIONAL),
            Holiday(date(year, 10, 12), "Fiesta Nacional de España", HolidayType.NACIONAL),
            Holiday(date(year, 11, 1), "Todos los Santos", HolidayType.NACIONAL),
            Holiday(date(year, 12, 6), "Día de la Constitución", HolidayType.NACIONAL),
            Holiday(date(year, 12, 8), "Inmaculada Concepción", HolidayType.NACIONAL),
            Holiday(date(year, 12, 25), "Navidad", HolidayType.NACIONAL),
        ]
        
        # ========== FESTIVOS MÓVILES (Calculados) ==========
        # Semana Santa - depende de la luna pascual
        pascua = self._calculate_easter(year)
        festivos_moviles = [
            Holiday(pascua - timedelta(days=2), "Viernes Santo", HolidayType.NACIONAL),
            Holiday(pascua + timedelta(days=1), "Lunes de Pascua", HolidayType.AUTONOMICO),
        ]
        
        # ========== FESTIVOS ESPECIALES POR AÑO ==========
        festivos_especiales = self._get_special_holidays(year)
        
        return festivos_fijos + festivos_moviles + festivos_especiales
    
    def _calculate_easter(self, year: int) -> date:
        """
        Calcula la fecha de Domingo de Pascua usando el algoritmo de Gauss.
        """
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return date(year, month, day)
    
    def _get_special_holidays(self, year: int) -> List[Holiday]:
        """
        Festivos especiales que varían por año (puentes, etc.).
        Actualizar esta función cada año con las decisiones de las autoridades.
        """
        specials = []
        
        if year == 2026:
            # San Mateo 2026 (21-26 septiembre) - ALTA DEMANDA
            for day in range(21, 27):
                specials.append(Holiday(
                    date(2026, 9, day), 
                    f"Fiestas de San Mateo (día {day})", 
                    HolidayType.LOCAL, 
                    es_alta_demanda=True
                ))
            # Segundo festivo local de Logroño 2026 (por determinar)
            # specials.append(Holiday(date(2026, X, X), "Festivo Local", HolidayType.LOCAL))
        
        elif year == 2027:
            # Placeholder para 2027 - actualizar cuando se publique el BOE/BOR
            pass
        
        return specials
    
    # ========== API PÚBLICA ==========
    
    def es_festivo(self, fecha: date) -> bool:
        """Comprueba si una fecha es festivo."""
        year = fecha.year
        if year not in self._holidays:
            self._holidays[year] = self._get_holidays_for_year(year)
        return any(h.fecha == fecha for h in self._holidays.get(year, []))
    
    def es_alta_demanda(self, fecha: date) -> bool:
        """Comprueba si una fecha es de alta demanda (San Mateo, San Bernabé, etc.)."""
        year = fecha.year
        if year not in self._holidays:
            self._holidays[year] = self._get_holidays_for_year(year)
        return any(h.fecha == fecha and h.es_alta_demanda for h in self._holidays.get(year, []))
    
    def es_vispera_festivo(self, fecha: date) -> bool:
        """Comprueba si la fecha es víspera de festivo (día anterior)."""
        siguiente = fecha + timedelta(days=1)
        return self.es_festivo(siguiente)
    
    def get_festivo(self, fecha: date) -> Optional[Holiday]:
        """Devuelve el objeto Holiday si la fecha es festivo, None si no."""
        year = fecha.year
        if year not in self._holidays:
            self._holidays[year] = self._get_holidays_for_year(year)
        for h in self._holidays.get(year, []):
            if h.fecha == fecha:
                return h
        return None
    
    def get_festivos_mes(self, year: int, month: int) -> List[Holiday]:
        """Devuelve todos los festivos de un mes específico."""
        if year not in self._holidays:
            self._holidays[year] = self._get_holidays_for_year(year)
        return [h for h in self._holidays.get(year, []) if h.fecha.month == month]
    
    def get_todos_festivos(self, year: int) -> List[Holiday]:
        """Devuelve todos los festivos de un año."""
        if year not in self._holidays:
            self._holidays[year] = self._get_holidays_for_year(year)
        return self._holidays.get(year, [])


# Singleton global para uso en toda la aplicación
_holiday_service: Optional[HolidayService] = None


def get_holiday_service() -> HolidayService:
    """Devuelve la instancia singleton del servicio de festivos."""
    global _holiday_service
    if _holiday_service is None:
        _holiday_service = HolidayService()
    return _holiday_service
