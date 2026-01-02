"""Data model for floorplan configuration."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import json
import yaml


@dataclass
class GridConfig:
    """Grid configuration for the floorplan.
    
    Attributes:
        enabled: Whether grid is displayed
        size: Grid cell size in pixels
        snap: Whether to snap objects to grid
    """
    
    enabled: bool = True
    size: int = 20
    snap: bool = True
    
    def __post_init__(self) -> None:
        """Validate grid configuration."""
        if self.size < 1:
            raise ValueError("Grid size must be positive")


@dataclass
class BackgroundConfig:
    """Background image configuration.
    
    Attributes:
        image: Path to background image file
        opacity: Image opacity (0-1)
    """
    
    image: Optional[str] = None
    opacity: float = 0.5
    
    def __post_init__(self) -> None:
        """Validate background configuration."""
        if not 0 <= self.opacity <= 1:
            raise ValueError("Opacity must be between 0 and 1")


@dataclass
class LayerConfig:
    """Layer configuration for z-index ordering.
    
    Attributes:
        id: Layer identifier
        z_index: Z-index for stacking order
        visible: Whether layer is visible
    """
    
    id: str
    z_index: int = 0
    visible: bool = True


@dataclass
class Floorplan:
    """Represents a floorplan configuration.
    
    A floorplan contains the canvas configuration, background image,
    and collections of sensors, zones, and secondary cues placed on it.
    
    Attributes:
        id: Unique floorplan identifier
        name: Display name for the floorplan
        width: Canvas width in pixels
        height: Canvas height in pixels
        scale: Scale factor (pixels per meter)
        background: Background image configuration
        grid: Grid configuration
        layers: Layer configurations
        sensors: Dictionary of sensor configurations by entity_id
        zones: Dictionary of zone configurations by zone_id
        secondary_cues: Dictionary of secondary cue configurations by cue_id
    """
    
    id: str
    name: str
    width: int
    height: int
    scale: float = 10.0
    background: BackgroundConfig = field(default_factory=BackgroundConfig)
    grid: GridConfig = field(default_factory=GridConfig)
    layers: List[LayerConfig] = field(default_factory=lambda: [
        LayerConfig(id="background", z_index=0),
        LayerConfig(id="sensors", z_index=1),
        LayerConfig(id="secondary_cues", z_index=2),
        LayerConfig(id="trigger_zones", z_index=3),
        LayerConfig(id="motion_paths", z_index=4),
    ])
    sensors: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    zones: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    secondary_cues: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate floorplan configuration."""
        if self.width <= 0:
            raise ValueError("Width must be positive")
        if self.height <= 0:
            raise ValueError("Height must be positive")
        if self.scale <= 0:
            raise ValueError("Scale must be positive")
    
    @property
    def dimensions(self) -> Tuple[int, int]:
        """Get floorplan dimensions.
        
        Returns:
            (width, height) tuple
        """
        return (self.width, self.height)
    
    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio of floorplan.
        
        Returns:
            Width / height ratio
        """
        return self.width / self.height
    
    def pixel_to_meters(self, pixels: float) -> float:
        """Convert pixels to meters using scale.
        
        Args:
            pixels: Distance in pixels
            
        Returns:
            Distance in meters
        """
        return pixels / self.scale
    
    def meters_to_pixels(self, meters: float) -> float:
        """Convert meters to pixels using scale.
        
        Args:
            meters: Distance in meters
            
        Returns:
            Distance in pixels
        """
        return meters * self.scale
    
    def is_point_in_bounds(self, position: Tuple[float, float]) -> bool:
        """Check if a point is within floorplan bounds.
        
        Args:
            position: (x, y) coordinates
            
        Returns:
            True if point is within bounds
        """
        x, y = position
        return 0 <= x <= self.width and 0 <= y <= self.height
    
    def add_sensor(self, entity_id: str, config: Dict[str, Any]) -> None:
        """Add a sensor to the floorplan.
        
        Args:
            entity_id: Home Assistant entity ID
            config: Sensor configuration dictionary
        """
        self.sensors[entity_id] = config
    
    def remove_sensor(self, entity_id: str) -> None:
        """Remove a sensor from the floorplan.
        
        Args:
            entity_id: Home Assistant entity ID
        """
        if entity_id in self.sensors:
            del self.sensors[entity_id]
    
    def get_sensor(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get sensor configuration.
        
        Args:
            entity_id: Home Assistant entity ID
            
        Returns:
            Sensor configuration or None
        """
        return self.sensors.get(entity_id)
    
    def add_zone(self, zone_id: str, config: Dict[str, Any]) -> None:
        """Add a zone to the floorplan.
        
        Args:
            zone_id: Zone identifier
            config: Zone configuration dictionary
        """
        self.zones[zone_id] = config
    
    def remove_zone(self, zone_id: str) -> None:
        """Remove a zone from the floorplan.
        
        Args:
            zone_id: Zone identifier
        """
        if zone_id in self.zones:
            del self.zones[zone_id]
    
    def get_zone(self, zone_id: str) -> Optional[Dict[str, Any]]:
        """Get zone configuration.
        
        Args:
            zone_id: Zone identifier
            
        Returns:
            Zone configuration or None
        """
        return self.zones.get(zone_id)
    
    def add_secondary_cue(self, cue_id: str, config: Dict[str, Any]) -> None:
        """Add a secondary cue to the floorplan.
        
        Args:
            cue_id: Cue identifier
            config: Cue configuration dictionary
        """
        self.secondary_cues[cue_id] = config
    
    def remove_secondary_cue(self, cue_id: str) -> None:
        """Remove a secondary cue from the floorplan.
        
        Args:
            cue_id: Cue identifier
        """
        if cue_id in self.secondary_cues:
            del self.secondary_cues[cue_id]
    
    def get_secondary_cue(self, cue_id: str) -> Optional[Dict[str, Any]]:
        """Get secondary cue configuration.
        
        Args:
            cue_id: Cue identifier
            
        Returns:
            Cue configuration or None
        """
        return self.secondary_cues.get(cue_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert floorplan to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "scale": self.scale,
            "background": {
                "image": self.background.image,
                "opacity": self.background.opacity,
            },
            "grid": {
                "enabled": self.grid.enabled,
                "size": self.grid.size,
                "snap": self.grid.snap,
            },
            "layers": [
                {
                    "id": layer.id,
                    "z_index": layer.z_index,
                    "visible": layer.visible,
                }
                for layer in self.layers
            ],
            "sensors": self.sensors,
            "zones": self.zones,
            "secondary_cues": self.secondary_cues,
        }
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """Export floorplan as JSON.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_yaml(self) -> str:
        """Export floorplan as YAML.
        
        Returns:
            YAML string
        """
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Floorplan":
        """Create floorplan from dictionary.
        
        Args:
            data: Dictionary with floorplan data
            
        Returns:
            Floorplan instance
        """
        # Extract nested configurations
        background_data = data.get("background", {})
        background = BackgroundConfig(
            image=background_data.get("image"),
            opacity=background_data.get("opacity", 0.5),
        )
        
        grid_data = data.get("grid", {})
        grid = GridConfig(
            enabled=grid_data.get("enabled", True),
            size=grid_data.get("size", 20),
            snap=grid_data.get("snap", True),
        )
        
        layers_data = data.get("layers", [])
        layers = [
            LayerConfig(
                id=layer["id"],
                z_index=layer.get("z_index", 0),
                visible=layer.get("visible", True),
            )
            for layer in layers_data
        ]
        
        return cls(
            id=data["id"],
            name=data["name"],
            width=data["width"],
            height=data["height"],
            scale=data.get("scale", 10.0),
            background=background,
            grid=grid,
            layers=layers or cls.layers.default_factory(),
            sensors=data.get("sensors", {}),
            zones=data.get("zones", {}),
            secondary_cues=data.get("secondary_cues", {}),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Floorplan":
        """Create floorplan from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            Floorplan instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> "Floorplan":
        """Create floorplan from YAML string.
        
        Args:
            yaml_str: YAML string
            
        Returns:
            Floorplan instance
        """
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"Floorplan(id={self.id}, name={self.name}, "
            f"dimensions={self.width}x{self.height}, "
            f"sensors={len(self.sensors)}, zones={len(self.zones)}, "
            f"cues={len(self.secondary_cues)})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()
