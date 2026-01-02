"""Unit tests for time window correlator."""
from datetime import datetime, timedelta

import pytest

from custom_components.motiondirection.core.time_window_correlator import (
    TimeWindowCorrelator,
)
from custom_components.motiondirection.models import MotionEvent, MotionSequence


# ===== Basic Correlation Tests =====


def test_find_related_events_within_window(sample_motion_sequence: list[MotionEvent]):
    """Test finding related events within time window."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    # All events are within 2 seconds, should be related
    related = correlator.find_related_events(sample_motion_sequence)
    
    assert len(related) == 3
    assert all(event in sample_motion_sequence for event in related)


def test_find_related_events_outside_window():
    """Test that events outside window are not related."""
    correlator = TimeWindowCorrelator(time_window=1.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_2",
            timestamp=base_time + timedelta(seconds=5),  # Outside 1s window
            state="on",
        ),
    ]
    
    related = correlator.find_related_events(events)
    # Should only include events within the window from the first event
    assert len(related) <= 1


def test_find_related_events_empty():
    """Test finding related events with empty list."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    related = correlator.find_related_events([])
    assert len(related) == 0


def test_find_related_events_single():
    """Test finding related events with single event."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    event = MotionEvent(
        sensor_id="sensor_1",
        timestamp=datetime.now(),
        state="on",
    )
    
    related = correlator.find_related_events([event])
    assert len(related) == 1
    assert related[0] == event


# ===== Sequence Building Tests =====


def test_build_sequence_basic(sample_motion_sequence: list[MotionEvent]):
    """Test building a basic motion sequence."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    sequence = correlator.build_sequence(sample_motion_sequence)
    
    assert isinstance(sequence, MotionSequence)
    assert len(sequence.events) == 3
    assert sequence.start_time == sample_motion_sequence[0].timestamp


def test_build_sequence_empty():
    """Test building sequence from empty events."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    sequence = correlator.build_sequence([])
    
    assert isinstance(sequence, MotionSequence)
    assert len(sequence.events) == 0


def test_build_sequence_chronological_order():
    """Test that sequence events are in chronological order."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id="sensor_3",
            timestamp=base_time + timedelta(seconds=2),
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_2",
            timestamp=base_time + timedelta(seconds=1),
            state="on",
        ),
    ]
    
    sequence = correlator.build_sequence(events)
    
    # Should be sorted by timestamp
    for i in range(len(sequence.events) - 1):
        assert sequence.events[i].timestamp <= sequence.events[i + 1].timestamp


def test_build_sequence_confidence():
    """Test sequence confidence calculation."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_2",
            timestamp=base_time + timedelta(milliseconds=100),
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_3",
            timestamp=base_time + timedelta(milliseconds=200),
            state="on",
        ),
    ]
    
    sequence = correlator.build_sequence(events)
    
    # Tight timing should give high confidence
    assert sequence.confidence > 0.5


# ===== Time Window Tests =====


def test_time_window_adjustment():
    """Test adjusting time window."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    assert correlator.time_window == 5.0
    
    correlator.time_window = 10.0
    assert correlator.time_window == 10.0


def test_time_window_filtering():
    """Test that time window correctly filters events."""
    correlator = TimeWindowCorrelator(time_window=2.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_2",
            timestamp=base_time + timedelta(seconds=1),
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_3",
            timestamp=base_time + timedelta(seconds=3),  # Outside window
            state="on",
        ),
    ]
    
    related = correlator.find_related_events(events)
    
    # Third event should be filtered out
    assert len(related) == 2
    assert events[2] not in related


# ===== Event Grouping Tests =====


def test_group_by_time_window(large_event_stream: list[MotionEvent]):
    """Test grouping large event stream by time windows."""
    correlator = TimeWindowCorrelator(time_window=1.0)
    
    # Group events into time-based sequences
    groups = correlator.group_by_time_window(large_event_stream)
    
    assert len(groups) > 0
    
    # Verify each group respects the time window
    for group in groups:
        if len(group) > 1:
            time_span = (group[-1].timestamp - group[0].timestamp).total_seconds()
            assert time_span <= correlator.time_window


def test_group_by_time_window_single_group():
    """Test grouping when all events fit in one window."""
    correlator = TimeWindowCorrelator(time_window=10.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i}",
            timestamp=base_time + timedelta(seconds=i),
            state="on",
        )
        for i in range(5)
    ]
    
    groups = correlator.group_by_time_window(events)
    
    assert len(groups) == 1
    assert len(groups[0]) == 5


def test_group_by_time_window_multiple_groups():
    """Test grouping when events span multiple windows."""
    correlator = TimeWindowCorrelator(time_window=1.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_2",
            timestamp=base_time + timedelta(seconds=3),  # New group
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_3",
            timestamp=base_time + timedelta(seconds=6),  # Another new group
            state="on",
        ),
    ]
    
    groups = correlator.group_by_time_window(events)
    
    assert len(groups) == 3


# ===== Sensor Filtering Tests =====


def test_filter_duplicate_sensors():
    """Test filtering duplicate sensor activations."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_1",  # Duplicate
            timestamp=base_time + timedelta(milliseconds=100),
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_2",
            timestamp=base_time + timedelta(milliseconds=200),
            state="on",
        ),
    ]
    
    filtered = correlator.filter_duplicate_sensors(events)
    
    # Should keep only first occurrence of each sensor
    assert len(filtered) == 2
    sensor_ids = [e.sensor_id for e in filtered]
    assert sensor_ids == ["sensor_1", "sensor_2"]


def test_filter_duplicate_sensors_preserve_order():
    """Test that filtering preserves chronological order."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id="sensor_2",
            timestamp=base_time + timedelta(seconds=2),
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_2",  # Duplicate, but later
            timestamp=base_time + timedelta(seconds=3),
            state="on",
        ),
    ]
    
    filtered = correlator.filter_duplicate_sensors(events, keep="first")
    
    # Should keep events in original order
    assert len(filtered) == 2
    assert filtered[0].sensor_id == "sensor_2"
    assert filtered[1].sensor_id == "sensor_1"


# ===== Confidence Calculation Tests =====


def test_calculate_sequence_confidence_tight_timing():
    """Test confidence calculation for tightly timed sequence."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i}",
            timestamp=base_time + timedelta(milliseconds=i * 100),
            state="on",
        )
        for i in range(5)
    ]
    
    confidence = correlator.calculate_sequence_confidence(events)
    
    # Tight timing (100ms intervals) should give high confidence
    assert confidence > 0.7


def test_calculate_sequence_confidence_loose_timing():
    """Test confidence calculation for loosely timed sequence."""
    correlator = TimeWindowCorrelator(time_window=10.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i}",
            timestamp=base_time + timedelta(seconds=i * 3),
            state="on",
        )
        for i in range(3)
    ]
    
    confidence = correlator.calculate_sequence_confidence(events)
    
    # Loose timing (3s intervals) should give lower confidence
    assert confidence < 0.7


def test_calculate_sequence_confidence_single_event():
    """Test confidence calculation for single event."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    event = [
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=datetime.now(),
            state="on",
        )
    ]
    
    confidence = correlator.calculate_sequence_confidence(event)
    
    # Single event should have low confidence
    assert confidence < 0.5


# ===== Edge Cases =====


def test_events_at_exact_window_boundary():
    """Test events at exact time window boundary."""
    correlator = TimeWindowCorrelator(time_window=1.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id="sensor_1",
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id="sensor_2",
            timestamp=base_time + timedelta(seconds=1.0),  # Exactly at boundary
            state="on",
        ),
    ]
    
    related = correlator.find_related_events(events)
    
    # Events at boundary should be included
    assert len(related) == 2


def test_simultaneous_events():
    """Test handling of simultaneous events."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    timestamp = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i}",
            timestamp=timestamp,  # Same timestamp
            state="on",
        )
        for i in range(3)
    ]
    
    sequence = correlator.build_sequence(events)
    
    assert len(sequence.events) == 3
    assert all(e.timestamp == timestamp for e in sequence.events)
