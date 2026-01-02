"""Data model for motion sequences."""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from .motion_event import MotionEvent


@dataclass
class MotionSequence:
    """Represents a sequence of related motion events.
    
    A sequence contains motion events that occurred within a time window
    and are likely related to the same motion through the space.
    
    Attributes:
        events: List of motion events in chronological order
        confidence: Overall confidence score for this sequence
        pattern_type: Type of pattern detected (linear, circular, etc.)
        start_time: Timestamp of first event
        end_time: Timestamp of last event
        duration_ms: Duration of sequence in milliseconds
    """
    
    confidence: float = 0.0
    pattern_type: Optional[str] = None
    events: List[MotionEvent] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Sort events and calculate derived properties."""
        # Sort events by timestamp
        self.events.sort(key=lambda e: e.timestamp)
    
    @property
    def start_time(self) -> Optional[datetime]:
        """Get timestamp of first event."""
        return self.events[0].timestamp if self.events else None
    
    @property
    def end_time(self) -> Optional[datetime]:
        """Get timestamp of last event."""
        return self.events[-1].timestamp if self.events else None
    
    @property
    def duration_ms(self) -> float:
        """Get duration of sequence in milliseconds."""
        if len(self.events) < 2:
            return 0.0
        start = self.start_time
        end = self.end_time
        if start is None or end is None:
            return 0.0
        delta = end - start
        return delta.total_seconds() * 1000
    
    @property
    def sensor_count(self) -> int:
        """Get number of unique sensors in sequence."""
        return len(set(event.sensor.entity_id for event in self.events))
    
    def get_sensor_ids(self) -> List[str]:
        """Get list of sensor entity IDs in order.
        
        Returns:
            List of entity IDs
        """
        return [event.sensor.entity_id for event in self.events]
    
    def get_positions(self) -> List[Tuple[float, float]]:
        """Get list of sensor positions in order.
        
        Returns:
            List of (x, y) positions
        """
        return [event.sensor.position for event in self.events]
    
    def calculate_average_interval(self) -> float:
        """Calculate average time interval between events.
        
        Returns:
            Average interval in milliseconds
        """
        if len(self.events) < 2:
            return 0.0
        
        intervals = []
        for i in range(1, len(self.events)):
            delta = (self.events[i].timestamp - self.events[i-1].timestamp)
            intervals.append(delta.total_seconds() * 1000)
        
        return sum(intervals) / len(intervals)
    
    def is_valid(self, min_events: int = 2) -> bool:
        """Check if sequence is valid for direction detection.
        
        Args:
            min_events: Minimum number of events required
            
        Returns:
            True if sequence has enough events
        """
        return len(self.events) >= min_events
    
    def __len__(self) -> int:
        """Get number of events in sequence."""
        return len(self.events)
    
    def __str__(self) -> str:
        """String representation."""
        sensor_ids = " -> ".join(self.get_sensor_ids())
        return (
            f"MotionSequence("
            f"events={len(self.events)}, "
            f"duration={self.duration_ms:.0f}ms, "
            f"path={sensor_ids})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()
