"""
Motion Direction Detection Integration for Home Assistant.

This integration provides intelligent motion direction detection by analyzing
sequential triggering patterns of multiple motion sensors, with support for
visual floorplan configuration, trigger zones, and secondary cues.
"""
import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, INTEGRATION_VERSION
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
    
    # Zone service schemas
    SERVICE_CREATE_ZONE_SCHEMA = vol.Schema({
        vol.Required("floorplan_id"): cv.string,
        vol.Required("zone_id"): cv.string,
        vol.Required("name"): cv.string,
        vol.Required("polygon"): vol.All(cv.ensure_list, [vol.All(cv.ensure_list, [vol.Coerce(float)])]),
        vol.Optional("min_dwell_time", default=500): vol.All(vol.Coerce(int), vol.Range(min=100, max=10000)),
        vol.Optional("sensitivity", default=0.7): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
    })
    
    SERVICE_CALIBRATE_ZONE_SCHEMA = vol.Schema({
        vol.Required("zone_id"): cv.string,
        vol.Optional("mode", default="automatic"): vol.In(["automatic", "manual", "guided"]),
        vol.Optional("duration", default=300): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
        vol.Optional("learn_directions", default=True): cv.boolean,
    })
    
    SERVICE_UPDATE_ZONE_DIRECTION_SCHEMA = vol.Schema({
        vol.Required("zone_id"): cv.string,
        vol.Required("direction_name"): cv.string,
        vol.Optional("vector"): vol.All(cv.ensure_list, [vol.Coerce(float)]),
        vol.Optional("aliases"): vol.All(cv.ensure_list, [cv.string]),
    })
    
    SERVICE_TEST_ZONE_TRIGGER_SCHEMA = vol.Schema({
        vol.Required("zone_id"): cv.string,
        vol.Required("direction"): cv.string,
        vol.Optional("confidence", default=0.95): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
        vol.Optional("duration", default=2000): vol.All(vol.Coerce(int), vol.Range(min=100, max=10000)),
    })
    
    SERVICE_ANALYZE_ZONE_PATTERNS_SCHEMA = vol.Schema({
        vol.Optional("zone_id"): cv.string,
        vol.Optional("start_time"): cv.string,
        vol.Optional("end_time"): cv.string,
        vol.Optional("min_confidence", default=0.7): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
    })
    
    SERVICE_LEARN_ZONE_DIRECTIONS_SCHEMA = vol.Schema({
        vol.Required("zone_id"): cv.string,
        vol.Optional("learning_period", default=86400): vol.All(vol.Coerce(int), vol.Range(min=3600, max=604800)),
        vol.Optional("min_samples", default=20): vol.All(vol.Coerce(int), vol.Range(min=5, max=1000)),
        vol.Optional("update_config", default=True): cv.boolean,
    })
    
    # Cue service schemas
    SERVICE_ADD_SECONDARY_CUE_SCHEMA = vol.Schema({
        vol.Required("floorplan_id"): cv.string,
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("cue_type"): vol.In(["door", "light", "switch", "presence", "temperature", "vibration", "power", "media"]),
        vol.Required("position"): vol.All(cv.ensure_list, [vol.Coerce(float)]),
        vol.Optional("correlation_window", default=3000): vol.All(vol.Coerce(int), vol.Range(min=500, max=30000)),
        vol.Optional("confidence_weight", default=0.7): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
    })
    
    SERVICE_CONFIGURE_CUE_HINTS_SCHEMA = vol.Schema({
        vol.Required("cue_id"): cv.string,
        vol.Required("hints"): vol.All(cv.ensure_list, [dict]),
    })
    
    SERVICE_ANALYZE_CUE_CORRELATIONS_SCHEMA = vol.Schema({
        vol.Required("floorplan_id"): cv.string,
        vol.Optional("start_time"): cv.string,
        vol.Optional("end_time"): cv.string,
        vol.Optional("min_correlation", default=0.5): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
        vol.Optional("include_suggestions", default=True): cv.boolean,
    })
    
    SERVICE_LEARN_CUE_PATTERNS_SCHEMA = vol.Schema({
        vol.Required("floorplan_id"): cv.string,
        vol.Optional("learning_duration", default=604800): vol.All(vol.Coerce(int), vol.Range(min=86400, max=2592000)),
        vol.Optional("auto_apply", default=False): cv.boolean,
        vol.Optional("confidence_threshold", default=0.75): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=1.0)),
    })
    
    SERVICE_TEST_HYBRID_DETECTION_SCHEMA = vol.Schema({
        vol.Required("motion_sensor"): cv.entity_id,
        vol.Required("expected_direction"): cv.string,
        vol.Optional("test_duration", default=30): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
    })
    
    # Diagnostic service schemas
    SERVICE_GET_STATUS_SCHEMA = vol.Schema({
        vol.Optional("floorplan_id"): cv.string,
        vol.Optional("verbose", default=False): cv.boolean,
    })
    
    SERVICE_TEST_DETECTION_SCHEMA = vol.Schema({
        vol.Required("floorplan_id"): cv.string,
        vol.Optional("test_duration", default=60): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
        vol.Optional("verbose", default=False): cv.boolean,
    })
    
    SERVICE_VALIDATE_CONFIG_SCHEMA = vol.Schema({
        vol.Optional("floorplan_id"): cv.string,
    })
    
    # Analysis service schemas
    SERVICE_ANALYZE_PATTERN_SCHEMA = vol.Schema({
        vol.Required("start_time"): cv.string,
        vol.Required("end_time"): cv.string,
        vol.Optional("pattern_type", default="all"): vol.In(["linear", "circular", "zone_transition", "all"]),
        vol.Optional("min_confidence", default=0.6): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
        vol.Optional("floorplan_id"): cv.string,
    })
    
    SERVICE_GENERATE_REPORT_SCHEMA = vol.Schema({
        vol.Required("floorplan_id"): cv.string,
        vol.Optional("report_type", default="daily"): vol.In(["daily", "weekly", "monthly", "custom"]),
        vol.Optional("start_date"): cv.string,
        vol.Optional("end_date"): cv.string,
        vol.Optional("include_zones", default=True): cv.boolean,
        vol.Optional("include_cues", default=True): cv.boolean,
        vol.Optional("include_patterns", default=True): cv.boolean,
        vol.Optional("output_format", default="json"): vol.In(["pdf", "json", "yaml"]),
    })
    
    # Core service handlers
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
    
    # Zone service handlers
    @callback
    async def async_handle_create_zone(call: ServiceCall) -> None:
        """Handle create_zone service call."""
        floorplan_id = call.data["floorplan_id"]
        zone_id = call.data["zone_id"]
        name = call.data["name"]
        polygon = call.data["polygon"]
        min_dwell_time = call.data.get("min_dwell_time", 500)
        sensitivity = call.data.get("sensitivity", 0.7)
        
        _LOGGER.info("Create zone service called: %s on %s", zone_id, floorplan_id)
        
        coordinators = _get_coordinators(hass, floorplan_id)
        for coordinator in coordinators:
            try:
                from .models import TriggerZone
                zone = TriggerZone(
                    id=zone_id,
                    name=name,
                    polygon=polygon,
                    known_directions=[],
                    min_dwell_time=min_dwell_time,
                    sensitivity=sensitivity,
                )
                coordinator.get_zone_manager().add_zone(zone)
                _LOGGER.info("Zone created: %s", zone_id)
            except Exception as err:
                _LOGGER.error("Error creating zone: %s", err)
    
    @callback
    async def async_handle_calibrate_zone(call: ServiceCall) -> None:
        """Handle calibrate_zone service call."""
        zone_id = call.data["zone_id"]
        mode = call.data.get("mode", "automatic")
        duration = call.data.get("duration", 300)
        learn_directions = call.data.get("learn_directions", True)
        
        _LOGGER.info("Calibrate zone service called: %s, mode=%s, duration=%d", zone_id, mode, duration)
        _LOGGER.warning("Zone calibration is not yet fully implemented")
    
    @callback
    async def async_handle_update_zone_direction(call: ServiceCall) -> None:
        """Handle update_zone_direction service call."""
        zone_id = call.data["zone_id"]
        direction_name = call.data["direction_name"]
        vector = call.data.get("vector")
        aliases = call.data.get("aliases", [])
        
        _LOGGER.info("Update zone direction service called: %s, direction=%s", zone_id, direction_name)
        
        for coordinator in _get_coordinators(hass):
            try:
                zone_manager = coordinator.get_zone_manager()
                zone = zone_manager.get_zone(zone_id)
                if zone:
                    from .models import DirectionConfig
                    direction_config = DirectionConfig(
                        name=direction_name,
                        vector=tuple(vector) if vector else (0.0, 0.0),
                        aliases=aliases,
                    )
                    # Update zone's directions
                    zone.known_directions.append(direction_config)
                    _LOGGER.info("Zone direction updated: %s", zone_id)
                    break
            except Exception as err:
                _LOGGER.error("Error updating zone direction: %s", err)
    
    @callback
    async def async_handle_test_zone_trigger(call: ServiceCall) -> None:
        """Handle test_zone_trigger service call."""
        zone_id = call.data["zone_id"]
        direction = call.data["direction"]
        confidence = call.data.get("confidence", 0.95)
        duration = call.data.get("duration", 2000)
        
        _LOGGER.info("Test zone trigger service called: %s, direction=%s", zone_id, direction)
        _LOGGER.warning("Zone trigger testing is not yet fully implemented")
    
    @callback
    async def async_handle_analyze_zone_patterns(call: ServiceCall) -> None:
        """Handle analyze_zone_patterns service call."""
        zone_id = call.data.get("zone_id")
        min_confidence = call.data.get("min_confidence", 0.7)
        
        _LOGGER.info("Analyze zone patterns service called: zone=%s", zone_id)
        
        for coordinator in _get_coordinators(hass):
            try:
                pattern_analyzer = coordinator.get_pattern_analyzer()
                stats = pattern_analyzer.get_pattern_statistics()
                _LOGGER.info("Zone pattern analysis: %s", stats)
            except Exception as err:
                _LOGGER.error("Error analyzing zone patterns: %s", err)
    
    @callback
    async def async_handle_learn_zone_directions(call: ServiceCall) -> None:
        """Handle learn_zone_directions service call."""
        zone_id = call.data["zone_id"]
        learning_period = call.data.get("learning_period", 86400)
        min_samples = call.data.get("min_samples", 20)
        update_config = call.data.get("update_config", True)
        
        _LOGGER.info("Learn zone directions service called: %s, period=%d", zone_id, learning_period)
        _LOGGER.warning("Zone direction learning is not yet fully implemented")
    
    # Cue service handlers
    @callback
    async def async_handle_add_secondary_cue(call: ServiceCall) -> None:
        """Handle add_secondary_cue service call."""
        floorplan_id = call.data["floorplan_id"]
        entity_id = call.data["entity_id"]
        cue_type = call.data["cue_type"]
        position = tuple(call.data["position"])
        correlation_window = call.data.get("correlation_window", 3000)
        confidence_weight = call.data.get("confidence_weight", 0.7)
        
        _LOGGER.info("Add secondary cue service called: %s, type=%s", entity_id, cue_type)
        
        coordinators = _get_coordinators(hass, floorplan_id)
        for coordinator in coordinators:
            try:
                from .models import SecondaryCue, CueTypeRegistry
                
                # Get default hints for cue type
                default_hints = CueTypeRegistry.get_default_hints(cue_type)
                
                cue = SecondaryCue(
                    id=f"cue_{entity_id.replace('.', '_')}",
                    name=entity_id.split('.')[-1].replace('_', ' ').title(),
                    entity_id=entity_id,
                    cue_type=cue_type,
                    position=position,
                    directional_hints=[],  # Would be configured via configure_cue_hints
                    correlation_window=correlation_window,
                    confidence_weight=confidence_weight,
                )
                coordinator.get_hybrid_detector().add_cue(cue)
                _LOGGER.info("Secondary cue added: %s", cue.id)
            except Exception as err:
                _LOGGER.error("Error adding secondary cue: %s", err)
    
    @callback
    async def async_handle_configure_cue_hints(call: ServiceCall) -> None:
        """Handle configure_cue_hints service call."""
        cue_id = call.data["cue_id"]
        hints = call.data["hints"]
        
        _LOGGER.info("Configure cue hints service called: %s, hints=%d", cue_id, len(hints))
        _LOGGER.warning("Cue hint configuration is not yet fully implemented")
    
    @callback
    async def async_handle_analyze_cue_correlations(call: ServiceCall) -> None:
        """Handle analyze_cue_correlations service call."""
        floorplan_id = call.data["floorplan_id"]
        min_correlation = call.data.get("min_correlation", 0.5)
        include_suggestions = call.data.get("include_suggestions", True)
        
        _LOGGER.info("Analyze cue correlations service called: %s", floorplan_id)
        _LOGGER.warning("Cue correlation analysis is not yet fully implemented")
    
    @callback
    async def async_handle_learn_cue_patterns(call: ServiceCall) -> None:
        """Handle learn_cue_patterns service call."""
        floorplan_id = call.data["floorplan_id"]
        learning_duration = call.data.get("learning_duration", 604800)
        auto_apply = call.data.get("auto_apply", False)
        confidence_threshold = call.data.get("confidence_threshold", 0.75)
        
        _LOGGER.info("Learn cue patterns service called: %s, duration=%d", floorplan_id, learning_duration)
        _LOGGER.warning("Cue pattern learning is not yet fully implemented")
    
    @callback
    async def async_handle_test_hybrid_detection(call: ServiceCall) -> None:
        """Handle test_hybrid_detection service call."""
        motion_sensor = call.data["motion_sensor"]
        expected_direction = call.data["expected_direction"]
        test_duration = call.data.get("test_duration", 30)
        
        _LOGGER.info("Test hybrid detection service called: sensor=%s, direction=%s", motion_sensor, expected_direction)
        _LOGGER.warning("Hybrid detection testing is not yet fully implemented")
    
    # Analysis service handlers
    @callback
    async def async_handle_analyze_pattern(call: ServiceCall) -> None:
        """Handle analyze_pattern service call."""
        pattern_type = call.data.get("pattern_type", "all")
        min_confidence = call.data.get("min_confidence", 0.6)
        floorplan_id = call.data.get("floorplan_id")
        
        _LOGGER.info("Analyze pattern service called: type=%s, min_confidence=%.2f", pattern_type, min_confidence)
        
        coordinators = _get_coordinators(hass, floorplan_id)
        for coordinator in coordinators:
            try:
                pattern_analyzer = coordinator.get_pattern_analyzer()
                stats = pattern_analyzer.get_pattern_statistics()
                _LOGGER.info("Pattern analysis results: %s", stats)
            except Exception as err:
                _LOGGER.error("Error analyzing patterns: %s", err)
    
    @callback
    async def async_handle_generate_report(call: ServiceCall) -> None:
        """Handle generate_report service call."""
        floorplan_id = call.data["floorplan_id"]
        report_type = call.data.get("report_type", "daily")
        output_format = call.data.get("output_format", "json")
        include_zones = call.data.get("include_zones", True)
        include_cues = call.data.get("include_cues", True)
        include_patterns = call.data.get("include_patterns", True)
        
        _LOGGER.info("Generate report service called: %s, type=%s, format=%s", floorplan_id, report_type, output_format)
        
        coordinators = _get_coordinators(hass, floorplan_id)
        for coordinator in coordinators:
            try:
                # Gather report data
                report_data = {
                    "floorplan_id": coordinator.floorplan_id,
                    "report_type": report_type,
                    "timestamp": coordinator.data.get("timestamp").isoformat() if coordinator.data else None,
                }
                
                if include_patterns:
                    pattern_analyzer = coordinator.get_pattern_analyzer()
                    report_data["patterns"] = pattern_analyzer.get_pattern_statistics()
                
                if include_zones:
                    report_data["zones"] = {"count": len(coordinator.get_zone_manager().zones)}
                
                if include_cues:
                    report_data["cues"] = {"count": coordinator.get_hybrid_detector().get_cue_count()}
                
                _LOGGER.info("Report generated: %s", report_data)
                
                # In a full implementation, would save to file/persistent storage
                
            except Exception as err:
                _LOGGER.error("Error generating report: %s", err)
    
    # Diagnostic service handlers
    @callback
    async def async_handle_get_status(call: ServiceCall) -> ServiceResponse:
        """Handle get_status service call."""
        floorplan_id = call.data.get("floorplan_id")
        include_performance = call.data.get("include_performance", True)
        include_config = call.data.get("include_config", False)
        include_errors = call.data.get("include_errors", True)
        
        _LOGGER.info("Get status service called: %s", floorplan_id)
        
        status_data = {
            "integration_version": INTEGRATION_VERSION,
            "floorplans": {},
        }
        
        coordinators = _get_coordinators(hass, floorplan_id)
        for coordinator in coordinators:
            floorplan_status = {
                "state": "online" if coordinator.last_update_success else "offline",
                "last_update": coordinator.last_update_success_time.isoformat() if coordinator.last_update_success_time else None,
                "sensors_count": len([e for e in hass.data[DOMAIN].get("entities", []) if hasattr(e, "coordinator") and e.coordinator == coordinator]),
            }
            
            if include_performance:
                floorplan_status["performance"] = {
                    "detection_count": coordinator.get_detection_count(),
                    "average_detection_time": coordinator.get_average_detection_time(),
                    "queue_size": coordinator.get_event_queue_size(),
                }
            
            if include_config:
                floorplan_status["config"] = {
                    "detection_timeout": coordinator.detection_config.detection_timeout_ms,
                    "confidence_threshold": coordinator.detection_config.min_confidence_threshold,
                    "time_window": coordinator.detection_config.time_window_ms,
                }
            
            if include_errors:
                floorplan_status["errors"] = coordinator.get_recent_errors()
            
            status_data["floorplans"][coordinator.floorplan_id] = floorplan_status
        
        return status_data
    
    @callback
    async def async_handle_test_detection(call: ServiceCall) -> ServiceResponse:
        """Handle test_detection service call."""
        floorplan_id = call.data["floorplan_id"]
        test_sensors = call.data.get("test_sensors", [])
        test_duration = call.data.get("test_duration", 60)
        expected_direction = call.data.get("expected_direction")
        
        _LOGGER.info("Test detection service called: %s, duration=%d", floorplan_id, test_duration)
        
        coordinators = _get_coordinators(hass, floorplan_id)
        if not coordinators:
            return {
                "success": False,
                "error": f"Floorplan {floorplan_id} not found",
            }
        
        coordinator = coordinators[0]
        
        # Begin test mode
        test_results = {
            "floorplan_id": floorplan_id,
            "test_duration": test_duration,
            "test_sensors": test_sensors,
            "expected_direction": expected_direction,
            "detections": [],
            "accuracy": 0.0,
            "success": True,
        }
        
        try:
            # Enable test mode in coordinator
            coordinator.enable_test_mode(test_duration, test_sensors)
            
            # Wait for test duration (in production, would return immediately and fire event when done)
            await asyncio.sleep(min(test_duration, 5))  # Cap at 5 seconds for immediate feedback
            
            # Get test results
            test_detections = coordinator.get_test_results()
            test_results["detections"] = [
                {
                    "timestamp": d.timestamp.isoformat(),
                    "direction": d.direction,
                    "confidence": d.confidence,
                    "method": d.detection_method,
                }
                for d in test_detections
            ]
            
            # Calculate accuracy if expected direction provided
            if expected_direction:
                correct = sum(1 for d in test_detections if d.direction == expected_direction)
                test_results["accuracy"] = correct / len(test_detections) if test_detections else 0.0
            
            _LOGGER.info("Test detection completed: %d detections, %.2f accuracy", len(test_detections), test_results["accuracy"])
            
        except Exception as err:
            _LOGGER.error("Error during test detection: %s", err)
            test_results["success"] = False
            test_results["error"] = str(err)
        finally:
            # Disable test mode
            coordinator.disable_test_mode()
        
        return test_results
    
    @callback
    async def async_handle_validate_config(call: ServiceCall) -> ServiceResponse:
        """Handle validate_config service call."""
        config_path = call.data.get("config_path")
        config_yaml = call.data.get("config_yaml")
        
        _LOGGER.info("Validate config service called")
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {},
        }
        
        try:
            if config_yaml:
                # Validate inline YAML
                import yaml
                config_data = yaml.safe_load(config_yaml)
            elif config_path:
                # Load and validate file
                import yaml
                with open(config_path) as f:
                    config_data = yaml.safe_load(f)
            else:
                # Validate current configuration
                config_data = hass.data[DOMAIN].get("config", {})
            
            # Validate using config_schema
            from .config_schema import FLOORPLAN_SCHEMA
            
            validated_config: dict[str, Any] = FLOORPLAN_SCHEMA(config_data)
            
            # Additional validation checks
            validation_results["info"]["sensor_count"] = len(validated_config.get("sensors", []))
            validation_results["info"]["zone_count"] = len(validated_config.get("zones", []))
            validation_results["info"]["cue_count"] = len(validated_config.get("secondary_cues", []))
            
            # Check for potential issues
            if validation_results["info"]["sensor_count"] < 2:
                validation_results["warnings"].append("Less than 2 sensors configured - direction detection requires at least 2 sensors")
            
            if validation_results["info"]["zone_count"] == 0 and validated_config.get("detection_mode") == "zone_only":
                validation_results["errors"].append("No zones configured but detection_mode is 'zone_only'")
                validation_results["valid"] = False
            
            # Check sensor coordinates if floorplan dimensions provided
            floorplan_width = validated_config.get("floorplan", {}).get("width")
            floorplan_height = validated_config.get("floorplan", {}).get("height")
            
            if floorplan_width and floorplan_height:
                for sensor in validated_config.get("sensors", []):
                    x, y = sensor.get("x", 0), sensor.get("y", 0)
                    if x < 0 or x > floorplan_width or y < 0 or y > floorplan_height:
                        validation_results["warnings"].append(
                            f"Sensor '{sensor['entity_id']}' coordinates ({x}, {y}) outside floorplan bounds"
                        )
            
            _LOGGER.info("Config validation completed: %s", "valid" if validation_results["valid"] else "invalid")
            
        except vol.Invalid as err:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Schema validation error: {err}")
            _LOGGER.error("Config validation failed: %s", err)
        except Exception as err:
            validation_results["valid"] = False
            validation_results["errors"].append(f"Unexpected error: {err}")
            _LOGGER.error("Config validation error: %s", err)
        
        return validation_results
    
    # Register all services
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
    
    # Zone services
    hass.services.async_register(
        DOMAIN,
        "create_zone",
        async_handle_create_zone,
        schema=SERVICE_CREATE_ZONE_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "calibrate_zone",
        async_handle_calibrate_zone,
        schema=SERVICE_CALIBRATE_ZONE_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "update_zone_direction",
        async_handle_update_zone_direction,
        schema=SERVICE_UPDATE_ZONE_DIRECTION_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "test_zone_trigger",
        async_handle_test_zone_trigger,
        schema=SERVICE_TEST_ZONE_TRIGGER_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "analyze_zone_patterns",
        async_handle_analyze_zone_patterns,
        schema=SERVICE_ANALYZE_ZONE_PATTERNS_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "learn_zone_directions",
        async_handle_learn_zone_directions,
        schema=SERVICE_LEARN_ZONE_DIRECTIONS_SCHEMA,
    )
    
    # Cue services
    hass.services.async_register(
        DOMAIN,
        "add_secondary_cue",
        async_handle_add_secondary_cue,
        schema=SERVICE_ADD_SECONDARY_CUE_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "configure_cue_hints",
        async_handle_configure_cue_hints,
        schema=SERVICE_CONFIGURE_CUE_HINTS_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "analyze_cue_correlations",
        async_handle_analyze_cue_correlations,
        schema=SERVICE_ANALYZE_CUE_CORRELATIONS_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "learn_cue_patterns",
        async_handle_learn_cue_patterns,
        schema=SERVICE_LEARN_CUE_PATTERNS_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "test_hybrid_detection",
        async_handle_test_hybrid_detection,
        schema=SERVICE_TEST_HYBRID_DETECTION_SCHEMA,
    )
    
    # Analysis services
    hass.services.async_register(
        DOMAIN,
        "analyze_pattern",
        async_handle_analyze_pattern,
        schema=SERVICE_ANALYZE_PATTERN_SCHEMA,
    )
    
    hass.services.async_register(
        DOMAIN,
        "generate_report",
        async_handle_generate_report,
        schema=SERVICE_GENERATE_REPORT_SCHEMA,
    )
    
    # Diagnostic services
    hass.services.async_register(
        DOMAIN,
        "get_status",
        async_handle_get_status,
        schema=SERVICE_GET_STATUS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    
    hass.services.async_register(
        DOMAIN,
        "test_detection",
        async_handle_test_detection,
        schema=SERVICE_TEST_DETECTION_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    
    hass.services.async_register(
        DOMAIN,
        "validate_config",
        async_handle_validate_config,
        schema=SERVICE_VALIDATE_CONFIG_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    
    _LOGGER.info("All Motion Direction services registered (19 total)")



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
