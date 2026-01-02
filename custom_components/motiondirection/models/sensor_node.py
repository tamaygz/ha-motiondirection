"""Data model for sensor nodes on the floorplan."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple


@dataclass
class SensorNode:
    """Represents a motion sensor node on the floorplan.
    
    Attributes:
        entity_id: Home Assistant entity ID
        position: (x, y) coordinates on floorplan
        range: Detection range in floorplan units
        weight: Confidence weight for this sensor (0-1)
        sensor_type: Type of sensor (pir, radar, camera, hybrid)
        reliability: Historical reliability score (0-1)
        zone: Optional zone ID this sensor belongs to
        detection_angle: Detection angle in degrees (default 120)
        cooldown_period: Cooldown period in milliseconds (default 2000)
        last_triggered: Timestamp of last trigger
        trigger_count: Number of times triggered
    """
    
    entity_id: str
    position: Tuple[float, float]
    range: float = 50.0
    weight: float = 1.0
    sensor_type: str = "pir"
    reliability: float = 0.95
    zone: Optional[str] = None
    detection_angle: float = 120.0
    cooldown_period: int = 2000
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def __post_init__(self) -> None:
        """Validate sensor node data."""
        if not 0 <= self.weight <= 1:
            raise ValueError("Weight must be between 0 and 1")
        if not 0 <= self.reliability <= 1:
            raise ValueError("Reliability must be between 0 and 1")
        if self.range < 0:
            raise ValueError("Range must be non-negative")
        if not 0 < self.detection_angle <= 360:
            raise ValueError("Detection angle must be between 0 and 360 degrees")
        if self.cooldown_period < 0:
            raise ValueError("Cooldown period must be non-negative")
    
    def distance_to(self, other: "SensorNode") -> float:
        """Calculate Euclidean distance to another sensor.
        
        Args:
            other: Another sensor node
            
        Returns:
            Distance in floorplan units
        """
        dx = other.position[0] - self.position[0]
        dy = other.position[1] - self.position[1]
        return (dx**2 + dy**2) ** 0.5
    
    def is_overlapping(self, other: "SensorNode") -> bool:
        """Check if sensor range overlaps with another sensor.
        
        Args:
            other: Another sensor node
            
        Returns:
            True if ranges overlap
        """
        distance = self.distance_to(other)
        return distance < (self.range + other.range)
    
    def update_trigger(self, timestamp: datetime) -> None:
        """Update trigger information.
        
        Args:
            timestamp: Time of trigger
        """
        self.last_triggered = timestamp
        self.trigger_count += 1
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"SensorNode(entity_id={self.entity_id}, "
            f"position={self.position}, "
            f"type={self.sensor_type})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()
