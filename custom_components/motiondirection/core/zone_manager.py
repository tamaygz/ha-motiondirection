"""Zone manager for trigger zone detection and transitions."""
from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ..models import (
    DirectionConfig,
    MotionPath,
    MotionSequence,
    TriggerZone,
    ZoneTransition,
)

_LOGGER = logging.getLogger(__name__)


class TriggerZoneManager:
    """Manages trigger zones and their directional detection.
    
    Handles zone transition detection, direction matching, and zone
    state management. Tracks active transits and calculates dwell times.
    
    Attributes:
        zones: Dictionary of zone_id -> TriggerZone
        active_transits: Dictionary tracking ongoing zone transits
    """
    
    def __init__(self, zones: List[TriggerZone] | None = None) -> None:
        """Initialize zone manager.
        
        Args:
            zones: List of trigger zones
        """
        self.zones: Dict[str, TriggerZone] = {}
        self.active_transits: Dict[str, Dict] = {}
        
        if zones:
            for zone in zones:
                self.add_zone(zone)
        
        _LOGGER.info("TriggerZoneManager initialized with %d zones", len(self.zones))
    
    def add_zone(self, zone: TriggerZone) -> None:
        """Add zone to manager.
        
        Args:
            zone: Zone to add
        """
        self.zones[zone.id] = zone
        _LOGGER.info("Added zone: %s", zone.name)
    
    def remove_zone(self, zone_id: str) -> bool:
        """Remove zone from manager.
        
        Args:
            zone_id: Zone identifier
        
        Returns:
            True if zone was removed
        """
        if zone_id in self.zones:
            del self.zones[zone_id]
            _LOGGER.info("Removed zone: %s", zone_id)
            return True
        
        return False
    
    def get_zone(self, zone_id: str) -> TriggerZone | None:
        """Get zone by ID.
        
        Args:
            zone_id: Zone identifier
        
        Returns:
            Zone or None if not found
        """
        return self.zones.get(zone_id)
    
    def detect_zone_transition(
        self,
        motion_path: MotionPath,
        zone: TriggerZone,
    ) -> Optional[ZoneTransition]:
        """Detects if motion path crosses zone and determines direction.
        
        Args:
            motion_path: Path of motion events
            zone: Zone to check for transition
        
        Returns:
            ZoneTransition if detected, None otherwise
        """
        if not motion_path.points or len(motion_path.points) < 2:
            return None
        
        # Find entry and exit points
        entry_point = self._find_entry_point(motion_path, zone)
        exit_point = self._find_exit_point(motion_path, zone)
        
        if not entry_point or not exit_point:
            return None
        
        # Calculate direction vector through zone
        direction_vector = (
            exit_point[0] - entry_point[0],
            exit_point[1] - entry_point[1],
        )
        
        # Normalize
        magnitude = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
        if magnitude == 0:
            return None
        
        normalized_vector = (
            direction_vector[0] / magnitude,
            direction_vector[1] / magnitude,
        )
        
        # Match to known directions
        best_match = self._match_direction(zone, normalized_vector)
        
        if not best_match:
            return None
        
        # Calculate dwell time
        dwell_time = self._calculate_dwell_time(motion_path, zone)
        
        # Calculate confidence
        confidence = self._calculate_zone_confidence(
            zone,
            motion_path,
            dwell_time,
        )
        
        # Get entry and exit times
        entry_time = motion_path.points[0].timestamp if motion_path.points else None
        exit_time = motion_path.points[-1].timestamp if motion_path.points else None
        
        # Get triggered sensors
        triggered_sensors = [
            point.sensor_id
            for point in motion_path.points
            if point.sensor_id
        ]
        
        # Create transition
        transition = ZoneTransition(
            zone_id=zone.id,
            direction=best_match,
            entry_point=entry_point,
            exit_point=exit_point,
            dwell_time=dwell_time,
            confidence=confidence,
            entry_time=entry_time,
            exit_time=exit_time,
            triggered_sensors=triggered_sensors,
        )
        
        _LOGGER.info(
            "Zone transition detected: %s -> %s (dwell=%dms, conf=%.2f)",
            zone.name,
            best_match,
            dwell_time,
            confidence,
        )
        
        return transition
    
    def detect_zone_transitions_for_sequence(
        self,
        sequence: MotionSequence,
    ) -> List[ZoneTransition]:
        """Detect zone transitions for entire motion sequence.
        
        Args:
            sequence: Motion sequence
        
        Returns:
            List of detected transitions
        """
        transitions: list[ZoneTransition] = []
        
        # Convert sequence to motion path
        # This would require creating PathPoints from MotionEvents
        # For now, we'll return empty list as this requires more integration
        
        _LOGGER.debug("Checking %d zones for transitions", len(self.zones))
        
        return transitions
    
    def _find_entry_point(
        self,
        motion_path: MotionPath,
        zone: TriggerZone,
    ) -> Optional[Tuple[float, float]]:
        """Find where path enters zone.
        
        Args:
            motion_path: Motion path
            zone: Zone to check
        
        Returns:
            Entry point or None
        """
        for i, point in enumerate(motion_path.points):
            if zone.contains_point(point.position):
                # This is first point inside zone
                if i == 0:
                    # Path starts in zone
                    return point.position
                else:
                    # Interpolate entry point on zone boundary
                    prev_point = motion_path.points[i - 1]
                    return self._interpolate_boundary_crossing(
                        prev_point.position,
                        point.position,
                        zone,
                    )
        
        return None
    
    def _find_exit_point(
        self,
        motion_path: MotionPath,
        zone: TriggerZone,
    ) -> Optional[Tuple[float, float]]:
        """Find where path exits zone.
        
        Args:
            motion_path: Motion path
            zone: Zone to check
        
        Returns:
            Exit point or None
        """
        # Scan backwards to find last point in zone
        for i in range(len(motion_path.points) - 1, -1, -1):
            point = motion_path.points[i]
            
            if zone.contains_point(point.position):
                # This is last point inside zone
                if i == len(motion_path.points) - 1:
                    # Path ends in zone
                    return point.position
                else:
                    # Interpolate exit point on zone boundary
                    next_point = motion_path.points[i + 1]
                    return self._interpolate_boundary_crossing(
                        point.position,
                        next_point.position,
                        zone,
                    )
        
        return None
    
    def _interpolate_boundary_crossing(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float],
        zone: TriggerZone,
    ) -> Tuple[float, float]:
        """Interpolate where path crosses zone boundary.
        
        Uses binary search to find approximate crossing point.
        
        Args:
            point1: Point outside zone
            point2: Point inside zone
            zone: Zone
        
        Returns:
            Approximate boundary crossing point
        """
        # Binary search for crossing point
        for _ in range(10):  # 10 iterations gives good precision
            mid_x = (point1[0] + point2[0]) / 2
            mid_y = (point1[1] + point2[1]) / 2
            mid_point = (mid_x, mid_y)
            
            if zone.contains_point(mid_point):
                point2 = mid_point
            else:
                point1 = mid_point
        
        # Return midpoint
        return ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)
    
    def _match_direction(
        self,
        zone: TriggerZone,
        vector: Tuple[float, float],
    ) -> Optional[str]:
        """Match vector to zone's known directions.
        
        Args:
            zone: Zone with known directions
            vector: Direction vector to match
        
        Returns:
            Best matching direction name or None
        """
        if not zone.known_directions:
            return None
        
        best_match = None
        best_score = float('inf')
        
        for direction_config in zone.known_directions:
            # Calculate angle difference
            dot_product = (
                direction_config.vector[0] * vector[0]
                + direction_config.vector[1] * vector[1]
            )
            
            # Clamp to [-1, 1] to avoid math domain errors
            dot_product = max(-1.0, min(1.0, dot_product))
            
            angle = math.acos(dot_product)
            angle_degrees = math.degrees(angle)
            
            # Check if within tolerance
            if angle_degrees < best_score:
                best_score = angle_degrees
                best_match = direction_config.name
        
        # Use 30 degree tolerance
        if best_match and best_score <= 30.0:
            return best_match
        
        return None
    
    def _calculate_dwell_time(
        self,
        motion_path: MotionPath,
        zone: TriggerZone,
    ) -> int:
        """Calculate time spent in zone.
        
        Args:
            motion_path: Motion path
            zone: Zone
        
        Returns:
            Dwell time in milliseconds
        """
        entry_time = None
        exit_time = None
        
        for point in motion_path.points:
            if zone.contains_point(point.position):
                if entry_time is None:
                    entry_time = point.timestamp
                exit_time = point.timestamp
        
        if entry_time and exit_time:
            delta = (exit_time - entry_time).total_seconds() * 1000
            return int(delta)
        
        return 0
    
    def _calculate_zone_confidence(
        self,
        zone: TriggerZone,
        motion_path: MotionPath,
        dwell_time: int,
    ) -> float:
        """Calculate confidence for zone transition.
        
        Factors:
        - Dwell time (longer = more confident)
        - Number of points in zone
        - Path linearity through zone
        
        Args:
            zone: Zone
            motion_path: Motion path
            dwell_time: Time in zone (ms)
        
        Returns:
            Confidence score (0-1)
        """
        # Factor 1: Dwell time confidence
        if dwell_time < zone.min_dwell_time:
            dwell_confidence = dwell_time / zone.min_dwell_time
        else:
            dwell_confidence = 1.0
        
        # Factor 2: Point count confidence
        points_in_zone = sum(
            1 for point in motion_path.points
            if zone.contains_point(point.position)
        )
        point_confidence = min(points_in_zone / 3.0, 1.0)
        
        # Factor 3: Path confidence (from motion path)
        path_confidence = motion_path.confidence if motion_path.confidence else 0.7
        
        # Combine factors
        confidence = (
            dwell_confidence * 0.3
            + point_confidence * 0.3
            + path_confidence * 0.4
        )
        
        return max(0.0, min(confidence, 1.0))
    
    def get_zones_at_point(
        self,
        point: Tuple[float, float],
    ) -> List[TriggerZone]:
        """Get all zones containing a point.
        
        Args:
            point: Point to check
        
        Returns:
            List of zones containing point
        """
        return [
            zone
            for zone in self.zones.values()
            if zone.contains_point(point)
        ]
    
    def get_zone_count(self) -> int:
        """Get number of zones.
        
        Returns:
            Zone count
        """
        return len(self.zones)
