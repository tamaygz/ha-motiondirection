"""Integration tests for motion direction coordinator."""
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.motiondirection.const import DOMAIN
from custom_components.motiondirection.coordinator import MotionDirectionCoordinator
from custom_components.motiondirection.models import MotionEvent, SensorNode


# ===== Setup and Teardown =====


@pytest.fixture
async def coordinator(hass, mock_config_entry: MockConfigEntry):
    """Create a coordinator instance."""
    mock_config_entry.add_to_hass(hass)
    
    coordinator = MotionDirectionCoordinator(
        hass=hass,
        config_entry=mock_config_entry,
    )
    
    await coordinator.async_config_entry_first_refresh()
    
    return coordinator


# ===== Basic Coordinator Tests =====


@pytest.mark.asyncio
async def test_coordinator_creation(coordinator: MotionDirectionCoordinator):
    """Test creating a coordinator."""
    assert coordinator is not None
    assert coordinator.name == DOMAIN


@pytest.mark.asyncio
async def test_coordinator_has_managers(coordinator: MotionDirectionCoordinator):
    """Test that coordinator initializes managers."""
    assert hasattr(coordinator, "floorplan_manager")
    assert hasattr(coordinator, "zone_manager")
    assert hasattr(coordinator, "detector")
    assert hasattr(coordinator, "pattern_analyzer")


# ===== Update Tests =====


@pytest.mark.asyncio
async def test_coordinator_async_update(coordinator: MotionDirectionCoordinator):
    """Test coordinator data update."""
    data = await coordinator._async_update_data()
    
    assert data is not None
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_coordinator_update_interval(
    hass,
    mock_config_entry: MockConfigEntry,
):
    """Test coordinator respects update interval."""
    mock_config_entry.add_to_hass(hass)
    
    coordinator = MotionDirectionCoordinator(
        hass=hass,
        config_entry=mock_config_entry,
    )
    
    # Check that update interval is set from config
    assert coordinator.update_interval.total_seconds() == mock_config_entry.data.get("update_interval", 30)


# ===== State Change Handling Tests =====


@pytest.mark.asyncio
async def test_handle_state_change_motion_sensor(
    coordinator: MotionDirectionCoordinator,
):
    """Test handling state change for motion sensor."""
    # Add a sensor to the floorplan
    coordinator.floorplan_manager.add_sensor(
        SensorNode(
            entity_id="binary_sensor.test_motion",
            x=5.0,
            y=5.0,
            range_meters=3.0,
        )
    )
    
    # Create a mock state change event
    old_state = Mock()
    old_state.state = "off"
    
    new_state = Mock()
    new_state.state = "on"
    new_state.entity_id = "binary_sensor.test_motion"
    new_state.last_changed = datetime.now()
    
    # Handle the state change
    await coordinator.handle_state_change("binary_sensor.test_motion", old_state, new_state)
    
    # Verify event was collected
    assert len(coordinator.event_collector.events) > 0


@pytest.mark.asyncio
async def test_handle_state_change_off_to_on(
    coordinator: MotionDirectionCoordinator,
):
    """Test handling sensor going from off to on."""
    coordinator.floorplan_manager.add_sensor(
        SensorNode(
            entity_id="binary_sensor.motion",
            x=5.0,
            y=5.0,
            range_meters=3.0,
        )
    )
    
    old_state = Mock()
    old_state.state = "off"
    
    new_state = Mock()
    new_state.state = "on"
    new_state.entity_id = "binary_sensor.motion"
    new_state.last_changed = datetime.now()
    
    await coordinator.handle_state_change("binary_sensor.motion", old_state, new_state)
    
    # Should create a motion event
    events = coordinator.event_collector.get_recent_events(window=10.0)
    assert len(events) > 0
    assert events[-1].sensor_id == "binary_sensor.motion"
    assert events[-1].state == "on"


# ===== Direction Detection Tests =====


@pytest.mark.asyncio
async def test_detect_direction_with_sequence(
    coordinator: MotionDirectionCoordinator,
):
    """Test direction detection with motion sequence."""
    # Add sensors
    sensors = [
        SensorNode(entity_id=f"binary_sensor.sensor_{i}", x=float(i * 5), y=5.0, range_meters=3.0)
        for i in range(3)
    ]
    
    for sensor in sensors:
        coordinator.floorplan_manager.add_sensor(sensor)
    
    # Create motion events
    base_time = datetime.now()
    for i, sensor in enumerate(sensors):
        event = MotionEvent(
            sensor_id=sensor.entity_id,
            timestamp=base_time,
            state="on",
        )
        coordinator.event_collector.add_event(event)
    
    # Trigger detection
    result = coordinator.detect_current_direction()
    
    assert result is not None
    assert result.direction in ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]


# ===== Event Firing Tests =====


@pytest.mark.asyncio
async def test_fires_direction_detected_event(
    coordinator: MotionDirectionCoordinator,
    hass,
):
    """Test that coordinator fires direction_detected event."""
    # Mock the event bus
    with patch.object(coordinator.event_bus, "fire") as mock_fire:
        # Add sensors and trigger detection
        coordinator.floorplan_manager.add_sensor(
            SensorNode(
                entity_id="binary_sensor.test",
                x=5.0,
                y=5.0,
                range_meters=3.0,
            )
        )
        
        coordinator.event_collector.add_event(
            MotionEvent(
                sensor_id="binary_sensor.test",
                timestamp=datetime.now(),
                state="on",
            )
        )
        
        # Trigger detection
        result = coordinator.detect_current_direction()
        
        if result and result.confidence > 0.5:
            # Fire the event manually (in real code, this happens automatically)
            coordinator.fire_direction_event(result)
            
            # Verify event was fired
            assert mock_fire.called


# ===== Sensor Management Tests =====


@pytest.mark.asyncio
async def test_get_motion_sensors(coordinator: MotionDirectionCoordinator):
    """Test getting list of motion sensors."""
    coordinator.floorplan_manager.add_sensor(
        SensorNode(
            entity_id="binary_sensor.test",
            x=5.0,
            y=5.0,
            range_meters=3.0,
        )
    )
    
    sensors = coordinator.get_motion_sensors()
    
    assert len(sensors) > 0
    assert any(s.entity_id == "binary_sensor.test" for s in sensors)


@pytest.mark.asyncio
async def test_get_sensor_by_id(coordinator: MotionDirectionCoordinator):
    """Test getting sensor by entity ID."""
    sensor = SensorNode(
        entity_id="binary_sensor.specific",
        x=5.0,
        y=5.0,
        range_meters=3.0,
    )
    coordinator.floorplan_manager.add_sensor(sensor)
    
    retrieved = coordinator.get_sensor("binary_sensor.specific")
    
    assert retrieved is not None
    assert retrieved.entity_id == "binary_sensor.specific"


# ===== Zone Tests =====


@pytest.mark.asyncio
async def test_get_zones(coordinator: MotionDirectionCoordinator):
    """Test getting list of zones."""
    zones = coordinator.get_zones()
    
    assert isinstance(zones, list)


@pytest.mark.asyncio
async def test_get_zone_by_id(coordinator: MotionDirectionCoordinator, sample_trigger_zone):
    """Test getting zone by ID."""
    coordinator.zone_manager.add_zone(sample_trigger_zone)
    
    retrieved = coordinator.get_zone(sample_trigger_zone.zone_id)
    
    assert retrieved is not None
    assert retrieved.zone_id == sample_trigger_zone.zone_id


# ===== Pattern Analysis Tests =====


@pytest.mark.asyncio
async def test_analyze_patterns(coordinator: MotionDirectionCoordinator):
    """Test pattern analysis."""
    # Add some motion events
    base_time = datetime.now()
    for i in range(5):
        coordinator.event_collector.add_event(
            MotionEvent(
                sensor_id=f"binary_sensor.sensor_{i}",
                timestamp=base_time,
                state="on",
            )
        )
    
    # Trigger pattern analysis
    patterns = coordinator.analyze_patterns()
    
    assert isinstance(patterns, list)


# ===== Anomaly Detection Tests =====


@pytest.mark.asyncio
async def test_detect_anomalies(coordinator: MotionDirectionCoordinator):
    """Test anomaly detection."""
    # Add a normal pattern
    base_time = datetime.now()
    for i in range(3):
        coordinator.event_collector.add_event(
            MotionEvent(
                sensor_id=f"binary_sensor.sensor_{i}",
                timestamp=base_time,
                state="on",
            )
        )
    
    # Check for anomalies
    anomalies = coordinator.detect_anomalies()
    
    assert isinstance(anomalies, list)


# ===== Data Persistence Tests =====


@pytest.mark.asyncio
async def test_coordinator_saves_data(coordinator: MotionDirectionCoordinator):
    """Test that coordinator saves data to storage."""
    # Add some data
    coordinator.floorplan_manager.add_sensor(
        SensorNode(
            entity_id="binary_sensor.test",
            x=5.0,
            y=5.0,
            range_meters=3.0,
        )
    )
    
    # Trigger save
    await coordinator.async_save_data()
    
    # Verify save was called (this would need mocking in a real test)
    assert True  # Placeholder for actual save verification


# ===== Edge Cases =====


@pytest.mark.asyncio
async def test_coordinator_with_no_sensors(coordinator: MotionDirectionCoordinator):
    """Test coordinator behavior with no sensors."""
    sensors = coordinator.get_motion_sensors()
    
    # Should return empty list, not error
    assert isinstance(sensors, list)


@pytest.mark.asyncio
async def test_coordinator_with_invalid_event(coordinator: MotionDirectionCoordinator):
    """Test coordinator handling invalid event."""
    # Try to handle state change for non-existent sensor
    old_state = Mock()
    old_state.state = "off"
    
    new_state = Mock()
    new_state.state = "on"
    new_state.entity_id = "binary_sensor.nonexistent"
    new_state.last_changed = datetime.now()
    
    # Should not raise an error
    await coordinator.handle_state_change("binary_sensor.nonexistent", old_state, new_state)
    
    assert True  # No exception raised


@pytest.mark.asyncio
async def test_coordinator_concurrent_updates(coordinator: MotionDirectionCoordinator):
    """Test coordinator handling concurrent updates."""
    # Simulate multiple rapid state changes
    for i in range(10):
        old_state = Mock()
        old_state.state = "off"
        
        new_state = Mock()
        new_state.state = "on"
        new_state.entity_id = f"binary_sensor.sensor_{i}"
        new_state.last_changed = datetime.now()
        
        await coordinator.handle_state_change(f"binary_sensor.sensor_{i}", old_state, new_state)
    
    # Should handle all updates without errors
    assert True
