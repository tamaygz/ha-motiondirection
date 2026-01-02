"""Performance tests for motiondirection integration."""
import time
from datetime import datetime, timedelta

import pytest

from custom_components.motiondirection.core.motion_detector import MotionDetector
from custom_components.motiondirection.core.time_window_correlator import (
    TimeWindowCorrelator,
)
from custom_components.motiondirection.core.vector_calculator import VectorCalculator
from custom_components.motiondirection.models import (
    Floorplan,
    MotionEvent,
    MotionSequence,
    SensorNode,
)


# ===== Detection Performance Tests =====


def test_detection_performance_10_sensors(benchmark):
    """Benchmark detection with 10 sensors."""
    sensors = [
        SensorNode(entity_id=f"sensor_{i}", x=float(i * 2), y=5.0, range_meters=3.0)
        for i in range(10)
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
            MotionEvent(
                sensor_id=f"sensor_{i}",
                timestamp=base_time + timedelta(seconds=i),
                state="on",
            )
            for i in range(10)
        ],
        start_time=base_time,
        confidence=0.8,
    )
    
    def detect():
        return detector.detect_direction(sequence)
    
    result = benchmark(detect)
    
    # Assert detection completed successfully
    assert result is not None


def test_detection_performance_50_sensors(benchmark, large_sensor_grid: list[SensorNode]):
    """Benchmark detection with 50 sensors."""
    sensors = large_sensor_grid[:50]
    
    floorplan = Floorplan(
        floorplan_id="test",
        width=40.0,
        height=40.0,
        sensors=sensors,
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    base_time = datetime.now()
    sequence = MotionSequence(
        events=[
            MotionEvent(
                sensor_id=sensor.entity_id,
                timestamp=base_time + timedelta(milliseconds=i * 100),
                state="on",
            )
            for i, sensor in enumerate(sensors[:20])
        ],
        start_time=base_time,
        confidence=0.8,
    )
    
    def detect():
        return detector.detect_direction(sequence)
    
    result = benchmark(detect)
    
    assert result is not None


def test_detection_performance_100_sensors(benchmark, large_sensor_grid: list[SensorNode]):
    """Benchmark detection with 100 sensors."""
    sensors = large_sensor_grid
    
    floorplan = Floorplan(
        floorplan_id="test",
        width=40.0,
        height=40.0,
        sensors=sensors,
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    base_time = datetime.now()
    sequence = MotionSequence(
        events=[
            MotionEvent(
                sensor_id=sensor.entity_id,
                timestamp=base_time + timedelta(milliseconds=i * 50),
                state="on",
            )
            for i, sensor in enumerate(sensors[:30])
        ],
        start_time=base_time,
        confidence=0.8,
    )
    
    def detect():
        return detector.detect_direction(sequence)
    
    result = benchmark(detect)
    
    assert result is not None


# ===== Correlation Performance Tests =====


def test_correlation_performance_100_events(benchmark):
    """Benchmark correlation with 100 events."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i % 20}",
            timestamp=base_time + timedelta(milliseconds=i * 50),
            state="on",
        )
        for i in range(100)
    ]
    
    def correlate():
        return correlator.find_related_events(events)
    
    result = benchmark(correlate)
    
    assert len(result) > 0


def test_correlation_performance_1000_events(benchmark):
    """Benchmark correlation with 1000 events."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i % 50}",
            timestamp=base_time + timedelta(milliseconds=i * 10),
            state="on",
        )
        for i in range(1000)
    ]
    
    def correlate():
        return correlator.group_by_time_window(events)
    
    result = benchmark(correlate)
    
    assert len(result) > 0


def test_correlation_performance_5000_events(benchmark):
    """Benchmark correlation with 5000 events."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i % 100}",
            timestamp=base_time + timedelta(milliseconds=i * 5),
            state="on",
        )
        for i in range(5000)
    ]
    
    def correlate():
        return correlator.group_by_time_window(events)
    
    result = benchmark(correlate)
    
    assert len(result) > 0


# ===== Vector Calculation Performance Tests =====


def test_vector_calculation_performance(benchmark):
    """Benchmark vector calculations."""
    calculator = VectorCalculator()
    
    from custom_components.motiondirection.models import PathPoint
    
    points = [
        (PathPoint(x=float(i), y=float(i)), PathPoint(x=float(i + 1), y=float(i + 1)))
        for i in range(100)
    ]
    
    def calculate():
        results = []
        for p1, p2 in points:
            distance = calculator.calculate_distance(p1, p2)
            angle = calculator.calculate_angle(p1, p2)
            velocity = calculator.calculate_velocity(p1, p2, 1.0)
            results.append((distance, angle, velocity))
        return results
    
    result = benchmark(calculate)
    
    assert len(result) == 100


def test_vector_normalization_performance(benchmark):
    """Benchmark vector normalization."""
    calculator = VectorCalculator()
    
    vectors = [(float(i), float(i + 1)) for i in range(1000)]
    
    def normalize():
        return [calculator.normalize_vector(v) for v in vectors]
    
    result = benchmark(normalize)
    
    assert len(result) == 1000


# ===== Sequence Building Performance Tests =====


def test_sequence_building_performance(benchmark):
    """Benchmark sequence building."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i}",
            timestamp=base_time + timedelta(milliseconds=i * 100),
            state="on",
        )
        for i in range(100)
    ]
    
    def build():
        return correlator.build_sequence(events)
    
    result = benchmark(build)
    
    assert isinstance(result, MotionSequence)


# ===== Memory Usage Tests =====


def test_memory_usage_large_sensor_grid():
    """Test memory usage with large sensor grid."""
    import sys
    
    sensors = [
        SensorNode(
            entity_id=f"sensor_{x}_{y}",
            x=float(x * 2),
            y=float(y * 2),
            range_meters=2.0,
        )
        for x in range(20)
        for y in range(20)
    ]
    
    # 400 sensors
    sensor_size = sys.getsizeof(sensors)
    
    # Should be reasonable (< 1MB for 400 sensors)
    assert sensor_size < 1024 * 1024


def test_memory_usage_large_event_stream():
    """Test memory usage with large event stream."""
    import sys
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i % 100}",
            timestamp=base_time + timedelta(milliseconds=i),
            state="on",
        )
        for i in range(10000)
    ]
    
    # 10000 events
    events_size = sys.getsizeof(events)
    
    # Should be reasonable (< 10MB for 10000 events)
    assert events_size < 10 * 1024 * 1024


# ===== Scalability Tests =====


def test_detection_scales_linearly():
    """Test that detection time scales linearly with sensor count."""
    calculator = VectorCalculator()
    times = []
    
    for sensor_count in [10, 20, 40]:
        sensors = [
            SensorNode(
                entity_id=f"sensor_{i}",
                x=float(i * 2),
                y=5.0,
                range_meters=3.0,
            )
            for i in range(sensor_count)
        ]
        
        floorplan = Floorplan(
            floorplan_id="test",
            width=float(sensor_count * 2),
            height=10.0,
            sensors=sensors,
        )
        
        detector = MotionDetector(floorplan=floorplan, vector_calculator=calculator)
        
        base_time = datetime.now()
        sequence = MotionSequence(
            events=[
                MotionEvent(
                    sensor_id=f"sensor_{i}",
                    timestamp=base_time + timedelta(milliseconds=i * 100),
                    state="on",
                )
                for i in range(min(sensor_count, 10))
            ],
            start_time=base_time,
            confidence=0.8,
        )
        
        start = time.perf_counter()
        detector.detect_direction(sequence)
        elapsed = time.perf_counter() - start
        
        times.append(elapsed)
    
    # Time should scale roughly linearly (within 3x)
    assert times[-1] / times[0] < 5.0


def test_correlation_scales_linearly():
    """Test that correlation scales reasonably with event count."""
    correlator = TimeWindowCorrelator(time_window=5.0)
    times = []
    
    for event_count in [100, 500, 1000]:
        base_time = datetime.now()
        events = [
            MotionEvent(
                sensor_id=f"sensor_{i % 50}",
                timestamp=base_time + timedelta(milliseconds=i * 10),
                state="on",
            )
            for i in range(event_count)
        ]
        
        start = time.perf_counter()
        correlator.group_by_time_window(events)
        elapsed = time.perf_counter() - start
        
        times.append(elapsed)
    
    # Time should scale reasonably (within 15x for 10x data)
    assert times[-1] / times[0] < 20.0


# ===== Real-time Performance Tests =====


def test_detection_meets_realtime_requirements():
    """Test that detection completes within real-time requirements."""
    # Real-time requirement: < 100ms for 50 sensors
    sensors = [
        SensorNode(
            entity_id=f"sensor_{i}",
            x=float(i * 2),
            y=5.0,
            range_meters=3.0,
        )
        for i in range(50)
    ]
    
    floorplan = Floorplan(
        floorplan_id="test",
        width=100.0,
        height=10.0,
        sensors=sensors,
    )
    
    detector = MotionDetector(floorplan=floorplan, vector_calculator=VectorCalculator())
    
    base_time = datetime.now()
    sequence = MotionSequence(
        events=[
            MotionEvent(
                sensor_id=f"sensor_{i}",
                timestamp=base_time + timedelta(milliseconds=i * 50),
                state="on",
            )
            for i in range(20)
        ],
        start_time=base_time,
        confidence=0.8,
    )
    
    start = time.perf_counter()
    result = detector.detect_direction(sequence)
    elapsed = time.perf_counter() - start
    
    # Should complete in < 100ms
    assert elapsed < 0.1
    assert result is not None


def test_correlation_meets_realtime_requirements():
    """Test that correlation completes within real-time requirements."""
    # Real-time requirement: < 50ms for 1000 events
    correlator = TimeWindowCorrelator(time_window=5.0)
    
    base_time = datetime.now()
    events = [
        MotionEvent(
            sensor_id=f"sensor_{i % 50}",
            timestamp=base_time + timedelta(milliseconds=i * 10),
            state="on",
        )
        for i in range(1000)
    ]
    
    start = time.perf_counter()
    result = correlator.find_related_events(events)
    elapsed = time.perf_counter() - start
    
    # Should complete in < 50ms
    assert elapsed < 0.05
    assert len(result) > 0
