"""Constants for the Motion Direction integration."""
from datetime import timedelta
from typing import Final

# Integration domain
DOMAIN: Final = "motiondirection"

# Configuration keys
CONF_FLOORPLAN_ID: Final = "floorplan_id"
CONF_FLOORPLAN_NAME: Final = "floorplan_name"
CONF_WIDTH: Final = "width"
CONF_HEIGHT: Final = "height"
CONF_SCALE: Final = "scale"
CONF_BACKGROUND_IMAGE: Final = "background_image"
CONF_SENSORS: Final = "sensors"
CONF_ZONES: Final = "zones"
CONF_SECONDARY_CUES: Final = "secondary_cues"
CONF_TIME_WINDOW: Final = "time_window"
CONF_CONFIDENCE_THRESHOLD: Final = "confidence_threshold"
CONF_ENABLE_SECONDARY_CUES: Final = "enable_secondary_cues"
CONF_ENABLE_PATTERN_LEARNING: Final = "enable_pattern_learning"
CONF_HISTORY_RETENTION_DAYS: Final = "history_retention_days"
CONF_POSITION: Final = "position"
CONF_RANGE: Final = "range"
CONF_WEIGHT: Final = "weight"
CONF_TYPE: Final = "type"
CONF_RELIABILITY: Final = "reliability"
CONF_POLYGON: Final = "polygon"
CONF_KNOWN_DIRECTIONS: Final = "known_directions"
CONF_MIN_DWELL_TIME: Final = "min_dwell_time"
CONF_MAX_TRANSIT_TIME: Final = "max_transit_time"
CONF_SENSITIVITY: Final = "sensitivity"
CONF_CUE_TYPE: Final = "cue_type"
CONF_DIRECTIONAL_HINTS: Final = "directional_hints"
CONF_CORRELATION_WINDOW: Final = "correlation_window"
CONF_PRE_TRIGGER_WINDOW: Final = "pre_trigger_window"
CONF_POST_TRIGGER_WINDOW: Final = "post_trigger_window"
CONF_CONFIDENCE_WEIGHT: Final = "confidence_weight"
CONF_TRIGGER_STATES: Final = "trigger_states"
CONF_IGNORE_STATES: Final = "ignore_states"
CONF_X: Final = "x"
CONF_Y: Final = "y"
CONF_VECTOR: Final = "vector"
CONF_CONFIDENCE: Final = "confidence"
CONF_STATE_CHANGE: Final = "state_change"
CONF_FROM_STATE: Final = "from_state"
CONF_TO_STATE: Final = "to_state"
CONF_IMPLIED_DIRECTION: Final = "implied_direction"
CONF_DIMENSIONS: Final = "dimensions"
CONF_BACKGROUND: Final = "background"
CONF_IMAGE: Final = "image"
CONF_OPACITY: Final = "opacity"
CONF_GLOBAL: Final = "global"
CONF_FLOORPLANS: Final = "floorplans"
CONF_ADVANCED: Final = "advanced"
CONF_CUE_LEARNING: Final = "cue_learning"
CONF_MIN_SENSORS_FOR_DIRECTION: Final = "min_sensors_for_direction"
CONF_USE_SECONDARY_CUES: Final = "use_secondary_cues"
CONF_DEBOUNCE_TIME: Final = "debounce_time"
CONF_PARALLEL_PATHS: Final = "parallel_paths"
CONF_INTERPOLATION: Final = "interpolation"
CONF_ZONE_DETECTION: Final = "zone_detection"
CONF_ENABLED: Final = "enabled"
CONF_MIN_CONFIDENCE: Final = "min_confidence"
CONF_DIRECTION_TOLERANCE: Final = "direction_tolerance"
CONF_SECONDARY_CUE_SETTINGS: Final = "secondary_cue_settings"
CONF_DEFAULT_CORRELATION_WINDOW: Final = "default_correlation_window"
CONF_SPATIAL_CORRELATION_DISTANCE: Final = "spatial_correlation_distance"
CONF_MIN_CUE_CONFIDENCE: Final = "min_cue_confidence"
CONF_MIN_CONFIDENCE_FOR_SINGLE_MOTION: Final = "min_confidence_for_single_motion"
CONF_PATTERN_LEARNING: Final = "pattern_learning"
CONF_MIN_SAMPLES: Final = "min_samples"
CONF_LEARNING_WINDOW_DAYS: Final = "learning_window_days"
CONF_LEARNING_PERIOD: Final = "learning_period"
CONF_MIN_SAMPLES_FOR_PATTERN: Final = "min_samples_for_pattern"
CONF_PATTERNS_TO_LEARN: Final = "patterns_to_learn"
CONF_AUTO_SUGGEST: Final = "auto_suggest"
CONF_AUTO_APPLY: Final = "auto_apply"
CONF_DETECTION_ANGLE: Final = "detection_angle"
CONF_DETECTION_RANGE: Final = "detection_range"
CONF_COOLDOWN_PERIOD: Final = "cooldown_period"
CONF_IGNORE_BETWEEN: Final = "ignore_between"

# Default values
DEFAULT_TIME_WINDOW: Final = 5000  # milliseconds
MIN_TIME_WINDOW: Final = 500
MAX_TIME_WINDOW: Final = 30000
DEFAULT_CONFIDENCE_THRESHOLD: Final = 0.7
DEFAULT_HISTORY_RETENTION_DAYS: Final = 30
DEFAULT_DEBOUNCE_TIME: Final = 100  # milliseconds
DEFAULT_SCAN_INTERVAL: Final = timedelta(seconds=1)
DEFAULT_MIN_DWELL_TIME: Final = 500  # milliseconds
DEFAULT_MAX_TRANSIT_TIME: Final = 10000  # milliseconds
DEFAULT_SENSITIVITY: Final = 0.7
DEFAULT_CORRELATION_WINDOW: Final = 3000  # milliseconds
DEFAULT_PRE_TRIGGER_WINDOW: Final = 2000  # milliseconds
DEFAULT_POST_TRIGGER_WINDOW: Final = 2000  # milliseconds
DEFAULT_CONFIDENCE_WEIGHT: Final = 0.6
DEFAULT_RELIABILITY: Final = 0.8
DEFAULT_MIN_SENSORS: Final = 2
DEFAULT_LEARNING_PERIOD: Final = 604800  # 1 week in seconds
DEFAULT_MIN_SAMPLES: Final = 10

# Event buffer sizes
MAX_EVENT_BUFFER_SIZE: Final = 100
MAX_CUE_BUFFER_SIZE: Final = 200
MAX_PATTERN_HISTORY_SIZE: Final = 1000

# Event types
EVENT_MOTION_DETECTED: Final = "motiondirection_motion_detected"
EVENT_PATTERN_DETECTED: Final = "motiondirection_pattern_detected"
EVENT_ZONE_ENTERED: Final = "motiondirection_zone_entered"
EVENT_ZONE_EXITED: Final = "motiondirection_zone_exited"
EVENT_ZONE_DIRECTION_DETECTED: Final = "motiondirection_zone_direction_detected"
EVENT_ZONE_PATTERN_DETECTED: Final = "motiondirection_zone_pattern_detected"
EVENT_CUE_TRIGGERED: Final = "motiondirection_cue_triggered"
EVENT_HYBRID_DETECTION: Final = "motiondirection_hybrid_detection"
EVENT_CUE_CORRELATION_DETECTED: Final = "motiondirection_cue_correlation_detected"
EVENT_CUE_PATTERN_LEARNED: Final = "motiondirection_cue_pattern_learned"
EVENT_ANOMALY_DETECTED: Final = "motiondirection_anomaly_detected"

# Service names
SERVICE_CALIBRATE: Final = "calibrate"
SERVICE_CLEAR_HISTORY: Final = "clear_history"
SERVICE_SIMULATE: Final = "simulate"
SERVICE_CALIBRATE_ZONE: Final = "calibrate_zone"
SERVICE_CREATE_ZONE: Final = "create_zone"
SERVICE_UPDATE_ZONE_DIRECTION: Final = "update_zone_direction"
SERVICE_TEST_ZONE_TRIGGER: Final = "test_zone_trigger"
SERVICE_ANALYZE_ZONE_PATTERNS: Final = "analyze_zone_patterns"
SERVICE_LEARN_ZONE_DIRECTIONS: Final = "learn_zone_directions"
SERVICE_ADD_SECONDARY_CUE: Final = "add_secondary_cue"
SERVICE_CONFIGURE_CUE_HINTS: Final = "configure_cue_hints"
SERVICE_ANALYZE_CUE_CORRELATIONS: Final = "analyze_cue_correlations"
SERVICE_LEARN_CUE_PATTERNS: Final = "learn_cue_patterns"
SERVICE_TEST_HYBRID_DETECTION: Final = "test_hybrid_detection"
SERVICE_ANALYZE_PATTERN: Final = "analyze_pattern"
SERVICE_GENERATE_REPORT: Final = "generate_report"

# Entity attributes
ATTR_CONFIDENCE: Final = "confidence"
ATTR_DETECTION_METHOD: Final = "detection_method"
ATTR_VECTOR: Final = "vector"
ATTR_SPEED: Final = "speed"
ATTR_PATH: Final = "path"
ATTR_TRIGGERED_SENSORS: Final = "triggered_sensors"
ATTR_CONTRIBUTING_CUES: Final = "contributing_cues"
ATTR_CUE_CONFIDENCE: Final = "cue_confidence"
ATTR_ACTIVE_ZONES: Final = "active_zones"
ATTR_PATTERN_TYPE: Final = "pattern_type"
ATTR_PATTERN_CONFIDENCE: Final = "pattern_confidence"
ATTR_PATTERN_DURATION: Final = "pattern_duration"
ATTR_PATTERN_HISTORY: Final = "pattern_history"
ATTR_ZONE_SEQUENCE: Final = "zone_sequence"
ATTR_ZONE_ID: Final = "zone_id"
ATTR_ZONE_NAME: Final = "zone_name"
ATTR_DIRECTION: Final = "direction"
ATTR_ENTRY_POINT: Final = "entry_point"
ATTR_EXIT_POINT: Final = "exit_point"
ATTR_DWELL_TIME: Final = "dwell_time"
ATTR_TRANSIT_TIME: Final = "transit_time"
ATTR_ENTRY_TIME: Final = "entry_time"
ATTR_EXIT_TIME: Final = "exit_time"
ATTR_PREDICTED_DIRECTION: Final = "predicted_direction"
ATTR_AVAILABLE_DIRECTIONS: Final = "available_directions"
ATTR_HISTORY: Final = "history"
ATTR_OCCUPANCY_START: Final = "occupancy_start"
ATTR_OCCUPANCY_DURATION: Final = "occupancy_duration"
ATTR_LAST_DIRECTION: Final = "last_direction"
ATTR_MOTION_DETECTED: Final = "motion_detected"
ATTR_SENSORS_IN_ZONE: Final = "sensors_in_zone"
ATTR_PROGRESS: Final = "progress"
ATTR_CURRENT_POSITION: Final = "current_position"
ATTR_PREDICTED_EXIT: Final = "predicted_exit"
ATTR_TRANSITIONS_TODAY: Final = "transitions_today"
ATTR_TRANSITIONS_HOUR: Final = "transitions_hour"
ATTR_COMMON_DIRECTION: Final = "common_direction"
ATTR_DIRECTION_BREAKDOWN: Final = "direction_breakdown"
ATTR_AVERAGE_DWELL_TIME: Final = "average_dwell_time"
ATTR_AVERAGE_TRANSIT_TIME: Final = "average_transit_time"
ATTR_PEAK_HOUR: Final = "peak_hour"
ATTR_LAST_RESET: Final = "last_reset"
ATTR_CUE_ID: Final = "cue_id"
ATTR_CUE_TYPE: Final = "cue_type"
ATTR_ENTITY_ID: Final = "entity_id"
ATTR_LAST_TRIGGER: Final = "last_trigger"
ATTR_LAST_STATE_CHANGE: Final = "last_state_change"
ATTR_IMPLIED_DIRECTION: Final = "implied_direction"
ATTR_IMPLIED_CONFIDENCE: Final = "implied_confidence"
ATTR_CORRELATION_COUNT_TODAY: Final = "correlation_count_today"
ATTR_CORRELATION_SUCCESS_RATE: Final = "correlation_success_rate"
ATTR_ACTIVE_CORRELATIONS: Final = "active_correlations"
ATTR_CORRELATION_STATISTICS: Final = "correlation_statistics"
ATTR_TOP_CORRELATIONS: Final = "top_correlations"
ATTR_ANOMALY_SCORE: Final = "anomaly_score"
ATTR_ANOMALY_TYPE: Final = "anomaly_type"
ATTR_EXPECTED_PATTERN: Final = "expected_pattern"
ATTR_ACTUAL_PATTERN: Final = "actual_pattern"

# Pattern types
PATTERN_LINEAR: Final = "linear"
PATTERN_CIRCULAR: Final = "circular"
PATTERN_ZONE_TRANSITION: Final = "zone_transition"
PATTERN_STATIONARY: Final = "stationary"
PATTERN_RANDOM: Final = "random"
PATTERN_ANOMALY: Final = "anomaly"

# Detection methods
DETECTION_MULTI_SENSOR: Final = "multi_sensor"
DETECTION_HYBRID: Final = "hybrid"
DETECTION_CUE_ASSISTED: Final = "cue_assisted"
DETECTION_INSUFFICIENT: Final = "insufficient_data"

# Cue types
CUE_TYPE_DOOR: Final = "door"
CUE_TYPE_LIGHT: Final = "light"
CUE_TYPE_SWITCH: Final = "switch"
CUE_TYPE_PRESENCE: Final = "presence"
CUE_TYPE_TEMPERATURE: Final = "temperature"
CUE_TYPE_VIBRATION: Final = "vibration"
CUE_TYPE_POWER: Final = "power"
CUE_TYPE_MEDIA: Final = "media"

# Zone states
ZONE_STATE_IDLE: Final = "idle"
ZONE_STATE_OCCUPIED: Final = "occupied"
ZONE_STATE_TRANSIT: Final = "transit"

# Direction names (cardinal and ordinal)
DIRECTION_NORTH: Final = "north"
DIRECTION_SOUTH: Final = "south"
DIRECTION_EAST: Final = "east"
DIRECTION_WEST: Final = "west"
DIRECTION_NORTH_EAST: Final = "north_east"
DIRECTION_NORTH_WEST: Final = "north_west"
DIRECTION_SOUTH_EAST: Final = "south_east"
DIRECTION_SOUTH_WEST: Final = "south_west"

# Calibration modes
CALIBRATION_AUTOMATIC: Final = "automatic"
CALIBRATION_MANUAL: Final = "manual"
CALIBRATION_GUIDED: Final = "guided"

# Calibration types
CALIBRATION_TYPE_SENSORS: Final = "sensors"
CALIBRATION_TYPE_ZONES: Final = "zones"
CALIBRATION_TYPE_CUES: Final = "cues"
CALIBRATION_TYPE_ALL: Final = "all"

# Report formats
REPORT_FORMAT_PDF: Final = "pdf"
REPORT_FORMAT_JSON: Final = "json"
REPORT_FORMAT_YAML: Final = "yaml"

# Performance targets
TARGET_RESPONSE_TIME_MS: Final = 100
TARGET_MAX_SENSORS: Final = 50
TARGET_MAX_ZONES: Final = 50
TARGET_MAX_CUES: Final = 100
TARGET_MAX_EVENTS_PER_MINUTE: Final = 1000

# Storage keys
STORAGE_KEY: Final = f"{DOMAIN}.storage"
STORAGE_VERSION: Final = 1
