"""Data models for pattern analysis and detection."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from .motion_sequence import MotionSequence


@dataclass
class LearnedPattern:
    """Represents a learned motion pattern.
    
    Attributes:
        signature: Unique pattern signature
        occurrences: Number of times this pattern has been observed
        confidence: Confidence score for this pattern (0-1)
        example: Example motion sequence demonstrating this pattern
        first_seen: When pattern was first observed
        last_seen: When pattern was last observed
        time_of_day_distribution: Distribution of when pattern occurs
        day_of_week_distribution: Distribution by day of week
    """
    
    signature: str
    occurrences: int
    confidence: float
    example: MotionSequence
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    time_of_day_distribution: Optional[List[int]] = None
    day_of_week_distribution: Optional[List[int]] = None
    
    def __post_init__(self) -> None:
        """Validate learned pattern."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        if self.occurrences < 0:
            raise ValueError("Occurrences must be non-negative")
    
    def update_occurrence(self, timestamp: datetime) -> None:
        """Update pattern with new occurrence.
        
        Args:
            timestamp: When pattern was observed
        """
        self.occurrences += 1
        self.last_seen = timestamp
        
        if self.first_seen is None:
            self.first_seen = timestamp
    
    def get_average_time_of_day(self) -> Optional[int]:
        """Get average time of day when pattern occurs.
        
        Returns:
            Hour of day (0-23) or None if no data
        """
        if not self.time_of_day_distribution:
            return None
        
        # Find hour with most occurrences
        distribution = self.time_of_day_distribution
        max_hour = max(
            range(len(distribution)),
            key=lambda i: distribution[i]
        )
        return max_hour
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"LearnedPattern(signature={self.signature}, "
            f"occurrences={self.occurrences}, confidence={self.confidence:.2f})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()


@dataclass
class ZoneTransition:
    """Represents a transition through a zone.
    
    Attributes:
        zone_id: Zone identifier
        direction: Direction through zone
        entry_point: Where path entered zone (x, y)
        exit_point: Where path exited zone (x, y)
        dwell_time: Time spent in zone (milliseconds)
        confidence: Confidence of detection (0-1)
        entry_time: When zone was entered
        exit_time: When zone was exited
        triggered_sensors: Sensors that detected motion in zone
    """
    
    zone_id: str
    direction: str
    entry_point: Tuple[float, float]
    exit_point: Tuple[float, float]
    dwell_time: int
    confidence: float
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    triggered_sensors: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate zone transition."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        if self.dwell_time < 0:
            raise ValueError("Dwell time must be non-negative")
    
    @property
    def transit_speed(self) -> Optional[float]:
        """Calculate transit speed through zone.
        
        Returns:
            Speed in units per second or None if duration is zero
        """
        if self.dwell_time == 0:
            return None
        
        # Calculate distance between entry and exit
        dx = self.exit_point[0] - self.entry_point[0]
        dy = self.exit_point[1] - self.entry_point[1]
        distance = (dx**2 + dy**2) ** 0.5
        
        # Convert dwell time to seconds
        duration_s = self.dwell_time / 1000.0
        
        return distance / duration_s
    
    @property
    def direction_vector(self) -> Tuple[float, float]:
        """Get normalized direction vector through zone.
        
        Returns:
            (dx, dy) normalized vector
        """
        dx = self.exit_point[0] - self.entry_point[0]
        dy = self.exit_point[1] - self.entry_point[1]
        
        magnitude = (dx**2 + dy**2) ** 0.5
        if magnitude == 0:
            return (0.0, 0.0)
        
        return (dx / magnitude, dy / magnitude)
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"ZoneTransition(zone={self.zone_id}, direction={self.direction}, "
            f"dwell={self.dwell_time}ms, conf={self.confidence:.2f})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()


@dataclass
class DirectionResult:
    """Result from hybrid direction detection.
    
    Attributes:
        direction: Detected direction name
        confidence: Overall confidence (0-1)
        method: Detection method used
        contributing_cues: List of cue IDs that contributed
        motion_sensor_id: Primary motion sensor ID
        timestamp: When detection occurred
        vector: Direction vector (optional)
        speed: Estimated speed (optional)
    """
    
    direction: str
    confidence: float
    method: str
    contributing_cues: List[str] = field(default_factory=list)
    motion_sensor_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    vector: Optional[Tuple[float, float]] = None
    speed: Optional[float] = None
    
    def __post_init__(self) -> None:
        """Validate direction result."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        
        valid_methods = [
            "multi_sensor",
            "hybrid",
            "cue_assisted",
            "single_motion_with_cues",
            "insufficient_data"
        ]
        if self.method not in valid_methods:
            raise ValueError(f"Invalid detection method: {self.method}")
    
    @property
    def is_hybrid_detection(self) -> bool:
        """Check if this was hybrid detection.
        
        Returns:
            True if hybrid or cue-assisted detection
        """
        return self.method in ("hybrid", "cue_assisted", "single_motion_with_cues")
    
    @property
    def cue_count(self) -> int:
        """Get number of contributing cues.
        
        Returns:
            Number of cues
        """
        return len(self.contributing_cues)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for event data.
        
        Returns:
            Dictionary representation
        """
        return {
            "direction": self.direction,
            "confidence": self.confidence,
            "method": self.method,
            "contributing_cues": self.contributing_cues,
            "motion_sensor_id": self.motion_sensor_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "vector": self.vector,
            "speed": self.speed,
        }
    
    def __str__(self) -> str:
        """String representation."""
        cues_str = f", cues={len(self.contributing_cues)}" if self.contributing_cues else ""
        return (
            f"DirectionResult(direction={self.direction}, "
            f"conf={self.confidence:.2f}, method={self.method}{cues_str})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()
