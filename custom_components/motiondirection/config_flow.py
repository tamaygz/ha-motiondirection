"""Config flow for Motion Direction integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er, selector
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_BACKGROUND_IMAGE,
    CONF_CONFIDENCE_THRESHOLD,
    CONF_HEIGHT,
    CONF_SCALE,
    CONF_TIME_WINDOW,
    CONF_WIDTH,
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_TIME_WINDOW,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class MotionDirectionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Motion Direction."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self.data: dict[str, Any] = {}
        self.discovered_sensors: list[str] = []
        self.selected_sensors: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step - integration entry point."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(user_input[CONF_NAME])
            self._abort_if_unique_id_configured()

            # Store data and proceed to floorplan step
            self.data[CONF_NAME] = user_input[CONF_NAME]
            return await self.async_step_floorplan()

        # Show initial form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default="Main Floor"): cv.string,
                }
            ),
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/username/ha-motiondirection",
            },
        )

    async def async_step_floorplan(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle floorplan configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate dimensions
            if user_input[CONF_WIDTH] <= 0 or user_input[CONF_HEIGHT] <= 0:
                errors["base"] = "invalid_dimensions"
            elif user_input[CONF_SCALE] <= 0:
                errors["base"] = "invalid_scale"
            else:
                # Store floorplan data
                self.data.update(
                    {
                        CONF_WIDTH: user_input[CONF_WIDTH],
                        CONF_HEIGHT: user_input[CONF_HEIGHT],
                        CONF_SCALE: user_input[CONF_SCALE],
                        CONF_BACKGROUND_IMAGE: user_input.get(CONF_BACKGROUND_IMAGE),
                    }
                )
                return await self.async_step_sensors()

        # Show floorplan form
        return self.async_show_form(
            step_id="floorplan",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_WIDTH, default=1000): vol.All(
                        vol.Coerce(int), vol.Range(min=100, max=10000)
                    ),
                    vol.Required(CONF_HEIGHT, default=800): vol.All(
                        vol.Coerce(int), vol.Range(min=100, max=10000)
                    ),
                    vol.Required(CONF_SCALE, default=10): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=100)
                    ),
                    vol.Optional(CONF_BACKGROUND_IMAGE): cv.string,
                }
            ),
            errors=errors,
            description_placeholders={
                "width_help": "Width of floorplan in pixels",
                "height_help": "Height of floorplan in pixels",
                "scale_help": "Pixels per meter (for distance calculations)",
            },
        )

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle sensor discovery and selection step."""
        errors: dict[str, str] = {}

        # Discover motion sensors on first call
        if not self.discovered_sensors:
            self.discovered_sensors = await self._async_discover_motion_sensors(
                self.hass
            )

        if user_input is not None:
            selected = user_input.get("sensors", [])
            
            if not selected:
                errors["base"] = "no_sensors_selected"
            else:
                self.selected_sensors = selected
                self.data["sensor_count"] = len(selected)
                
                # Ask if user wants to add secondary cues
                return await self.async_step_cues_prompt()

        # Show sensor selection form
        return self.async_show_form(
            step_id="sensors",
            data_schema=vol.Schema(
                {
                    vol.Required("sensors"): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="binary_sensor",
                            device_class="motion",
                            multiple=True,
                        )
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
                "discovered_count": str(len(self.discovered_sensors)),
                "sensor_help": "Select motion sensors to track",
            },
        )

    async def async_step_cues_prompt(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Ask if user wants to add secondary cues."""
        if user_input is not None:
            if user_input.get("add_cues", False):
                return await self.async_step_cues()
            else:
                # Skip to zones
                return await self.async_step_zones_prompt()

        return self.async_show_form(
            step_id="cues_prompt",
            data_schema=vol.Schema(
                {
                    vol.Optional("add_cues", default=False): cv.boolean,
                }
            ),
            description_placeholders={
                "cues_help": "Secondary cues (doors, lights) improve detection accuracy",
            },
        )

    async def async_step_cues(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle secondary cues configuration step."""
        if user_input is not None:
            # Store cue configuration (simplified for now)
            self.data["cues_enabled"] = True
            self.data["cue_count"] = len(user_input.get("cue_entities", []))
            
            # Proceed to zones
            return await self.async_step_zones_prompt()

        # Show cue selection form
        return self.async_show_form(
            step_id="cues",
            data_schema=vol.Schema(
                {
                    vol.Optional("cue_entities"): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["binary_sensor", "light", "switch", "sensor"],
                            multiple=True,
                        )
                    ),
                }
            ),
            description_placeholders={
                "cue_help": "Select entities that can provide directional hints",
            },
        )

    async def async_step_zones_prompt(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Ask if user wants to create zones."""
        if user_input is not None:
            if user_input.get("add_zones", False):
                return await self.async_step_zones()
            else:
                # Skip to calibration
                return await self.async_step_calibration_prompt()

        return self.async_show_form(
            step_id="zones_prompt",
            data_schema=vol.Schema(
                {
                    vol.Optional("add_zones", default=False): cv.boolean,
                }
            ),
            description_placeholders={
                "zones_help": "Zones enable direction detection in specific areas",
            },
        )

    async def async_step_zones(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle zone creation step."""
        if user_input is not None:
            # Store zone info (zones will be created later via UI/services)
            self.data["zones_enabled"] = True
            
            # Proceed to calibration
            return await self.async_step_calibration_prompt()

        # Show zone configuration info
        return self.async_show_form(
            step_id="zones",
            data_schema=vol.Schema(
                {
                    vol.Optional("zone_note", default="Zones can be created later via the Lovelace card"): cv.string,
                }
            ),
            description_placeholders={
                "zone_help": "Zones will be configured using the floorplan editor card",
            },
        )

    async def async_step_calibration_prompt(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Ask if user wants to run calibration."""
        if user_input is not None:
            if user_input.get("run_calibration", False):
                return await self.async_step_calibration()
            else:
                # Complete setup with defaults
                return await self._async_create_entry()

        return self.async_show_form(
            step_id="calibration_prompt",
            data_schema=vol.Schema(
                {
                    vol.Optional("run_calibration", default=False): cv.boolean,
                }
            ),
            description_placeholders={
                "calibration_help": "Calibration optimizes detection parameters",
            },
        )

    async def async_step_calibration(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle calibration configuration step."""
        if user_input is not None:
            # Store calibration settings
            self.data.update(
                {
                    CONF_TIME_WINDOW: user_input[CONF_TIME_WINDOW],
                    CONF_CONFIDENCE_THRESHOLD: user_input[CONF_CONFIDENCE_THRESHOLD],
                }
            )
            
            # Complete setup
            return await self._async_create_entry()

        # Show calibration form
        return self.async_show_form(
            step_id="calibration",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TIME_WINDOW, default=DEFAULT_TIME_WINDOW
                    ): vol.All(vol.Coerce(int), vol.Range(min=500, max=30000)),
                    vol.Required(
                        CONF_CONFIDENCE_THRESHOLD, default=DEFAULT_CONFIDENCE_THRESHOLD
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
                }
            ),
            description_placeholders={
                "window_help": "Time window in milliseconds for event correlation",
                "threshold_help": "Minimum confidence (0-1) for direction detection",
            },
        )

    async def _async_create_entry(self) -> config_entries.FlowResult:
        """Create the config entry."""
        # Set defaults if not configured
        if CONF_TIME_WINDOW not in self.data:
            self.data[CONF_TIME_WINDOW] = DEFAULT_TIME_WINDOW
        if CONF_CONFIDENCE_THRESHOLD not in self.data:
            self.data[CONF_CONFIDENCE_THRESHOLD] = DEFAULT_CONFIDENCE_THRESHOLD

        return self.async_create_entry(
            title=self.data[CONF_NAME],
            data=self.data,
        )

    @staticmethod
    async def _async_discover_motion_sensors(hass: HomeAssistant) -> list[str]:
        """Discover motion sensors in Home Assistant.
        
        Args:
            hass: Home Assistant instance
        
        Returns:
            List of motion sensor entity IDs
        """
        motion_sensors = []
        
        # Get all binary_sensor entities with motion device class
        entity_registry = er.async_get(hass)
        
        for entity in entity_registry.entities.values():
            if (
                entity.domain == "binary_sensor"
                and entity.device_class == "motion"
                and not entity.disabled
            ):
                motion_sensors.append(entity.entity_id)
        
        _LOGGER.info("Discovered %d motion sensors", len(motion_sensors))
        return motion_sensors

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MotionDirectionOptionsFlow:
        """Get the options flow for this handler."""
        return MotionDirectionOptionsFlow(config_entry)


class MotionDirectionOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Motion Direction."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Update options
            return self.async_create_entry(title="", data=user_input)

        # Show options form
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_TIME_WINDOW,
                        default=self.config_entry.data.get(
                            CONF_TIME_WINDOW, DEFAULT_TIME_WINDOW
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=500, max=30000)),
                    vol.Required(
                        CONF_CONFIDENCE_THRESHOLD,
                        default=self.config_entry.data.get(
                            CONF_CONFIDENCE_THRESHOLD, DEFAULT_CONFIDENCE_THRESHOLD
                        ),
                    ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=1.0)),
                }
            ),
            errors=errors,
        )
