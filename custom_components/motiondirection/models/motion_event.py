"""Data model for motion events."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .sensor_node import SensorNode


@dataclass
class MotionEvent:
    """Represents a single motion detection event.
    
    Attributes:
        sensor: The sensor that detected motion
        timestamp: When the motion was detected
        state: New state of the sensor (typically 'on' for motion detected)
        previous_state: Previous state of the sensor
        confidence: Confidence score for this detection (0-1)
        context: Optional context information from Home Assistant
    """
    
    sensor: SensorNode
    timestamp: datetime
    state: str
    previous_state: Optional[str] = None
    confidence: float = 1.0
    context: Optional[dict] = None
    
    def __post_init__(self) -> None:
        """Validate motion event data."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
    
    def is_motion_start(self) -> bool:
        """Check if this event represents the start of motion.
        
        Returns:
            True if motion started (off -> on transition)
        """
        return (
            self.previous_state in (None, "off", "clear") 
            and self.state in ("on", "detected")
        )
    
    def is_motion_end(self) -> bool:
        """Check if this event represents the end of motion.
        
        Returns:
            True if motion ended (on -> off transition)
        """
        return (
            self.previous_state in ("on", "detected") 
            and self.state in ("off", "clear")
        )
    
    def time_since(self, other: "MotionEvent") -> float:
        """Calculate time difference from another event.
        
        Args:
            other: Another motion event
            
        Returns:
            Time difference in milliseconds
        """
        delta = abs((self.timestamp - other.timestamp).total_seconds())
        return delta * 1000
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"MotionEvent(sensor={self.sensor.entity_id}, "
            f"timestamp={self.timestamp.isoformat()}, "
            f"state={self.state})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()
