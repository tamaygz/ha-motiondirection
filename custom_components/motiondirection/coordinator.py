"""DataUpdateCoordinator for Motion Direction integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .core import (
    EventBus,
    FloorplanManager,
    HybridMotionDetector,
    MotionDetector,
    PatternAnalyzer,
    TriggerZoneManager,
)
from .core.event_bus import create_timestamp
from .models import (
    DirectionResult,
    HybridDetectionEventData,
    MotionDetectedEventData,
    MotionEvent,
    PatternDetectedEventData,
)

_LOGGER = logging.getLogger(__name__)


class MotionDirectionCoordinator(DataUpdateCoordinator):
    """Coordinator to manage motion direction data updates.
    
    Coordinates between motion detection engines, pattern analysis,
    zone management, and entity updates.
    
    Attributes:
        motion_detector: Core motion detection engine
        hybrid_detector: Hybrid detection with secondary cues
        pattern_analyzer: Pattern recognition engine
        floorplan_manager: Floorplan and sensor management
        zone_manager: Trigger zone management
        last_direction: Last detected direction result
        last_pattern: Last detected pattern type
        motion_detected: Current motion detection state
        anomaly_detected: Current anomaly state
    """
    
    def __init__(
        self,
        hass: HomeAssistant,
        floorplan_id: str,
    ) -> None:
        """Initialize coordinator.
        
        Args:
            hass: Home Assistant instance
            floorplan_id: ID of the floorplan to coordinate
        """
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{floorplan_id}",
            update_interval=timedelta(seconds=1),
        )
        
        self.floorplan_id = floorplan_id
        
        # Initialize event bus
        self.event_bus = EventBus(hass)
        
        # Initialize managers
        self.floorplan_manager = FloorplanManager(hass, floorplan_id)
        self.zone_manager = TriggerZoneManager(hass)
        self.motion_detector = MotionDetector(hass, sensors={})  # Sensors added later
        self.hybrid_detector = HybridMotionDetector(hass)
        self.pattern_analyzer = PatternAnalyzer()
        
        # State tracking
        self.last_direction: DirectionResult | None = None
        self.last_pattern: str | None = None
        self.motion_detected: bool = False
        self.anomaly_detected: bool = False
        self.active_zones: list[str] = []
        self.last_sequence: Any | None = None  # Last motion sequence for anomaly detection
        self._recent_events: list[Any] = []  # Recent motion events for sequence building
        
        _LOGGER.info(
            "MotionDirectionCoordinator initialized for floorplan: %s",
            floorplan_id,
        )
    
    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from motion detection engines.
        
        Returns:
            Dictionary of current state data
            
        Raises:
            UpdateFailed: If update fails
        """
        try:
            return {
                "last_direction": self.last_direction,
                "last_pattern": self.last_pattern,
                "motion_detected": self.motion_detected,
                "anomaly_detected": self.anomaly_detected,
                "active_zones": self.active_zones,
                "timestamp": datetime.now(),
            }
        except Exception as err:
            raise UpdateFailed(f"Error updating motion direction data: {err}") from err
    
    @callback
    async def async_process_motion_event(
        self,
        event: MotionEvent,
    ) -> None:
        """Process a motion sensor event.
        
        Args:
            event: Motion event to process
        """
        try:
            # Process with hybrid detector
            result = await self.hybrid_detector.process_motion_event(event)
            
            if result:
                self.last_direction = result
                self.motion_detected = True
                
                # Fire motion detected event
                motion_event_data = MotionDetectedEventData(
                    direction=result.direction,
                    confidence=result.confidence,
                    detection_method=result.method,
                    timestamp=create_timestamp(),
                    vector=list(result.vector) if result.vector else None,
                    speed=result.speed,
                    triggered_sensors=[result.motion_sensor_id] if result.motion_sensor_id else [],
                    contributing_cues=result.contributing_cues,
                    cue_confidence=len(result.contributing_cues) * 0.1,  # Simplified calculation
                )
                self.event_bus.fire_motion_detected(motion_event_data)
                
                # Fire hybrid detection event if cues were used
                if result.is_hybrid_detection and result.contributing_cues:
                    hybrid_event_data = HybridDetectionEventData(
                        direction=result.direction,
                        motion_confidence=result.confidence,
                        cue_confidence=len(result.contributing_cues) * 0.1,
                        combined_confidence=result.confidence,
                        timestamp=create_timestamp(),
                        motion_sensor=result.motion_sensor_id,
                        contributing_cues=result.contributing_cues,
                    )
                    self.event_bus.fire_hybrid_detection(hybrid_event_data)
                
                # Check zones - use detect_zone_transition method
                # Note: Would need path data for full zone transition detection
                # For now, just check if position is in any zone
                self.active_zones = []
                
                # Analyze pattern
                # Note: Would need to build sequence from events
                # For now, just mark as detected
                self.last_pattern = "linear"  # Placeholder
                
                # Request update
                await self.async_request_refresh()
                
                _LOGGER.debug(
                    "Processed motion event: direction=%s, confidence=%.2f",
                    result.direction,
                    result.confidence,
                )
            
        except Exception as err:
            _LOGGER.error("Error processing motion event: %s", err)
    
    @callback
    def set_motion_state(self, detected: bool) -> None:
        """Set motion detected state.
        
        Args:
            detected: Motion detection state
        """
        if self.motion_detected != detected:
            self.motion_detected = detected
            self.async_set_updated_data(self.data)
    
    @callback
    def set_anomaly_state(self, detected: bool) -> None:
        """Set anomaly detected state.
        
        Args:
            detected: Anomaly detection state
        """
        if self.anomaly_detected != detected:
            self.anomaly_detected = detected
            self.async_set_updated_data(self.data)
    
    async def async_clear_history(self) -> None:
        """Clear motion history."""
        self.pattern_analyzer.clear_history()
        self.pattern_analyzer.clear_learned_patterns()
        
        self.last_direction = None
        self.last_pattern = None
        self.motion_detected = False
        self.anomaly_detected = False
        self.active_zones = []
        
        await self.async_request_refresh()
        
        _LOGGER.info("Motion history cleared for floorplan: %s", self.floorplan_id)
    
    async def async_calibrate(self, duration: int = 300) -> None:
        """Run calibration routine.
        
        Args:
            duration: Calibration duration in seconds
        """
        _LOGGER.info(
            "Starting calibration for floorplan %s (%d seconds)",
            self.floorplan_id,
            duration,
        )
        
        # Placeholder for calibration logic
        # Would involve collecting motion events and adjusting parameters
        
        _LOGGER.info("Calibration complete for floorplan: %s", self.floorplan_id)
    
    def get_zone_manager(self) -> TriggerZoneManager:
        """Get zone manager instance.
        
        Returns:
            Zone manager
        """
        return self.zone_manager
    
    def get_floorplan_manager(self) -> FloorplanManager:
        """Get floorplan manager instance.
        
        Returns:
            Floorplan manager
        """
        return self.floorplan_manager
    
    def get_hybrid_detector(self) -> HybridMotionDetector:
        """Get hybrid detector instance.
        
        Returns:
            Hybrid detector
        """
        return self.hybrid_detector
    
    def get_pattern_analyzer(self) -> PatternAnalyzer:
        """Get pattern analyzer instance.
        
        Returns:
            Pattern analyzer
        """
        return self.pattern_analyzer
    
    def get_zone_state(self, zone_id: str) -> dict[str, Any]:
        """Get the current state of a zone.
        
        Args:
            zone_id: Zone identifier
            
        Returns:
            Dictionary with zone state data
        """
        # Placeholder - will be populated by zone manager events
        return {}
    
    def get_zone_statistics(self, zone_id: str) -> dict[str, Any]:
        """Get statistics for a zone.
        
        Args:
            zone_id: Zone identifier
            
        Returns:
            Dictionary with zone statistics
        """
        # Placeholder - will be populated by zone manager
        return {}
    
    def get_cue_state(self, cue_id: str) -> dict[str, Any]:
        """Get the current state of a secondary cue.
        
        Args:
            cue_id: Cue identifier
            
        Returns:
            Dictionary with cue state data
        """
        # Placeholder - will be populated by hybrid detector
        return {}
    
    def get_correlation_data(self) -> dict[str, Any]:
        """Get correlation analysis data.
        
        Returns:
            Dictionary with correlation data
        """
        # Placeholder - will be populated by hybrid detector
        return {
            "active_correlations": [],
            "correlation_statistics": {},
            "top_correlations": [],
        }
    
    # Diagnostic and test mode methods
    def get_detection_count(self) -> int:
        """Get total number of detections processed.
        
        Returns:
            Total detection count
        """
        return getattr(self, "_detection_count", 0)
    
    def get_average_detection_time(self) -> float:
        """Get average detection processing time in milliseconds.
        
        Returns:
            Average detection time in ms
        """
        return getattr(self, "_avg_detection_time", 0.0)
    
    def get_event_queue_size(self) -> int:
        """Get current size of event processing queue.
        
        Returns:
            Queue size
        """
        return len(getattr(self, "_event_queue", []))
    
    def get_recent_errors(self) -> list[str]:
        """Get list of recent errors.
        
        Returns:
            List of error messages
        """
        return getattr(self, "_recent_errors", [])
    
    def enable_test_mode(self, duration: int, test_sensors: list[str]) -> None:
        """Enable test mode for detection validation.
        
        Args:
            duration: Test duration in seconds
            test_sensors: List of sensor entity IDs to test
        """
        self._test_mode = True
        self._test_duration = duration
        self._test_sensors = test_sensors
        self._test_detections: list[Any] = []
        _LOGGER.info("Test mode enabled for %d seconds with sensors: %s", duration, test_sensors)
    
    def disable_test_mode(self) -> None:
        """Disable test mode."""
        self._test_mode = False
        _LOGGER.info("Test mode disabled")
    
    def get_test_results(self) -> list[Any]:
        """Get test mode detection results.
        
        Returns:
            List of detection results from test mode
        """
        return getattr(self, "_test_detections", [])
    
    def detect_anomaly(
        self,
        current_result: DirectionResult | None = None,
        sensitivity: float = 0.7,
    ) -> tuple[bool, float, str, str | None, str | None]:
        """Detect anomalies in motion patterns.
        
        Compares current detection against learned patterns to detect unusual behavior.
        
        Args:
            current_result: Current direction result to check (uses last_direction if None)
            sensitivity: Anomaly detection sensitivity (0.0-1.0, higher = more sensitive)
            
        Returns:
            Tuple of (is_anomaly, anomaly_score, anomaly_type, expected_pattern, actual_pattern)
        """
        if current_result is None:
            current_result = self.last_direction
        
        if not current_result:
            return (False, 0.0, "", None, None)
        
        # Get learned patterns from pattern analyzer
        learned_patterns = self.pattern_analyzer.learned_patterns
        
        if not learned_patterns:
            # No learned patterns yet - cannot detect anomalies
            return (False, 0.0, "", None, None)
        
        # Create simple signature from current result
        current_signature = current_result.motion_sensor_id if current_result.motion_sensor_id else "unknown"
        current_direction = current_result.direction
        
        # Check if current pattern matches any learned patterns
        max_similarity = 0.0
        best_match = None
        
        for signature, learned in learned_patterns.items():
            # Simple similarity: check if sensor is in learned pattern
            if current_signature in signature:
                similarity = 0.8  # High similarity if sensor matches
                
                # Check direction too
                if learned.example and hasattr(learned.example, "direction"):
                    if learned.example.direction == current_direction:
                        similarity = 1.0  # Perfect match
                
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_match = learned
        
        # Calculate anomaly score (1.0 = completely different, 0.0 = perfect match)
        anomaly_score = 1.0 - max_similarity
        
        # Determine if this is an anomaly based on sensitivity threshold
        is_anomaly = anomaly_score > sensitivity
        
        if not is_anomaly:
            return (False, anomaly_score, "", None, None)
        
        # Determine anomaly type based on confidence and method
        if current_result.confidence < 0.5:
            anomaly_type = "unusual_timing"
        elif current_result.method == "insufficient_data":
            anomaly_type = "unexpected_path"
        else:
            anomaly_type = "wrong_direction"
        
        # Format patterns for display
        expected = best_match.signature if best_match else "unknown"
        actual = f"{current_signature}->{current_direction}"
        
        _LOGGER.info(
            "Anomaly detected: score=%.2f, type=%s, expected=%s, actual=%s",
            anomaly_score,
            anomaly_type,
            expected,
            actual,
        )
        
        return (is_anomaly, anomaly_score, anomaly_type, expected, actual)
    
    def _calculate_pattern_similarity_deprecated(self, signature1: str, signature2: str) -> float:
        """Calculate similarity between two pattern signatures.
        
        Args:
            signature1: First pattern signature
            signature2: Second pattern signature
            
        Returns:
            Similarity score (0.0-1.0)
        """
        # Simple string similarity using common subsequence
        sensors1 = signature1.split("->")
        sensors2 = signature2.split("->")
        
        # Calculate overlap
        common = len(set(sensors1) & set(sensors2))
        total = max(len(sensors1), len(sensors2))
        
        if total == 0:
            return 0.0
        
        # Base similarity on sensor overlap
        overlap_similarity = common / total
        
        # Adjust for sequence order (Levenshtein-like)
        sequence_similarity = self._sequence_similarity(sensors1, sensors2)
        
        # Weighted average
        return (overlap_similarity * 0.4) + (sequence_similarity * 0.6)
    
    def _sequence_similarity(self, seq1: list[str], seq2: list[str]) -> float:
        """Calculate similarity between two sequences.
        
        Args:
            seq1: First sequence
            seq2: Second sequence
            
        Returns:
            Similarity score (0.0-1.0)
        """
        if not seq1 or not seq2:
            return 0.0
        
        # Simple dynamic programming approach
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        
        # Longest common subsequence length
        lcs_length = dp[m][n]
        
        # Normalize by average length
        avg_length = (m + n) / 2
        return lcs_length / avg_length if avg_length > 0 else 0.0
    
    def _determine_anomaly_type(
        self,
        current: Any,
        expected: Any | None,
    ) -> str:
        """Determine the type of anomaly detected.
        
        Args:
            current: Current motion sequence
            expected: Expected motion sequence (or None)
            
        Returns:
            Anomaly type: unexpected_path, unusual_timing, or wrong_direction
        """
        if not expected:
            return "unexpected_path"
        
        # Check timing differences
        if abs(current.total_duration_ms - expected.total_duration_ms) > 2000:
            return "unusual_timing"
        
        # Check if direction is reversed
        current_sensors = [e.sensor.entity_id for e in current.events]
        expected_sensors = [e.sensor.entity_id for e in expected.events]
        
        if current_sensors == expected_sensors[::-1]:
            return "wrong_direction"
        
        # Default to unexpected path
        return "unexpected_path"
    
    def _format_pattern(self, learned: Any) -> str:
        """Format learned pattern for display.
        
        Args:
            learned: Learned pattern object
            
        Returns:
            Formatted pattern string
        """
        if not learned or not learned.example:
            return "unknown"
        
        return learned.signature
