# HA-MotionDirection API Reference

Complete API reference for services, events, sensors, and states.

## Table of Contents

1. [Services](#services)
2. [Events](#events)
3. [Sensors](#sensors)
4. [States and Attributes](#states-and-attributes)
5. [Data Models](#data-models)

## Services

### motiondirection.update_floorplan

Update or create a floorplan with sensor positions.

**Service Data Schema**:

```yaml
floorplan_id:
  description: Unique identifier for the floorplan
  required: true
  type: string
  example: "main_floor"

width:
  description: Width of the floorplan in meters
  required: true
  type: float
  example: 20.0

height:
  description: Height of the floorplan in meters
  required: true
  type: float
  example: 15.0

sensors:
  description: List of motion sensors with positions
  required: true
  type: list
  schema:
    entity_id:
      description: Entity ID of the motion sensor
      required: true
      type: string
      example: "binary_sensor.living_room_motion"
    
    x:
      description: X coordinate (meters from left edge)
      required: true
      type: float
      example: 5.0
    
    y:
      description: Y coordinate (meters from bottom edge)
      required: true
      type: float
      example: 5.0
    
    range_meters:
      description: Detection range radius in meters
      required: true
      type: float
      example: 3.0
    
    floor:
      description: Floor level (for multi-story homes)
      required: false
      type: integer
      default: 0
      example: 1
```

**Example**:

```yaml
service: motiondirection.update_floorplan
data:
  floorplan_id: "main_floor"
  width: 20.0
  height: 15.0
  sensors:
    - entity_id: binary_sensor.living_room_motion
      x: 5.0
      y: 5.0
      range_meters: 3.0
    - entity_id: binary_sensor.kitchen_motion
      x: 15.0
      y: 5.0
      range_meters: 3.0
    - entity_id: binary_sensor.hallway_motion
      x: 10.0
      y: 10.0
      range_meters: 3.0
```

---

### motiondirection.create_trigger_zone

Create a new trigger zone with directional configurations.

**Service Data Schema**:

```yaml
zone_id:
  description: Unique identifier for the zone
  required: true
  type: string
  example: "living_room"

polygon:
  description: List of points defining zone boundary
  required: true
  type: list
  schema:
    x:
      description: X coordinate of polygon point
      required: true
      type: float
    y:
      description: Y coordinate of polygon point
      required: true
      type: float

directions:
  description: List of directional configurations for this zone
  required: true
  type: list
  schema:
    name:
      description: Name of this direction (e.g., "to_kitchen")
      required: true
      type: string
    
    vector:
      description: Direction vector [x, y] (normalized recommended)
      required: true
      type: list
      example: [1.0, 0.0]
    
    entry_side:
      description: Which edge/corner of polygon for this direction
      required: true
      type: string
      enum: 
        - "top"
        - "bottom"
        - "left"
        - "right"
        - "top_left"
        - "top_right"
        - "bottom_left"
        - "bottom_right"
    
    confidence_threshold:
      description: Minimum confidence to trigger this direction
      required: false
      type: float
      default: 0.7
      min: 0.0
      max: 1.0
```

**Example**:

```yaml
service: motiondirection.create_trigger_zone
data:
  zone_id: "living_room"
  polygon:
    - x: 0.0
      y: 0.0
    - x: 10.0
      y: 0.0
    - x: 10.0
      y: 10.0
    - x: 0.0
      y: 10.0
  directions:
    - name: "to_kitchen"
      vector: [1.0, 0.0]
      entry_side: "right"
      confidence_threshold: 0.7
    - name: "to_hallway"
      vector: [0.0, 1.0]
      entry_side: "top"
      confidence_threshold: 0.7
```

---

### motiondirection.update_trigger_zone

Update an existing trigger zone's configuration.

**Service Data Schema**:

```yaml
zone_id:
  description: ID of zone to update
  required: true
  type: string

polygon:
  description: New polygon points (optional)
  required: false
  type: list
  schema: (same as create_trigger_zone)

directions:
  description: Updated direction configurations (optional)
  required: false
  type: list
  schema: (same as create_trigger_zone)
```

**Example**:

```yaml
service: motiondirection.update_trigger_zone
data:
  zone_id: "living_room"
  directions:
    - name: "to_kitchen"
      vector: [1.0, 0.0]
      entry_side: "right"
      confidence_threshold: 0.65  # Lowered threshold
```

---

### motiondirection.delete_trigger_zone

Delete a trigger zone.

**Service Data Schema**:

```yaml
zone_id:
  description: ID of zone to delete
  required: true
  type: string
```

**Example**:

```yaml
service: motiondirection.delete_trigger_zone
data:
  zone_id: "living_room"
```

---

### motiondirection.register_secondary_cue

Register a secondary cue to enhance detection accuracy.

**Service Data Schema**:

```yaml
cue_id:
  description: Unique identifier for the cue
  required: true
  type: string
  example: "front_door"

entity_id:
  description: Entity ID of the cue sensor/device
  required: true
  type: string
  example: "binary_sensor.front_door"

cue_type:
  description: Type of cue
  required: true
  type: string
  enum:
    - "door"
    - "light"
    - "lock"
    - "appliance"
    - "media"
    - "climate"
    - "custom"

location:
  description: Physical location of the cue
  required: true
  type: object
  schema:
    x:
      description: X coordinate
      required: true
      type: float
    y:
      description: Y coordinate
      required: true
      type: float

confidence_boost:
  description: Confidence boost when cue triggers (0.0-1.0)
  required: false
  type: float
  default: 0.15
  min: 0.0
  max: 1.0

directional_hint:
  description: Explicit direction hint when cue triggers
  required: false
  type: object
  schema:
    from_state:
      description: State transition: from
      required: true
      type: string
    
    to_state:
      description: State transition: to
      required: true
      type: string
    
    direction:
      description: Direction name this hint suggests
      required: true
      type: string
    
    weight:
      description: How much to trust this hint (0.0-1.0)
      required: false
      type: float
      default: 0.8
```

**Example**:

```yaml
service: motiondirection.register_secondary_cue
data:
  cue_id: "front_door"
  entity_id: binary_sensor.front_door_contact
  cue_type: "door"
  location:
    x: 5.0
    y: 0.0
  confidence_boost: 0.15
  directional_hint:
    from_state: "off"
    to_state: "on"
    direction: "entering"
    weight: 0.8
```

---

### motiondirection.analyze_pattern

Manually trigger pattern analysis on historical data.

**Service Data Schema**:

```yaml
time_range:
  description: Time range to analyze in seconds
  required: false
  type: integer
  default: 3600
  example: 86400  # 24 hours

pattern_id:
  description: Specific pattern ID to analyze (optional)
  required: false
  type: string
  example: "morning_routine"

learn_new:
  description: Whether to learn new patterns
  required: false
  type: boolean
  default: true

min_occurrences:
  description: Minimum occurrences to consider a pattern
  required: false
  type: integer
  default: 3
```

**Example**:

```yaml
service: motiondirection.analyze_pattern
data:
  time_range: 86400  # Last 24 hours
  learn_new: true
  min_occurrences: 5
```

---

## Events

### motiondirection_direction_detected

Fired when motion direction is detected with sufficient confidence.

**Event Data**:

```yaml
direction:
  description: Detected direction name
  type: string
  example: "north"

confidence:
  description: Detection confidence score
  type: float
  range: 0.0 - 1.0
  example: 0.85

method:
  description: Detection method used
  type: string
  enum: ["vector", "zone", "cue", "hybrid", "pattern"]
  example: "vector"

contributing_sensors:
  description: List of sensor entity IDs that contributed
  type: list
  example:
    - "binary_sensor.living_room_motion"
    - "binary_sensor.hallway_motion"

active_zones:
  description: List of currently active zone IDs
  type: list
  example:
    - "living_room"
    - "hallway"

pattern_match:
  description: Matched learned pattern ID (if any)
  type: string
  optional: true
  example: "morning_routine"

timestamp:
  description: ISO 8601 timestamp of detection
  type: string
  example: "2026-01-02T10:30:00"
```

**Example Listener**:

```yaml
automation:
  - alias: "Direction Detected Handler"
    trigger:
      - platform: event
        event_type: motiondirection_direction_detected
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.confidence > 0.7 }}"
    action:
      - service: light.turn_on
        target:
          entity_id: >
            {% if trigger.event.data.direction == 'north' %}
              light.hallway
            {% elif trigger.event.data.direction == 'east' %}
              light.kitchen
            {% endif %}
```

---

### motiondirection_zone_transition

Fired when motion transitions from one zone to another.

**Event Data**:

```yaml
from_zone:
  description: Source zone ID
  type: string
  example: "living_room"

to_zone:
  description: Destination zone ID
  type: string
  example: "kitchen"

direction:
  description: Direction name for this transition
  type: string
  example: "to_kitchen"

confidence:
  description: Transition confidence score
  type: float
  range: 0.0 - 1.0
  example: 0.82

dwell_time:
  description: Time spent in source zone (seconds)
  type: float
  example: 120.5

timestamp:
  description: ISO 8601 timestamp of transition
  type: string
  example: "2026-01-02T10:30:00"
```

**Example Listener**:

```yaml
automation:
  - alias: "Zone Transition Handler"
    trigger:
      - platform: event
        event_type: motiondirection_zone_transition
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.to_zone == 'bedroom' }}"
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.bedroom
        data:
          temperature: 22
```

---

### motiondirection_pattern_learned

Fired when a new motion pattern is learned.

**Event Data**:

```yaml
pattern_id:
  description: Unique identifier for the pattern
  type: string
  example: "morning_routine"

sequence:
  description: Sequence signature (comma-separated sensor IDs)
  type: string
  example: "bedroom,bathroom,kitchen"

occurrence_count:
  description: Number of times pattern has been observed
  type: integer
  example: 10

average_confidence:
  description: Average confidence across occurrences
  type: float
  range: 0.0 - 1.0
  example: 0.87

typical_time:
  description: Typical time of day (HH:MM format)
  type: string
  example: "08:30"

variability:
  description: Pattern variability score (lower = more consistent)
  type: float
  range: 0.0 - 1.0
  example: 0.15
```

**Example Listener**:

```yaml
automation:
  - alias: "Pattern Learned Handler"
    trigger:
      - platform: event
        event_type: motiondirection_pattern_learned
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.occurrence_count >= 10 }}"
    action:
      - service: persistent_notification.create
        data:
          title: "New Pattern Learned"
          message: >
            Pattern "{{ trigger.event.data.pattern_id }}" learned 
            ({{ trigger.event.data.occurrence_count }} occurrences)
```

---

### motiondirection_anomaly_detected

Fired when unusual or unexpected motion pattern is detected.

**Event Data**:

```yaml
anomaly_type:
  description: Type of anomaly
  type: string
  enum:
    - "unusual_sequence"
    - "unusual_timing"
    - "unexpected_direction"
    - "impossible_speed"
    - "zone_violation"
  example: "unusual_sequence"

description:
  description: Human-readable description
  type: string
  example: "Motion detected in unusual order"

severity:
  description: Anomaly severity level
  type: string
  enum: ["low", "medium", "high"]
  example: "medium"

affected_zones:
  description: List of zones involved in anomaly
  type: list
  example:
    - "bedroom"
    - "garage"

deviation_score:
  description: How much this deviates from normal (0.0-1.0)
  type: float
  range: 0.0 - 1.0
  example: 0.75

timestamp:
  description: ISO 8601 timestamp of detection
  type: string
  example: "2026-01-02T03:15:00"
```

**Example Listener**:

```yaml
automation:
  - alias: "Anomaly Detection Handler"
    trigger:
      - platform: event
        event_type: motiondirection_anomaly_detected
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.severity in ['medium', 'high'] }}"
    action:
      - service: notify.mobile_app
        data:
          title: "Motion Anomaly"
          message: >
            {{ trigger.event.data.description }}
            Severity: {{ trigger.event.data.severity }}
```

---

## Sensors

### sensor.motion_direction

Main motion direction sensor.

**State**: Current detected direction name

**Possible States**:
- `"north"`, `"south"`, `"east"`, `"west"`
- `"northeast"`, `"northwest"`, `"southeast"`, `"southwest"`
- `"unknown"` (no direction detected or low confidence)
- Custom direction names from zones

**Attributes**:

```yaml
confidence:
  description: Current detection confidence
  type: float
  range: 0.0 - 1.0
  example: 0.85

method:
  description: Detection method used
  type: string
  enum: ["vector", "zone", "cue", "hybrid", "pattern"]

contributing_sensors:
  description: List of sensor entity IDs
  type: list
  example:
    - "binary_sensor.living_room_motion"
    - "binary_sensor.hallway_motion"

detected_at:
  description: ISO 8601 timestamp of last detection
  type: string
  example: "2026-01-02T10:30:00"

active_zones:
  description: List of currently active zone IDs
  type: list
  example:
    - "living_room"

pattern_match:
  description: Matched learned pattern (if any)
  type: string
  optional: true
  example: "morning_routine"

sequence_length:
  description: Number of sensors in current sequence
  type: integer
  example: 3

time_window_used:
  description: Time window used for correlation (seconds)
  type: float
  example: 5.0
```

---

### sensor.motion_direction_confidence

Confidence score for current direction detection.

**State**: Confidence value (0.0 - 1.0)

**Unit**: None (dimensionless, 0-1 scale)

**Attributes**:

```yaml
method:
  description: Detection method
  type: string

contributing_factors:
  description: List of factors that influenced confidence
  type: list
  example:
    - "vector_alignment"
    - "cue_correlation"
    - "pattern_match"

last_update:
  description: ISO 8601 timestamp of last update
  type: string
```

---

### sensor.motion_direction_method

Detection method used for current direction.

**State**: Method name

**Possible States**:
- `"vector"` - Pure vector-based detection
- `"zone"` - Zone-based detection
- `"cue"` - Secondary cue-assisted detection
- `"hybrid"` - Combined detection methods
- `"pattern"` - Pattern recognition-based
- `"none"` - No detection active

**Attributes**:

```yaml
algorithm_version:
  description: Version of detection algorithm
  type: string
  example: "1.0.0"

last_method_change:
  description: When method last changed
  type: string
```

---

### sensor.zone_<zone_id>

Per-zone direction sensor (created for each defined zone).

**Entity ID**: `sensor.zone_<zone_id>` (e.g., `sensor.zone_living_room`)

**State**: Current direction within this zone

**Attributes**:

```yaml
zone_id:
  description: Zone identifier
  type: string
  example: "living_room"

occupancy:
  description: Whether zone is currently occupied
  type: boolean
  example: true

last_direction:
  description: Last detected direction in this zone
  type: string
  example: "to_kitchen"

transition_count:
  description: Total transitions in/out of zone
  type: integer
  example: 42

average_dwell_time:
  description: Average time spent in zone
  type: string
  format: "HH:MM:SS"
  example: "00:05:30"

last_entry:
  description: Last entry timestamp
  type: string
  example: "2026-01-02T10:25:00"

last_exit:
  description: Last exit timestamp
  type: string
  example: "2026-01-02T10:30:00"
```

---

### sensor.cue_<cue_id>

Per-cue state sensor (created for each registered secondary cue).

**Entity ID**: `sensor.cue_<cue_id>` (e.g., `sensor.cue_front_door`)

**State**: Current state of the cue entity

**Attributes**:

```yaml
cue_id:
  description: Cue identifier
  type: string
  example: "front_door"

cue_type:
  description: Type of cue
  type: string
  example: "door"

last_trigger:
  description: Last trigger timestamp
  type: string
  example: "2026-01-02T10:30:00"

correlation_count:
  description: Times cue correlated with motion
  type: integer
  example: 42

effectiveness:
  description: Cue effectiveness score (0.0-1.0)
  type: float
  range: 0.0 - 1.0
  example: 0.78

confidence_contribution:
  description: Average confidence boost provided
  type: float
  example: 0.15
```

---

## States and Attributes

### Integration Config Entry

The integration's config entry stores:

```yaml
data:
  name: "Motion Direction Tracker"
  update_interval: 5
  
options:
  confidence_threshold: 0.7
  time_window: 5
  enable_pattern_learning: true
  enable_anomaly_detection: true
```

### Storage Format

The integration stores data in `.storage/motiondirection.json`:

```json
{
  "version": 1,
  "key": "motiondirection",
  "data": {
    "floorplans": {
      "main_floor": {
        "width": 20.0,
        "height": 15.0,
        "sensors": [...]
      }
    },
    "zones": {
      "living_room": {...}
    },
    "cues": {
      "front_door": {...}
    },
    "learned_patterns": {
      "morning_routine": {...}
    }
  }
}
```

---

## Data Models

### SensorNode

```python
@dataclass
class SensorNode:
    entity_id: str
    x: float
    y: float
    range_meters: float
    floor: int = 0
```

### MotionEvent

```python
@dataclass
class MotionEvent:
    sensor_id: str
    timestamp: datetime
    state: str
    attributes: dict = field(default_factory=dict)
```

### DirectionResult

```python
@dataclass
class DirectionResult:
    direction: str
    confidence: float
    method: str
    contributing_sensors: list[str]
    hints: list[DirectionalHint] = field(default_factory=list)
    active_zones: list[str] = field(default_factory=list)
```

### TriggerZone

```python
@dataclass
class TriggerZone:
    zone_id: str
    polygon: list[PathPoint]
    directions: list[DirectionConfig]
```

### DirectionConfig

```python
@dataclass
class DirectionConfig:
    name: str
    vector: tuple[float, float]
    entry_side: str
    confidence_threshold: float
```

### SecondaryCue

```python
@dataclass
class SecondaryCue:
    cue_id: str
    entity_id: str
    cue_type: str
    location: PathPoint
    confidence_boost: float
    directional_hint: DirectionalHint | None = None
```

---

For more information:
- [User Guide](USER_GUIDE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [GitHub Issues](https://github.com/tamaygz/ha-motiondirection/issues)
