"""
Motion Direction Detection Integration for Home Assistant.

This integration provides intelligent motion direction detection by analyzing
sequential triggering patterns of multiple motion sensors, with support for
visual floorplan configuration, trigger zones, and secondary cues.
"""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
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
    
    # Register services (will be implemented in future commits)
    # await async_register_services(hass)
    
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
    
    This will be implemented when service handlers are created.
    
    Args:
        hass: Home Assistant instance
    """
    # TODO: Register services
    # - calibrate
    # - clear_history
    # - simulate
    # - calibrate_zone
    # - create_zone
    # - update_zone_direction
    # - test_zone_trigger
    # - analyze_zone_patterns
    # - learn_zone_directions
    # - add_secondary_cue
    # - configure_cue_hints
    # - analyze_cue_correlations
    # - learn_cue_patterns
    # - test_hybrid_detection
    # - analyze_pattern
    # - generate_report
    pass
