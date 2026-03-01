"""
Servicio de Clima - Integración con OpenWeatherMap
Valida condiciones meteorológicas para asignación de terraza.
"""

import os
import httpx
from datetime import datetime
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class WeatherInfo:
    """Información meteorológica simplificada."""
    descripcion: str
    temperatura: float  # Celsius
    sensacion_termica: float
    lluvia_probable: bool
    porcentaje_nubes: int
    viento_kmh: float
    es_favorable: bool
    avisos: List[str]


class WeatherService:
    """
    Servicio de consulta meteorológica para Logroño.
    Utiliza OpenWeatherMap API (gratuita hasta 1000 calls/día).
    """
    
    # Configuración de la API
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    CITY = "Logroño,ES"
    
    # Umbrales para terraza
    TEMP_MIN_FAVORABLE = 12  # Celsius
    TEMP_MIN_CONFORTABLE = 16
    VIENTO_MAX_KMH = 30
    NUBES_MAX_PERCENT = 80
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self._cache: Optional[Tuple[datetime, WeatherInfo]] = None
        self._cache_duration_minutes = 30
    
    async def get_weather(self) -> Optional[WeatherInfo]:
        """
        Obtiene el clima actual de Logroño.
        Usa caché de 30 minutos para evitar llamadas excesivas.
        """
        # Verificar caché
        if self._cache:
            cached_time, cached_info = self._cache
            if (datetime.now() - cached_time).total_seconds() < self._cache_duration_minutes * 60:
                return cached_info
        
        # Si no hay API key, devolver clima "desconocido"
        if not self.api_key:
            return self._get_unknown_weather()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    self.BASE_URL,
                    params={
                        "q": self.CITY,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "es"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                weather_info = self._parse_response(data)
                self._cache = (datetime.now(), weather_info)
                return weather_info
                
        except Exception as e:
            print(f"⚠️ Error obteniendo clima: {e}")
            return self._get_unknown_weather()
    
    def get_weather_sync(self) -> Optional[WeatherInfo]:
        """Versión síncrona para uso en contextos no-async."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Ya estamos en un contexto async, usar httpx sync
                return self._get_weather_sync_direct()
            return loop.run_until_complete(self.get_weather())
        except RuntimeError:
            return self._get_weather_sync_direct()
    
    def _get_weather_sync_direct(self) -> Optional[WeatherInfo]:
        """Llamada síncrona directa a la API."""
        # Verificar caché
        if self._cache:
            cached_time, cached_info = self._cache
            if (datetime.now() - cached_time).total_seconds() < self._cache_duration_minutes * 60:
                return cached_info
        
        if not self.api_key:
            return self._get_unknown_weather()
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    self.BASE_URL,
                    params={
                        "q": self.CITY,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "es"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                weather_info = self._parse_response(data)
                self._cache = (datetime.now(), weather_info)
                return weather_info
                
        except Exception as e:
            print(f"⚠️ Error obteniendo clima: {e}")
            return self._get_unknown_weather()
    
    def _parse_response(self, data: dict) -> WeatherInfo:
        """Parsea la respuesta de OpenWeatherMap."""
        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        wind = data.get("wind", {})
        clouds = data.get("clouds", {})
        rain = data.get("rain", {})
        
        temperatura = main.get("temp", 20)
        sensacion = main.get("feels_like", temperatura)
        descripcion = weather.get("description", "desconocido")
        weather_main = weather.get("main", "")
        nubes = clouds.get("all", 0)
        viento_ms = wind.get("speed", 0)
        viento_kmh = viento_ms * 3.6
        
        # Detectar lluvia
        lluvia = weather_main.lower() in ["rain", "drizzle", "thunderstorm"] or len(rain) > 0
        
        # Evaluar si es favorable para terraza
        avisos = []
        es_favorable = True
        
        if lluvia:
            es_favorable = False
            avisos.append("Lluvia prevista - no recomendar terraza")
        
        if temperatura < self.TEMP_MIN_FAVORABLE:
            es_favorable = False
            avisos.append(f"Temperatura baja ({temperatura:.0f}°C) - solo interior")
        elif temperatura < self.TEMP_MIN_CONFORTABLE:
            avisos.append(f"Temperatura fresca ({temperatura:.0f}°C) - avisar al cliente")
        
        if viento_kmh > self.VIENTO_MAX_KMH:
            avisos.append(f"Viento fuerte ({viento_kmh:.0f} km/h)")
            if viento_kmh > 40:
                es_favorable = False
        
        return WeatherInfo(
            descripcion=descripcion.capitalize(),
            temperatura=temperatura,
            sensacion_termica=sensacion,
            lluvia_probable=lluvia,
            porcentaje_nubes=nubes,
            viento_kmh=viento_kmh,
            es_favorable=es_favorable,
            avisos=avisos
        )
    
    def _get_unknown_weather(self) -> WeatherInfo:
        """Devuelve clima por defecto cuando no hay API disponible."""
        return WeatherInfo(
            descripcion="Información no disponible",
            temperatura=18,  # Asumimos temperatura media
            sensacion_termica=18,
            lluvia_probable=False,
            porcentaje_nubes=50,
            viento_kmh=10,
            es_favorable=True,  # Asumimos que está bien
            avisos=["⚠️ Sin datos meteorológicos - verificar manualmente"]
        )
    
    # ========== API PÚBLICA SIMPLIFICADA ==========
    
    def es_favorable_terraza(self) -> Tuple[bool, List[str]]:
        """
        Verifica si el clima es favorable para terraza.
        Retorna (favorable, lista_de_avisos).
        """
        weather = self.get_weather_sync()
        if weather is None:
            return True, ["Sin datos meteorológicos"]
        return weather.es_favorable, weather.avisos
    
    def get_aviso_cliente(self) -> Optional[str]:
        """
        Genera un mensaje de aviso para el cliente sobre la terraza.
        Retorna None si no hay nada que avisar.
        """
        weather = self.get_weather_sync()
        if weather is None or not weather.avisos:
            return None
        
        if not weather.es_favorable:
            return "Por el clima actual, le recomendamos reservar en el interior."
        
        if any("fresca" in a.lower() for a in weather.avisos):
            return f"La temperatura actual es de {weather.temperatura:.0f}°C. En terraza no disponemos de calefactor."
        
        return None


# Singleton global
_weather_service: Optional[WeatherService] = None


def get_weather_service() -> WeatherService:
    """Devuelve la instancia singleton del servicio de clima."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
