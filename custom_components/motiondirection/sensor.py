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
    
    # Create zone sensors for each zone
    for zone in coordinator.zone_manager.zones.values():
        entities.extend([
            ZoneDirectionSensor(coordinator, config_entry, zone),
            ZoneStatisticsSensor(coordinator, config_entry, zone),
        ])
    
    # Create secondary cue sensors for each cue
    for cue in coordinator.hybrid_detector.cues.values():
        entities.append(SecondaryCueStatusSensor(coordinator, config_entry, cue.id))
    
    # Create global correlation sensor
    entities.append(CueCorrelationSensor(coordinator, config_entry))
    
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


class ZoneDirectionSensor(CoordinatorEntity, SensorEntity):
    """Sensor for zone direction detection."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:compass-outline"

    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
        zone: Any,
    ) -> None:
        """Initialize the zone direction sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{config_entry.entry_id}_zone_{zone.id}_direction"
        self._attr_name = f"{zone.name} Direction"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_zone_{zone.id}")},
            name=f"Zone {zone.name}",
            model="Trigger Zone",
            manufacturer="MotionDirection",
        )

    @property
    def native_value(self) -> str | None:
        """Return the current direction."""
        return self._zone.last_direction

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {
            "zone_id": self._zone.id,
            "zone_name": self._zone.name,
            "available_directions": [d.name for d in self._zone.known_directions],
        }

        # Get zone state from coordinator
        zone_state = self.coordinator.get_zone_state(self._zone.id)
        if zone_state:
            attrs.update({
                "confidence": zone_state.get("confidence"),
                "vector": zone_state.get("vector"),
                "entry_time": zone_state.get("entry_time"),
                "exit_time": zone_state.get("exit_time"),
                "dwell_time": zone_state.get("dwell_time"),
                "transit_speed": zone_state.get("transit_speed"),
                "triggered_sensors": zone_state.get("triggered_sensors", []),
                "history": zone_state.get("history", []),
            })

        return attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class ZoneStatisticsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for zone statistics."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:chart-line"
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
        zone: Any,
    ) -> None:
        """Initialize the zone statistics sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{config_entry.entry_id}_zone_{zone.id}_statistics"
        self._attr_name = f"{zone.name} Statistics"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_zone_{zone.id}")},
            name=f"Zone {zone.name}",
            model="Trigger Zone",
            manufacturer="MotionDirection",
        )

    @property
    def native_value(self) -> int | None:
        """Return the total transitions today."""
        stats = self.coordinator.get_zone_statistics(self._zone.id)
        return stats.get("transitions_today") if stats else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        stats = self.coordinator.get_zone_statistics(self._zone.id)
        if not stats:
            return {
                "zone_id": self._zone.id,
                "zone_name": self._zone.name,
            }

        return {
            "zone_id": self._zone.id,
            "zone_name": self._zone.name,
            "transitions_today": stats.get("transitions_today", 0),
            "transitions_hour": stats.get("transitions_hour", 0),
            "common_direction": stats.get("common_direction"),
            "direction_breakdown": stats.get("direction_breakdown", {}),
            "average_dwell_time": stats.get("average_dwell_time"),
            "average_transit_time": stats.get("average_transit_time"),
            "peak_hour": stats.get("peak_hour"),
            "last_reset": stats.get("last_reset"),
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class SecondaryCueStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for secondary cue status."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:electric-switch"

    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
        cue_id: str,
    ) -> None:
        """Initialize the secondary cue status sensor."""
        super().__init__(coordinator)
        self._cue_id = cue_id
        self._attr_unique_id = f"{config_entry.entry_id}_cue_{cue_id}_status"
        self._attr_name = f"Cue {cue_id} Status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_cue_{cue_id}")},
            name=f"Secondary Cue {cue_id}",
            model="Secondary Cue",
            manufacturer="MotionDirection",
        )

    @property
    def native_value(self) -> str | None:
        """Return the cue status (active, idle, or triggered)."""
        cue_state = self.coordinator.get_cue_state(self._cue_id)
        return cue_state.get("status") if cue_state else "idle"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        cue = self.coordinator.hybrid_detector.cues.get(self._cue_id)
        if not cue:
            return {"cue_id": self._cue_id}

        cue_state = self.coordinator.get_cue_state(self._cue_id)
        attrs = {
            "cue_id": self._cue_id,
            "cue_type": cue.cue_type,
            "entity_id": cue.entity_id,
            "position": {"x": cue.position[0], "y": cue.position[1]},
        }

        if cue_state:
            attrs.update({
                "last_trigger": cue_state.get("last_trigger"),
                "last_state_change": cue_state.get("last_state_change"),
                "implied_direction": cue_state.get("implied_direction"),
                "implied_confidence": cue_state.get("implied_confidence"),
                "correlation_count_today": cue_state.get("correlation_count_today", 0),
                "correlation_success_rate": cue_state.get("correlation_success_rate"),
            })

        return attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class CueCorrelationSensor(CoordinatorEntity, SensorEntity):
    """Sensor for cue correlation analysis."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:chart-scatter-plot"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the cue correlation sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_cue_correlation"
        self._attr_name = "Cue Correlation Analysis"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name="MotionDirection",
            model="Motion Direction Integration",
            manufacturer="MotionDirection",
        )

    @property
    def native_value(self) -> int | None:
        """Return the number of active correlations."""
        correlation_data = self.coordinator.get_correlation_data()
        active = correlation_data.get("active_correlations", [])
        return len(active)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        correlation_data = self.coordinator.get_correlation_data()
        return {
            "active_correlations": correlation_data.get("active_correlations", []),
            "correlation_statistics": correlation_data.get("correlation_statistics", {}),
            "top_correlations": correlation_data.get("top_correlations", []),
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
