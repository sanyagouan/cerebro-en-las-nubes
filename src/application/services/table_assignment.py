"""
Servicio de Asignación de Mesas - En Las Nubes Restobar
Algoritmo completo de asignación basado en capacidad, zona y disponibilidad.
"""

from datetime import date, time
from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

from src.core.entities.table import (
    Table, TableZone, TableStatus, 
    get_all_tables, get_tables_by_zone, get_table_by_id,
    MESAS_TERRAZA, MESAS_INTERIOR, MESAS_AUXILIARES
)
from src.core.entities.booking import ZonePreference, SpecialRequest
from src.infrastructure.services.weather_service import get_weather_service


@dataclass
class AsignacionResult:
    """Resultado de una asignación de mesa."""
    exito: bool
    mesa_id: Optional[str] = None
    mesa_nombre: Optional[str] = None
    zona: Optional[str] = None
    usa_auxiliar: bool = False
    auxiliar_id: Optional[str] = None
    avisos: List[str] = None
    motivo_fallo: Optional[str] = None
    requiere_escalado: bool = False
    
    def __post_init__(self):
        if self.avisos is None:
            self.avisos = []


class TableAssignmentService:
    """
    Servicio de asignación inteligente de mesas.
    Implementa el algoritmo completo del documento de requisitos.
    """
    
    # Capacidad máxima antes de escalado obligatorio
    MAX_PAX_SIN_ESCALADO = 10
    
    def __init__(self):
        self.weather_service = get_weather_service()
        # Estado de ocupación (en producción vendría de Airtable)
        self._ocupacion: dict = {}  # {mesa_id: {fecha: {turno: reserva_id}}}
    
    def asignar_mesa(
        self,
        pax: int,
        fecha: date,
        turno: str,
        zona_preferencia: ZonePreference = ZonePreference.NO_PREFERENCE,
        solicitudes: List[SpecialRequest] = None
    ) -> AsignacionResult:
        """
        Asigna la mejor mesa disponible según los criterios del negocio.
        """
        solicitudes = solicitudes or []
        avisos = []
        
        # ========== VALIDACIÓN GRUPOS GRANDES ==========
        if pax > self.MAX_PAX_SIN_ESCALADO:
            return AsignacionResult(
                exito=False,
                motivo_fallo=f"Grupos de más de {self.MAX_PAX_SIN_ESCALADO} personas requieren confirmación del maître",
                requiere_escalado=True
            )
        
        # ========== RESTRICCIÓN MASCOTA → SOLO TERRAZA ==========
        if SpecialRequest.MASCOTA in solicitudes:
            zona_preferencia = ZonePreference.TERRAZA
            avisos.append("Mascota: solo mesa en terraza")
        
        # ========== VERIFICAR CLIMA PARA TERRAZA ==========
        if zona_preferencia in [ZonePreference.TERRAZA, ZonePreference.NO_PREFERENCE]:
            favorable, weather_avisos = self.weather_service.es_favorable_terraza()
            
            if not favorable:
                if zona_preferencia == ZonePreference.TERRAZA:
                    # Cliente quiere terraza obligatoriamente pero clima malo
                    if SpecialRequest.MASCOTA in solicitudes:
                        avisos.extend(weather_avisos)
                        avisos.append("⚠️ AVISAR: Clima adverso pero requiere terraza por mascota")
                    else:
                        avisos.append("Clima no favorable - recomendamos interior")
                        zona_preferencia = ZonePreference.NO_PREFERENCE
                else:
                    avisos.append("Terraza no recomendada por clima")
            else:
                avisos.extend(weather_avisos)
        
        # ========== BUSCAR MESA SEGÚN CAPACIDAD ==========
        resultado = self._buscar_mesa_por_capacidad(
            pax=pax,
            fecha=fecha,
            turno=turno,
            zona_preferencia=zona_preferencia
        )
        
        if resultado is not None:
            mesa, usa_auxiliar, aux_id = resultado
            return AsignacionResult(
                exito=True,
                mesa_id=mesa["id"],
                mesa_nombre=mesa.get("nombre", mesa["id"]),
                zona=mesa["zona"],
                usa_auxiliar=usa_auxiliar,
                auxiliar_id=aux_id,
                avisos=avisos + self._get_avisos_mesa(mesa)
            )
        
        # ========== NO HAY DISPONIBILIDAD ==========
        return AsignacionResult(
            exito=False,
            motivo_fallo="No hay mesas disponibles para ese número de personas en la fecha y turno seleccionados",
            avisos=avisos
        )
    
    def _buscar_mesa_por_capacidad(
        self,
        pax: int,
        fecha: date,
        turno: str,
        zona_preferencia: ZonePreference
    ) -> Optional[Tuple[dict, bool, Optional[str]]]:
        """
        Busca la mejor mesa según el número de comensales.
        Retorna (mesa_dict, usa_auxiliar, auxiliar_id) o None.
        """
        
        # ========== 1-2 PERSONAS ==========
        if pax <= 2:
            return self._buscar_1_2_personas(fecha, turno, zona_preferencia)
        
        # ========== 3 PERSONAS ==========
        elif pax == 3:
            return self._buscar_3_personas(fecha, turno, zona_preferencia)
        
        # ========== 4-6 PERSONAS ==========
        elif pax <= 6:
            return self._buscar_4_6_personas(fecha, turno, zona_preferencia)
        
        # ========== 7-8 PERSONAS ==========
        elif pax <= 8:
            return self._buscar_7_8_personas(fecha, turno)
        
        # ========== 9-10 PERSONAS ==========
        elif pax <= 10:
            return self._buscar_9_10_personas(fecha, turno)
        
        return None
    
    def _buscar_1_2_personas(
        self, fecha: date, turno: str, zona_pref: ZonePreference
    ) -> Optional[Tuple[dict, bool, Optional[str]]]:
        """Lógica para 1-2 personas: priorizar mesas pequeñas."""
        
        # Orden de prioridad interior: C2-A → C2-B → C2-C
        orden_interior = ["C2-A", "C2-B", "C2-C"]
        # Terraza: cualquier T1-T8
        orden_terraza = [f"T{i}" for i in range(1, 9)]
        
        if zona_pref == ZonePreference.INTERIOR:
            candidatas = orden_interior
        elif zona_pref == ZonePreference.TERRAZA:
            candidatas = orden_terraza
        else:
            candidatas = orden_interior + orden_terraza
        
        for mesa_id in candidatas:
            if self._esta_disponible(mesa_id, fecha, turno):
                return self._get_mesa_dict(mesa_id), False, None
        
        return None
    
    def _buscar_3_personas(
        self, fecha: date, turno: str, zona_pref: ZonePreference
    ) -> Optional[Tuple[dict, bool, Optional[str]]]:
        """Lógica para 3 personas: C2-B flexible, luego C6-A/B."""
        
        orden_interior = ["C2-B", "C6-A", "C6-B"]
        orden_terraza = [f"T{i}" for i in range(1, 9)]
        
        if zona_pref == ZonePreference.INTERIOR:
            candidatas = orden_interior
        elif zona_pref == ZonePreference.TERRAZA:
            candidatas = orden_terraza
        else:
            candidatas = orden_interior + orden_terraza
        
        for mesa_id in candidatas:
            if self._esta_disponible(mesa_id, fecha, turno):
                return self._get_mesa_dict(mesa_id), False, None
        
        return None
    
    def _buscar_4_6_personas(
        self, fecha: date, turno: str, zona_pref: ZonePreference
    ) -> Optional[Tuple[dict, bool, Optional[str]]]:
        """Lógica para 4-6 personas: mesas de 6 o terraza."""
        
        orden_interior = ["C6-A", "C6-B"]
        orden_terraza = [f"T{i}" for i in range(1, 9)]
        
        if zona_pref == ZonePreference.INTERIOR:
            candidatas = orden_interior
        elif zona_pref == ZonePreference.TERRAZA:
            candidatas = orden_terraza
        else:
            candidatas = orden_interior + orden_terraza
        
        for mesa_id in candidatas:
            if self._esta_disponible(mesa_id, fecha, turno):
                return self._get_mesa_dict(mesa_id), False, None
        
        # Fallback: mesas grandes si no hay de 6
        for mesa_id in ["C8-A", "C8-B", "C8-C", "C7"]:
            if self._esta_disponible(mesa_id, fecha, turno):
                return self._get_mesa_dict(mesa_id), False, None
        
        return None
    
    def _buscar_7_8_personas(
        self, fecha: date, turno: str
    ) -> Optional[Tuple[dict, bool, Optional[str]]]:
        """Lógica para 7-8 personas: mesas de 8 (SIN terraza)."""
        
        # Solo interior para grupos de 7-8
        orden = ["C8-A", "C8-B", "C8-C", "C7"]
        
        for mesa_id in orden:
            if self._esta_disponible(mesa_id, fecha, turno):
                return self._get_mesa_dict(mesa_id), False, None
        
        # Último recurso: C6-B con auxiliar AUX-4
        if self._esta_disponible("C6-B", fecha, turno) and self._esta_disponible("AUX-4", fecha, turno):
            return self._get_mesa_dict("C6-B"), True, "AUX-4"
        
        return None
    
    def _buscar_9_10_personas(
        self, fecha: date, turno: str
    ) -> Optional[Tuple[dict, bool, Optional[str]]]:
        """Lógica para 9-10 personas: requiere auxiliar obligatoriamente."""
        
        # Configuraciones posibles: C8-X + AUX-X
        configs = [
            ("C8-A", "AUX-1"),
            ("C8-B", "AUX-2"),
            ("C8-C", "AUX-3"),
        ]
        
        for mesa_id, aux_id in configs:
            if self._esta_disponible(mesa_id, fecha, turno) and self._esta_disponible(aux_id, fecha, turno):
                return self._get_mesa_dict(mesa_id), True, aux_id
        
        return None
    
    # ========== UTILIDADES INTERNAS ==========
    
    def _esta_disponible(self, mesa_id: str, fecha: date, turno: str) -> bool:
        """Verifica si una mesa está disponible."""
        key = (mesa_id, fecha.isoformat(), turno)
        return key not in self._ocupacion
    
    def _marcar_ocupada(self, mesa_id: str, fecha: date, turno: str, reserva_id: str):
        """Marca una mesa como ocupada."""
        key = (mesa_id, fecha.isoformat(), turno)
        self._ocupacion[key] = reserva_id
    
    def _liberar_mesa(self, mesa_id: str, fecha: date, turno: str):
        """Libera una mesa ocupada."""
        key = (mesa_id, fecha.isoformat(), turno)
        self._ocupacion.pop(key, None)
    
    def _get_mesa_dict(self, mesa_id: str) -> Optional[dict]:
        """Obtiene el diccionario de configuración de una mesa."""
        all_mesas = MESAS_TERRAZA + MESAS_INTERIOR + MESAS_AUXILIARES
        for mesa in all_mesas:
            if mesa["id"] == mesa_id:
                return mesa
        return None
    
    def _get_avisos_mesa(self, mesa: dict) -> List[str]:
        """Genera avisos obligatorios para una mesa."""
        avisos = []
        
        if mesa.get("requiere_aviso") and mesa.get("notas"):
            avisos.append(f"⚠️ {mesa['notas']}")
        
        if mesa.get("zona") == "Terraza":
            avisos.append("🌤️ Mesa en terraza (clima dependiente)")
        
        return avisos
    
    # ========== SINCRONIZACIÓN CON AIRTABLE ==========
    
    def cargar_ocupacion_desde_airtable(self, reservas: List[dict]):
        """
        Carga el estado de ocupación desde las reservas de Airtable.
        """
        self._ocupacion.clear()
        for reserva in reservas:
            mesa_id = reserva.get("mesa_asignada")
            fecha = reserva.get("fecha")
            turno = reserva.get("turno", "T1")
            reserva_id = reserva.get("id")
            
            if mesa_id and fecha and reserva_id:
                key = (mesa_id, fecha, turno)
                self._ocupacion[key] = reserva_id


# Singleton global
_assignment_service: Optional[TableAssignmentService] = None


def get_table_assignment_service() -> TableAssignmentService:
    """Devuelve la instancia singleton del servicio de asignación."""
    global _assignment_service
    if _assignment_service is None:
        _assignment_service = TableAssignmentService()
    return _assignment_service
