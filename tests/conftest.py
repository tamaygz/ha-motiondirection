"""Shared pytest fixtures for motiondirection tests."""
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.motiondirection.const import DOMAIN
from custom_components.motiondirection.models import (
    DirectionConfig,
    Floorplan,
    MotionEvent,
    PathPoint,
    SecondaryCue,
    SensorNode,
    TriggerZone,
)


# ===== Sensor Fixtures =====


@pytest.fixture
def sample_sensor() -> SensorNode:
    """Create a sample sensor node."""
    return SensorNode(
        entity_id="binary_sensor.living_room_motion",
        x=5.0,
        y=5.0,
        range_meters=3.0,
    )


@pytest.fixture
def sample_sensors() -> list[SensorNode]:
    """Create a list of sample sensor nodes."""
    return [
        SensorNode(
            entity_id="binary_sensor.living_room_motion",
            x=5.0,
            y=5.0,
            range_meters=3.0,
        ),
        SensorNode(
            entity_id="binary_sensor.kitchen_motion",
            x=10.0,
            y=5.0,
            range_meters=3.0,
        ),
        SensorNode(
            entity_id="binary_sensor.hallway_motion",
            x=15.0,
            y=5.0,
            range_meters=3.0,
        ),
    ]


@pytest.fixture
def large_sensor_grid() -> list[SensorNode]:
    """Create a large grid of sensors for performance testing."""
    sensors = []
    for x in range(10):
        for y in range(10):
            sensors.append(
                SensorNode(
                    entity_id=f"binary_sensor.grid_{x}_{y}",
                    x=float(x * 2),
                    y=float(y * 2),
                    range_meters=2.0,
                )
            )
    return sensors


# ===== Motion Event Fixtures =====


@pytest.fixture
def sample_motion_event(sample_sensor: SensorNode) -> MotionEvent:
    """Create a sample motion event."""
    return MotionEvent(
        sensor_id=sample_sensor.entity_id,
        timestamp=datetime.now(),
        state="on",
    )


@pytest.fixture
def sample_motion_sequence(sample_sensors: list[SensorNode]) -> list[MotionEvent]:
    """Create a sequence of motion events."""
    base_time = datetime.now()
    return [
        MotionEvent(
            sensor_id=sample_sensors[0].entity_id,
            timestamp=base_time,
            state="on",
        ),
        MotionEvent(
            sensor_id=sample_sensors[1].entity_id,
            timestamp=base_time + timedelta(seconds=1),
            state="on",
        ),
        MotionEvent(
            sensor_id=sample_sensors[2].entity_id,
            timestamp=base_time + timedelta(seconds=2),
            state="on",
        ),
    ]


@pytest.fixture
def large_event_stream() -> list[MotionEvent]:
    """Create a large stream of motion events for performance testing."""
    base_time = datetime.now()
    events = []
    for i in range(1000):
        events.append(
            MotionEvent(
                sensor_id=f"binary_sensor.sensor_{i % 50}",
                timestamp=base_time + timedelta(milliseconds=i * 100),
                state="on",
            )
        )
    return events


# ===== Floorplan Fixtures =====


@pytest.fixture
def sample_floorplan(sample_sensors: list[SensorNode]) -> Floorplan:
    """Create a sample floorplan with sensors."""
    return Floorplan(
        floorplan_id="main",
        width=20.0,
        height=10.0,
        sensors=sample_sensors,
    )


@pytest.fixture
def empty_floorplan() -> Floorplan:
    """Create an empty floorplan."""
    return Floorplan(
        floorplan_id="empty",
        width=10.0,
        height=10.0,
        sensors=[],
    )


# ===== Trigger Zone Fixtures =====


@pytest.fixture
def sample_trigger_zone() -> TriggerZone:
    """Create a sample trigger zone."""
    return TriggerZone(
        zone_id="living_room",
        polygon=[
            PathPoint(x=0.0, y=0.0),
            PathPoint(x=10.0, y=0.0),
            PathPoint(x=10.0, y=10.0),
            PathPoint(x=0.0, y=10.0),
        ],
        directions=[
            DirectionConfig(
                name="to_kitchen",
                vector=(1.0, 0.0),
                entry_side="right",
                confidence_threshold=0.7,
            )
        ],
    )


@pytest.fixture
def sample_trigger_zones() -> list[TriggerZone]:
    """Create multiple trigger zones."""
    return [
        TriggerZone(
            zone_id="living_room",
            polygon=[
                PathPoint(x=0.0, y=0.0),
                PathPoint(x=10.0, y=0.0),
                PathPoint(x=10.0, y=10.0),
                PathPoint(x=0.0, y=10.0),
            ],
            directions=[
                DirectionConfig(
                    name="to_kitchen",
                    vector=(1.0, 0.0),
                    entry_side="right",
                    confidence_threshold=0.7,
                )
            ],
        ),
        TriggerZone(
            zone_id="kitchen",
            polygon=[
                PathPoint(x=10.0, y=0.0),
                PathPoint(x=20.0, y=0.0),
                PathPoint(x=20.0, y=10.0),
                PathPoint(x=10.0, y=10.0),
            ],
            directions=[
                DirectionConfig(
                    name="to_living_room",
                    vector=(-1.0, 0.0),
                    entry_side="left",
                    confidence_threshold=0.7,
                )
            ],
        ),
    ]


# ===== Secondary Cue Fixtures =====


@pytest.fixture
def sample_cue() -> SecondaryCue:
    """Create a sample secondary cue."""
    return SecondaryCue(
        cue_id="door_open",
        entity_id="binary_sensor.front_door",
        cue_type="door",
        location=PathPoint(x=5.0, y=0.0),
        confidence_boost=0.15,
    )


@pytest.fixture
def sample_cues() -> list[SecondaryCue]:
    """Create multiple secondary cues."""
    return [
        SecondaryCue(
            cue_id="door_open",
            entity_id="binary_sensor.front_door",
            cue_type="door",
            location=PathPoint(x=5.0, y=0.0),
            confidence_boost=0.15,
        ),
        SecondaryCue(
            cue_id="light_on",
            entity_id="light.living_room",
            cue_type="light",
            location=PathPoint(x=5.0, y=5.0),
            confidence_boost=0.10,
        ),
    ]


# ===== Config Entry Fixtures =====


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Motion Direction Tracker",
            "update_interval": 5,
        },
        options={
            "confidence_threshold": 0.7,
            "time_window": 5,
        },
        entry_id="test_entry_id",
        unique_id="test_unique_id",
    )


# ===== Hass Mock Fixtures =====


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock()
    hass.data = {}
    hass.states = Mock()
    hass.services = Mock()
    hass.config_entries = Mock()
    hass.bus = Mock()
    
    # Mock async methods
    hass.async_block_till_done = AsyncMock()
    hass.async_create_task = Mock(side_effect=lambda coro: coro)
    
    return hass


# ===== Helper Functions =====


def create_motion_event_at_time(
    sensor_id: str,
    timestamp: datetime,
    state: str = "on",
) -> MotionEvent:
    """Helper to create a motion event at a specific time."""
    return MotionEvent(
        sensor_id=sensor_id,
        timestamp=timestamp,
        state=state,
    )


def create_sensor_at_position(
    entity_id: str,
    x: float,
    y: float,
    range_meters: float = 3.0,
) -> SensorNode:
    """Helper to create a sensor at a specific position."""
    return SensorNode(
        entity_id=entity_id,
        x=x,
        y=y,
        range_meters=range_meters,
    )


# ===== Pytest Configuration =====


pytest_plugins = "pytest_homeassistant_custom_component"


# ===== Async Test Utilities =====


@pytest.fixture
def assert_setup_component():
    """Fixture to assert component setup."""
    async def _assert_setup(hass, component_name: str) -> bool:
        """Assert that a component is set up."""
        return component_name in hass.data
    
    return _assert_setup
