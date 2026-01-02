"""YAML configuration schema validation for MotionDirection integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_ENTITY_ID, CONF_ID, CONF_NAME, CONF_TYPE
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_ADVANCED,
    CONF_AUTO_APPLY,
    CONF_AUTO_SUGGEST,
    CONF_BACKGROUND,
    CONF_CONFIDENCE,
    CONF_CONFIDENCE_THRESHOLD,
    CONF_CONFIDENCE_WEIGHT,
    CONF_COOLDOWN_PERIOD,
    CONF_CORRELATION_WINDOW,
    CONF_CUE_LEARNING,
    CONF_CUE_TYPE,
    CONF_DEBOUNCE_TIME,
    CONF_DEFAULT_CORRELATION_WINDOW,
    CONF_DETECTION_ANGLE,
    CONF_DETECTION_RANGE,
    CONF_DIMENSIONS,
    CONF_DIRECTIONAL_HINTS,
    CONF_DIRECTION_TOLERANCE,
    CONF_ENABLED,
    CONF_FLOORPLANS,
    CONF_FROM_STATE,
    CONF_GLOBAL,
    CONF_HEIGHT,
    CONF_HISTORY_RETENTION_DAYS,
    CONF_IGNORE_BETWEEN,
    CONF_IMAGE,
    CONF_IMPLIED_DIRECTION,
    CONF_INTERPOLATION,
    CONF_KNOWN_DIRECTIONS,
    CONF_LEARNING_PERIOD,
    CONF_LEARNING_WINDOW_DAYS,
    CONF_MIN_CONFIDENCE,
    CONF_MIN_CONFIDENCE_FOR_SINGLE_MOTION,
    CONF_MIN_CUE_CONFIDENCE,
    CONF_MIN_DWELL_TIME,
    CONF_MIN_SAMPLES,
    CONF_MIN_SAMPLES_FOR_PATTERN,
    CONF_MIN_SENSORS_FOR_DIRECTION,
    CONF_OPACITY,
    CONF_PARALLEL_PATHS,
    CONF_PATTERN_LEARNING,
    CONF_PATTERNS_TO_LEARN,
    CONF_POLYGON,
    CONF_POSITION,
    CONF_RANGE,
    CONF_RELIABILITY,
    CONF_SCALE,
    CONF_SECONDARY_CUE_SETTINGS,
    CONF_SECONDARY_CUES,
    CONF_SENSITIVITY,
    CONF_SENSORS,
    CONF_SPATIAL_CORRELATION_DISTANCE,
    CONF_STATE_CHANGE,
    CONF_TIME_WINDOW,
    CONF_TO_STATE,
    CONF_USE_SECONDARY_CUES,
    CONF_VECTOR,
    CONF_WEIGHT,
    CONF_WIDTH,
    CONF_X,
    CONF_Y,
    CONF_ZONE_DETECTION,
    CONF_ZONES,
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_CORRELATION_WINDOW,
    DEFAULT_HISTORY_RETENTION_DAYS,
    DEFAULT_LEARNING_PERIOD,
    DEFAULT_MIN_SAMPLES,
    DEFAULT_MIN_SENSORS,
    DEFAULT_TIME_WINDOW,
    DOMAIN,
)

# Position schema
POSITION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_X): vol.Coerce(float),
        vol.Required(CONF_Y): vol.Coerce(float),
    }
)

# State change schema for directional hints
STATE_CHANGE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_FROM_STATE): cv.string,
        vol.Optional(CONF_TO_STATE): cv.string,
    }
)

# Directional hint schema
DIRECTIONAL_HINT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_STATE_CHANGE): STATE_CHANGE_SCHEMA,
        vol.Required(CONF_IMPLIED_DIRECTION): cv.string,
        vol.Required(CONF_CONFIDENCE): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
    }
)

# Known direction schema for zones
KNOWN_DIRECTION_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_VECTOR): vol.All(
            cv.ensure_list,
            vol.Length(min=2, max=2),
            [vol.Coerce(float)],
        ),
        vol.Optional("aliases", default=[]): cv.ensure_list,
        vol.Optional("entry_edge"): cv.string,
        vol.Optional("exit_edge"): cv.string,
    }
)

# Secondary cue schema
SECONDARY_CUE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_POSITION): POSITION_SCHEMA,
        vol.Required(CONF_CUE_TYPE): vol.In([
            "door",
            "light",
            "switch",
            "presence",
            "temperature",
            "vibration",
            "power",
            "media",
        ]),
        vol.Required(CONF_DIRECTIONAL_HINTS): vol.All(
            cv.ensure_list,
            [DIRECTIONAL_HINT_SCHEMA],
        ),
        vol.Optional(CONF_CORRELATION_WINDOW, default=DEFAULT_CORRELATION_WINDOW): cv.positive_int,
        vol.Optional(CONF_CONFIDENCE_WEIGHT, default=0.7): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional(CONF_RELIABILITY, default=0.8): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
    }
)

# Sensor schema
SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENTITY_ID): cv.entity_id,
        vol.Required(CONF_POSITION): POSITION_SCHEMA,
        vol.Optional(CONF_RANGE, default=50): cv.positive_int,
        vol.Optional(CONF_WEIGHT, default=1.0): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional(CONF_TYPE, default="pir"): vol.In([
            "pir",
            "radar",
            "camera",
            "hybrid",
        ]),
        vol.Optional(CONF_RELIABILITY, default=0.9): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
    }
)

# Zone schema
ZONE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_POLYGON): vol.All(
            cv.ensure_list,
            vol.Length(min=3),
            [vol.All(cv.ensure_list, vol.Length(min=2, max=2), [vol.Coerce(float)])],
        ),
        vol.Required(CONF_KNOWN_DIRECTIONS): vol.All(
            cv.ensure_list,
            [KNOWN_DIRECTION_SCHEMA],
        ),
        vol.Optional(CONF_MIN_DWELL_TIME, default=500): cv.positive_int,
        vol.Optional("max_transit_time", default=10000): cv.positive_int,
        vol.Optional(CONF_SENSITIVITY, default=0.7): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
    }
)

# Dimensions schema
DIMENSIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_WIDTH): cv.positive_int,
        vol.Required(CONF_HEIGHT): cv.positive_int,
        vol.Required(CONF_SCALE): vol.Coerce(float),
    }
)

# Background schema
BACKGROUND_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IMAGE): cv.string,
        vol.Optional(CONF_OPACITY, default=0.5): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
    }
)

# Floorplan schema
FLOORPLAN_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_DIMENSIONS): DIMENSIONS_SCHEMA,
        vol.Optional(CONF_BACKGROUND): BACKGROUND_SCHEMA,
        vol.Optional(CONF_SENSORS, default=[]): vol.All(
            cv.ensure_list,
            [SENSOR_SCHEMA],
        ),
        vol.Optional(CONF_SECONDARY_CUES, default=[]): vol.All(
            cv.ensure_list,
            [SECONDARY_CUE_SCHEMA],
        ),
        vol.Optional(CONF_ZONES, default=[]): vol.All(
            cv.ensure_list,
            [ZONE_SCHEMA],
        ),
    }
)

# Global settings schema
GLOBAL_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_TIME_WINDOW, default=DEFAULT_TIME_WINDOW): vol.All(
            cv.positive_int,
            vol.Range(min=500, max=30000),
        ),
        vol.Optional(CONF_MIN_SENSORS_FOR_DIRECTION, default=DEFAULT_MIN_SENSORS): cv.positive_int,
        vol.Optional(CONF_USE_SECONDARY_CUES, default=True): cv.boolean,
        vol.Optional(CONF_CONFIDENCE_THRESHOLD, default=DEFAULT_CONFIDENCE_THRESHOLD): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional(CONF_HISTORY_RETENTION_DAYS, default=DEFAULT_HISTORY_RETENTION_DAYS): cv.positive_int,
    }
)

# Zone detection settings schema
ZONE_DETECTION_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENABLED, default=True): cv.boolean,
        vol.Optional(CONF_MIN_CONFIDENCE, default=0.6): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional(CONF_DIRECTION_TOLERANCE, default=30): vol.All(
            cv.positive_int,
            vol.Range(min=1, max=180),
        ),
    }
)

# Secondary cue settings schema
SECONDARY_CUE_SETTINGS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENABLED, default=True): cv.boolean,
        vol.Optional(CONF_DEFAULT_CORRELATION_WINDOW, default=DEFAULT_CORRELATION_WINDOW): cv.positive_int,
        vol.Optional(CONF_SPATIAL_CORRELATION_DISTANCE, default=100): cv.positive_int,
        vol.Optional(CONF_MIN_CUE_CONFIDENCE, default=0.5): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional(CONF_MIN_CONFIDENCE_FOR_SINGLE_MOTION, default=0.5): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
    }
)

# Pattern learning schema
PATTERN_LEARNING_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENABLED, default=True): cv.boolean,
        vol.Optional(CONF_MIN_SAMPLES, default=DEFAULT_MIN_SAMPLES): cv.positive_int,
        vol.Optional(CONF_LEARNING_WINDOW_DAYS, default=7): cv.positive_int,
    }
)

# Sensitivity schema
SENSITIVITY_SCHEMA = vol.Schema(
    {
        vol.Optional("low", default=0.3): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional("medium", default=0.5): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional("high", default=0.8): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
    }
)

# Advanced settings schema
ADVANCED_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_DEBOUNCE_TIME, default=100): cv.positive_int,
        vol.Optional(CONF_PARALLEL_PATHS, default=True): cv.boolean,
        vol.Optional(CONF_INTERPOLATION, default="linear"): vol.In([
            "linear",
            "cubic",
            "predictive",
        ]),
        vol.Optional(CONF_SENSITIVITY, default={}): SENSITIVITY_SCHEMA,
        vol.Optional(CONF_ZONE_DETECTION, default={}): ZONE_DETECTION_SCHEMA,
        vol.Optional(CONF_SECONDARY_CUE_SETTINGS, default={}): SECONDARY_CUE_SETTINGS_SCHEMA,
        vol.Optional(CONF_PATTERN_LEARNING, default={}): PATTERN_LEARNING_SCHEMA,
    }
)

# Pattern type schema for cue learning
PATTERN_TYPE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TYPE): vol.In(["sequence", "correlation"]),
        vol.Optional("description"): cv.string,
        vol.Optional("window", default=5000): cv.positive_int,
    }
)

# Cue learning schema
CUE_LEARNING_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENABLED, default=True): cv.boolean,
        vol.Optional(CONF_LEARNING_PERIOD, default=DEFAULT_LEARNING_PERIOD): cv.positive_int,
        vol.Optional(CONF_MIN_SAMPLES_FOR_PATTERN, default=10): cv.positive_int,
        vol.Optional(CONF_CONFIDENCE_THRESHOLD, default=0.7): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional(CONF_PATTERNS_TO_LEARN, default=[]): vol.All(
            cv.ensure_list,
            [PATTERN_TYPE_SCHEMA],
        ),
        vol.Optional(CONF_AUTO_SUGGEST, default=True): cv.boolean,
        vol.Optional(CONF_AUTO_APPLY, default=False): cv.boolean,
    }
)

# Per-sensor configuration schema
SENSOR_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_TYPE, default="pir"): vol.In([
            "pir",
            "radar",
            "camera",
            "hybrid",
        ]),
        vol.Optional(CONF_DETECTION_ANGLE): vol.All(
            cv.positive_int,
            vol.Range(min=1, max=360),
        ),
        vol.Optional(CONF_DETECTION_RANGE): vol.Coerce(float),
        vol.Optional(CONF_COOLDOWN_PERIOD): cv.positive_int,
        vol.Optional(CONF_RELIABILITY, default=0.95): vol.All(
            vol.Coerce(float), vol.Range(min=0.0, max=1.0)
        ),
        vol.Optional(CONF_ZONES, default=[]): cv.ensure_list,
        vol.Optional(CONF_IGNORE_BETWEEN): cv.string,
    }
)

# Main configuration schema
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(DOMAIN): vol.Schema(
            {
                vol.Optional(CONF_GLOBAL, default={}): GLOBAL_SCHEMA,
                vol.Optional(CONF_FLOORPLANS, default=[]): vol.All(
                    cv.ensure_list,
                    [FLOORPLAN_SCHEMA],
                ),
                vol.Optional(CONF_ADVANCED, default={}): ADVANCED_SCHEMA,
                vol.Optional(CONF_CUE_LEARNING, default={}): CUE_LEARNING_SCHEMA,
                vol.Optional("sensor_config", default={}): vol.Schema(
                    {cv.entity_id: SENSOR_CONFIG_SCHEMA}
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def validate_polygon(polygon: list[list[float]]) -> bool:
    """Validate polygon has minimum 3 points and no self-intersection.
    
    Args:
        polygon: List of [x, y] coordinate pairs
        
    Returns:
        True if valid
        
    Raises:
        vol.Invalid: If polygon is invalid
    """
    if len(polygon) < 3:
        raise vol.Invalid("Polygon must have at least 3 points")
    
    # Check for duplicate points
    for i, point in enumerate(polygon):
        for j, other_point in enumerate(polygon[i + 1:], start=i + 1):
            if point[0] == other_point[0] and point[1] == other_point[1]:
                raise vol.Invalid(f"Duplicate point at indices {i} and {j}")
    
    return True


def validate_zone_directions(zone: dict[str, Any]) -> dict[str, Any]:
    """Validate zone has at least one known direction.
    
    Args:
        zone: Zone configuration dictionary
        
    Returns:
        Validated zone configuration
        
    Raises:
        vol.Invalid: If zone has no known directions
    """
    if not zone.get(CONF_KNOWN_DIRECTIONS):
        raise vol.Invalid("Zone must have at least one known direction")
    
    # Validate polygon
    validate_polygon(zone[CONF_POLYGON])
    
    return zone


def validate_floorplan(floorplan: dict[str, Any]) -> dict[str, Any]:
    """Validate floorplan configuration.
    
    Args:
        floorplan: Floorplan configuration dictionary
        
    Returns:
        Validated floorplan configuration
        
    Raises:
        vol.Invalid: If floorplan is invalid
    """
    # Validate at least one sensor
    if not floorplan.get(CONF_SENSORS):
        raise vol.Invalid("Floorplan must have at least one sensor")
    
    # Validate zones if present
    for zone in floorplan.get(CONF_ZONES, []):
        validate_zone_directions(zone)
    
    # Validate sensor positions are within floorplan
    dimensions = floorplan[CONF_DIMENSIONS]
    width = dimensions[CONF_WIDTH]
    height = dimensions[CONF_HEIGHT]
    
    for sensor in floorplan[CONF_SENSORS]:
        pos = sensor[CONF_POSITION]
        if not (0 <= pos[CONF_X] <= width and 0 <= pos[CONF_Y] <= height):
            raise vol.Invalid(
                f"Sensor {sensor[CONF_ENTITY_ID]} position ({pos[CONF_X]}, {pos[CONF_Y]}) "
                f"is outside floorplan dimensions ({width}x{height})"
            )
    
    # Validate secondary cue positions
    for cue in floorplan.get(CONF_SECONDARY_CUES, []):
        pos = cue[CONF_POSITION]
        if not (0 <= pos[CONF_X] <= width and 0 <= pos[CONF_Y] <= height):
            raise vol.Invalid(
                f"Secondary cue {cue[CONF_ENTITY_ID]} position ({pos[CONF_X]}, {pos[CONF_Y]}) "
                f"is outside floorplan dimensions ({width}x{height})"
            )
    
    return floorplan


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate complete configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Validated configuration
        
    Raises:
        vol.Invalid: If configuration is invalid
    """
    # Validate schema
    config = CONFIG_SCHEMA(config)
    
    # Additional validation
    if DOMAIN in config:
        domain_config = config[DOMAIN]
        
        # Validate floorplans
        for floorplan in domain_config.get(CONF_FLOORPLANS, []):
            validate_floorplan(floorplan)
        
        # Validate sensor_config references existing sensors in floorplans
        sensor_config = domain_config.get("sensor_config", {})
        valid_sensors = {
            sensor[CONF_ENTITY_ID]
            for floorplan in domain_config.get(CONF_FLOORPLANS, [])
            for sensor in floorplan.get(CONF_SENSORS, [])
        }
        
        for entity_id in sensor_config.keys():
            if entity_id not in valid_sensors:
                raise vol.Invalid(
                    f"sensor_config references unknown sensor: {entity_id}"
                )
    
    return config
