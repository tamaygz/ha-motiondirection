"""Unit tests for motion detector."""
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from custom_components.motiondirection.core.motion_detector import MotionDetector
from custom_components.motiondirection.core.vector_calculator import VectorCalculator
from custom_components.motiondirection.models import (
    DirectionResult,
    Floorplan,
    MotionEvent,
    MotionSequence,
    PathPoint,
    SensorNode,
)


@pytest.fixture
def motion_detector(sample_floorplan: Floorplan) -> MotionDetector:
    """Create a motion detector with sample floorplan."""
    vector_calc = VectorCalculator()
    return MotionDetector(floorplan=sample_floorplan, vector_calculator=vector_calc)


# ===== Basic Detection Tests =====


def test_detect_direction_linear_movement(
    motion_detector: MotionDetector,
    sample_motion_sequence: list[MotionEvent],
):
    """Test detecting direction from linear movement."""
    sequence = MotionSequence(
        events=sample_motion_sequence,
        start_time=sample_motion_sequence[0].timestamp,
        confidence=0.8,
    )
    
    result = motion_detector.detect_direction(sequence)
    
    assert isinstance(result, DirectionResult)
    assert result.direction in ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]
    assert 0.0 <= result.confidence <= 1.0


def test_detect_direction_single_sensor():
    """Test detection with single sensor activation."""
    floorplan = Floorplan(
        floorplan_id="test",
        width=10.0,
        height=10.0,
        sensors=[
            SensorNode(
                entity_id="binary_sensor.test",
                x=5.0,
                y=5.0,
                range_meters=3.0,
            )
        ],
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    sequence = MotionSequence(
        events=[
            MotionEvent(
                sensor_id="binary_sensor.test",
                timestamp=datetime.now(),
                state="on",
            )
        ],
        start_time=datetime.now(),
        confidence=0.5,
    )
    
    result = detector.detect_direction(sequence)
    
    # Single sensor should have low confidence
    assert result.confidence < 0.7


def test_detect_direction_empty_sequence(motion_detector: MotionDetector):
    """Test detection with empty sequence."""
    sequence = MotionSequence(
        events=[],
        start_time=datetime.now(),
        confidence=0.0,
    )
    
    result = motion_detector.detect_direction(sequence)
    
    assert result.confidence == 0.0


# ===== Direction Tests =====


def test_detect_eastward_movement():
    """Test detecting eastward movement."""
    sensors = [
        SensorNode(entity_id="sensor_1", x=0.0, y=5.0, range_meters=3.0),
        SensorNode(entity_id="sensor_2", x=5.0, y=5.0, range_meters=3.0),
        SensorNode(entity_id="sensor_3", x=10.0, y=5.0, range_meters=3.0),
    ]
    
    floorplan = Floorplan(
        floorplan_id="test",
        width=20.0,
        height=10.0,
        sensors=sensors,
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    base_time = datetime.now()
    sequence = MotionSequence(
        events=[
            MotionEvent(sensor_id="sensor_1", timestamp=base_time, state="on"),
            MotionEvent(sensor_id="sensor_2", timestamp=base_time + timedelta(seconds=1), state="on"),
            MotionEvent(sensor_id="sensor_3", timestamp=base_time + timedelta(seconds=2), state="on"),
        ],
        start_time=base_time,
        confidence=0.8,
    )
    
    result = detector.detect_direction(sequence)
    
    assert result.direction == "east"
    assert result.confidence > 0.5


def test_detect_northward_movement():
    """Test detecting northward movement."""
    sensors = [
        SensorNode(entity_id="sensor_1", x=5.0, y=0.0, range_meters=3.0),
        SensorNode(entity_id="sensor_2", x=5.0, y=5.0, range_meters=3.0),
        SensorNode(entity_id="sensor_3", x=5.0, y=10.0, range_meters=3.0),
    ]
    
    floorplan = Floorplan(
        floorplan_id="test",
        width=10.0,
        height=20.0,
        sensors=sensors,
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    base_time = datetime.now()
    sequence = MotionSequence(
        events=[
            MotionEvent(sensor_id="sensor_1", timestamp=base_time, state="on"),
            MotionEvent(sensor_id="sensor_2", timestamp=base_time + timedelta(seconds=1), state="on"),
            MotionEvent(sensor_id="sensor_3", timestamp=base_time + timedelta(seconds=2), state="on"),
        ],
        start_time=base_time,
        confidence=0.8,
    )
    
    result = detector.detect_direction(sequence)
    
    assert result.direction == "north"
    assert result.confidence > 0.5


# ===== Confidence Tests =====


def test_confidence_with_clear_pattern():
    """Test that clear motion patterns have high confidence."""
    sensors = [
        SensorNode(entity_id=f"sensor_{i}", x=float(i * 5), y=5.0, range_meters=3.0)
        for i in range(5)
    ]
    
    floorplan = Floorplan(
        floorplan_id="test",
        width=25.0,
        height=10.0,
        sensors=sensors,
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    base_time = datetime.now()
    sequence = MotionSequence(
        events=[
            MotionEvent(
                sensor_id=f"sensor_{i}",
                timestamp=base_time + timedelta(seconds=i),
                state="on",
            )
            for i in range(5)
        ],
        start_time=base_time,
        confidence=0.9,
    )
    
    result = detector.detect_direction(sequence)
    
    assert result.confidence > 0.6


def test_confidence_with_erratic_pattern():
    """Test that erratic patterns have lower confidence."""
    sensors = [
        SensorNode(entity_id="sensor_1", x=0.0, y=0.0, range_meters=3.0),
        SensorNode(entity_id="sensor_2", x=10.0, y=10.0, range_meters=3.0),
        SensorNode(entity_id="sensor_3", x=2.0, y=15.0, range_meters=3.0),
    ]
    
    floorplan = Floorplan(
        floorplan_id="test",
        width=20.0,
        height=20.0,
        sensors=sensors,
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    base_time = datetime.now()
    sequence = MotionSequence(
        events=[
            MotionEvent(sensor_id="sensor_1", timestamp=base_time, state="on"),
            MotionEvent(sensor_id="sensor_2", timestamp=base_time + timedelta(seconds=1), state="on"),
            MotionEvent(sensor_id="sensor_3", timestamp=base_time + timedelta(seconds=2), state="on"),
        ],
        start_time=base_time,
        confidence=0.5,
    )
    
    result = detector.detect_direction(sequence)
    
    # Erratic pattern should have lower confidence
    assert result.confidence < 0.8


# ===== Contributing Sensors Tests =====


def test_contributing_sensors_list(
    motion_detector: MotionDetector,
    sample_motion_sequence: list[MotionEvent],
):
    """Test that contributing sensors are tracked."""
    sequence = MotionSequence(
        events=sample_motion_sequence,
        start_time=sample_motion_sequence[0].timestamp,
        confidence=0.8,
    )
    
    result = motion_detector.detect_direction(sequence)
    
    assert len(result.contributing_sensors) > 0
    assert all(isinstance(s, str) for s in result.contributing_sensors)


def test_contributing_sensors_match_sequence(
    motion_detector: MotionDetector,
    sample_motion_sequence: list[MotionEvent],
):
    """Test that contributing sensors match sequence events."""
    sequence = MotionSequence(
        events=sample_motion_sequence,
        start_time=sample_motion_sequence[0].timestamp,
        confidence=0.8,
    )
    
    result = motion_detector.detect_direction(sequence)
    
    sequence_sensor_ids = {e.sensor_id for e in sample_motion_sequence}
    contributing_sensor_ids = set(result.contributing_sensors)
    
    # All contributing sensors should be from the sequence
    assert contributing_sensor_ids.issubset(sequence_sensor_ids)


# ===== Method Detection Tests =====


def test_detection_method(
    motion_detector: MotionDetector,
    sample_motion_sequence: list[MotionEvent],
):
    """Test that detection method is set correctly."""
    sequence = MotionSequence(
        events=sample_motion_sequence,
        start_time=sample_motion_sequence[0].timestamp,
        confidence=0.8,
    )
    
    result = motion_detector.detect_direction(sequence)
    
    assert result.method in ["vector", "zone", "hybrid", "cue"]


# ===== Edge Cases =====


def test_simultaneous_sensors():
    """Test detection with simultaneous sensor activations."""
    sensors = [
        SensorNode(entity_id="sensor_1", x=0.0, y=0.0, range_meters=3.0),
        SensorNode(entity_id="sensor_2", x=5.0, y=0.0, range_meters=3.0),
        SensorNode(entity_id="sensor_3", x=10.0, y=0.0, range_meters=3.0),
    ]
    
    floorplan = Floorplan(
        floorplan_id="test",
        width=15.0,
        height=5.0,
        sensors=sensors,
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    timestamp = datetime.now()
    sequence = MotionSequence(
        events=[
            MotionEvent(sensor_id="sensor_1", timestamp=timestamp, state="on"),
            MotionEvent(sensor_id="sensor_2", timestamp=timestamp, state="on"),
            MotionEvent(sensor_id="sensor_3", timestamp=timestamp, state="on"),
        ],
        start_time=timestamp,
        confidence=0.5,
    )
    
    result = detector.detect_direction(sequence)
    
    # Simultaneous activations should have low confidence
    assert result.confidence < 0.7


def test_reverse_order_sensors():
    """Test detection with sensors triggered in reverse order."""
    sensors = [
        SensorNode(entity_id="sensor_1", x=0.0, y=0.0, range_meters=3.0),
        SensorNode(entity_id="sensor_2", x=5.0, y=0.0, range_meters=3.0),
        SensorNode(entity_id="sensor_3", x=10.0, y=0.0, range_meters=3.0),
    ]
    
    floorplan = Floorplan(
        floorplan_id="test",
        width=15.0,
        height=5.0,
        sensors=sensors,
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    base_time = datetime.now()
    sequence = MotionSequence(
        events=[
            MotionEvent(sensor_id="sensor_3", timestamp=base_time, state="on"),
            MotionEvent(sensor_id="sensor_2", timestamp=base_time + timedelta(seconds=1), state="on"),
            MotionEvent(sensor_id="sensor_1", timestamp=base_time + timedelta(seconds=2), state="on"),
        ],
        start_time=base_time,
        confidence=0.8,
    )
    
    result = detector.detect_direction(sequence)
    
    # Should detect westward movement
    assert result.direction == "west"


def test_unknown_sensor():
    """Test handling of events from unknown sensors."""
    floorplan = Floorplan(
        floorplan_id="test",
        width=10.0,
        height=10.0,
        sensors=[
            SensorNode(entity_id="sensor_1", x=5.0, y=5.0, range_meters=3.0)
        ],
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    sequence = MotionSequence(
        events=[
            MotionEvent(sensor_id="unknown_sensor", timestamp=datetime.now(), state="on"),
        ],
        start_time=datetime.now(),
        confidence=0.5,
    )
    
    result = detector.detect_direction(sequence)
    
    # Should handle gracefully with low confidence
    assert result.confidence < 0.5
