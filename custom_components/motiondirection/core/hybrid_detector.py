"""Hybrid motion detector combining sensors with secondary cues."""
from __future__ import annotations

import logging
import math
from collections import deque
from datetime import datetime
from typing import Deque, Dict, List, Optional, Tuple

from homeassistant.core import HomeAssistant, callback

from ..models import (
    DirectionResult,
    DirectionalHint,
    MotionEvent,
    SecondaryCue,
    StateChange,
)
from .cue_type_registry import CueTypeRegistry

_LOGGER = logging.getLogger(__name__)


class CueEvent:
    """Represents a secondary cue state change event.
    
    Attributes:
        cue: Secondary cue configuration
        timestamp: When event occurred
        old_state: Previous state
        new_state: New state
        entity_id: Entity that triggered
    """
    
    def __init__(
        self,
        cue: SecondaryCue,
        timestamp: datetime,
        old_state: str,
        new_state: str,
        entity_id: str,
    ) -> None:
        """Initialize cue event."""
        self.cue = cue
        self.timestamp = timestamp
        self.old_state = old_state
        self.new_state = new_state
        self.entity_id = entity_id


class HybridMotionDetector:
    """Combines motion sensors and secondary cues for direction detection.
    
    Uses temporal and spatial correlation to combine motion sensor events
    with secondary cues (doors, lights, etc.) for improved direction
    detection, especially with single motion sensors.
    
    Attributes:
        hass: Home Assistant instance
        motion_buffer: Recent motion events
        cue_buffer: Recent cue events
        cues: Dictionary of configured secondary cues
    """
    
    def __init__(
        self,
        hass: HomeAssistant,
        cues: Dict[str, SecondaryCue] | None = None,
    ) -> None:
        """Initialize hybrid detector.
        
        Args:
            hass: Home Assistant instance
            cues: Dictionary of cue_id -> SecondaryCue
        """
        self.hass = hass
        self.motion_buffer: Deque[MotionEvent] = deque(maxlen=100)
        self.cue_buffer: Deque[CueEvent] = deque(maxlen=200)
        self.cues: Dict[str, SecondaryCue] = cues or {}
        
        _LOGGER.info(
            "HybridMotionDetector initialized with %d cues",
            len(self.cues),
        )
    
    def add_cue(self, cue: SecondaryCue) -> None:
        """Add secondary cue.
        
        Args:
            cue: Secondary cue configuration
        """
        self.cues[cue.id] = cue
        _LOGGER.info("Added secondary cue: %s (%s)", cue.id, cue.cue_type)
    
    def remove_cue(self, cue_id: str) -> bool:
        """Remove secondary cue.
        
        Args:
            cue_id: Cue identifier
        
        Returns:
            True if cue was removed
        """
        if cue_id in self.cues:
            del self.cues[cue_id]
            _LOGGER.info("Removed secondary cue: %s", cue_id)
            return True
        
        return False
    
    @callback
    def process_cue_event(
        self,
        cue_id: str,
        old_state: str,
        new_state: str,
        timestamp: datetime | None = None,
    ) -> None:
        """Process secondary cue state change.
        
        Args:
            cue_id: Cue identifier
            old_state: Previous state
            new_state: New state
            timestamp: Event timestamp (defaults to now)
        """
        cue = self.cues.get(cue_id)
        if not cue:
            _LOGGER.warning("Unknown cue: %s", cue_id)
            return
        
        # Create cue event
        cue_event = CueEvent(
            cue=cue,
            timestamp=timestamp or datetime.now(),
            old_state=old_state,
            new_state=new_state,
            entity_id=cue.entity_id,
        )
        
        # Add to buffer
        self.cue_buffer.append(cue_event)
        
        _LOGGER.debug(
            "Cue event: %s %s->%s",
            cue_id,
            old_state,
            new_state,
        )
    
    async def process_motion_event(
        self,
        event: MotionEvent,
    ) -> Optional[DirectionResult]:
        """Process motion sensor event with cue correlation.
        
        Args:
            event: Motion event
        
        Returns:
            Direction result or None
        """
        # Add to buffer
        self.motion_buffer.append(event)
        
        # Find correlated cues (using dynamic time windows per cue type)
        correlated_cues = self._find_correlated_cues_dynamic(event)
        
        # Determine detection method
        if len(self.motion_buffer) >= 2:
            # Multi-sensor detection would be handled by MotionDetector
            # This is hybrid/cue-assisted mode
            if correlated_cues:
                result = self._calculate_hybrid_direction(event, correlated_cues)
                if result:
                    _LOGGER.info(
                        "Hybrid detection: %s (conf=%.2f, cues=%d)",
                        result.direction,
                        result.confidence,
                        len(correlated_cues),
                    )
                    return result
        
        elif correlated_cues:
            # Single motion + cues (cue-assisted)
            result = self._calculate_hybrid_direction(event, correlated_cues)
            if result:
                result.method = "cue_assisted"
                _LOGGER.info(
                    "Cue-assisted detection: %s (conf=%.2f, cues=%d)",
                    result.direction,
                    result.confidence,
                    len(correlated_cues),
                )
                return result
        
        return None
    
    def _calculate_hybrid_direction(
        self,
        motion: MotionEvent,
        cues: List[CueEvent],
    ) -> Optional[DirectionResult]:
        """Calculate direction using motion + secondary cues.
        
        Args:
            motion: Motion event
            cues: Correlated cue events
        
        Returns:
            Direction result or None
        """
        direction_votes: Dict[str, float] = {}
        total_confidence = 0.0
        contributing_cues = []
        
        # Collect direction votes from cues
        for cue_event in cues:
            for hint in cue_event.cue.directional_hints:
                if self._matches_state_change(cue_event, hint.state_change):
                    direction = hint.implied_direction
                    
                    # Calculate confidence from multiple factors
                    confidence = (
                        hint.confidence
                        * cue_event.cue.confidence_weight
                        * cue_event.cue.reliability
                    )
                    
                    # Add vote
                    if direction not in direction_votes:
                        direction_votes[direction] = 0.0
                    
                    direction_votes[direction] += confidence
                    total_confidence += confidence
                    contributing_cues.append(cue_event.cue.id)
        
        # Find winner
        if direction_votes:
            best_direction = max(
                direction_votes.items(),
                key=lambda x: x[1],
            )
            
            final_confidence = (
                best_direction[1] / total_confidence
                if total_confidence > 0
                else 0.0
            )
            
            return DirectionResult(
                direction=best_direction[0],
                confidence=final_confidence,
                method="hybrid",
                contributing_cues=contributing_cues,
                motion_sensor_id=motion.sensor.entity_id,
                timestamp=motion.timestamp,
            )
        
        return None
    
    def _find_correlated_cues_dynamic(
        self,
        motion: MotionEvent,
    ) -> List[CueEvent]:
        """Find cues that correlate with motion event using type-specific windows.
        
        Uses the CueTypeRegistry to get appropriate correlation windows for each
        cue type, improving accuracy by respecting the typical response times
        of different cue types.
        
        Args:
            motion: Motion event
        
        Returns:
            List of correlated cue events
        """
        correlated = []
        motion_time = motion.timestamp
        
        for cue_event in self.cue_buffer:
            # Get cue-type-specific correlation window from registry
            time_window = CueTypeRegistry.get_correlation_window(
                cue_event.cue.cue_type
            )
            
            # Check temporal correlation
            time_diff = abs(
                (cue_event.timestamp - motion_time).total_seconds() * 1000
            )
            
            if time_diff <= time_window:
                # Check spatial correlation
                if self._is_spatially_correlated(motion, cue_event):
                    correlated.append(cue_event)
                    _LOGGER.debug(
                        "Cue %s correlated (type=%s, window=%dms, diff=%.0fms)",
                        cue_event.cue.id,
                        cue_event.cue.cue_type,
                        time_window,
                        time_diff,
                    )
        
        return correlated
    
    def _find_correlated_cues(
        self,
        motion: MotionEvent,
        time_window: int,
    ) -> List[CueEvent]:
        """Find cues that correlate with motion event.
        
        Uses temporal and spatial correlation with a fixed time window.
        Deprecated: Use _find_correlated_cues_dynamic() instead.
        
        Args:
            motion: Motion event
            time_window: Time window in milliseconds
        
        Returns:
            List of correlated cue events
        """
        correlated = []
        motion_time = motion.timestamp
        
        for cue_event in self.cue_buffer:
            # Check temporal correlation
            time_diff = abs(
                (cue_event.timestamp - motion_time).total_seconds() * 1000
            )
            
            if time_diff <= time_window:
                # Check spatial correlation
                if self._is_spatially_correlated(motion, cue_event):
                    correlated.append(cue_event)
        
        return correlated
    
    def _is_spatially_correlated(
        self,
        motion: MotionEvent,
        cue: CueEvent,
    ) -> bool:
        """Check if cue is near enough to motion to be relevant.
        
        Args:
            motion: Motion event
            cue: Cue event
        
        Returns:
            True if spatially correlated
        """
        # Calculate distance
        distance = self._calculate_distance(
            motion.sensor.position,
            cue.cue.position,
        )
        
        # Get threshold for cue type
        threshold = self._get_correlation_distance(cue.cue.cue_type)
        
        return distance <= threshold
    
    @staticmethod
    def _calculate_distance(
        pos1: Tuple[float, float],
        pos2: Tuple[float, float],
    ) -> float:
        """Calculate Euclidean distance between two positions.
        
        Args:
            pos1: First position
            pos2: Second position
        
        Returns:
            Distance
        """
        return math.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
    
    @staticmethod
    def _get_correlation_distance(cue_type: str) -> float:
        """Get maximum correlation distance for cue type.
        
        Different cue types have different effective ranges.
        
        Args:
            cue_type: Type of cue
        
        Returns:
            Maximum distance in floorplan units
        """
        distances = {
            "door": 50.0,
            "light": 100.0,
            "switch": 80.0,
            "presence": 200.0,
            "temperature": 150.0,
            "vibration": 30.0,
            "power": 100.0,
            "media": 150.0,
        }
        return distances.get(cue_type, 100.0)
    
    @staticmethod
    def _matches_state_change(
        cue_event: CueEvent,
        expected: StateChange,
    ) -> bool:
        """Check if cue event matches expected state change.
        
        Args:
            cue_event: Actual cue event
            expected: Expected state change
        
        Returns:
            True if matches
        """
        # Check from_state if specified
        if expected.from_state and cue_event.old_state != expected.from_state:
            return False
        
        # Check to_state (always required)
        if cue_event.new_state != expected.to_state:
            return False
        
        return True
    
    def get_cue_count(self) -> int:
        """Get number of configured cues.
        
        Returns:
            Cue count
        """
        return len(self.cues)
    
    def clear_buffers(self) -> None:
        """Clear event buffers."""
        self.motion_buffer.clear()
        self.cue_buffer.clear()
        _LOGGER.info("Cleared event buffers")
