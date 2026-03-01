"""
TableTetrisEngine - Algoritmo profesional de asignación de mesas.
En Las Nubes Restobar - Sistema Cerebro

Basado en: Rule-based feasibility + Bounded search + Scoring
Learning: EMA aggregates para turn times y no-show rates
"""

from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import logging

from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ========== ENUMS Y TIPOS ==========


class ZonePreference(str, Enum):
    INTERIOR = "Interior"
    TERRAZA = "Terraza"
    NO_PREFERENCE = "Sin preferencia"


class TableStatus(str, Enum):
    LIBRE = "Libre"
    OCUPADA = "Ocupada"
    RESERVADA = "Reservada"
    BLOQUEADA = "Bloqueada"
    HOLD = "Hold"


# ========== CONFIGURACIÓN DE COMBINACIONES ==========

ALLOWED_COMBOS: List[Dict[str, Any]] = [
    {
        "id": "COMBO-10A",
        "tables": ["Mesa 7", "AUX-1"],
        "capacity_min": 8,
        "capacity_max": 10,
        "zone": "Interior",
    },
    {
        "id": "COMBO-10B",
        "tables": ["Mesa 8", "AUX-2"],
        "capacity_min": 8,
        "capacity_max": 10,
        "zone": "Interior",
    },
    {
        "id": "COMBO-10C",
        "tables": ["Mesa 9", "AUX-3"],
        "capacity_min": 8,
        "capacity_max": 10,
        "zone": "Interior",
    },
    {
        "id": "COMBO-8",
        "tables": ["Mesa 6", "AUX-4"],
        "capacity_min": 6,
        "capacity_max": 8,
        "zone": "Interior",
    },
]

SCORING_WEIGHTS = {
    "waste": 1.0,
    "combo_penalty": 2.0,
    "zone_mismatch": 3.0,
    "aux_penalty": 1.5,
    "priority": 0.5,
    "future_blocking": 1.0,
}

# Grupos >10 requieren humano
MAX_PAX_WITHOUT_HUMAN = 10


# ========== DATA CLASSES ==========


@dataclass
class TableCandidate:
    """Candidato para asignación (mesa simple o combinación)."""

    id: str
    tables: List[str]  # Lista de IDs de mesas
    capacity_min: int
    capacity_max: int
    zone: str
    is_combo: bool = False
    uses_aux: bool = False
    priority: int = 5
    notes: str = ""

    def effective_capacity(self, party_size: int) -> int:
        """Capacidad efectiva para un grupo dado."""
        if party_size <= self.capacity_max:
            return max(party_size, self.capacity_min)
        return self.capacity_max


@dataclass
class AssignmentResult:
    """Resultado de una asignación."""

    success: bool
    table_id: Optional[str] = None
    table_name: Optional[str] = None
    tables: List[str] = field(default_factory=list)  # Para combos
    zone: Optional[str] = None
    uses_combo: bool = False
    uses_aux: bool = False
    aux_table_id: Optional[str] = None
    score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    reason: Optional[str] = None
    needs_human: bool = False
    suggest_waitlist: bool = False
    hold_id: Optional[str] = None


# ========== ENGINE PRINCIPAL ==========


class TableTetrisEngine:
    """
    Algoritmo de asignación de mesas basado en scoring.

    WORKFLOW:
    1. Feasibility filter (hard constraints)
    2. Candidate generation (single tables + combos)
    3. Scoring (pick lowest score)
    4. Return result with explanation
    """

    def __init__(self, redis_client=None, weights: Dict[str, float] = None):
        self.redis_client = redis_client
        self.weights = {**SCORING_WEIGHTS, **(weights or {})}

        # Cache de mesas (en producción viene de Airtable)
        self._tables_cache: Dict[str, Dict] = {}
        self._combos_cache: List[TableCandidate] = []

        # Inicializar combinaciones
        self._init_combos()

    def _init_combos(self):
        """Inicializa las combinaciones predefinidas."""
        for combo_data in ALLOWED_COMBOS:
            self._combos_cache.append(
                TableCandidate(
                    id=combo_data["id"],
                    tables=combo_data["tables"],
                    capacity_min=combo_data["capacity_min"],
                    capacity_max=combo_data["capacity_max"],
                    zone=combo_data["zone"],
                    is_combo=True,
                    uses_aux="AUX" in str(combo_data["tables"]),
                )
            )

    def load_tables_from_dict(self, tables: List[Dict]):
        """Carga las mesas desde una lista de diccionarios."""
        for table in tables:
            self._tables_cache[table["id"]] = table

    # ========== ASIGNACIÓN PRINCIPAL ==========

    async def assign_table(
        self,
        party_size: int,
        fecha: date,
        turno: str,
        zone_preference: ZonePreference = ZonePreference.NO_PREFERENCE,
        has_pets: bool = False,
        terrace_closed: bool = False,
        available_tables: List[str] = None,
    ) -> AssignmentResult:
        """
        Asigna la mejor mesa disponible.

        Args:
            party_size: Número de comensales
            fecha: Fecha de la reserva
            turno: Turno (T1, T2)
            zone_preference: Preferencia de zona
            has_pets: Si traen mascota (terraza obligatoria)
            terrace_closed: Si la terraza está cerrada por clima
            available_tables: Lista de IDs de mesas disponibles

        Returns:
            AssignmentResult con el resultado de la asignación
        """
        warnings = []

        # ========== 1. VALIDACIÓN GRUPOS GRANDES ==========
        if party_size > MAX_PAX_WITHOUT_HUMAN:
            # Sugerir mejores combinaciones
            suggested = self._suggest_large_group_combos(party_size)
            return AssignmentResult(
                success=False,
                reason=f"Grupos de más de {MAX_PAX_WITHOUT_HUMAN} personas requieren confirmación del maître",
                needs_human=True,
                warnings=[f"Sugerencias: {', '.join(suggested)}"],
            )

        # ========== 2. RESTRICCIÓN MASCOTAS ==========
        if has_pets:
            zone_preference = ZonePreference.TERRAZA
            warnings.append("Mascota: solo mesa en terraza")

        # ========== 3. VERIFICAR TERRAZA CERRADA ==========
        if terrace_closed and zone_preference == ZonePreference.TERRAZA:
            if has_pets:
                return AssignmentResult(
                    success=False,
                    reason="Terraza cerrada por clima, pero mascota requiere terraza",
                    warnings=["Contactar cliente para opciones"],
                    needs_human=True,
                )
            else:
                zone_preference = ZonePreference.INTERIOR
                warnings.append("Terraza cerrada - asignando interior")

        # ========== 4. GENERAR CANDIDATOS ==========
        candidates = self._generate_candidates(
            party_size=party_size,
            zone_preference=zone_preference,
            available_tables=available_tables or [],
        )

        if not candidates:
            return AssignmentResult(
                success=False,
                reason="No hay mesas disponibles para ese número de personas",
                suggest_waitlist=True,
                warnings=warnings,
            )

        # ========== 5. SCORING Y SELECCIÓN ==========
        best_candidate, score, breakdown = self._score_and_select(
            candidates=candidates,
            party_size=party_size,
            zone_preference=zone_preference,
        )

        # ========== 6. GENERAR RESULTADO ==========
        result = AssignmentResult(
            success=True,
            table_id=best_candidate.id,
            table_name=best_candidate.id if not best_candidate.is_combo else None,
            tables=best_candidate.tables,
            zone=best_candidate.zone,
            uses_combo=best_candidate.is_combo,
            uses_aux=best_candidate.uses_aux,
            aux_table_id=best_candidate.tables[1]
            if best_candidate.uses_aux and len(best_candidate.tables) > 1
            else None,
            score=score,
            score_breakdown=breakdown,
            warnings=warnings + self._get_table_warnings(best_candidate),
        )

        # ========== 7. CREAR HOLD EN REDIS (si disponible) ==========
        if self.redis_client:
            hold_id = await self._create_hold(
                table_ids=best_candidate.tables,
                fecha=fecha,
                turno=turno,
                party_size=party_size,
            )
            result.hold_id = hold_id

        return result

    # ========== GENERACIÓN DE CANDIDATOS ==========

    def _generate_candidates(
        self,
        party_size: int,
        zone_preference: ZonePreference,
        available_tables: List[str],
    ) -> List[TableCandidate]:
        """Genera candidatos viables para el grupo."""
        candidates = []

        # 1. Mesas simples
        for table_id, table_data in self._tables_cache.items():
            if available_tables and table_id not in available_tables:
                continue

            # Filtro de zona
            if zone_preference != ZonePreference.NO_PREFERENCE:
                if table_data.get("zona") != zone_preference.value:
                    continue

            # Filtro de capacidad
            cap_max = table_data.get("capacidad_max", table_data.get("Capacidad", 0))
            cap_min = table_data.get("capacidad_min", 1)

            if cap_max >= party_size:
                candidates.append(
                    TableCandidate(
                        id=table_id,
                        tables=[table_id],
                        capacity_min=cap_min,
                        capacity_max=cap_max,
                        zone=table_data.get("zona", "Interior"),
                        is_combo=False,
                        uses_aux=False,
                        priority=table_data.get("prioridad", 5),
                        notes=table_data.get("notas", ""),
                    )
                )

        # 2. Combinaciones (solo si party_size > capacidad máxima de mesas simples)
        max_single_capacity = max((c.capacity_max for c in candidates), default=0)

        if party_size > max_single_capacity or not candidates:
            for combo in self._combos_cache:
                # Filtro de disponibilidad
                if available_tables:
                    if not all(t in available_tables for t in combo.tables):
                        continue

                # Filtro de zona
                if zone_preference != ZonePreference.NO_PREFERENCE:
                    if combo.zone != zone_preference.value:
                        continue

                # Filtro de capacidad
                if combo.capacity_max >= party_size:
                    candidates.append(combo)

        return candidates

    # ========== SCORING ==========

    def _score_and_select(
        self,
        candidates: List[TableCandidate],
        party_size: int,
        zone_preference: ZonePreference,
    ) -> Tuple[TableCandidate, float, Dict[str, float]]:
        """
        Calcula scores y selecciona el mejor candidato.

        SCORING FUNCTION:
        score = w1*waste + w2*combo_penalty + w3*zone_mismatch +
                w4*aux_penalty + w5*priority + w6*future_blocking
        """
        best_candidate = None
        best_score = float("inf")
        best_breakdown = {}

        for candidate in candidates:
            breakdown = {}

            # 1. Waste (desperdicio de capacidad)
            waste = candidate.capacity_max - party_size
            breakdown["waste"] = waste * self.weights["waste"]

            # 2. Combo penalty
            combo_penalty = 5.0 if candidate.is_combo else 0.0
            breakdown["combo_penalty"] = combo_penalty * self.weights["combo_penalty"]

            # 3. Zone mismatch
            zone_mismatch = 0.0
            if zone_preference != ZonePreference.NO_PREFERENCE:
                if candidate.zone != zone_preference.value:
                    zone_mismatch = 10.0
            breakdown["zone_mismatch"] = zone_mismatch * self.weights["zone_mismatch"]

            # 4. Aux penalty
            aux_penalty = 3.0 if candidate.uses_aux else 0.0
            breakdown["aux_penalty"] = aux_penalty * self.weights["aux_penalty"]

            # 5. Priority (lower is better)
            breakdown["priority"] = candidate.priority * self.weights["priority"]

            # 6. Future blocking (simplified: penalize large tables for small groups)
            future_blocking = 0.0
            if party_size <= 2 and candidate.capacity_max >= 6:
                future_blocking = 5.0
            elif party_size <= 4 and candidate.capacity_max >= 8:
                future_blocking = 3.0
            breakdown["future_blocking"] = (
                future_blocking * self.weights["future_blocking"]
            )

            # Score total
            total_score = sum(breakdown.values())

            if total_score < best_score:
                best_score = total_score
                best_candidate = candidate
                best_breakdown = breakdown

        return best_candidate, best_score, best_breakdown

    # ========== UTILIDADES ==========

    def _suggest_large_group_combos(self, party_size: int) -> List[str]:
        """Sugiere combinaciones para grupos grandes."""
        suggestions = []
        for combo in self._combos_cache:
            if combo.capacity_max >= party_size:
                suggestions.append(f"{combo.id} ({combo.capacity_max} personas)")
        return suggestions[:3]  # Top 3

    def _get_table_warnings(self, candidate: TableCandidate) -> List[str]:
        """Genera warnings para una mesa."""
        warnings = []

        if candidate.notes:
            warnings.append(f"⚠️ {candidate.notes}")

        if candidate.zone == "Terraza":
            warnings.append("🌤️ Mesa en terraza (clima dependiente)")

        if candidate.uses_aux:
            warnings.append("🔧 Requiere mesa auxiliar")

        return warnings

    # ========== REDIS HOLD ==========

    async def _create_hold(
        self, table_ids: List[str], fecha: date, turno: str, party_size: int
    ) -> Optional[str]:
        """
        Crea un hold temporal en Redis para prevenir double-booking.

        TTL: 5 minutos (tiempo para confirmar la reserva)
        """
        if not self.redis_client:
            return None

        hold_id = self._generate_hold_id(table_ids, fecha, turno)
        hold_key = f"hold:{fecha.isoformat()}:{turno}:{hold_id}"

        hold_data = {
            "table_ids": json.dumps(table_ids),
            "party_size": party_size,
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending",
        }

        try:
            # Set con TTL de 5 minutos
            await self.redis_client.setex(
                hold_key,
                300,  # 5 minutos
                json.dumps(hold_data),
            )
            logger.info(f"Created hold {hold_id} for tables {table_ids}")
            return hold_id
        except Exception as e:
            logger.error(f"Failed to create hold: {e}")
            return None

    def _generate_hold_id(self, table_ids: List[str], fecha: date, turno: str) -> str:
        """Genera un ID único para el hold."""
        data = f"{fecha.isoformat()}:{turno}:{':'.join(sorted(table_ids))}"
        return hashlib.md5(data.encode()).hexdigest()[:12]

    async def confirm_hold(self, hold_id: str, fecha: date, turno: str) -> bool:
        """Confirma un hold, convirtiéndolo en reserva permanente."""
        if not self.redis_client:
            return True

        hold_key = f"hold:{fecha.isoformat()}:{turno}:{hold_id}"

        try:
            hold_data = await self.redis_client.get(hold_key)
            if not hold_data:
                return False

            data = json.loads(hold_data)
            data["status"] = "confirmed"

            # Extender TTL a 24 horas para reservas confirmadas
            await self.redis_client.setex(
                hold_key,
                86400,  # 24 horas
                json.dumps(data),
            )
            return True
        except Exception as e:
            logger.error(f"Failed to confirm hold: {e}")
            return False

    async def release_hold(self, hold_id: str, fecha: date, turno: str) -> bool:
        """Libera un hold (cancelación o timeout)."""
        if not self.redis_client:
            return True

        hold_key = f"hold:{fecha.isoformat()}:{turno}:{hold_id}"

        try:
            await self.redis_client.delete(hold_key)
            return True
        except Exception as e:
            logger.error(f"Failed to release hold: {e}")
            return False


# ========== SINGLETON ==========

_engine_instance: Optional[TableTetrisEngine] = None


def get_tetris_engine(redis_client=None) -> TableTetrisEngine:
    """Obtiene la instancia singleton del engine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = TableTetrisEngine(redis_client=redis_client)
    return _engine_instance
