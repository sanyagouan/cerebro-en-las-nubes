"""
Servicio de Asignación Automática de Mesas.

Este módulo implementa el algoritmo de 3 fases para asignar la mesa
óptima según el número de personas y preferencias del cliente.

FASE 1: Buscar mesa individual con capacidad exacta
FASE 2: Buscar mesa individual con capacidad ampliada
FASE 3: Buscar configuración de mesas combinadas (solo terraza)

Autor: Sistema En Las Nubes
Fecha: 2026-03-11
"""

import os
import logging
from typing import List, Optional, Tuple
from datetime import datetime, date
from pyairtable import Api

from src.core.entities.mesa import (
    Mesa,
    ConfiguracionMesa,
    SolicitudAsignacion,
    ResultadoAsignacion,
    EstadoMesa,
    ZonaMesa,
    DisponibilidadMesa,
    EstadisticasAsignacion
)

# Configurar logger
logger = logging.getLogger(__name__)


class TableAssignmentService:
    """Servicio para asignación automática de mesas.
    
    Implementa el algoritmo de 3 fases para encontrar la mesa óptima:
    
    1. FASE 1 - Capacidad Exacta:
       - Busca mesa con capacidad_estandar == num_personas
       - Prioriza por orden_prioridad (menor = mejor)
       - Respeta preferencia de zona si se especifica
    
    2. FASE 2 - Capacidad Ampliada:
       - Busca mesa donde capacidad_estandar < num_personas <= capacidad_ampliada
       - Minimiza desperdicio (diferencia más pequeña)
       - Ordena por: diferencia, capacidad, prioridad
    
    3. FASE 3 - Configuraciones (Solo Terraza):
       - Busca configuraciones predefinidas de mesas combinadas
       - Solo para grupos > 2 personas
       - Verifica que todas las mesas de la configuración estén disponibles
    
    Attributes:
        api: Cliente de Airtable API
        base_id: ID de la base de Airtable
        table_mesas: Tabla de mesas individuales
        table_configuraciones: Tabla de configuraciones de mesas
    """
    
    def __init__(self):
        """Inicializa el servicio con la configuración de Airtable."""
        self.api = Api(os.getenv("AIRTABLE_API_KEY"))
        self.base_id = "appQ2ZXAR68cqDmJt"
        self.table_mesas = self.api.table(self.base_id, "tblRSjdDIa5SrudL5")
        # ID de tabla ConfiguracionesMesas (creada en FASE 1)
        self.table_configuraciones = self.api.table(self.base_id, "tblNNh29nlg4tPSYs")
        
        logger.info("TableAssignmentService inicializado")
    
    async def asignar_mesa(self, solicitud: SolicitudAsignacion) -> ResultadoAsignacion:
        """Asigna mesa óptima usando algoritmo de 3 fases.
        
        Este es el método principal del servicio. Ejecuta las 3 fases
        en orden hasta encontrar una mesa disponible.
        
        Args:
            solicitud: Datos de la solicitud (personas, fecha, hora, preferencias)
        
        Returns:
            ResultadoAsignacion con la mesa asignada o alternativas si no hay disponibilidad
        
        Example:
            >>> solicitud = SolicitudAsignacion(
            ...     num_personas=4,
            ...     fecha="2026-03-15",
            ...     hora="14:00",
            ...     preferencia_zona=ZonaMesa.TERRAZA
            ... )
            >>> resultado = await service.asignar_mesa(solicitud)
            >>> print(resultado.mesa_asignada.nombre)
            "Mesa Terraza 1"
        """
        logger.info(f"Asignando mesa para {solicitud.num_personas} personas - {solicitud.fecha} {solicitud.hora}")
        
        # 1. Validar que el restobar está abierto
        if not self._esta_abierto(solicitud.fecha, solicitud.hora):
            logger.warning(f"Restobar cerrado: {solicitud.fecha} {solicitud.hora}")
            return ResultadoAsignacion(
                exito=False,
                mensaje="El restobar está cerrado en ese horario. Abrimos de martes a domingo para comidas (13:00-17:00) y cenas (20:00-23:00). Los lunes permanecemos cerrados."
            )
        
        # 2. Obtener mesas disponibles
        mesas_disponibles = await self._get_mesas_disponibles(
            solicitud.fecha,
            solicitud.hora,
            solicitud.preferencia_zona
        )
        
        logger.info(f"Mesas disponibles encontradas: {len(mesas_disponibles)}")
        
        if not mesas_disponibles:
            logger.warning("No hay mesas disponibles")
            return ResultadoAsignacion(
                exito=False,
                mensaje=f"No hay mesas disponibles para el {solicitud.fecha} a las {solicitud.hora}",
                alternativas=await self._buscar_alternativas(solicitud)
            )
        
        # 3. Si hay preferencia de mesa específica, intentar asignarla directamente
        if solicitud.preferencia_mesa:
            mesa_especifica = self._buscar_mesa_por_id(mesas_disponibles, solicitud.preferencia_mesa)
            if mesa_especifica and self._validar_capacidad(mesa_especifica, solicitud.num_personas):
                logger.info(f"Mesa específica asignada: {mesa_especifica.id_mesa}")
                return ResultadoAsignacion(
                    exito=True,
                    mesa_asignada=mesa_especifica,
                    mensaje=f"Mesa {mesa_especifica.nombre} asignada según preferencia"
                )
        
        # 4. Ejecutar algoritmo de 3 fases
        
        # FASE 1: Capacidad exacta
        logger.debug("FASE 1: Buscando capacidad exacta...")
        mesa_fase1 = self._buscar_capacidad_exacta(
            mesas_disponibles,
            solicitud.num_personas,
            solicitud.preferencia_zona
        )
        if mesa_fase1:
            logger.info(f"FASE 1 exitosa: {mesa_fase1.id_mesa}")
            return ResultadoAsignacion(
                exito=True,
                mesa_asignada=mesa_fase1,
                mensaje=f"Mesa {mesa_fase1.nombre} asignada (capacidad exacta: {mesa_fase1.capacidad_estandar} personas)"
            )
        
        # FASE 2: Capacidad ampliada
        logger.debug("FASE 2: Buscando capacidad ampliada...")
        mesa_fase2 = self._buscar_capacidad_ampliada(
            mesas_disponibles,
            solicitud.num_personas,
            solicitud.preferencia_zona
        )
        if mesa_fase2:
            logger.info(f"FASE 2 exitosa: {mesa_fase2.id_mesa}")
            return ResultadoAsignacion(
                exito=True,
                mesa_asignada=mesa_fase2,
                mensaje=f"Mesa {mesa_fase2.nombre} asignada (capacidad ampliada: {mesa_fase2.capacidad_ampliada} personas)"
            )
        
        # FASE 3: Configuraciones (solo para grupos > 2)
        if solicitud.num_personas > 2:
            logger.debug("FASE 3: Buscando configuraciones de mesas...")
            config_fase3 = await self._buscar_configuracion(mesas_disponibles, solicitud.num_personas)
            if config_fase3:
                logger.info(f"FASE 3 exitosa: {config_fase3.id_configuracion}")
                return ResultadoAsignacion(
                    exito=True,
                    configuracion_asignada=config_fase3,
                    mensaje=f"Configuración {config_fase3.nombre} asignada ({len(config_fase3.mesas_incluidas)} mesas combinadas, capacidad: {config_fase3.capacidad_total} personas)"
                )
        
        # No se encontró mesa
        logger.warning(f"No se encontró mesa para {solicitud.num_personas} personas")
        return ResultadoAsignacion(
            exito=False,
            mensaje=f"No hay mesa disponible para {solicitud.num_personas} personas. Tenemos mesas para grupos más pequeños o más grandes.",
            alternativas=self._obtener_alternativas_cercanas(mesas_disponibles, solicitud.num_personas)
        )
    
    def _buscar_capacidad_exacta(
        self,
        mesas: List[Mesa],
        num_personas: int,
        zona_preferida: Optional[ZonaMesa] = None
    ) -> Optional[Mesa]:
        """FASE 1: Busca mesa con capacidad estándar exacta.
        
        Prioriza:
        1. Capacidad exacta (capacidad_estandar == num_personas)
        2. Zona preferida (si se especifica)
        3. Menor orden_prioridad (mesas más pequeñas primero)
        
        Args:
            mesas: Lista de mesas disponibles
            num_personas: Número de comensales
            zona_preferida: Zona preferida por el cliente (opcional)
        
        Returns:
            Mesa óptima o None si no hay coincidencia exacta
        """
        # Filtrar por capacidad exacta
        candidatas = [
            m for m in mesas
            if m.capacidad_estandar == num_personas and m.activa
        ]
        
        if not candidatas:
            return None
        
        # Si hay zona preferida, priorizar mesas de esa zona
        if zona_preferida:
            mesas_zona_preferida = [
                m for m in candidatas
                if m.zona == zona_preferida or m.zona == zona_preferida.value
            ]
            if mesas_zona_preferida:
                # Ordenar por prioridad dentro de la zona preferida
                mesas_zona_preferida.sort(key=lambda m: m.orden_prioridad)
                logger.debug(f"FASE 1: {len(mesas_zona_preferida)} mesas en zona preferida '{zona_preferida.value}'")
                return mesas_zona_preferida[0]
        
        # Si no hay zona preferida o no hay mesas en esa zona, ordenar por prioridad global
        candidatas.sort(key=lambda m: m.orden_prioridad)
        logger.debug(f"FASE 1: {len(candidatas)} mesas con capacidad exacta")
        
        return candidatas[0]
    
    def _buscar_capacidad_ampliada(
        self,
        mesas: List[Mesa],
        num_personas: int,
        zona_preferida: Optional[ZonaMesa] = None
    ) -> Optional[Mesa]:
        """FASE 2: Busca mesa con capacidad ampliada.
        
        Minimiza desperdicio:
        - Si 4 personas: prefiere mesa cap.6 sobre cap.10
        - Ordena por: (diferencia, capacidad, prioridad)
        - Prioriza zona preferida si se especifica
        
        Args:
            mesas: Lista de mesas disponibles
            num_personas: Número de comensales
            zona_preferida: Zona preferida por el cliente (opcional)
        
        Returns:
            Mesa óptima o None si no hay capacidad ampliada suficiente
        """
        candidatas = [
            m for m in mesas
            if m.capacidad_estandar < num_personas <= m.capacidad_ampliada
            and m.activa
        ]
        
        if not candidatas:
            return None
        
        # Si hay zona preferida, priorizar mesas de esa zona
        if zona_preferida:
            mesas_zona_preferida = [
                m for m in candidatas
                if m.zona == zona_preferida or m.zona == zona_preferida.value
            ]
            if mesas_zona_preferida:
                # Ordenar por desperdicio mínimo dentro de la zona preferida
                mesas_zona_preferida.sort(key=lambda m: (
                    m.capacidad_ampliada - num_personas,  # Diferencia
                    m.capacidad_ampliada,                  # Capacidad total
                    m.orden_prioridad                      # Prioridad
                ))
                logger.debug(f"FASE 2: {len(mesas_zona_preferida)} mesas en zona preferida '{zona_preferida.value}'")
                return mesas_zona_preferida[0]
        
        # Si no hay zona preferida o no hay mesas en esa zona, ordenar por prioridad global
        # Ordenar por desperdicio mínimo
        # 1. Diferencia entre capacidad ampliada y personas (menor = mejor)
        # 2. Capacidad total (menor = mejor)
        # 3. Prioridad (menor = mejor)
        candidatas.sort(key=lambda m: (
            m.capacidad_ampliada - num_personas,  # Diferencia
            m.capacidad_ampliada,                  # Capacidad total
            m.orden_prioridad                      # Prioridad
        ))
        
        logger.debug(f"FASE 2: {len(candidatas)} mesas con capacidad ampliada")
        
        return candidatas[0]
    
    async def _buscar_configuracion(self, mesas: List[Mesa], num_personas: int) -> Optional[ConfiguracionMesa]:
        """FASE 3: Busca configuración de mesas combinadas.
        
        Solo para terraza. Busca configuración predefinida
        que se ajuste al número de personas.
        
        Args:
            mesas: Lista de mesas disponibles
            num_personas: Número de comensales
        
        Returns:
            ConfiguracionMesa óptima o None si no hay configuración disponible
        """
        # Obtener configuraciones activas
        configs = await self._get_configuraciones_activas()
        
        if not configs:
            logger.debug("FASE 3: No hay configuraciones activas")
            return None
        
        # Filtrar por capacidad (que cubra el número de personas)
        configs_adecuadas = [
            c for c in configs
            if c.capacidad_total >= num_personas and c.activa
        ]
        
        if not configs_adecuadas:
            logger.debug(f"FASE 3: No hay configuraciones para {num_personas} personas")
            return None
        
        # Ordenar por capacidad más cercana (minimizar desperdicio)
        configs_adecuadas.sort(key=lambda c: c.capacidad_total)
        
        # Verificar que todas las mesas de la configuración están disponibles
        mesas_disponibles_ids = {m.id_mesa for m in mesas}
        
        for config in configs_adecuadas:
            mesas_config = set(config.mesas_incluidas)
            
            if mesas_config.issubset(mesas_disponibles_ids):
                # Todas las mesas están disponibles
                logger.debug(f"FASE 3: Configuración {config.id_configuracion} disponible")
                return config
        
        logger.debug("FASE 3: Ninguna configuración tiene todas las mesas disponibles")
        return None
    
    async def _get_mesas_disponibles(
        self,
        fecha: str,
        hora: str,
        zona: Optional[ZonaMesa] = None
    ) -> List[Mesa]:
        """Obtiene mesas disponibles para una fecha y hora.
        
        Args:
            fecha: YYYY-MM-DD
            hora: HH:MM
            zona: Filtrar por zona (opcional)
        
        Returns:
            Lista de mesas disponibles
        """
        try:
            # Construir fórmula de filtrado
            # Nota: Airtable usa {Disponible} (checkbox) y {Estado} con valores: Libre, Ocupada, Reservada, Bloqueada
            formula = "AND({Disponible} = TRUE(), {Estado} = 'Libre')"
            if zona:
                formula = f"AND({{Disponible}} = TRUE(), {{Estado}} = 'Libre', {{Zona}} = '{zona.value}')"
            
            records = self.table_mesas.all(formula=formula)
            
            mesas = []
            for record in records:
                mesa = self._record_to_mesa(record)
                if mesa.estado == EstadoMesa.LIBRE:
                    mesas.append(mesa)
            
            logger.debug(f"Encontradas {len(mesas)} mesas disponibles")
            return mesas
            
        except Exception as e:
            logger.error(f"Error obteniendo mesas disponibles: {e}")
            return []
    
    async def _get_configuraciones_activas(self) -> List[ConfiguracionMesa]:
        """Obtiene configuraciones de mesas activas desde Airtable.
        
        Returns:
            Lista de configuraciones activas
        """
        try:
            # Consultar configuraciones activas en Airtable
            records = self.table_configuraciones.all(formula="{Activa} = TRUE()")
            configs = [self._record_to_config(r) for r in records]
            logger.debug(f"Encontradas {len(configs)} configuraciones activas")
            return configs
        except Exception as e:
            logger.error(f"Error obteniendo configuraciones: {e}")
            return []
    
    def _esta_abierto(self, fecha: str, hora: str) -> bool:
        """Verifica si el restobar está abierto.
        
        Horarios:
        - Lunes: Cerrado
        - Martes-Viernes: 13:00-17:00 (comidas), 20:00-23:00 (cenas)
        - Sábado: 13:00-17:00 (comidas), 20:00-00:00 (cenas hasta medianoche)
        - Domingo: 13:00-17:00 (comidas), 20:00-23:00 (cenas)
        
        Args:
            fecha: Fecha en formato YYYY-MM-DD
            hora: Hora en formato HH:MM
        
        Returns:
            True si está abierto, False si está cerrado
        """
        try:
            dt = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
            dia_semana = dt.weekday()  # 0=Lunes, 6=Domingo
            hora_num = dt.hour
            
            # Lunes cerrado
            if dia_semana == 0:
                logger.debug(f"Lunes {fecha}: cerrado")
                return False
            
            # Horarios de comidas (13:00 - 17:00)
            if 13 <= hora_num < 17:
                logger.debug(f"{fecha} {hora}: abierto (comidas)")
                return True
            
            # Horarios de cenas (20:00 - 23:00)
            if 20 <= hora_num < 23:
                logger.debug(f"{fecha} {hora}: abierto (cenas)")
                return True
            
            # Sábado noche hasta 00:00
            if dia_semana == 5 and hora_num == 23:
                logger.debug(f"Sábado {fecha} {hora}: abierto (cenas extendidas)")
                return True
            
            logger.debug(f"{fecha} {hora}: cerrado (fuera de horario)")
            return False
            
        except Exception as e:
            logger.error(f"Error verificando horario: {e}")
            return False
    
    async def _buscar_alternativas(self, solicitud: SolicitudAsignacion) -> List[Mesa]:
        """Busca alternativas cuando no hay disponibilidad.
        
        Busca mesas disponibles en horarios cercanos (±1 hora).
        
        Args:
            solicitud: Solicitud original
        
        Returns:
            Lista de mesas alternativas (vacía por ahora, TODO)
        """
        # TODO: Implementar búsqueda de alternativas en horarios cercanos
        return []
    
    def _obtener_alternativas_cercanas(
        self,
        mesas: List[Mesa],
        num_personas: int
    ) -> List[Mesa]:
        """Obtiene alternativas cercanas a la capacidad solicitada.
        
        Retorna mesas con capacidad ±2 personas.
        
        Args:
            mesas: Lista de mesas disponibles
            num_personas: Número de comensales solicitado
        
        Returns:
            Lista de hasta 3 mesas alternativas
        """
        alternativas = [
            m for m in mesas
            if abs(m.capacidad_estandar - num_personas) <= 2
            or abs(m.capacidad_ampliada - num_personas) <= 2
        ]
        
        # Ordenar por cercanía a la capacidad solicitada
        alternativas.sort(key=lambda m: min(
            abs(m.capacidad_estandar - num_personas),
            abs(m.capacidad_ampliada - num_personas)
        ))
        
        return alternativas[:3]  # Máximo 3 alternativas
    
    def _buscar_mesa_por_id(self, mesas: List[Mesa], id_mesa: str) -> Optional[Mesa]:
        """Busca una mesa específica por su ID.
        
        Args:
            mesas: Lista de mesas disponibles
            id_mesa: ID de la mesa a buscar
        
        Returns:
            Mesa encontrada o None
        """
        for mesa in mesas:
            if mesa.id_mesa == id_mesa:
                return mesa
        return None
    
    def _validar_capacidad(self, mesa: Mesa, num_personas: int) -> bool:
        """Valida si una mesa tiene capacidad para el número de personas.
        
        Args:
            mesa: Mesa a validar
            num_personas: Número de comensales
        
        Returns:
            True si la mesa tiene capacidad suficiente
        """
        return (
            mesa.capacidad_estandar >= num_personas or
            mesa.capacidad_ampliada >= num_personas
        )
    
    def _record_to_mesa(self, record: dict) -> Mesa:
        """Convierte record de Airtable a modelo Mesa.
        
        Args:
            record: Registro de Airtable
        
        Returns:
            Modelo Mesa
        """
        fields = record.get("fields", {})
        
        # Parsear mesas auxiliares (string separado por comas)
        mesas_aux = None
        if fields.get("Mesas Auxiliares"):
            mesas_aux = [m.strip() for m in fields["Mesas Auxiliares"].split(",") if m.strip()]
        
        # Parsear mesas compatibles (string separado por comas)
        mesas_comp = None
        if fields.get("Mesas_Compatibles"):
            mesas_comp = [m.strip() for m in fields["Mesas_Compatibles"].split(",") if m.strip()]
        
        return Mesa(
            id=record.get("id"),
            id_mesa=fields.get("ID Mesa", fields.get("Nombre de Mesa", "")),
            nombre=fields.get("Nombre de Mesa", ""),
            zona=fields.get("Zona", "Sala Exterior"),
            ubicacion_detallada=fields.get("Ubicacion_Detallada", fields.get("Notas")),
            capacidad_estandar=fields.get("Capacidad", fields.get("Capacidad_Estandar", 2)),
            capacidad_ampliada=fields.get("Capacidad Ampliada", fields.get("Capacidad_Ampliada", 4)),
            mesas_auxiliares=mesas_aux,
            es_combinable=bool(fields.get("Mesas_Compatibles")),
            mesas_compatibles=mesas_comp,
            notas=fields.get("Notas"),
            orden_prioridad=fields.get("Prioridad", fields.get("Orden_Prioridad", 1)),
        )
    
    def _record_to_config(self, record: dict) -> ConfiguracionMesa:
        """Convierte record de Airtable a modelo ConfiguracionMesa.
        
        Args:
            record: Registro de Airtable
        
        Returns:
            Modelo ConfiguracionMesa
        """
        fields = record.get("fields", {})
        
        # Parsear mesas incluidas (string separado por comas)
        mesas_incluidas = []
        if fields.get("Mesas_Incluidas"):
            mesas_incluidas = [m.strip() for m in fields["Mesas_Incluidas"].split(",") if m.strip()]
        
        return ConfiguracionMesa(
            id=record.get("id"),
            id_configuracion=fields.get("ID_Configuracion", ""),
            nombre=fields.get("Nombre", ""),
            mesas_incluidas=mesas_incluidas,
            capacidad_total=fields.get("Capacidad_Total", 4),
            ubicacion=fields.get("Ubicacion", "Terraza"),
            activa=fields.get("Activa", True),
            notas=fields.get("Notas")
        )
    
    async def get_estadisticas(self) -> EstadisticasAsignacion:
        """Obtiene estadísticas del sistema de mesas.
        
        Returns:
            EstadisticasAsignacion con conteos y capacidades
        """
        try:
            # Obtener todas las mesas
            all_mesas = self.table_mesas.all()
            mesas = [self._record_to_mesa(r) for r in all_mesas]
            
            # Conteos
            total_mesas = len(mesas)
            mesas_disponibles = len([m for m in mesas if m.estado == EstadoMesa.DISPONIBLE and m.activa])
            mesas_interior = len([m for m in mesas if m.zona != ZonaMesa.TERRAZA])
            mesas_terraza = len([m for m in mesas if m.zona == ZonaMesa.TERRAZA])
            
            # Configuraciones activas
            configs = await self._get_configuraciones_activas()
            
            # Capacidad total
            capacidad_total = sum(m.capacidad_estandar for m in mesas if m.activa)
            
            return EstadisticasAsignacion(
                total_mesas=total_mesas,
                mesas_disponibles=mesas_disponibles,
                mesas_interior=mesas_interior,
                mesas_terraza=mesas_terraza,
                configuraciones_activas=len(configs),
                capacidad_total=capacidad_total
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return EstadisticasAsignacion(
                total_mesas=0,
                mesas_disponibles=0,
                mesas_interior=0,
                mesas_terraza=0,
                configuraciones_activas=0,
                capacidad_total=0
            )
    
    async def get_disponibilidad(
        self,
        fecha: str,
        hora: str,
        zona: Optional[ZonaMesa] = None
    ) -> List[DisponibilidadMesa]:
        """Obtiene disponibilidad detallada de todas las mesas.
        
        Args:
            fecha: Fecha YYYY-MM-DD
            hora: Hora HH:MM
            zona: Filtrar por zona (opcional)
        
        Returns:
            Lista de DisponibilidadMesa con estado de cada mesa
        """
        mesas = await self._get_mesas_disponibles(fecha, hora, zona)
        
        disponibilidad = []
        for mesa in mesas:
            disponibilidad.append(DisponibilidadMesa(
                mesa=mesa,
                disponible=mesa.estado == EstadoMesa.DISPONIBLE,
                motivo_no_disponibilidad=None if mesa.estado == EstadoMesa.DISPONIBLE else f"Mesa {mesa.estado.value.lower()}"
            ))
        
        return disponibilidad


# Factory function para inyección de dependencias
def get_table_assignment_service() -> TableAssignmentService:
    """Factory function para obtener instancia del servicio.
    
    Returns:
        Instancia de TableAssignmentService
    """
    return TableAssignmentService()
