"""Data model for motion paths."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass
class PathPoint:
    """A point along a motion path.
    
    Attributes:
        position: (x, y) coordinates
        timestamp: Time of this point
        sensor_id: Optional sensor entity ID at this point
        confidence: Confidence score for this point
    """
    
    position: Tuple[float, float]
    timestamp: datetime
    sensor_id: Optional[str] = None
    confidence: float = 1.0
    
    def __post_init__(self) -> None:
        """Validate path point data."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")


@dataclass
class MotionPath:
    """Represents a complete motion path through the space.
    
    A path is a series of points that represents the inferred trajectory
    of motion through the floorplan, potentially interpolated between sensors.
    
    Attributes:
        points: List of path points in chronological order
        confidence: Overall confidence score for this path
        direction_vector: Normalized direction vector (dx, dy)
        speed: Estimated speed in units per second
        pattern_type: Type of pattern (linear, circular, etc.)
    """
    
    points: List[PathPoint] = field(default_factory=list)
    confidence: float = 0.0
    direction_vector: Optional[Tuple[float, float]] = None
    speed: Optional[float] = None
    pattern_type: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Sort points by timestamp."""
        self.points.sort(key=lambda p: p.timestamp)
    
    @property
    def start_position(self) -> Optional[Tuple[float, float]]:
        """Get starting position of path."""
        return self.points[0].position if self.points else None
    
    @property
    def end_position(self) -> Optional[Tuple[float, float]]:
        """Get ending position of path."""
        return self.points[-1].position if self.points else None
    
    @property
    def start_time(self) -> Optional[datetime]:
        """Get start time of path."""
        return self.points[0].timestamp if self.points else None
    
    @property
    def end_time(self) -> Optional[datetime]:
        """Get end time of path."""
        return self.points[-1].timestamp if self.points else None
    
    @property
    def duration_ms(self) -> float:
        """Get duration of path in milliseconds."""
        if len(self.points) < 2:
            return 0.0
        delta = self.end_time - self.start_time
        return delta.total_seconds() * 1000
    
    def calculate_total_distance(self) -> float:
        """Calculate total distance traveled along path.
        
        Returns:
            Total distance in floorplan units
        """
        if len(self.points) < 2:
            return 0.0
        
        total = 0.0
        for i in range(1, len(self.points)):
            p1 = self.points[i-1].position
            p2 = self.points[i].position
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            total += (dx**2 + dy**2) ** 0.5
        
        return total
    
    def calculate_average_speed(self) -> float:
        """Calculate average speed along path.
        
        Returns:
            Speed in units per second
        """
        if len(self.points) < 2:
            return 0.0
        
        distance = self.calculate_total_distance()
        duration_s = self.duration_ms / 1000
        
        if duration_s == 0:
            return 0.0
        
        return distance / duration_s
    
    def get_direction_name(self) -> Optional[str]:
        """Get cardinal/ordinal direction name from vector.
        
        Returns:
            Direction name (north, south_east, etc.) or None
        """
        if not self.direction_vector:
            return None
        
        dx, dy = self.direction_vector
        
        # Cardinal directions
        if abs(dx) < 0.3:  # Primarily vertical
            return "north" if dy < 0 else "south"
        if abs(dy) < 0.3:  # Primarily horizontal
            return "east" if dx > 0 else "west"
        
        # Ordinal directions
        if dx > 0 and dy < 0:
            return "north_east"
        if dx > 0 and dy > 0:
            return "south_east"
        if dx < 0 and dy < 0:
            return "north_west"
        if dx < 0 and dy > 0:
            return "south_west"
        
        return None
    
    def __len__(self) -> int:
        """Get number of points in path."""
        return len(self.points)
    
    def __str__(self) -> str:
        """String representation."""
        direction = self.get_direction_name() or "unknown"
        return (
            f"MotionPath("
            f"points={len(self.points)}, "
            f"direction={direction}, "
            f"confidence={self.confidence:.2f})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()
