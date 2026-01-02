"""Event collection system for motion sensors."""
import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import Callable, Deque, Dict, List, Optional

from homeassistant.const import EVENT_STATE_CHANGED, STATE_ON
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers.event import async_track_state_change_event

from ..models import MotionEvent, SensorNode

_LOGGER = logging.getLogger(__name__)


class EventCollector:
    """Collects and buffers motion sensor events with debouncing.
    
    This class monitors Home Assistant motion sensor state changes and
    buffers them for processing by the motion detection engine.
    
    Attributes:
        hass: Home Assistant instance
        sensors: Dictionary of sensor_id -> SensorNode
        buffer_size: Maximum number of events to buffer
        debounce_time: Minimum time between events from same sensor (ms)
        event_buffer: Deque of buffered motion events
        last_trigger_times: Dictionary tracking last trigger time per sensor
        event_callback: Optional callback for new events
    """
    
    DEFAULT_BUFFER_SIZE = 100
    DEFAULT_DEBOUNCE_TIME = 100  # milliseconds
    
    def __init__(
        self,
        hass: HomeAssistant,
        sensors: Dict[str, SensorNode],
        buffer_size: int = DEFAULT_BUFFER_SIZE,
        debounce_time: int = DEFAULT_DEBOUNCE_TIME,
        event_callback: Optional[Callable[[MotionEvent], None]] = None,
    ) -> None:
        """Initialize event collector.
        
        Args:
            hass: Home Assistant instance
            sensors: Dictionary of configured sensors
            buffer_size: Maximum events to buffer
            debounce_time: Minimum time between events (ms)
            event_callback: Optional callback for new events
        """
        self.hass = hass
        self.sensors = sensors
        self.buffer_size = buffer_size
        self.debounce_time = debounce_time
        self.event_callback = event_callback
        
        self.event_buffer: Deque[MotionEvent] = deque(maxlen=buffer_size)
        self.last_trigger_times: Dict[str, datetime] = {}
        self._unsubscribe_callbacks: List[Callable[[], None]] = []
        
        _LOGGER.info(
            "EventCollector initialized with %d sensors, buffer_size=%d, debounce=%dms",
            len(sensors),
            buffer_size,
            debounce_time,
        )
    
    async def start(self) -> None:
        """Start monitoring sensor state changes."""
        sensor_ids = list(self.sensors.keys())
        
        if not sensor_ids:
            _LOGGER.warning("No sensors configured for event collection")
            return
        
        # Subscribe to state changes for all sensors
        unsubscribe = async_track_state_change_event(
            self.hass,
            sensor_ids,
            self._handle_state_change,
        )
        self._unsubscribe_callbacks.append(unsubscribe)
        
        _LOGGER.info("EventCollector started monitoring %d sensors", len(sensor_ids))
    
    async def stop(self) -> None:
        """Stop monitoring sensor state changes."""
        for unsubscribe in self._unsubscribe_callbacks:
            unsubscribe()
        self._unsubscribe_callbacks.clear()
        
        _LOGGER.info("EventCollector stopped")
    
    @callback
    def _handle_state_change(self, event: Event) -> None:
        """Handle sensor state change event.
        
        Args:
            event: Home Assistant state change event
        """
        entity_id = event.data.get("entity_id")
        new_state: Optional[State] = event.data.get("new_state")
        old_state: Optional[State] = event.data.get("old_state")
        
        if not entity_id or not new_state:
            return
        
        # Only process motion detected (on) events
        if new_state.state != STATE_ON:
            return
        
        # Get sensor configuration
        sensor = self.sensors.get(entity_id)
        if not sensor:
            _LOGGER.warning("Received event from unconfigured sensor: %s", entity_id)
            return
        
        # Check debounce
        now = datetime.now()
        last_trigger = self.last_trigger_times.get(entity_id)
        
        if last_trigger:
            time_diff_ms = (now - last_trigger).total_seconds() * 1000
            if time_diff_ms < self.debounce_time:
                _LOGGER.debug(
                    "Debounced event from %s (%.1fms since last)",
                    entity_id,
                    time_diff_ms,
                )
                return
        
        # Create motion event
        motion_event = MotionEvent(
            sensor=sensor,
            timestamp=now,
            state="on",
            confidence=sensor.reliability,
        )
        
        # Add to buffer
        self.event_buffer.append(motion_event)
        self.last_trigger_times[entity_id] = now
        
        _LOGGER.debug(
            "Motion event: sensor=%s, buffer_size=%d",
            entity_id,
            len(self.event_buffer),
        )
        
        # Call callback if provided
        if self.event_callback:
            self.event_callback(motion_event)
    
    def get_recent_events(self, count: Optional[int] = None) -> List[MotionEvent]:
        """Get recent motion events from buffer.
        
        Args:
            count: Maximum number of events to return (None for all)
        
        Returns:
            List of recent motion events (newest first)
        """
        events = list(self.event_buffer)
        events.reverse()  # Newest first
        
        if count is not None:
            events = events[:count]
        
        return events
    
    def get_events_since(self, timestamp: datetime) -> List[MotionEvent]:
        """Get all events since a given timestamp.
        
        Args:
            timestamp: Cutoff timestamp
        
        Returns:
            List of events after timestamp (oldest first)
        """
        return [
            event
            for event in self.event_buffer
            if event.timestamp >= timestamp
        ]
    
    def clear_buffer(self) -> None:
        """Clear the event buffer."""
        self.event_buffer.clear()
        _LOGGER.debug("Event buffer cleared")
    
    def update_sensors(self, sensors: Dict[str, SensorNode]) -> None:
        """Update sensor configuration.
        
        Args:
            sensors: New sensor configuration
        """
        old_count = len(self.sensors)
        self.sensors = sensors
        
        _LOGGER.info(
            "Sensors updated: %d -> %d",
            old_count,
            len(sensors),
        )
    
    @property
    def buffer_count(self) -> int:
        """Get current number of events in buffer.
        
        Returns:
            Number of buffered events
        """
        return len(self.event_buffer)
    
    @property
    def is_monitoring(self) -> bool:
        """Check if collector is actively monitoring.
        
        Returns:
            True if monitoring sensors
        """
        return len(self._unsubscribe_callbacks) > 0
