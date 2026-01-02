"""Binary sensor platform for Motion Direction integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
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
    """Set up Motion Direction binary sensor entities.
    
    Args:
        hass: Home Assistant instance
        config_entry: Config entry
        async_add_entities: Callback to add entities
    """
    coordinator: MotionDirectionCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        MotionDetectedBinarySensor(coordinator, config_entry),
        MotionAnomalyBinarySensor(coordinator, config_entry),
    ]
    
    # Create zone occupancy and transit sensors for each zone
    for zone in coordinator.zone_manager.zones.values():
        entities.extend([
            ZoneOccupancyBinarySensor(coordinator, config_entry, zone),
            ZoneTransitBinarySensor(coordinator, config_entry, zone),
        ])
    
    async_add_entities(entities)


class MotionDetectedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for motion detection state.
    
    Indicates whether motion is currently detected by the system.
    """
    
    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize motion detected binary sensor.
        
        Args:
            coordinator: Motion direction coordinator
            config_entry: Config entry
        """
        super().__init__(coordinator)
        
        self._attr_name = "Motion Detected"
        self._attr_unique_id = f"{config_entry.entry_id}_motion_detected"
        self._attr_device_class = BinarySensorDeviceClass.MOTION
        self._attr_icon = "mdi:motion-sensor"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"Motion Direction {coordinator.floorplan_id}",
            manufacturer="Motion Direction",
            model="Motion Detection System",
            sw_version="1.0.0",
        )
    
    @property
    def is_on(self) -> bool:
        """Return true if motion is detected.
        
        Returns:
            Motion detection state
        """
        return self.coordinator.motion_detected
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes.
        
        Returns:
            Dictionary of attributes
        """
        attributes: dict[str, Any] = {}
        
        # Add active zones
        if self.coordinator.active_zones:
            attributes["active_zones"] = self.coordinator.active_zones
            attributes["zone_count"] = len(self.coordinator.active_zones)
        
        # Add detection method
        if self.coordinator.last_direction:
            attributes["detection_method"] = self.coordinator.last_direction.method
            
            # Add sensor count (triggered sensors)
            if self.coordinator.last_direction.motion_sensor_id:
                attributes["sensor_count"] = 1
                
            # Add cue count if hybrid/cue-assisted
            if hasattr(self.coordinator.last_direction, "contributing_cues"):
                cues = self.coordinator.last_direction.contributing_cues
                if cues:
                    attributes["cue_count"] = len(cues)
        
        return attributes
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class MotionAnomalyBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for motion anomaly detection.
    
    Indicates when unusual or unexpected motion patterns are detected.
    """
    
    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize motion anomaly binary sensor.
        
        Args:
            coordinator: Motion direction coordinator
            config_entry: Config entry
        """
        super().__init__(coordinator)
        
        self._attr_name = "Motion Anomaly"
        self._attr_unique_id = f"{config_entry.entry_id}_motion_anomaly"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:alert-circle"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.entry_id)},
            name=f"Motion Direction {coordinator.floorplan_id}",
            manufacturer="Motion Direction",
            model="Motion Detection System",
            sw_version="1.0.0",
        )
        
        # Anomaly tracking
        self._anomaly_score: float = 0.0
        self._anomaly_type: str | None = None
        self._expected_pattern: str | None = None
        self._actual_pattern: str | None = None
    
    @property
    def is_on(self) -> bool:
        """Return true if anomaly is detected.
        
        Returns:
            Anomaly detection state
        """
        return self.coordinator.anomaly_detected
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes.
        
        Returns:
            Dictionary of attributes
        """
        attributes: dict[str, Any] = {}
        
        if self.coordinator.anomaly_detected:
            attributes["anomaly_score"] = round(self._anomaly_score, 2)
            
            if self._anomaly_type:
                attributes["anomaly_type"] = self._anomaly_type
            
            if self._expected_pattern:
                attributes["expected_pattern"] = self._expected_pattern
            
            if self._actual_pattern:
                attributes["actual_pattern"] = self._actual_pattern
        
        return attributes
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Run anomaly detection if we have a recent direction result
        if self.coordinator.last_direction:
            # Detect anomalies using coordinator's detection logic
            is_anomaly, score, anomaly_type, expected, actual = self.coordinator.detect_anomaly(
                sensitivity=0.7,
            )
            
            if is_anomaly:
                self.set_anomaly(score, anomaly_type, expected, actual)
                
                # Fire anomaly event
                from ..models.event_data import AnomalyDetectedEventData
                from ..core.event_bus import create_timestamp
                
                self.coordinator.event_bus.fire_anomaly_detected(
                    AnomalyDetectedEventData(
                        anomaly_type=anomaly_type,
                        anomaly_score=round(score, 2),
                        expected_pattern=expected or "unknown",
                        actual_pattern=actual or "unknown",
                        confidence=self.coordinator.last_direction.confidence,
                        triggered_sensors=[self.coordinator.last_direction.motion_sensor_id] if self.coordinator.last_direction.motion_sensor_id else [],
                        timestamp=create_timestamp(),
                    ),
                )
            else:
                # Reset anomaly if no longer detected
                if self._anomaly_score > 0:
                    self._anomaly_score = 0.0
                    self._anomaly_type = None
                    self._expected_pattern = None
                    self._actual_pattern = None
                    self.coordinator.set_anomaly_state(False)
        
        self.async_write_ha_state()
    
    def set_anomaly(
        self,
        score: float,
        anomaly_type: str,
        expected: str | None = None,
        actual: str | None = None,
    ) -> None:
        """Set anomaly detection data.
        
        Args:
            score: Anomaly score (0.0-1.0)
            anomaly_type: Type of anomaly
            expected: Expected pattern
            actual: Actual pattern
        """
        self._anomaly_score = score
        self._anomaly_type = anomaly_type
        self._expected_pattern = expected
        self._actual_pattern = actual
        
        self.coordinator.set_anomaly_state(score > 0.7)


class ZoneOccupancyBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for zone occupancy detection."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY

    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
        zone: Any,
    ) -> None:
        """Initialize the zone occupancy binary sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{config_entry.entry_id}_zone_{zone.id}_occupied"
        self._attr_name = f"{zone.name} Occupied"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_zone_{zone.id}")},
            name=f"Zone {zone.name}",
            model="Trigger Zone",
            manufacturer="MotionDirection",
        )

    @property
    def is_on(self) -> bool:
        """Return True if zone is occupied."""
        return self._zone.current_state == "occupied"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {
            "zone_id": self._zone.id,
            "zone_name": self._zone.name,
        }

        # Get zone state from coordinator
        zone_state = self.coordinator.get_zone_state(self._zone.id)
        if zone_state:
            attrs.update({
                "occupancy_start": zone_state.get("occupancy_start"),
                "occupancy_duration": zone_state.get("occupancy_duration"),
                "last_direction": zone_state.get("last_direction"),
                "motion_detected": zone_state.get("motion_detected", False),
                "sensors_in_zone": zone_state.get("sensors_in_zone", []),
            })

        return attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()


class ZoneTransitBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for zone transit detection."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.MOTION

    def __init__(
        self,
        coordinator: MotionDirectionCoordinator,
        config_entry: ConfigEntry,
        zone: Any,
    ) -> None:
        """Initialize the zone transit binary sensor."""
        super().__init__(coordinator)
        self._zone = zone
        self._attr_unique_id = f"{config_entry.entry_id}_zone_{zone.id}_transit"
        self._attr_name = f"{zone.name} Transit"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{config_entry.entry_id}_zone_{zone.id}")},
            name=f"Zone {zone.name}",
            model="Trigger Zone",
            manufacturer="MotionDirection",
        )

    @property
    def is_on(self) -> bool:
        """Return True if zone is in transit state."""
        return self._zone.current_state == "transit"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attrs = {
            "zone_id": self._zone.id,
        }

        # Get zone state from coordinator
        zone_state = self.coordinator.get_zone_state(self._zone.id)
        if zone_state:
            attrs.update({
                "direction": zone_state.get("direction"),
                "confidence": zone_state.get("confidence"),
                "entry_point": zone_state.get("entry_point"),
                "current_position": zone_state.get("current_position"),
                "predicted_exit": zone_state.get("predicted_exit"),
                "progress": zone_state.get("progress"),
            })

        return attrs

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
