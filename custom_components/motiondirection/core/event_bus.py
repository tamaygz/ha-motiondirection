"""Event firing utility for Home Assistant event bus integration."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

from ..const import DOMAIN
from ..models.event_data import (
    AnomalyDetectedEventData,
    CueCorrelationDetectedEventData,
    CuePatternLearnedEventData,
    CueTriggeredEventData,
    HybridDetectionEventData,
    MotionDetectedEventData,
    PatternDetectedEventData,
    ZoneDirectionDetectedEventData,
    ZoneEnteredEventData,
    ZoneExitedEventData,
    ZonePatternDetectedEventData,
)

_LOGGER = logging.getLogger(__name__)


class EventBus:
    """Event bus wrapper for firing custom events."""
    
    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize event bus.
        
        Args:
            hass: Home Assistant instance
        """
        self.hass = hass
        self._event_counts: Dict[str, int] = {}
    
    def fire_motion_detected(
        self,
        event_data: MotionDetectedEventData,
    ) -> None:
        """Fire motion detected event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_motion_detected"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_pattern_detected(
        self,
        event_data: PatternDetectedEventData,
    ) -> None:
        """Fire pattern detected event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_pattern_detected"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_zone_entered(
        self,
        event_data: ZoneEnteredEventData,
    ) -> None:
        """Fire zone entered event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_zone_entered"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_zone_exited(
        self,
        event_data: ZoneExitedEventData,
    ) -> None:
        """Fire zone exited event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_zone_exited"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_zone_direction_detected(
        self,
        event_data: ZoneDirectionDetectedEventData,
    ) -> None:
        """Fire zone direction detected event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_zone_direction_detected"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_zone_pattern_detected(
        self,
        event_data: ZonePatternDetectedEventData,
    ) -> None:
        """Fire zone pattern detected event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_zone_pattern_detected"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_cue_triggered(
        self,
        event_data: CueTriggeredEventData,
    ) -> None:
        """Fire cue triggered event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_cue_triggered"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_hybrid_detection(
        self,
        event_data: HybridDetectionEventData,
    ) -> None:
        """Fire hybrid detection event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_hybrid_detection"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_cue_correlation_detected(
        self,
        event_data: CueCorrelationDetectedEventData,
    ) -> None:
        """Fire cue correlation detected event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_cue_correlation_detected"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_cue_pattern_learned(
        self,
        event_data: CuePatternLearnedEventData,
    ) -> None:
        """Fire cue pattern learned event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_cue_pattern_learned"
        self._fire_event(event_type, event_data.to_dict())
    
    def fire_anomaly_detected(
        self,
        event_data: AnomalyDetectedEventData,
    ) -> None:
        """Fire anomaly detected event.
        
        Args:
            event_data: Event data
        """
        event_type = f"{DOMAIN}_anomaly_detected"
        self._fire_event(event_type, event_data.to_dict())
    
    def _fire_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> None:
        """Fire event on Home Assistant event bus.
        
        Args:
            event_type: Event type name
            event_data: Event data dictionary
        """
        try:
            # Fire the event
            self.hass.bus.async_fire(event_type, event_data)
            
            # Track event count
            self._event_counts[event_type] = self._event_counts.get(event_type, 0) + 1
            
            _LOGGER.debug(
                "Fired event %s (count: %d): %s",
                event_type,
                self._event_counts[event_type],
                event_data,
            )
        except Exception as err:
            _LOGGER.error("Error firing event %s: %s", event_type, err)
    
    def get_event_counts(self) -> Dict[str, int]:
        """Get event firing counts.
        
        Returns:
            Dictionary of event types to counts
        """
        return self._event_counts.copy()
    
    def reset_event_counts(self) -> None:
        """Reset event counts."""
        self._event_counts.clear()
        _LOGGER.info("Event counts reset")


def create_timestamp() -> str:
    """Create ISO format timestamp string.
    
    Returns:
        ISO format timestamp
    """
    return datetime.now().isoformat()
