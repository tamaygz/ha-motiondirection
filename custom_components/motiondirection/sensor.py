"""Sensor platform for Motion Direction integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MotionDirectionCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Motion Direction sensor entities.
    
    Args:
        hass: Home Assistant instance
        config_entry: Config entry
        async_add_entities: Callback to add entities
    """
    coordinator: MotionDirectionCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        MotionDirectionSensor(coordinator, config_entry),
        MotionPatternSensor(coordinator, config_entry),
    ]
    
    async_add_entities(entities)


class MotionDirectionSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity for motion direction detection.
    
    Represents the primary direction of detected motion with rich attributes
    including confidence, detection method, speed, and contributing sensors.
    """
    
    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize motion direction sensor.
        
        Args:
            coordinator: Motion direction coordinator
            config_entry: Config entry
        """
        super().__init__(coordinator)
        
        self._attr_name = "Motion Direction"
        self._attr_unique_id = f"{config_entry.entry_id}_motion_direction"
        self._attr_icon = "mdi:compass"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"Motion Direction {coordinator.floorplan_id}",
            manufacturer="Motion Direction",
            model="Motion Detection System",
            sw_version="1.0.0",
        )
    
    @property
    def native_value(self) -> str | None:
        """Return the current direction.
        
        Returns:
            Direction string or None
        """
        if self.coordinator.last_direction:
            return self.coordinator.last_direction.direction
        return None
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes.
        
        Returns:
            Dictionary of attributes
        """
        if not self.coordinator.last_direction:
            return {}
        
        result = self.coordinator.last_direction
        
        attributes = {
            "confidence": round(result.confidence, 2),
            "detection_method": result.method,
            "last_update": result.timestamp.isoformat(),
        }
        
        # Add vector if available
        if hasattr(result, "vector") and result.vector:
            attributes["vector"] = result.vector
        
        # Add speed if available
        if hasattr(result, "speed") and result.speed:
            attributes["speed"] = round(result.speed, 2)
            attributes["speed_unit"] = UnitOfSpeed.METERS_PER_SECOND
        
        # Add triggered sensors
        if result.motion_sensor_id:
            attributes["triggered_sensors"] = [result.motion_sensor_id]
        
        # Add contributing cues
        if hasattr(result, "contributing_cues") and result.contributing_cues:
            attributes["contributing_cues"] = result.contributing_cues
            attributes["cue_count"] = len(result.contributing_cues)
        
        # Add active zones
        if self.coordinator.active_zones:
            attributes["active_zones"] = self.coordinator.active_zones
        
        return attributes
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class MotionPatternSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity for motion pattern classification.
    
    Classifies detected motion into patterns: linear, circular, stationary,
    random, or zone_transition.
    """
    
    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize motion pattern sensor.
        
        Args:
            coordinator: Motion direction coordinator
            config_entry: Config entry
        """
        super().__init__(coordinator)
        
        self._attr_name = "Motion Pattern"
        self._attr_unique_id = f"{config_entry.entry_id}_motion_pattern"
        self._attr_icon = "mdi:chart-line-variant"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_options = [
            "linear",
            "circular",
            "stationary",
            "random",
            "zone_transition",
            "insufficient_data",
        ]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"Motion Direction {coordinator.floorplan_id}",
            manufacturer="Motion Direction",
            model="Motion Detection System",
            sw_version="1.0.0",
        )
        
        # Pattern history buffer
        self._pattern_history: list[dict[str, Any]] = []
    
    @property
    def native_value(self) -> str | None:
        """Return the current pattern type.
        
        Returns:
            Pattern type or None
        """
        return self.coordinator.last_pattern
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes.
        
        Returns:
            Dictionary of attributes
        """
        attributes: dict[str, Any] = {}
        
        if self.coordinator.last_pattern:
            attributes["pattern_type"] = self.coordinator.last_pattern
        
        # Add pattern confidence if available
        if self.coordinator.last_direction:
            attributes["pattern_confidence"] = round(
                self.coordinator.last_direction.confidence,
                2,
            )
        
        # Add pattern history (last 10)
        if self._pattern_history:
            attributes["pattern_history"] = self._pattern_history[-10:]
        
        # Add zone sequence if available
        if self.coordinator.active_zones:
            attributes["zone_sequence"] = self.coordinator.active_zones
        
        # Get pattern statistics from analyzer
        pattern_stats = self.coordinator.get_pattern_analyzer().get_pattern_statistics()
        if pattern_stats:
            attributes["pattern_statistics"] = pattern_stats
        
        return attributes
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Update pattern history
        if self.coordinator.last_pattern:
            self._pattern_history.append({
                "pattern": self.coordinator.last_pattern,
                "timestamp": datetime.now().isoformat(),
                "confidence": (
                    self.coordinator.last_direction.confidence
                    if self.coordinator.last_direction
                    else 0.0
                ),
            })
            
            # Keep only last 100 entries
            if len(self._pattern_history) > 100:
                self._pattern_history = self._pattern_history[-100:]
        
        self.async_write_ha_state()
