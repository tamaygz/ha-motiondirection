"""Data models for trigger zones."""
from dataclasses import dataclass, field
from datetime import datetime
import math
from typing import List, Optional, Tuple


@dataclass
class DirectionConfig:
    """Configuration for a specific direction through a zone.
    
    Attributes:
        name: Direction name (e.g., "east", "west", "entrance", "exit")
        vector: Normalized direction vector (dx, dy)
        entry_edge: Which edge typically used for entry (optional)
        exit_edge: Which edge typically used for exit (optional)
        aliases: Alternative names for this direction
    """
    
    name: str
    vector: Tuple[float, float]
    entry_edge: Optional[str] = None
    exit_edge: Optional[str] = None
    aliases: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Validate direction configuration."""
        # Validate vector is normalized (magnitude close to 1)
        magnitude = math.sqrt(self.vector[0]**2 + self.vector[1]**2)
        if not (0.9 <= magnitude <= 1.1):
            # Auto-normalize if not already normalized
            if magnitude > 0:
                self.vector = (
                    self.vector[0] / magnitude,
                    self.vector[1] / magnitude
                )
            else:
                raise ValueError("Direction vector cannot be zero")
    
    def matches_vector(
        self, 
        test_vector: Tuple[float, float], 
        tolerance: float = 30.0
    ) -> bool:
        """Check if test vector matches this direction within tolerance.
        
        Uses dot product to calculate angle between vectors.
        
        Args:
            test_vector: Vector to test (should be normalized)
            tolerance: Tolerance in degrees (default 30.0)
            
        Returns:
            True if vectors match within tolerance
        """
        # Normalize test vector if needed
        magnitude = math.sqrt(test_vector[0]**2 + test_vector[1]**2)
        if magnitude == 0:
            return False
        
        normalized_test = (
            test_vector[0] / magnitude,
            test_vector[1] / magnitude
        )
        
        # Calculate dot product
        dot_product = (
            self.vector[0] * normalized_test[0] + 
            self.vector[1] * normalized_test[1]
        )
        
        # Clamp to valid range for acos
        dot_product = max(-1.0, min(1.0, dot_product))
        
        # Calculate angle in radians, then convert to degrees
        angle_rad = math.acos(dot_product)
        angle_deg = math.degrees(angle_rad)
        
        return angle_deg <= tolerance
    
    def get_reverse_direction(self) -> "DirectionConfig":
        """Get the reverse direction configuration.
        
        Returns:
            DirectionConfig with reversed vector
        """
        reverse_name = f"{self.name}_reverse"
        if "north" in self.name:
            reverse_name = self.name.replace("north", "south")
        elif "south" in self.name:
            reverse_name = self.name.replace("south", "north")
        if "east" in self.name:
            reverse_name = reverse_name.replace("east", "west")
        elif "west" in self.name:
            reverse_name = reverse_name.replace("west", "east")
        
        return DirectionConfig(
            name=reverse_name,
            vector=(-self.vector[0], -self.vector[1]),
            entry_edge=self.exit_edge,
            exit_edge=self.entry_edge,
            aliases=[f"{alias}_reverse" for alias in self.aliases]
        )
    
    def __str__(self) -> str:
        """String representation."""
        return f"DirectionConfig(name={self.name}, vector={self.vector})"
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()


@dataclass
class TriggerZone:
    """Represents a triggerable zone on the floorplan.
    
    A zone is defined by a polygon boundary and can detect when motion
    enters, exits, or passes through it in specific directions.
    
    Attributes:
        id: Unique zone identifier
        name: Display name for the zone
        polygon: Zone boundary points [(x1, y1), (x2, y2), ...]
        known_directions: List of configured directions through this zone
        min_dwell_time: Minimum time in zone to trigger (milliseconds)
        max_transit_time: Maximum time for transit through zone (milliseconds)
        sensitivity: Detection sensitivity (0-1)
        current_state: Current zone state (idle, occupied, transit)
        last_direction: Last detected direction through zone
        last_trigger_time: Timestamp of last trigger
    """
    
    id: str
    name: str
    polygon: List[Tuple[float, float]]
    known_directions: List[DirectionConfig] = field(default_factory=list)
    min_dwell_time: int = 500
    max_transit_time: int = 10000
    sensitivity: float = 0.7
    current_state: str = "idle"
    last_direction: Optional[str] = None
    last_trigger_time: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Validate zone configuration."""
        if len(self.polygon) < 3:
            raise ValueError("Polygon must have at least 3 points")
        if not 0 <= self.sensitivity <= 1:
            raise ValueError("Sensitivity must be between 0 and 1")
        if self.min_dwell_time < 0:
            raise ValueError("min_dwell_time must be non-negative")
        if self.max_transit_time < 0:
            raise ValueError("max_transit_time must be non-negative")
        if self.current_state not in ("idle", "occupied", "transit"):
            raise ValueError("Invalid zone state")
    
    @property
    def center(self) -> Tuple[float, float]:
        """Calculate geometric center (centroid) of polygon.
        
        Returns:
            (x, y) coordinates of center point
        """
        if not self.polygon:
            return (0.0, 0.0)
        
        x_coords = [p[0] for p in self.polygon]
        y_coords = [p[1] for p in self.polygon]
        
        return (
            sum(x_coords) / len(x_coords),
            sum(y_coords) / len(y_coords)
        )
    
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """Check if point is inside zone polygon using ray casting.
        
        Uses the ray casting algorithm: cast a horizontal ray from the point
        to the right and count intersections with polygon edges. Odd number
        of intersections means the point is inside.
        
        Args:
            point: (x, y) coordinates to test
            
        Returns:
            True if point is inside polygon
        """
        x, y = point
        n = len(self.polygon)
        inside = False
        
        p1x, p1y = self.polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = self.polygon[i % n]
            
            # Check if ray crosses edge
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            
            p1x, p1y = p2x, p2y
        
        return inside
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get axis-aligned bounding box of zone.
        
        Returns:
            (min_x, min_y, max_x, max_y) tuple
        """
        if not self.polygon:
            return (0.0, 0.0, 0.0, 0.0)
        
        x_coords = [p[0] for p in self.polygon]
        y_coords = [p[1] for p in self.polygon]
        
        return (
            min(x_coords),
            min(y_coords),
            max(x_coords),
            max(y_coords)
        )
    
    def calculate_area(self) -> float:
        """Calculate area of polygon using shoelace formula.
        
        Returns:
            Area in square units
        """
        if len(self.polygon) < 3:
            return 0.0
        
        n = len(self.polygon)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += self.polygon[i][0] * self.polygon[j][1]
            area -= self.polygon[j][0] * self.polygon[i][1]
        
        return abs(area) / 2.0
    
    def get_direction_by_name(self, name: str) -> Optional[DirectionConfig]:
        """Get direction configuration by name or alias.
        
        Args:
            name: Direction name or alias
            
        Returns:
            DirectionConfig or None if not found
        """
        name_lower = name.lower()
        
        for direction in self.known_directions:
            if direction.name.lower() == name_lower:
                return direction
            if name_lower in [alias.lower() for alias in direction.aliases]:
                return direction
        
        return None
    
    def add_direction(self, direction: DirectionConfig) -> None:
        """Add a direction to this zone.
        
        Args:
            direction: DirectionConfig to add
        """
        # Check if direction with same name already exists
        existing = self.get_direction_by_name(direction.name)
        if existing:
            # Update existing direction
            self.known_directions.remove(existing)
        
        self.known_directions.append(direction)
    
    def update_state(
        self, 
        new_state: str, 
        direction: Optional[str] = None
    ) -> None:
        """Update zone state.
        
        Args:
            new_state: New state (idle, occupied, transit)
            direction: Direction of motion (optional)
        """
        if new_state not in ("idle", "occupied", "transit"):
            raise ValueError(f"Invalid zone state: {new_state}")
        
        self.current_state = new_state
        if direction:
            self.last_direction = direction
        self.last_trigger_time = datetime.now()
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"TriggerZone(id={self.id}, name={self.name}, "
            f"points={len(self.polygon)}, directions={len(self.known_directions)}, "
            f"state={self.current_state})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()
