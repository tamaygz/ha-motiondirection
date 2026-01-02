"""Unit tests for motiondirection data models."""
from datetime import datetime

import pytest

from custom_components.motiondirection.models import (
    DirectionConfig,
    DirectionResult,
    DirectionalHint,
    Floorplan,
    LearnedPattern,
    MotionEvent,
    MotionPath,
    MotionSequence,
    PathPoint,
    SecondaryCue,
    SensorNode,
    StateChange,
    TriggerZone,
    ZoneTransition,
)


# ===== SensorNode Tests =====


def test_sensor_node_creation(sample_sensor: SensorNode):
    """Test creating a sensor node."""
    assert sample_sensor.entity_id == "binary_sensor.living_room_motion"
    assert sample_sensor.x == 5.0
    assert sample_sensor.y == 5.0
    assert sample_sensor.range_meters == 3.0


def test_sensor_node_with_floor():
    """Test sensor node with floor specification."""
    sensor = SensorNode(
        entity_id="binary_sensor.upstairs_motion",
        x=5.0,
        y=5.0,
        range_meters=3.0,
        floor=2,
    )
    assert sensor.floor == 2


def test_sensor_node_coordinates():
    """Test sensor node coordinate access."""
    sensor = SensorNode(
        entity_id="binary_sensor.test",
        x=10.0,
        y=20.0,
        range_meters=5.0,
    )
    assert sensor.x == 10.0
    assert sensor.y == 20.0


# ===== MotionEvent Tests =====


def test_motion_event_creation(sample_motion_event: MotionEvent):
    """Test creating a motion event."""
    assert sample_motion_event.sensor_id == "binary_sensor.living_room_motion"
    assert sample_motion_event.state == "on"
    assert isinstance(sample_motion_event.timestamp, datetime)


def test_motion_event_with_attributes():
    """Test motion event with additional attributes."""
    event = MotionEvent(
        sensor_id="binary_sensor.test",
        timestamp=datetime.now(),
        state="on",
        attributes={"illuminance": 100, "temperature": 22.5},
    )
    assert event.attributes == {"illuminance": 100, "temperature": 22.5}


def test_motion_event_ordering(sample_motion_sequence: list[MotionEvent]):
    """Test motion event chronological ordering."""
    assert sample_motion_sequence[0].timestamp < sample_motion_sequence[1].timestamp
    assert sample_motion_sequence[1].timestamp < sample_motion_sequence[2].timestamp


# ===== MotionSequence Tests =====


def test_motion_sequence_creation():
    """Test creating a motion sequence."""
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_2",
            timestamp=base_time,
            state="on",
        ),
    ]
    
    sequence = MotionSequence(
        events=events,
        start_time=base_time,
        confidence=0.85,
    )
    
    assert len(sequence.events) == 2
    assert sequence.confidence == 0.85
    assert sequence.start_time == base_time


def test_motion_sequence_with_direction():
    """Test motion sequence with detected direction."""
    sequence = MotionSequence(
        events=[],
        start_time=datetime.now(),
        confidence=0.9,
        detected_direction="north",
    )
    assert sequence.detected_direction == "north"


# ===== MotionPath Tests =====


def test_motion_path_creation():
    """Test creating a motion path."""
    points = [
        PathPoint(x=0.0, y=0.0, timestamp=datetime.now()),
        PathPoint(x=5.0, y=5.0, timestamp=datetime.now()),
    ]
    
    path = MotionPath(
        path_id="path_1",
        points=points,
        confidence=0.8,
    )
    
    assert path.path_id == "path_1"
    assert len(path.points) == 2
    assert path.confidence == 0.8


def test_motion_path_empty():
    """Test empty motion path."""
    path = MotionPath(
        path_id="empty_path",
        points=[],
        confidence=0.0,
    )
    assert len(path.points) == 0


# ===== PathPoint Tests =====


def test_path_point_creation():
    """Test creating a path point."""
    point = PathPoint(x=10.0, y=20.0)
    assert point.x == 10.0
    assert point.y == 20.0
    assert point.timestamp is None


def test_path_point_with_timestamp():
    """Test path point with timestamp."""
    now = datetime.now()
    point = PathPoint(x=5.0, y=5.0, timestamp=now)
    assert point.timestamp == now


def test_path_point_coordinates():
    """Test path point coordinate access."""
    point = PathPoint(x=15.5, y=25.5)
    assert point.x == 15.5
    assert point.y == 25.5


# ===== Floorplan Tests =====


def test_floorplan_creation(sample_floorplan: Floorplan):
    """Test creating a floorplan."""
    assert sample_floorplan.floorplan_id == "main"
    assert sample_floorplan.width == 20.0
    assert sample_floorplan.height == 10.0
    assert len(sample_floorplan.sensors) == 3


def test_floorplan_empty(empty_floorplan: Floorplan):
    """Test empty floorplan."""
    assert len(empty_floorplan.sensors) == 0
    assert empty_floorplan.width > 0
    assert empty_floorplan.height > 0


def test_floorplan_dimensions():
    """Test floorplan with various dimensions."""
    fp = Floorplan(
        floorplan_id="test",
        width=50.0,
        height=30.0,
        sensors=[],
    )
    assert fp.width == 50.0
    assert fp.height == 30.0


# ===== TriggerZone Tests =====


def test_trigger_zone_creation(sample_trigger_zone: TriggerZone):
    """Test creating a trigger zone."""
    assert sample_trigger_zone.zone_id == "living_room"
    assert len(sample_trigger_zone.polygon) == 4
    assert len(sample_trigger_zone.directions) == 1


def test_trigger_zone_directions():
    """Test trigger zone with multiple directions."""
    zone = TriggerZone(
        zone_id="hallway",
        polygon=[
            PathPoint(x=0.0, y=0.0),
            PathPoint(x=5.0, y=0.0),
            PathPoint(x=5.0, y=10.0),
            PathPoint(x=0.0, y=10.0),
        ],
        directions=[
            DirectionConfig(
                name="north",
                vector=(0.0, 1.0),
                entry_side="top",
                confidence_threshold=0.7,
            ),
            DirectionConfig(
                name="south",
                vector=(0.0, -1.0),
                entry_side="bottom",
                confidence_threshold=0.7,
            ),
        ],
    )
    assert len(zone.directions) == 2


def test_trigger_zone_polygon_points():
    """Test trigger zone polygon structure."""
    polygon = [
        PathPoint(x=0.0, y=0.0),
        PathPoint(x=10.0, y=0.0),
        PathPoint(x=10.0, y=10.0),
        PathPoint(x=0.0, y=10.0),
    ]
    zone = TriggerZone(
        zone_id="square",
        polygon=polygon,
        directions=[],
    )
    assert len(zone.polygon) == 4
    assert zone.polygon[0].x == 0.0
    assert zone.polygon[2].y == 10.0


# ===== DirectionConfig Tests =====


def test_direction_config_creation():
    """Test creating a direction configuration."""
    config = DirectionConfig(
        name="to_kitchen",
        vector=(1.0, 0.0),
        entry_side="right",
        confidence_threshold=0.75,
    )
    assert config.name == "to_kitchen"
    assert config.vector == (1.0, 0.0)
    assert config.entry_side == "right"
    assert config.confidence_threshold == 0.75


def test_direction_config_vector_normalization():
    """Test direction config with various vectors."""
    config = DirectionConfig(
        name="diagonal",
        vector=(1.0, 1.0),
        entry_side="corner",
        confidence_threshold=0.7,
    )
    assert config.vector == (1.0, 1.0)


# ===== SecondaryCue Tests =====


def test_secondary_cue_creation(sample_cue: SecondaryCue):
    """Test creating a secondary cue."""
    assert sample_cue.cue_id == "door_open"
    assert sample_cue.entity_id == "binary_sensor.front_door"
    assert sample_cue.cue_type == "door"
    assert sample_cue.confidence_boost == 0.15


def test_secondary_cue_location():
    """Test secondary cue location."""
    cue = SecondaryCue(
        cue_id="test",
        entity_id="light.test",
        cue_type="light",
        location=PathPoint(x=10.0, y=15.0),
        confidence_boost=0.1,
    )
    assert cue.location.x == 10.0
    assert cue.location.y == 15.0


def test_secondary_cue_types():
    """Test different secondary cue types."""
    door_cue = SecondaryCue(
        cue_id="door",
        entity_id="binary_sensor.door",
        cue_type="door",
        location=PathPoint(x=0.0, y=0.0),
        confidence_boost=0.2,
    )
    light_cue = SecondaryCue(
        cue_id="light",
        entity_id="light.room",
        cue_type="light",
        location=PathPoint(x=0.0, y=0.0),
        confidence_boost=0.1,
    )
    assert door_cue.cue_type == "door"
    assert light_cue.cue_type == "light"


# ===== DirectionalHint Tests =====


def test_directional_hint_creation():
    """Test creating a directional hint."""
    hint = DirectionalHint(
        direction="north",
        confidence=0.8,
        source="vector",
    )
    assert hint.direction == "north"
    assert hint.confidence == 0.8
    assert hint.source == "vector"


def test_directional_hint_with_reason():
    """Test directional hint with reason."""
    hint = DirectionalHint(
        direction="south",
        confidence=0.9,
        source="cue",
        reason="Door opened to south",
    )
    assert hint.reason == "Door opened to south"


# ===== StateChange Tests =====


def test_state_change_creation():
    """Test creating a state change."""
    now = datetime.now()
    change = StateChange(
        entity_id="binary_sensor.test",
        old_state="off",
        new_state="on",
        timestamp=now,
    )
    assert change.entity_id == "binary_sensor.test"
    assert change.old_state == "off"
    assert change.new_state == "on"
    assert change.timestamp == now


def test_state_change_attributes():
    """Test state change with attributes."""
    change = StateChange(
        entity_id="light.test",
        old_state="off",
        new_state="on",
        timestamp=datetime.now(),
        attributes={"brightness": 255},
    )
    assert change.attributes == {"brightness": 255}


# ===== LearnedPattern Tests =====


def test_learned_pattern_creation():
    """Test creating a learned pattern."""
    pattern = LearnedPattern(
        pattern_id="morning_routine",
        sequence_signature="sensor_1,sensor_2,sensor_3",
        occurrence_count=10,
        average_confidence=0.85,
        typical_time_of_day="08:00",
    )
    assert pattern.pattern_id == "morning_routine"
    assert pattern.occurrence_count == 10
    assert pattern.average_confidence == 0.85


def test_learned_pattern_statistics():
    """Test learned pattern with statistics."""
    pattern = LearnedPattern(
        pattern_id="test",
        sequence_signature="a,b,c",
        occurrence_count=50,
        average_confidence=0.9,
        typical_time_of_day="12:00",
        last_seen=datetime.now(),
    )
    assert pattern.occurrence_count == 50
    assert pattern.average_confidence == 0.9
    assert pattern.last_seen is not None


# ===== ZoneTransition Tests =====


def test_zone_transition_creation():
    """Test creating a zone transition."""
    transition = ZoneTransition(
        from_zone="living_room",
        to_zone="kitchen",
        timestamp=datetime.now(),
        confidence=0.8,
    )
    assert transition.from_zone == "living_room"
    assert transition.to_zone == "kitchen"
    assert transition.confidence == 0.8


def test_zone_transition_with_direction():
    """Test zone transition with direction."""
    transition = ZoneTransition(
        from_zone="bedroom",
        to_zone="bathroom",
        timestamp=datetime.now(),
        confidence=0.9,
        direction="north",
    )
    assert transition.direction == "north"


# ===== DirectionResult Tests =====


def test_direction_result_creation():
    """Test creating a direction result."""
    result = DirectionResult(
        direction="north",
        confidence=0.85,
        method="vector",
        contributing_sensors=["sensor_1", "sensor_2"],
    )
    assert result.direction == "north"
    assert result.confidence == 0.85
    assert result.method == "vector"
    assert len(result.contributing_sensors) == 2


def test_direction_result_with_hints():
    """Test direction result with hints."""
    hints = [
        DirectionalHint(direction="north", confidence=0.8, source="vector"),
        DirectionalHint(direction="north", confidence=0.9, source="cue"),
    ]
    result = DirectionResult(
        direction="north",
        confidence=0.85,
        method="hybrid",
        contributing_sensors=["sensor_1"],
        hints=hints,
    )
    assert len(result.hints) == 2


def test_direction_result_zones():
    """Test direction result with zone information."""
    result = DirectionResult(
        direction="east",
        confidence=0.9,
        method="zone",
        contributing_sensors=["sensor_1"],
        active_zones=["living_room", "hallway"],
    )
    assert len(result.active_zones) == 2
    assert "living_room" in result.active_zones
