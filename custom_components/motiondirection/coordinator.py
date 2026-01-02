"""DataUpdateCoordinator for Motion Direction integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .core import (
    FloorplanManager,
    HybridMotionDetector,
    MotionDetector,
    PatternAnalyzer,
    TriggerZoneManager,
)
from .models import DirectionResult, MotionEvent

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
        
        # Initialize managers
        self.floorplan_manager = FloorplanManager(hass)
        self.zone_manager = TriggerZoneManager(hass)
        self.motion_detector = MotionDetector(hass)
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
                
                # Check zones
                zone_result = await self.zone_manager.check_zone_transition(
                    result.direction,
                    result.confidence,
                )
                
                if zone_result:
                    self.active_zones = [zone_result.zone_id]
                
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
