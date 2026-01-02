"""Floorplan manager for spatial configuration and sensor placement."""
from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Any, Dict

import yaml

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from ..const import DOMAIN, STORAGE_VERSION
from ..models import Floorplan, SensorNode

_LOGGER = logging.getLogger(__name__)


class FloorplanManager:
    """Manages floorplan configuration and sensor placement.
    
    Handles CRUD operations for floorplans, sensor positioning, and
    spatial calculations. Uses HA Storage API for persistence.
    
    Attributes:
        hass: Home Assistant instance
        floorplan_id: Unique floorplan identifier
        floorplan: Current floorplan configuration
        _store: Storage handler for persistence
    """
    
    def __init__(self, hass: HomeAssistant, floorplan_id: str) -> None:
        """Initialize floorplan manager.
        
        Args:
            hass: Home Assistant instance
            floorplan_id: Unique floorplan identifier
        """
        self.hass = hass
        self.floorplan_id = floorplan_id
        self.floorplan: Floorplan | None = None
        
        # Initialize storage
        self._store = Store(
            hass,
            STORAGE_VERSION,
            f"{DOMAIN}.floorplan.{floorplan_id}",
        )
    
    def _sensor_dict_to_node(self, entity_id: str, config: Dict[str, Any]) -> SensorNode:
        """Convert sensor dictionary to SensorNode object.
        
        Args:
            entity_id: Sensor entity ID
            config: Sensor configuration dictionary
            
        Returns:
            SensorNode object
        """
        return SensorNode(
            entity_id=entity_id,
            position=tuple(config["position"]),
            range=config.get("range", 50.0),
            weight=config.get("weight", 1.0),
            sensor_type=config.get("sensor_type", "pir"),
            reliability=config.get("reliability", 0.95),
            zone=config.get("zone"),
            detection_angle=config.get("detection_angle", 120.0),
            cooldown_period=config.get("cooldown_period", 2000),
        )
    
    def _sensor_node_to_dict(self, sensor: SensorNode) -> Dict[str, Any]:
        """Convert SensorNode object to dictionary.
        
        Args:
            sensor: SensorNode object
            
        Returns:
            Sensor configuration dictionary
        """
        return {
            "position": list(sensor.position),
            "range": sensor.range,
            "weight": sensor.weight,
            "sensor_type": sensor.sensor_type,
            "reliability": sensor.reliability,
            "zone": sensor.zone,
            "detection_angle": sensor.detection_angle,
            "cooldown_period": sensor.cooldown_period,
        }
    
    async def async_load(self) -> Floorplan | None:
        """Load floorplan from storage.
        
        Returns:
            Loaded floorplan or None if not found
        """
        try:
            data = await self._store.async_load()
            
            if data is None:
                _LOGGER.debug("No stored floorplan found for %s", self.floorplan_id)
                return None
            
            # Deserialize floorplan
            self.floorplan = self._deserialize_floorplan(data)
            
            _LOGGER.info("Loaded floorplan: %s", self.floorplan_id)
            return self.floorplan
        
        except Exception as ex:
            _LOGGER.exception("Error loading floorplan: %s", ex)
            return None
    
    async def async_save(self) -> None:
        """Save floorplan to storage."""
        if self.floorplan is None:
            _LOGGER.warning("No floorplan to save")
            return
        
        try:
            # Serialize floorplan
            data = self._serialize_floorplan(self.floorplan)
            
            # Save to storage
            await self._store.async_save(data)
            
            _LOGGER.info("Saved floorplan: %s", self.floorplan_id)
        
        except Exception as ex:
            _LOGGER.exception("Error saving floorplan: %s", ex)
    
    async def async_create(
        self,
        name: str,
        width: int,
        height: int,
        scale: int = 10,
        background_image: str | None = None,
    ) -> Floorplan:
        """Create new floorplan.
        
        Args:
            name: Floorplan name
            width: Width in pixels
            height: Height in pixels
            scale: Pixels per meter
            background_image: Optional background image path
        
        Returns:
            Created floorplan
        
        Raises:
            ValueError: If dimensions invalid
        """
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive")
        
        if scale <= 0:
            raise ValueError("Scale must be positive")
        
        # Create floorplan
        self.floorplan = Floorplan(
            id=self.floorplan_id,
            name=name,
            width=width,
            height=height,
            scale=scale,
        )
        
        if background_image:
            self.floorplan.background.image = background_image
        
        # Save to storage
        await self.async_save()
        
        _LOGGER.info(
            "Created floorplan: %s (%dx%d, scale=%d)",
            name,
            width,
            height,
            scale,
        )
        
        return self.floorplan
    
    async def async_update(self, **kwargs: Any) -> None:
        """Update floorplan properties.
        
        Args:
            **kwargs: Properties to update
        """
        if self.floorplan is None:
            raise ValueError("No floorplan loaded")
        
        # Update properties
        for key, value in kwargs.items():
            if hasattr(self.floorplan, key):
                setattr(self.floorplan, key, value)
                _LOGGER.debug("Updated %s: %s", key, value)
        
        # Save changes
        await self.async_save()
    
    async def async_delete(self) -> None:
        """Delete floorplan from storage."""
        await self._store.async_remove()
        self.floorplan = None
        
        _LOGGER.info("Deleted floorplan: %s", self.floorplan_id)
    
    def add_sensor(
        self,
        entity_id: str,
        position: tuple[float, float],
        sensor_range: float = 5.0,
        weight: float = 1.0,
        sensor_type: str = "motion",
        reliability: float = 0.8,
    ) -> SensorNode:
        """Add sensor to floorplan.
        
        Args:
            entity_id: Sensor entity ID
            position: (x, y) position on floorplan
            sensor_range: Detection range in meters
            weight: Weight for direction calculation
            sensor_type: Type of sensor
            reliability: Reliability score (0-1)
        
        Returns:
            Created sensor node
        
        Raises:
            ValueError: If position outside floorplan bounds
        """
        if self.floorplan is None:
            raise ValueError("No floorplan loaded")
        
        # Validate position
        if not self._is_position_valid(position):
            raise ValueError(
                f"Position {position} outside floorplan bounds "
                f"({self.floorplan.width}x{self.floorplan.height})"
            )
        
        # Create sensor node
        sensor = SensorNode(
            entity_id=entity_id,
            position=position,
            range=sensor_range,
            weight=weight,
            sensor_type=sensor_type,
            reliability=reliability,
        )
        
        # Add to floorplan - convert sensor to dict for storage
        sensor_config = {
            "position": position,
            "range": sensor_range,
            "weight": weight,
            "sensor_type": sensor_type,
            "reliability": reliability,
        }
        self.floorplan.add_sensor(entity_id, sensor_config)
        
        _LOGGER.info("Added sensor %s at %s", entity_id, position)
        
        return sensor
    
    def remove_sensor(self, entity_id: str) -> bool:
        """Remove sensor from floorplan.
        
        Args:
            entity_id: Sensor entity ID
        
        Returns:
            True if sensor was removed
        """
        if self.floorplan is None:
            return False
        
        if entity_id in self.floorplan.sensors:
            self.floorplan.remove_sensor(entity_id)
            _LOGGER.info("Removed sensor: %s", entity_id)
            return True
        
        return False
    
    def update_sensor_position(
        self,
        entity_id: str,
        position: tuple[float, float],
    ) -> bool:
        """Update sensor position.
        
        Args:
            entity_id: Sensor entity ID
            position: New (x, y) position
        
        Returns:
            True if position was updated
        
        Raises:
            ValueError: If position outside bounds
        """
        if self.floorplan is None:
            return False
        
        if not self._is_position_valid(position):
            raise ValueError("Position outside floorplan bounds")
        
        sensor_config = self.floorplan.get_sensor(entity_id)
        if sensor_config:
            sensor_config["position"] = list(position)
            _LOGGER.info("Updated sensor %s position to %s", entity_id, position)
            return True
        
        return False
    
    def get_sensor(self, entity_id: str) -> SensorNode | None:
        """Get sensor by entity ID.
        
        Args:
            entity_id: Sensor entity ID
        
        Returns:
            Sensor node or None if not found
        """
        if self.floorplan is None:
            return None
        
        sensor_config = self.floorplan.get_sensor(entity_id)
        if sensor_config:
            return self._sensor_dict_to_node(entity_id, sensor_config)
        return None
    
    def get_all_sensors(self) -> list[SensorNode]:
        """Get all sensors on floorplan.
        
        Returns:
            List of sensor nodes
        """
        if self.floorplan is None:
            return []
        
        return [
            self._sensor_dict_to_node(entity_id, config)
            for entity_id, config in self.floorplan.sensors.items()
        ]
    
    def detect_overlaps(
        self,
        threshold: float = 0.5,
    ) -> list[tuple[SensorNode, SensorNode]]:
        """Detect overlapping sensor ranges.
        
        Args:
            threshold: Overlap threshold (0-1, where 1 = complete overlap)
        
        Returns:
            List of overlapping sensor pairs
        """
        if self.floorplan is None:
            return []
        
        overlaps = []
        sensors = self.get_all_sensors()
        
        for i, sensor1 in enumerate(sensors):
            for sensor2 in sensors[i + 1:]:
                overlap_ratio = self._calculate_overlap(sensor1, sensor2)
                
                if overlap_ratio >= threshold:
                    overlaps.append((sensor1, sensor2))
        
        if overlaps:
            _LOGGER.info("Detected %d sensor overlaps", len(overlaps))
        
        return overlaps
    
    def snap_to_grid(
        self,
        position: tuple[float, float],
    ) -> tuple[float, float]:
        """Snap position to grid.
        
        Args:
            position: Original position
        
        Returns:
            Snapped position
        """
        if self.floorplan is None or not self.floorplan.grid.enabled:
            return position
        
        grid_size = self.floorplan.grid.size
        
        snapped_x = round(position[0] / grid_size) * grid_size
        snapped_y = round(position[1] / grid_size) * grid_size
        
        return (snapped_x, snapped_y)
    
    async def async_import_from_yaml(self, yaml_path: str) -> None:
        """Import floorplan from YAML file.
        
        Args:
            yaml_path: Path to YAML file
        """
        try:
            yaml_file = Path(yaml_path)
            
            if not yaml_file.exists():
                raise FileNotFoundError(f"YAML file not found: {yaml_path}")
            
            with yaml_file.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            
            # Deserialize and set floorplan
            self.floorplan = self._deserialize_floorplan(data)
            
            # Save to storage
            await self.async_save()
            
            _LOGGER.info("Imported floorplan from %s", yaml_path)
        
        except Exception as ex:
            _LOGGER.exception("Error importing YAML: %s", ex)
            raise
    
    async def async_export_to_yaml(self, yaml_path: str) -> None:
        """Export floorplan to YAML file.
        
        Args:
            yaml_path: Path to output YAML file
        """
        if self.floorplan is None:
            raise ValueError("No floorplan to export")
        
        try:
            # Serialize floorplan
            data = self._serialize_floorplan(self.floorplan)
            
            # Write YAML
            yaml_file = Path(yaml_path)
            yaml_file.parent.mkdir(parents=True, exist_ok=True)
            
            with yaml_file.open("w", encoding="utf-8") as file:
                yaml.dump(data, file, default_flow_style=False)
            
            _LOGGER.info("Exported floorplan to %s", yaml_path)
        
        except Exception as ex:
            _LOGGER.exception("Error exporting YAML: %s", ex)
            raise
    
    async def async_discover_sensors(self) -> list[str]:
        """Discover motion sensors in Home Assistant.
        
        Returns:
            List of discovered sensor entity IDs
        """
        discovered = []
        
        # Get entity registry
        entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)
        
        for entity in entity_registry.entities.values():
            # Filter for motion/occupancy sensors
            if (
                entity.domain == "binary_sensor"
                and entity.device_class in ("motion", "occupancy")
                and not entity.disabled
            ):
                discovered.append(entity.entity_id)
        
        _LOGGER.info("Discovered %d motion sensors", len(discovered))
        
        return discovered
    
    def _is_position_valid(self, position: tuple[float, float]) -> bool:
        """Check if position is within floorplan bounds.
        
        Args:
            position: Position to check
        
        Returns:
            True if position is valid
        """
        if self.floorplan is None:
            return False
        
        x, y = position
        return (
            0 <= x <= self.floorplan.width
            and 0 <= y <= self.floorplan.height
        )
    
    def _calculate_overlap(
        self,
        sensor1: SensorNode,
        sensor2: SensorNode,
    ) -> float:
        """Calculate overlap ratio between two sensors.
        
        Args:
            sensor1: First sensor
            sensor2: Second sensor
        
        Returns:
            Overlap ratio (0-1)
        """
        # Calculate distance between sensors
        dx = sensor2.position[0] - sensor1.position[0]
        dy = sensor2.position[1] - sensor1.position[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calculate sum of ranges
        range_sum = sensor1.range + sensor2.range
        
        # No overlap if distance >= sum of ranges
        if distance >= range_sum:
            return 0.0
        
        # Calculate overlap ratio
        # Maximum overlap (1.0) when sensors at same position
        # Decreases linearly to 0 as distance approaches range_sum
        overlap = 1.0 - (distance / range_sum)
        
        return max(0.0, min(overlap, 1.0))
    
    @staticmethod
    def _serialize_floorplan(floorplan: Floorplan) -> dict[str, Any]:
        """Serialize floorplan to dictionary.
        
        Args:
            floorplan: Floorplan to serialize
        
        Returns:
            Serialized data
        """
        return {
            "id": floorplan.id,
            "name": floorplan.name,
            "width": floorplan.width,
            "height": floorplan.height,
            "scale": floorplan.scale,
            "grid": {
                "enabled": floorplan.grid.enabled,
                "size": floorplan.grid.size,
                "snap": floorplan.grid.snap,
            },
            "background": {
                "image": floorplan.background.image,
                "opacity": floorplan.background.opacity,
            },
            "sensors": floorplan.sensors,
            "zones": floorplan.zones,
            "secondary_cues": floorplan.secondary_cues,
        }
    
    @staticmethod
    def _deserialize_floorplan(data: dict[str, Any]) -> Floorplan:
        """Deserialize floorplan from dictionary.
        
        Args:
            data: Serialized data
        
        Returns:
            Deserialized floorplan
        """
        floorplan = Floorplan(
            id=data["id"],
            name=data["name"],
            width=data["width"],
            height=data["height"],
            scale=data["scale"],
        )
        
        # Set grid configuration
        if "grid" in data:
            floorplan.grid.enabled = data["grid"].get("enabled", True)
            floorplan.grid.size = data["grid"].get("size", 20)
            floorplan.grid.snap = data["grid"].get("snap", True)
        
        # Set background configuration
        if "background" in data:
            floorplan.background.image = data["background"].get("image")
            floorplan.background.opacity = data["background"].get("opacity", 0.5)
        
        # Add sensors, zones, and cues directly as dictionaries
        floorplan.sensors = data.get("sensors", {})
        floorplan.zones = data.get("zones", {})
        floorplan.secondary_cues = data.get("secondary_cues", {})
        
        return floorplan
