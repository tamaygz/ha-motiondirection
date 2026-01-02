"""
Motion Direction Detection Integration for Home Assistant.

This integration provides intelligent motion direction detection by analyzing
sequential triggering patterns of multiple motion sensors, with support for
visual floorplan configuration, trigger zones, and secondary cues.
"""
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import MotionDirectionCoordinator

_LOGGER = logging.getLogger(__name__)

# Platforms to set up
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Motion Direction component from YAML configuration.
    
    Args:
        hass: Home Assistant instance
        config: Configuration dictionary
        
    Returns:
        True if setup was successful
    """
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Motion Direction from a config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry
        
    Returns:
        True if setup was successful
    """
    _LOGGER.info("Setting up Motion Direction integration")
    
    # Get floorplan ID from config entry
    floorplan_id = entry.data.get("floorplan_id", "default")
    
    # Create coordinator
    coordinator = MotionDirectionCoordinator(hass, floorplan_id)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    await async_register_services(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry
        
    Returns:
        True if unload was successful
    """
    _LOGGER.info("Unloading Motion Direction integration")
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Remove data
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry.
    
    Args:
        hass: Home Assistant instance
        entry: Config entry
    """
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_register_services(hass: HomeAssistant) -> None:
    """Register integration services.
    
    Args:
        hass: Home Assistant instance
    """
    # Only register services once
    if hass.services.has_service(DOMAIN, "calibrate"):
        return
    
    # Service schema definitions
    SERVICE_CALIBRATE_SCHEMA = vol.Schema({
        vol.Optional("floorplan_id"): cv.string,
        vol.Optional("mode", default="automatic"): vol.In(["automatic", "manual", "guided"]),
        vol.Optional("duration", default=300): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
        vol.Optional("calibration_type", default="all"): vol.In(["sensors", "zones", "cues", "all"]),
    })
    
    SERVICE_CLEAR_HISTORY_SCHEMA = vol.Schema({
        vol.Optional("floorplan_id"): cv.string,
        vol.Optional("before_date"): cv.string,
        vol.Optional("entity_types"): vol.All(cv.ensure_list, [vol.In(["motion", "zone", "cue"])]),
    })
    
    SERVICE_SIMULATE_SCHEMA = vol.Schema({
        vol.Required("floorplan_id"): cv.string,
        vol.Optional("include_zones", default=True): cv.boolean,
        vol.Optional("include_cues", default=False): cv.boolean,
    })
    
    @callback
    async def async_handle_calibrate(call: ServiceCall) -> None:
        """Handle calibrate service call.
        
        Args:
            call: Service call data
        """
        floorplan_id = call.data.get("floorplan_id")
        mode = call.data.get("mode", "automatic")
        duration = call.data.get("duration", 300)
        calibration_type = call.data.get("calibration_type", "all")
        
        _LOGGER.info(
            "Calibrate service called: floorplan=%s, mode=%s, duration=%d, type=%s",
            floorplan_id,
            mode,
            duration,
            calibration_type,
        )
        
        # Get coordinator for floorplan
        coordinators = _get_coordinators(hass, floorplan_id)
        
        for coordinator in coordinators:
            try:
                await coordinator.async_calibrate(duration)
                _LOGGER.info("Calibration completed for floorplan: %s", coordinator.floorplan_id)
            except Exception as err:
                _LOGGER.error("Error during calibration: %s", err)
    
    @callback
    async def async_handle_clear_history(call: ServiceCall) -> None:
        """Handle clear_history service call.
        
        Args:
            call: Service call data
        """
        floorplan_id = call.data.get("floorplan_id")
        entity_types = call.data.get("entity_types", ["motion", "zone", "cue"])
        
        _LOGGER.info(
            "Clear history service called: floorplan=%s, types=%s",
            floorplan_id,
            entity_types,
        )
        
        # Get coordinator for floorplan
        coordinators = _get_coordinators(hass, floorplan_id)
        
        for coordinator in coordinators:
            try:
                await coordinator.async_clear_history()
                _LOGGER.info("History cleared for floorplan: %s", coordinator.floorplan_id)
            except Exception as err:
                _LOGGER.error("Error clearing history: %s", err)
    
    @callback
    async def async_handle_simulate(call: ServiceCall) -> None:
        """Handle simulate service call.
        
        Args:
            call: Service call data
        """
        floorplan_id = call.data.get("floorplan_id")
        include_zones = call.data.get("include_zones", True)
        include_cues = call.data.get("include_cues", False)
        
        _LOGGER.info(
            "Simulate service called: floorplan=%s, zones=%s, cues=%s",
            floorplan_id,
            include_zones,
            include_cues,
        )
        
        # Simulation logic would be implemented here
        _LOGGER.warning("Simulation service is not yet fully implemented")
    
    # Register services
    hass.services.async_register(
        DOMAIN,
        "calibrate",
        async_handle_calibrate,
        schema=SERVICE_CALIBRATE_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "clear_history",
        async_handle_clear_history,
        schema=SERVICE_CLEAR_HISTORY_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "simulate",
        async_handle_simulate,
        schema=SERVICE_SIMULATE_SCHEMA,
    )
    
    _LOGGER.info("Motion Direction services registered")


def _get_coordinators(
    hass: HomeAssistant,
    floorplan_id: str | None = None,
) -> list[MotionDirectionCoordinator]:
    """Get coordinators for specified floorplan or all.
    
    Args:
        hass: Home Assistant instance
        floorplan_id: Floorplan ID filter (optional)
    
    Returns:
        List of coordinators
    """
    coordinators = []
    
    for entry_id, coordinator in hass.data.get(DOMAIN, {}).items():
        if isinstance(coordinator, MotionDirectionCoordinator):
            if floorplan_id is None or coordinator.floorplan_id == floorplan_id:
                coordinators.append(coordinator)
    
    return coordinators
