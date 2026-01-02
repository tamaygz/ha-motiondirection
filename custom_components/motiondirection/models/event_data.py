"""Event data models for Home Assistant event bus."""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MotionDetectedEventData:
    """Data for motiondirection_motion_detected event.
    
    Attributes:
        direction: Detected direction name
        confidence: Detection confidence (0-1)
        detection_method: Method used (multi_sensor, hybrid, cue_assisted, etc.)
        vector: Direction vector (dx, dy)
        speed: Estimated speed in m/s
        path: List of sensor positions in path
        triggered_sensors: List of sensor entity IDs
        contributing_cues: List of cue entity IDs (if hybrid detection)
        cue_confidence: Confidence contribution from cues
        timestamp: Detection timestamp
    """
    
    direction: str
    confidence: float
    detection_method: str
    timestamp: str  # ISO format
    vector: Optional[List[float]] = None
    speed: Optional[float] = None
    path: Optional[List[List[float]]] = None
    triggered_sensors: List[str] = field(default_factory=list)
    contributing_cues: List[str] = field(default_factory=list)
    cue_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class PatternDetectedEventData:
    """Data for motiondirection_pattern_detected event.
    
    Attributes:
        pattern_type: Type of pattern (linear, circular, etc.)
        confidence: Pattern confidence (0-1)
        duration_ms: Pattern duration in milliseconds
        sensor_sequence: Ordered list of sensor entity IDs
        zone_sequence: Ordered list of zone IDs (if applicable)
        timestamp: Detection timestamp
    """
    
    pattern_type: str
    confidence: float
    duration_ms: float
    timestamp: str  # ISO format
    sensor_sequence: List[str] = field(default_factory=list)
    zone_sequence: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ZoneEnteredEventData:
    """Data for motiondirection_zone_entered event.
    
    Attributes:
        zone_id: Zone identifier
        zone_name: Zone display name
        entry_point: Entry position (x, y)
        entry_time: Entry timestamp
        direction: Detected direction through zone
        confidence: Detection confidence
        triggered_sensors: Sensors that detected entry
    """
    
    zone_id: str
    zone_name: str
    entry_time: str  # ISO format
    entry_point: Optional[List[float]] = None
    direction: Optional[str] = None
    confidence: float = 0.0
    triggered_sensors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ZoneExitedEventData:
    """Data for motiondirection_zone_exited event.
    
    Attributes:
        zone_id: Zone identifier
        zone_name: Zone display name
        exit_point: Exit position (x, y)
        exit_time: Exit timestamp
        direction: Detected direction through zone
        dwell_time_ms: Time spent in zone in milliseconds
        confidence: Detection confidence
        triggered_sensors: Sensors that detected exit
    """
    
    zone_id: str
    zone_name: str
    exit_time: str  # ISO format
    exit_point: Optional[List[float]] = None
    direction: Optional[str] = None
    dwell_time_ms: float = 0.0
    confidence: float = 0.0
    triggered_sensors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ZoneDirectionDetectedEventData:
    """Data for motiondirection_zone_direction_detected event.
    
    Attributes:
        zone_id: Zone identifier
        zone_name: Zone display name
        direction: Detected direction name
        confidence: Detection confidence
        entry_point: Entry position
        exit_point: Exit position
        transit_time_ms: Transit time in milliseconds
        timestamp: Detection timestamp
    """
    
    zone_id: str
    zone_name: str
    direction: str
    confidence: float
    timestamp: str  # ISO format
    entry_point: Optional[List[float]] = None
    exit_point: Optional[List[float]] = None
    transit_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ZonePatternDetectedEventData:
    """Data for motiondirection_zone_pattern_detected event.
    
    Attributes:
        zone_id: Zone identifier
        zone_name: Zone display name
        pattern_type: Type of pattern detected
        pattern_confidence: Pattern confidence
        occurrences: Number of times pattern observed
        timestamp: Detection timestamp
    """
    
    zone_id: str
    zone_name: str
    pattern_type: str
    pattern_confidence: float
    timestamp: str  # ISO format
    occurrences: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class CueTriggeredEventData:
    """Data for motiondirection_cue_triggered event.
    
    Attributes:
        cue_id: Cue identifier
        cue_entity_id: Cue Home Assistant entity ID
        cue_type: Type of cue (door, light, etc.)
        state_change: State change description (e.g., "off -> on")
        position: Cue position (x, y)
        timestamp: Trigger timestamp
        correlated_motion: Whether correlated with motion
        motion_sensor: Motion sensor entity ID if correlated
    """
    
    cue_id: str
    cue_entity_id: str
    cue_type: str
    state_change: str
    timestamp: str  # ISO format
    position: Optional[List[float]] = None
    correlated_motion: bool = False
    motion_sensor: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class HybridDetectionEventData:
    """Data for motiondirection_hybrid_detection event.
    
    Attributes:
        direction: Detected direction
        motion_confidence: Confidence from motion sensors
        cue_confidence: Confidence from cues
        combined_confidence: Final combined confidence
        motion_sensor: Primary motion sensor entity ID
        contributing_cues: List of contributing cue entity IDs
        cue_details: Details about each contributing cue
        timestamp: Detection timestamp
    """
    
    direction: str
    motion_confidence: float
    cue_confidence: float
    combined_confidence: float
    timestamp: str  # ISO format
    motion_sensor: Optional[str] = None
    contributing_cues: List[str] = field(default_factory=list)
    cue_details: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class CueCorrelationDetectedEventData:
    """Data for motiondirection_cue_correlation_detected event.
    
    Attributes:
        cue_id: Cue identifier
        motion_sensor: Motion sensor entity ID
        correlation_strength: Strength of correlation (0-1)
        time_offset_ms: Time offset between cue and motion in milliseconds
        spatial_distance: Distance between cue and motion sensor
        confidence: Detection confidence
        timestamp: Detection timestamp
    """
    
    cue_id: str
    motion_sensor: str
    correlation_strength: float
    time_offset_ms: float
    timestamp: str  # ISO format
    spatial_distance: float = 0.0
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class CuePatternLearnedEventData:
    """Data for motiondirection_cue_pattern_learned event.
    
    Attributes:
        cue_id: Cue identifier
        pattern_type: Type of pattern learned
        pattern_description: Human-readable description
        confidence: Pattern confidence
        occurrences: Number of times pattern observed
        suggested_hint: Suggested directional hint
        timestamp: Learning timestamp
    """
    
    cue_id: str
    pattern_type: str
    pattern_description: str
    confidence: float
    timestamp: str  # ISO format
    occurrences: int = 1
    suggested_hint: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class AnomalyDetectedEventData:
    """Data for motiondirection_anomaly_detected event.
    
    Attributes:
        anomaly_type: Type of anomaly (unexpected_path, unusual_timing, wrong_direction)
        description: Human-readable description
        severity: Severity level (low, medium, high)
        expected_pattern: Expected pattern description
        actual_pattern: Actual pattern observed
        confidence: Detection confidence
        affected_sensors: List of sensor entity IDs involved
        timestamp: Detection timestamp
    """
    
    anomaly_type: str
    description: str
    severity: str
    confidence: float
    timestamp: str  # ISO format
    expected_pattern: Optional[str] = None
    actual_pattern: Optional[str] = None
    affected_sensors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event firing."""
        return {k: v for k, v in asdict(self).items() if v is not None}
