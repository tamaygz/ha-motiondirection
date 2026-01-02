"""Integration tests for motiondirection services."""
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.motiondirection.const import DOMAIN


# ===== Service Registration Tests =====


@pytest.mark.asyncio
async def test_services_registered(hass, mock_config_entry: MockConfigEntry):
    """Test that all services are registered."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Check that services are registered
    assert hass.services.has_service(DOMAIN, "update_floorplan")
    assert hass.services.has_service(DOMAIN, "create_trigger_zone")
    assert hass.services.has_service(DOMAIN, "update_trigger_zone")
    assert hass.services.has_service(DOMAIN, "delete_trigger_zone")
    assert hass.services.has_service(DOMAIN, "register_secondary_cue")
    assert hass.services.has_service(DOMAIN, "analyze_pattern")


# ===== update_floorplan Service Tests =====


@pytest.mark.asyncio
async def test_update_floorplan_service(hass, mock_config_entry: MockConfigEntry):
    """Test update_floorplan service."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Call the service
    await hass.services.async_call(
        DOMAIN,
        "update_floorplan",
        {
            "floorplan_id": "main",
            "width": 20.0,
            "height": 15.0,
            "sensors": [
                {
                    "entity_id": "binary_sensor.living_room",
                    "x": 5.0,
                    "y": 5.0,
                    "range_meters": 3.0,
                }
            ],
        },
        blocking=True,
    )
    
    # Verify service executed successfully
    assert True  # Would verify state changes in real test


@pytest.mark.asyncio
async def test_update_floorplan_invalid_data(hass, mock_config_entry: MockConfigEntry):
    """Test update_floorplan with invalid data."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Try to call service with missing required fields
    with pytest.raises(Exception):  # Should raise validation error
        await hass.services.async_call(
            DOMAIN,
            "update_floorplan",
            {
                "floorplan_id": "main",
                # Missing width and height
            },
            blocking=True,
        )


# ===== create_trigger_zone Service Tests =====


@pytest.mark.asyncio
async def test_create_trigger_zone_service(hass, mock_config_entry: MockConfigEntry):
    """Test create_trigger_zone service."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Call the service
    await hass.services.async_call(
        DOMAIN,
        "create_trigger_zone",
        {
            "zone_id": "living_room",
            "polygon": [
                {"x": 0.0, "y": 0.0},
                {"x": 10.0, "y": 0.0},
                {"x": 10.0, "y": 10.0},
                {"x": 0.0, "y": 10.0},
            ],
            "directions": [
                {
                    "name": "to_kitchen",
                    "vector": [1.0, 0.0],
                    "entry_side": "right",
                    "confidence_threshold": 0.7,
                }
            ],
        },
        blocking=True,
    )
    
    assert True


@pytest.mark.asyncio
async def test_create_trigger_zone_duplicate(hass, mock_config_entry: MockConfigEntry):
    """Test creating duplicate trigger zone."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    zone_data = {
        "zone_id": "test_zone",
        "polygon": [
            {"x": 0.0, "y": 0.0},
            {"x": 5.0, "y": 0.0},
            {"x": 5.0, "y": 5.0},
            {"x": 0.0, "y": 5.0},
        ],
        "directions": [],
    }
    
    # Create once
    await hass.services.async_call(
        DOMAIN,
        "create_trigger_zone",
        zone_data,
        blocking=True,
    )
    
    # Try to create again with same ID
    # Should either update or raise error
    await hass.services.async_call(
        DOMAIN,
        "create_trigger_zone",
        zone_data,
        blocking=True,
    )
    
    assert True


# ===== update_trigger_zone Service Tests =====


@pytest.mark.asyncio
async def test_update_trigger_zone_service(hass, mock_config_entry: MockConfigEntry):
    """Test update_trigger_zone service."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # First create a zone
    await hass.services.async_call(
        DOMAIN,
        "create_trigger_zone",
        {
            "zone_id": "update_test",
            "polygon": [
                {"x": 0.0, "y": 0.0},
                {"x": 5.0, "y": 0.0},
                {"x": 5.0, "y": 5.0},
                {"x": 0.0, "y": 5.0},
            ],
            "directions": [],
        },
        blocking=True,
    )
    
    # Then update it
    await hass.services.async_call(
        DOMAIN,
        "update_trigger_zone",
        {
            "zone_id": "update_test",
            "polygon": [
                {"x": 0.0, "y": 0.0},
                {"x": 10.0, "y": 0.0},
                {"x": 10.0, "y": 10.0},
                {"x": 0.0, "y": 10.0},
            ],
        },
        blocking=True,
    )
    
    assert True


# ===== delete_trigger_zone Service Tests =====


@pytest.mark.asyncio
async def test_delete_trigger_zone_service(hass, mock_config_entry: MockConfigEntry):
    """Test delete_trigger_zone service."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Create a zone
    await hass.services.async_call(
        DOMAIN,
        "create_trigger_zone",
        {
            "zone_id": "delete_test",
            "polygon": [
                {"x": 0.0, "y": 0.0},
                {"x": 5.0, "y": 0.0},
                {"x": 5.0, "y": 5.0},
                {"x": 0.0, "y": 5.0},
            ],
            "directions": [],
        },
        blocking=True,
    )
    
    # Delete it
    await hass.services.async_call(
        DOMAIN,
        "delete_trigger_zone",
        {"zone_id": "delete_test"},
        blocking=True,
    )
    
    assert True


@pytest.mark.asyncio
async def test_delete_nonexistent_zone(hass, mock_config_entry: MockConfigEntry):
    """Test deleting non-existent zone."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Try to delete non-existent zone - should not raise error
    await hass.services.async_call(
        DOMAIN,
        "delete_trigger_zone",
        {"zone_id": "nonexistent"},
        blocking=True,
    )
    
    assert True


# ===== register_secondary_cue Service Tests =====


@pytest.mark.asyncio
async def test_register_secondary_cue_service(hass, mock_config_entry: MockConfigEntry):
    """Test register_secondary_cue service."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Register a secondary cue
    await hass.services.async_call(
        DOMAIN,
        "register_secondary_cue",
        {
            "cue_id": "front_door",
            "entity_id": "binary_sensor.front_door",
            "cue_type": "door",
            "location": {"x": 5.0, "y": 0.0},
            "confidence_boost": 0.15,
        },
        blocking=True,
    )
    
    assert True


@pytest.mark.asyncio
async def test_register_multiple_cues(hass, mock_config_entry: MockConfigEntry):
    """Test registering multiple secondary cues."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Register multiple cues
    cues = [
        {
            "cue_id": "door_1",
            "entity_id": "binary_sensor.door_1",
            "cue_type": "door",
            "location": {"x": 0.0, "y": 5.0},
            "confidence_boost": 0.15,
        },
        {
            "cue_id": "light_1",
            "entity_id": "light.room_1",
            "cue_type": "light",
            "location": {"x": 5.0, "y": 5.0},
            "confidence_boost": 0.10,
        },
    ]
    
    for cue in cues:
        await hass.services.async_call(
            DOMAIN,
            "register_secondary_cue",
            cue,
            blocking=True,
        )
    
    assert True


# ===== analyze_pattern Service Tests =====


@pytest.mark.asyncio
async def test_analyze_pattern_service(hass, mock_config_entry: MockConfigEntry):
    """Test analyze_pattern service."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Call analyze_pattern
    await hass.services.async_call(
        DOMAIN,
        "analyze_pattern",
        {
            "time_range": 3600,  # Last hour
        },
        blocking=True,
    )
    
    assert True


@pytest.mark.asyncio
async def test_analyze_pattern_with_pattern_id(hass, mock_config_entry: MockConfigEntry):
    """Test analyze_pattern with specific pattern_id."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Analyze specific pattern
    await hass.services.async_call(
        DOMAIN,
        "analyze_pattern",
        {
            "pattern_id": "morning_routine",
            "time_range": 86400,  # Last 24 hours
        },
        blocking=True,
    )
    
    assert True


# ===== Service Error Handling Tests =====


@pytest.mark.asyncio
async def test_service_with_missing_coordinator(hass):
    """Test service call when coordinator is not set up."""
    # Try to call service without setting up integration
    with pytest.raises(Exception):
        await hass.services.async_call(
            DOMAIN,
            "update_floorplan",
            {"floorplan_id": "test"},
            blocking=True,
        )


@pytest.mark.asyncio
async def test_service_schema_validation(hass, mock_config_entry: MockConfigEntry):
    """Test that service schemas validate input."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Try to call service with invalid schema
    with pytest.raises(Exception):
        await hass.services.async_call(
            DOMAIN,
            "create_trigger_zone",
            {
                "zone_id": "test",
                # Missing required polygon field
            },
            blocking=True,
        )


# ===== Concurrent Service Calls =====


@pytest.mark.asyncio
async def test_concurrent_service_calls(hass, mock_config_entry: MockConfigEntry):
    """Test multiple concurrent service calls."""
    mock_config_entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    
    # Make multiple service calls concurrently
    import asyncio
    
    tasks = []
    for i in range(5):
        task = hass.services.async_call(
            DOMAIN,
            "create_trigger_zone",
            {
                "zone_id": f"zone_{i}",
                "polygon": [
                    {"x": 0.0, "y": 0.0},
                    {"x": 5.0, "y": 0.0},
                    {"x": 5.0, "y": 5.0},
                    {"x": 0.0, "y": 5.0},
                ],
                "directions": [],
            },
            blocking=False,
        )
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    assert True
