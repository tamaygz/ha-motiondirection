# HA-MotionDirection User Guide

Complete guide to configuring and using the HA-MotionDirection integration.

## Table of Contents

1. [Installation](#installation)
2. [Initial Configuration](#initial-configuration)
3. [Floorplan Setup](#floorplan-setup)
4. [Trigger Zones](#trigger-zones)
5. [Secondary Cues](#secondary-cues)
6. [Sensors and States](#sensors-and-states)
7. [Services](#services)
8. [Events](#events)
9. [Automation Examples](#automation-examples)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Navigate to **Integrations**
3. Click the **⋮** menu (three dots) in the top right
4. Select **Custom repositories**
5. Add repository URL: `https://github.com/tamaygz/ha-motiondirection`
6. Select category: **Integration**
7. Click **Add**
8. Search for "Motion Direction"
9. Click **Download**
10. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/tamaygz/ha-motiondirection/releases)
2. Extract the archive
3. Copy the `custom_components/motiondirection` folder to your Home Assistant `config/custom_components/` directory
4. Restart Home Assistant

## Initial Configuration

### Adding the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Motion Direction"
4. Click on the integration to start setup

### Configuration Options

During setup, you'll configure:

- **Update Interval** (default: 5 seconds)
  - How often the integration checks for new motion events
  - Lower values = more responsive but higher CPU usage
  - Recommended: 3-10 seconds

- **Confidence Threshold** (default: 0.7)
  - Minimum confidence score (0.0-1.0) to report a direction
  - Higher values = more accurate but fewer detections
  - Recommended: 0.6-0.8

- **Time Window** (default: 5 seconds)
  - Maximum time between sensor triggers to consider them related
  - Adjust based on space size and walking speed
  - Recommended: 3-10 seconds

## Floorplan Setup

The floorplan is the foundation of motion direction detection. It defines sensor positions in 2D space.

### Understanding Coordinates

- **Origin (0, 0)**: Bottom-left corner of your space
- **X-axis**: Horizontal (left to right)
- **Y-axis**: Vertical (bottom to top)
- **Units**: Meters (recommended) or any consistent unit

### Creating a Floorplan

#### Via Service Call

```yaml
service: motiondirection.update_floorplan
data:
  floorplan_id: "main_floor"
  width: 20.0  # Total width in meters
  height: 15.0  # Total height in meters
  sensors:
    - entity_id: binary_sensor.living_room_motion
      x: 5.0
      y: 5.0
      range_meters: 3.0  # Detection range
    - entity_id: binary_sensor.kitchen_motion
      x: 15.0
      y: 5.0
      range_meters: 3.0
    - entity_id: binary_sensor.hallway_motion
      x: 10.0
      y: 10.0
      range_meters: 3.0
    - entity_id: binary_sensor.bedroom_motion
      x: 5.0
      y: 13.0
      range_meters: 2.5
```

#### Via YAML Configuration

```yaml
# configuration.yaml (optional - service call is preferred)
motiondirection:
  floorplans:
    - id: "main_floor"
      width: 20.0
      height: 15.0
      sensors:
        - entity_id: binary_sensor.living_room_motion
          x: 5.0
          y: 5.0
          range_meters: 3.0
```

### Sensor Placement Tips

1. **Coverage Overlap**: Sensors should have overlapping detection ranges for accurate direction detection
2. **Strategic Positioning**: Place sensors at doorways and transition points
3. **Consistent Heights**: Mount all sensors at the same height for best results
4. **Test and Adjust**: Walk through your space and verify triggers

### Measuring Your Space

1. Draw a simple floor plan on paper
2. Mark sensor locations
3. Measure distances between sensors
4. Note room dimensions
5. Transfer measurements to configuration

## Trigger Zones

Trigger zones are polygonal areas with defined directional behaviors. They're perfect for room-specific automation.

### Creating a Trigger Zone

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
      vector: [1.0, 0.0]  # East direction
      entry_side: "right"
      confidence_threshold: 0.7
    - name: "to_hallway"
      vector: [0.0, 1.0]  # North direction
      entry_side: "top"
      confidence_threshold: 0.7
```

### Direction Vectors

Direction vectors define expected motion directions within a zone:

- **North**: `[0.0, 1.0]`
- **South**: `[0.0, -1.0]`
- **East**: `[1.0, 0.0]`
- **West**: `[-1.0, 0.0]`
- **Northeast**: `[0.707, 0.707]` (normalized)
- **Southeast**: `[0.707, -0.707]`
- **Southwest**: `[-0.707, -0.707]`
- **Northwest**: `[-0.707, 0.707]`

### Entry Sides

The `entry_side` parameter specifies which edge of the polygon corresponds to the direction:

- `"top"`: North edge
- `"bottom"`: South edge
- `"left"`: West edge
- `"right"`: East edge
- `"top_left"`: Northwest corner
- `"top_right"`: Northeast corner
- `"bottom_left"`: Southwest corner
- `"bottom_right"`: Southeast corner

### Updating a Zone

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

### Deleting a Zone

```yaml
service: motiondirection.delete_trigger_zone
data:
  zone_id: "living_room"
```

## Secondary Cues

Secondary cues enhance detection accuracy using additional sensors like doors and lights.

### Registering a Secondary Cue

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
    direction: "north"
    weight: 0.8
```

### Cue Types

- **door**: Door contact sensors
- **light**: Light switches and bulbs
- **lock**: Smart locks
- **appliance**: Appliances (e.g., refrigerator door)
- **media**: Media players
- **climate**: HVAC changes
- **custom**: Custom cues

### Confidence Boost

The `confidence_boost` parameter increases detection confidence when the cue is triggered:

- **0.05-0.10**: Minor boost for weak indicators
- **0.10-0.15**: Standard boost for typical cues
- **0.15-0.25**: Strong boost for reliable indicators
- **0.25+**: Very strong boost (use sparingly)

### Directional Hints

Directional hints provide explicit direction information:

```yaml
directional_hint:
  from_state: "off"
  to_state: "on"
  direction: "to_kitchen"
  weight: 0.8  # How much to trust this hint (0.0-1.0)
```

## Sensors and States

### Main Motion Direction Sensor

**Entity**: `sensor.motion_direction`

**Attributes**:
```yaml
state: "north"
confidence: 0.85
method: "vector"
contributing_sensors:
  - binary_sensor.living_room_motion
  - binary_sensor.hallway_motion
detected_at: "2026-01-02T10:30:00"
active_zones:
  - "living_room"
  - "hallway"
pattern_match: "morning_routine"
```

### Confidence Sensor

**Entity**: `sensor.motion_direction_confidence`

**State**: 0.0 to 1.0 (0-100%)

**Interpretation**:
- **0.0-0.5**: Low confidence, may be unreliable
- **0.5-0.7**: Moderate confidence
- **0.7-0.9**: High confidence, reliable
- **0.9-1.0**: Very high confidence, very reliable

### Detection Method Sensor

**Entity**: `sensor.motion_direction_method`

**Possible Values**:
- `"vector"`: Pure vector-based detection
- `"zone"`: Zone-based detection
- `"cue"`: Cue-assisted detection
- `"hybrid"`: Combined detection methods
- `"pattern"`: Pattern recognition

### Zone Sensors

Each zone gets its own sensor:

**Entity**: `sensor.zone_<zone_id>`

**Attributes**:
```yaml
state: "to_kitchen"
zone_id: "living_room"
occupancy: true
last_direction: "to_kitchen"
transition_count: 15
average_dwell_time: "00:05:30"
```

### Cue Sensors

Each secondary cue gets a sensor:

**Entity**: `sensor.cue_<cue_id>`

**Attributes**:
```yaml
state: "on"
cue_type: "door"
last_trigger: "2026-01-02T10:30:00"
correlation_count: 42
effectiveness: 0.78
```

## Services

### update_floorplan

Update floorplan configuration.

```yaml
service: motiondirection.update_floorplan
data:
  floorplan_id: "main"
  width: 20.0
  height: 15.0
  sensors:
    - entity_id: binary_sensor.sensor1
      x: 5.0
      y: 5.0
      range_meters: 3.0
```

### create_trigger_zone

Create a new trigger zone.

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
```

### update_trigger_zone

Modify an existing trigger zone.

```yaml
service: motiondirection.update_trigger_zone
data:
  zone_id: "living_room"
  directions:
    - name: "to_kitchen"
      vector: [1.0, 0.0]
      entry_side: "right"
      confidence_threshold: 0.65
```

### delete_trigger_zone

Remove a trigger zone.

```yaml
service: motiondirection.delete_trigger_zone
data:
  zone_id: "living_room"
```

### register_secondary_cue

Register a secondary cue.

```yaml
service: motiondirection.register_secondary_cue
data:
  cue_id: "front_door"
  entity_id: binary_sensor.front_door
  cue_type: "door"
  location:
    x: 5.0
    y: 0.0
  confidence_boost: 0.15
```

### analyze_pattern

Manually trigger pattern analysis.

```yaml
service: motiondirection.analyze_pattern
data:
  time_range: 3600  # Last hour in seconds
  pattern_id: "morning_routine"  # Optional: analyze specific pattern
```

## Events

### motiondirection_direction_detected

Fired when motion direction is detected with sufficient confidence.

**Event Data**:
```yaml
direction: "north"
confidence: 0.85
method: "vector"
contributing_sensors:
  - binary_sensor.living_room_motion
  - binary_sensor.hallway_motion
active_zones:
  - "living_room"
timestamp: "2026-01-02T10:30:00"
```

**Example Automation**:
```yaml
automation:
  - alias: "Light Ahead of Motion"
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

### motiondirection_zone_transition

Fired when motion transitions between zones.

**Event Data**:
```yaml
from_zone: "living_room"
to_zone: "kitchen"
direction: "to_kitchen"
confidence: 0.82
timestamp: "2026-01-02T10:30:00"
```

### motiondirection_pattern_learned

Fired when a new motion pattern is learned.

**Event Data**:
```yaml
pattern_id: "evening_routine"
sequence: "bedroom,bathroom,kitchen"
occurrence_count: 10
average_confidence: 0.87
typical_time: "18:30"
```

### motiondirection_anomaly_detected

Fired when unusual motion pattern is detected.

**Event Data**:
```yaml
anomaly_type: "unusual_sequence"
description: "Motion detected in unusual order"
severity: "medium"  # low, medium, high
affected_zones:
  - "bedroom"
  - "garage"
timestamp: "2026-01-02T03:15:00"
```

## Automation Examples

### Example 1: Directional Lighting

Turn on lights ahead of detected motion direction:

```yaml
automation:
  - alias: "Directional Lighting"
    trigger:
      - platform: event
        event_type: motiondirection_direction_detected
    condition:
      - condition: sun
        after: sunset
      - condition: template
        value_template: "{{ trigger.event.data.confidence > 0.7 }}"
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.direction == 'to_kitchen' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.kitchen
                data:
                  brightness_pct: 80
          - conditions:
              - condition: template
                value_template: "{{ trigger.event.data.direction == 'to_bedroom' }}"
            sequence:
              - service: light.turn_on
                target:
                  entity_id: light.bedroom
                data:
                  brightness_pct: 30
```

### Example 2: Zone-Based Climate Control

Adjust HVAC based on zone transitions:

```yaml
automation:
  - alias: "Climate - Zone Transition"
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

### Example 3: Security Alert on Anomaly

```yaml
automation:
  - alias: "Security Alert - Anomaly"
    trigger:
      - platform: event
        event_type: motiondirection_anomaly_detected
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.severity in ['medium', 'high'] }}"
      - condition: state
        entity_id: alarm_control_panel.home
        state: "armed_away"
    action:
      - service: notify.mobile_app
        data:
          title: "Security Alert"
          message: >
            Unusual motion detected: {{ trigger.event.data.description }}
            Zones: {{ trigger.event.data.affected_zones | join(', ') }}
```

### Example 4: Pattern-Based Scene

```yaml
automation:
  - alias: "Morning Routine Scene"
    trigger:
      - platform: event
        event_type: motiondirection_pattern_learned
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.pattern_id == 'morning_routine' }}"
      - condition: time
        after: "06:00:00"
        before: "09:00:00"
    action:
      - service: scene.turn_on
        target:
          entity_id: scene.morning
```

## Troubleshooting

### Direction Not Detected

**Problem**: No direction is being detected despite motion events.

**Solutions**:
1. Check that at least 3 sensors are configured
2. Verify sensor coordinates in floorplan
3. Ensure time_window is appropriate for your space
4. Lower confidence_threshold temporarily
5. Check logs for errors: `Settings → System → Logs`

### Low Confidence Scores

**Problem**: Direction is detected but with low confidence (<0.6).

**Solutions**:
1. Add more sensors to increase coverage
2. Register secondary cues (doors, lights)
3. Check for sensor dead zones
4. Ensure sensor ranges overlap
5. Verify sensors are triggered in sequence (not simultaneously)

### Zones Not Triggering

**Problem**: Zone sensors remain inactive.

**Solutions**:
1. Verify zone polygon contains sensor locations
2. Check entry_side matches expected direction
3. Ensure confidence_threshold isn't too high
4. Validate polygon points form a valid shape
5. Test with zone-specific direction vectors

### Erratic or Wrong Directions

**Problem**: Detected directions don't match actual movement.

**Solutions**:
1. Review sensor placement on floorplan
2. Check for incorrect sensor coordinates
3. Verify range_meters is accurate
4. Increase time_window if sensors trigger slowly
5. Check for interference from pets or other motion sources

### High False Positive Rate

**Problem**: Many detections that don't correspond to real movement.

**Solutions**:
1. Increase confidence_threshold
2. Reduce sensor sensitivity if possible
3. Add more secondary cues for verification
4. Check for environmental triggers (pets, curtains, etc.)
5. Enable pattern learning to filter known false patterns

## Best Practices

### Sensor Placement

1. **Coverage**: Aim for 80-100% floor coverage
2. **Overlap**: 20-30% overlap between sensor ranges
3. **Height**: Mount all sensors at same height (typically 2-2.5m)
4. **Doorways**: Always place sensors near doorways and transitions
5. **Corners**: Avoid placing sensors in corners where coverage is limited

### Configuration

1. **Start Simple**: Begin with basic floorplan, add zones later
2. **Iterate**: Test and refine coordinates based on real usage
3. **Document**: Keep notes on sensor positions and measurements
4. **Version Control**: Save configuration backups before major changes
5. **Test Thoroughly**: Walk through space in different patterns

### Performance

1. **Update Interval**: Don't set below 3 seconds unless necessary
2. **Sensor Count**: 5-15 sensors is optimal for most homes
3. **Zone Count**: Limit to 5-10 zones for best performance
4. **History**: Enable pattern learning after 1 week of data
5. **Cleanup**: Periodically review and remove unused cues/zones

### Automation

1. **Confidence Checks**: Always verify confidence in automations
2. **Failsafes**: Include manual override options
3. **Testing**: Test automations during daytime first
4. **Logging**: Enable debug logging during initial setup
5. **Graceful Degradation**: Automations should work even if direction detection fails

---

For more information, see:
- [API Reference](API_REFERENCE.md)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [GitHub Issues](https://github.com/tamaygz/ha-motiondirection/issues)
