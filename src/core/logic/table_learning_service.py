"""
TableLearningService - Lightweight learning from historical data.
Uses EMA (Exponential Moving Average) for online updates.
"""

from datetime import datetime, date
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# EMA smoothing factor (0.1 = slow adaptation, 0.3 = faster)
EMA_ALPHA = 0.15


@dataclass
class DurationStats:
    """Statistics for dining duration."""

    mean_minutes: float
    std_minutes: float
    sample_count: int


class TableLearningService:
    """
    Lightweight learning from historical reservation data.

    TRACKS:
    - Turn time by party_size, weekday, time_slot, zone
    - No-show rate by channel, lead_time, weekday

    Uses EMA for online updates - no ML models needed.
    """

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        # In-memory cache (would be Redis in production)
        self._turn_times: Dict[str, DurationStats] = {}
        self._no_show_rates: Dict[str, float] = {}

    def _make_key(self, *parts) -> str:
        """Create a composite key."""
        return ":".join(str(p) for p in parts)

    def get_expected_duration(
        self, party_size: int, weekday: int, time_slot: str, zone: str
    ) -> int:
        """
        Get expected dining duration in minutes.

        Args:
            party_size: Number of guests
            weekday: 0=Monday, 6=Sunday
            time_slot: "T1" or "T2"
            zone: "Interior" or "Terraza"

        Returns:
            Expected duration in minutes (default: 90)
        """
        key = self._make_key(party_size, weekday, time_slot, zone)

        if key in self._turn_times:
            return int(self._turn_times[key].mean_minutes)

        # Default estimates based on common patterns
        if party_size <= 2:
            return 75  # Couples eat faster
        elif party_size <= 4:
            return 90  # Standard
        elif party_size <= 6:
            return 105  # Groups take longer
        else:
            return 120  # Large groups

    def update_from_outcome(
        self,
        party_size: int,
        weekday: int,
        time_slot: str,
        zone: str,
        actual_duration_minutes: int,
    ) -> None:
        """
        Update duration estimate based on actual outcome.
        Uses EMA for smooth updates.
        """
        key = self._make_key(party_size, weekday, time_slot, zone)

        if key in self._turn_times:
            # EMA update
            old_stats = self._turn_times[key]
            new_mean = (
                EMA_ALPHA * actual_duration_minutes
                + (1 - EMA_ALPHA) * old_stats.mean_minutes
            )
            new_count = old_stats.sample_count + 1

            self._turn_times[key] = DurationStats(
                mean_minutes=new_mean,
                std_minutes=old_stats.std_minutes * 0.9,  # Simplified
                sample_count=new_count,
            )
        else:
            # First observation
            self._turn_times[key] = DurationStats(
                mean_minutes=float(actual_duration_minutes),
                std_minutes=15.0,  # Initial estimate
                sample_count=1,
            )

        logger.debug(
            f"Updated duration for {key}: {self._turn_times[key].mean_minutes:.1f} min"
        )

    def get_no_show_rate(
        self, channel: str, lead_time_days: int, weekday: int
    ) -> float:
        """
        Get probability of no-show.

        Args:
            channel: "VAPI", "WhatsApp", "Web", "Presencial"
            lead_time_days: Days between booking and reservation
            weekday: 0=Monday, 6=Sunday

        Returns:
            Probability of no-show (0.0 to 1.0)
        """
        # Bucket lead time
        if lead_time_days <= 1:
            lead_bucket = "same_day"
        elif lead_time_days <= 3:
            lead_bucket = "short"
        elif lead_time_days <= 7:
            lead_bucket = "medium"
        else:
            lead_bucket = "long"

        key = self._make_key(channel, lead_bucket, weekday)

        if key in self._no_show_rates:
            return self._no_show_rates[key]

        # Default estimates
        # WhatsApp confirmations reduce no-show
        defaults = {
            "VAPI:short": 0.05,
            "VAPI:medium": 0.10,
            "WhatsApp:short": 0.03,
            "WhatsApp:medium": 0.05,
            "Web:short": 0.08,
            "Web:medium": 0.12,
            "Presencial:same_day": 0.02,
        }

        return defaults.get(f"{channel}:{lead_bucket}", 0.10)

    def update_no_show_rate(
        self, channel: str, lead_time_days: int, weekday: int, was_no_show: bool
    ) -> None:
        """Update no-show rate based on outcome."""
        if lead_time_days <= 1:
            lead_bucket = "same_day"
        elif lead_time_days <= 3:
            lead_bucket = "short"
        elif lead_time_days <= 7:
            lead_bucket = "medium"
        else:
            lead_bucket = "long"

        key = self._make_key(channel, lead_bucket, weekday)

        old_rate = self._no_show_rates.get(key, 0.10)
        outcome = 1.0 if was_no_show else 0.0

        # EMA update
        self._no_show_rates[key] = EMA_ALPHA * outcome + (1 - EMA_ALPHA) * old_rate

        logger.debug(f"Updated no-show rate for {key}: {self._no_show_rates[key]:.2%}")


# Singleton
_learning_service: Optional[TableLearningService] = None


def get_learning_service(redis_client=None) -> TableLearningService:
    """Get the singleton learning service instance."""
    global _learning_service
    if _learning_service is None:
        _learning_service = TableLearningService(redis_client=redis_client)
    return _learning_service
