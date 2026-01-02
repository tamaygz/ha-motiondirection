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
