"""Motion detection orchestrator for direction analysis."""
import logging
from datetime import datetime
from typing import Callable, Dict, Optional

from homeassistant.core import HomeAssistant

from ..models import DirectionResult, MotionEvent, SensorNode
from .event_collector import EventCollector
from .time_window_correlator import TimeWindowCorrelator
from .vector_calculator import VectorCalculator

_LOGGER = logging.getLogger(__name__)


class MotionDetector:
    """High-level motion direction detection orchestrator.
    
    Coordinates EventCollector, TimeWindowCorrelator, and VectorCalculator
    to detect motion direction from multiple sensors. Fires events and
    provides callbacks for entity updates.
    
    Detection pipeline:
    1. Collect motion events from sensors (EventCollector)
    2. Correlate events into sequences (TimeWindowCorrelator)
    3. Calculate direction vectors and confidence (VectorCalculator)
    4. Convert vectors to direction names
    5. Check confidence threshold
    6. Fire events and trigger callbacks
    
    Attributes:
        hass: Home Assistant instance
        event_collector: Motion event collector
        correlator: Time window correlator
        calculator: Vector calculator
        confidence_threshold: Minimum confidence for detection
        detection_callback: Optional callback for detections
        floorplan_id: ID of associated floorplan
    """
    
    DEFAULT_CONFIDENCE_THRESHOLD = 0.7
    EVENT_TYPE = "motiondirection_motion_detected"
    
    def __init__(
        self,
        hass: HomeAssistant,
        sensors: Dict[str, SensorNode],
        floorplan_id: str = "default",
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        window_size: int = TimeWindowCorrelator.DEFAULT_WINDOW_SIZE,
        detection_callback: Optional[Callable[[DirectionResult], None]] = None,
    ) -> None:
        """Initialize motion detector.
        
        Args:
            hass: Home Assistant instance
            sensors: Dictionary of sensor configurations
            floorplan_id: ID of associated floorplan
            confidence_threshold: Minimum confidence for detection
            window_size: Time window for correlation (ms)
            detection_callback: Optional callback for detections
        
        Raises:
            ValueError: If confidence threshold not in [0, 1]
        """
        if not 0 <= confidence_threshold <= 1:
            raise ValueError(
                f"Confidence threshold must be between 0 and 1, got {confidence_threshold}"
            )
        
        self.hass = hass
        self.floorplan_id = floorplan_id
        self.confidence_threshold = confidence_threshold
        self.detection_callback = detection_callback
        
        # Initialize components
        self.event_collector = EventCollector(
            hass=hass,
            sensors=sensors,
            event_callback=self._on_motion_event,
        )
        
        self.correlator = TimeWindowCorrelator(
            default_window_size=window_size,
        )
        
        self.calculator = VectorCalculator()
        
        self._is_running = False
        
        _LOGGER.info(
            "MotionDetector initialized for floorplan=%s with %d sensors, "
            "threshold=%.2f, window=%dms",
            floorplan_id,
            len(sensors),
            confidence_threshold,
            window_size,
        )
    
    async def async_start(self) -> None:
        """Start motion detection."""
        if self._is_running:
            _LOGGER.warning("MotionDetector already running")
            return
        
        await self.event_collector.start()
        self._is_running = True
        
        _LOGGER.info("MotionDetector started")
    
    async def async_stop(self) -> None:
        """Stop motion detection."""
        if not self._is_running:
            return
        
        await self.event_collector.stop()
        self._is_running = False
        
        _LOGGER.info("MotionDetector stopped")
    
    def _on_motion_event(self, event: MotionEvent) -> None:
        """Handle new motion event from collector.
        
        Processes recent events to detect direction patterns.
        
        Args:
            event: New motion event
        """
        try:
            # Get recent events for correlation
            recent_events = self.event_collector.get_recent_events(count=20)
            
            if len(recent_events) < 2:
                _LOGGER.debug("Not enough events for detection (%d)", len(recent_events))
                return
            
            # Correlate events into sequences
            sequences = self.correlator.correlate_events(recent_events)
            
            if not sequences:
                _LOGGER.debug("No sequences formed from events")
                return
            
            # Process most recent sequence
            sequence = sequences[-1]
            
            # Calculate direction vector
            vector = self.calculator.calculate_sequence_vector(sequence)
            
            if vector == (0.0, 0.0):
                _LOGGER.debug("Zero vector calculated")
                return
            
            # Calculate confidence
            confidence = self.calculator.calculate_confidence(sequence)
            
            # Check threshold
            if confidence < self.confidence_threshold:
                _LOGGER.debug(
                    "Confidence %.3f below threshold %.3f",
                    confidence,
                    self.confidence_threshold,
                )
                return
            
            # Convert vector to direction name
            angle = self.calculator.vector_to_angle(vector)
            direction = self.calculator.angle_to_direction(angle)
            
            # Calculate speed (optional)
            speed = self._calculate_speed(sequence)
            
            # Create detection result
            result = DirectionResult(
                direction=direction,
                confidence=confidence,
                method="multi_sensor",
                motion_sensor_id=sequence.events[0].sensor.entity_id,
                timestamp=datetime.now(),
                vector=vector,
                speed=speed,
            )
            
            # Fire event
            self._fire_detection_event(result, sequence)
            
            # Trigger callback
            if self.detection_callback:
                self.detection_callback(result)
            
            _LOGGER.info(
                "Motion detected: direction=%s, confidence=%.3f, sensors=%d",
                direction,
                confidence,
                len(sequence.events),
            )
        
        except Exception as ex:
            _LOGGER.exception("Error processing motion event: %s", ex)
    
    def _fire_detection_event(
        self,
        result: DirectionResult,
        sequence,
    ) -> None:
        """Fire motion detection event to HA event bus.
        
        Args:
            result: Detection result
            sequence: Motion sequence
        """
        # Build sensor path
        path = [event.sensor.entity_id for event in sequence.events]
        
        # Build event data
        event_data = {
            "floorplan_id": self.floorplan_id,
            "direction": result.direction,
            "confidence": result.confidence,
            "detection_method": result.method,
            "path": path,
            "vector": list(result.vector) if result.vector else None,
            "speed": result.speed,
            "timestamp": result.timestamp.isoformat() if result.timestamp else None,
        }
        
        # Fire event asynchronously
        self.hass.bus.async_fire(self.EVENT_TYPE, event_data)
        
        _LOGGER.debug("Fired event: %s", event_data)
    
    def _calculate_speed(self, sequence) -> Optional[float]:
        """Calculate average speed from sequence.
        
        Args:
            sequence: Motion sequence
        
        Returns:
            Speed in m/s or None if cannot calculate
        """
        if len(sequence.events) < 2:
            return None
        
        try:
            # Calculate total distance
            total_distance = 0.0
            for i in range(len(sequence.events) - 1):
                s1 = sequence.events[i].sensor
                s2 = sequence.events[i + 1].sensor
                
                dx = s2.position[0] - s1.position[0]
                dy = s2.position[1] - s1.position[1]
                distance = (dx**2 + dy**2) ** 0.5
                
                total_distance += distance
            
            # Calculate total time
            total_time = (
                sequence.events[-1].timestamp - sequence.events[0].timestamp
            ).total_seconds()
            
            if total_time <= 0:
                return None
            
            # Speed in units per second (assuming positions in meters)
            speed = total_distance / total_time
            
            return round(speed, 2)
        
        except Exception as ex:
            _LOGGER.debug("Error calculating speed: %s", ex)
            return None
    
    def update_sensors(self, sensors: Dict[str, SensorNode]) -> None:
        """Update sensor configuration.
        
        Args:
            sensors: New sensor configuration
        """
        self.event_collector.update_sensors(sensors)
        _LOGGER.info("Sensors updated in MotionDetector")
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """Update confidence threshold.
        
        Args:
            threshold: New confidence threshold
        
        Raises:
            ValueError: If threshold not in [0, 1]
        """
        if not 0 <= threshold <= 1:
            raise ValueError(
                f"Confidence threshold must be between 0 and 1, got {threshold}"
            )
        
        old_threshold = self.confidence_threshold
        self.confidence_threshold = threshold
        
        _LOGGER.info(
            "Confidence threshold updated: %.2f -> %.2f",
            old_threshold,
            threshold,
        )
    
    def set_window_size(self, window_size: int) -> None:
        """Update time window size.
        
        Args:
            window_size: New window size in milliseconds
        
        Raises:
            ValueError: If window size outside valid range
        """
        self.correlator.set_default_window_size(window_size)
        _LOGGER.info("Window size updated to %dms", window_size)
    
    def clear_history(self) -> None:
        """Clear event history buffer."""
        self.event_collector.clear_buffer()
        _LOGGER.info("Event history cleared")
    
    @property
    def is_running(self) -> bool:
        """Check if detector is running.
        
        Returns:
            True if actively detecting
        """
        return self._is_running
    
    @property
    def sensor_count(self) -> int:
        """Get number of configured sensors.
        
        Returns:
            Number of sensors
        """
        return len(self.event_collector.sensors)
    
    @property
    def event_count(self) -> int:
        """Get number of buffered events.
        
        Returns:
            Number of events in buffer
        """
        return self.event_collector.buffer_count
