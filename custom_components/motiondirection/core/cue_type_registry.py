"""
Secondary Cue Type Registry.

Defines supported cue types and their default behaviors for hybrid motion detection.
"""

from typing import Any, Optional
import logging

_LOGGER = logging.getLogger(__name__)


class CueTypeRegistry:
    """
    Registry of secondary cue types and their default configurations.
    
    This registry defines the behavior of different cue types (doors, lights, etc.)
    including their typical correlation windows, confidence levels, and default
    directional hints.
    
    The registry follows the Registry Pattern to provide a centralized,
    extensible configuration system for cue types.
    """
    
    # Core registry: Maps cue type names to their configurations
    CUE_TYPES: dict[str, dict[str, Any]] = {
        "door": {
            "domains": ["binary_sensor", "cover"],
            "default_states": ["open", "opening", "on"],
            "confidence": 0.85,
            "typical_correlation": 1000,  # milliseconds
            "bidirectional": True,
            "default_hints": [
                {"state": "open", "implies": "entering"},
                {"state": "closed", "implies": "exiting"}
            ],
            "description": "Door sensors (contact sensors, door position sensors)",
        },
        "light": {
            "domains": ["light", "switch"],
            "default_states": ["on"],
            "confidence": 0.65,
            "typical_correlation": 2000,
            "bidirectional": False,
            "default_hints": [
                {"state": "on", "implies": "entering"}
            ],
            "description": "Light switches and smart bulbs",
        },
        "switch": {
            "domains": ["switch", "input_boolean"],
            "default_states": ["on"],
            "confidence": 0.60,
            "typical_correlation": 1500,
            "bidirectional": True,
            "default_hints": [],  # User-defined
            "description": "Generic switches and input booleans",
        },
        "presence": {
            "domains": ["device_tracker", "person", "binary_sensor"],
            "default_states": ["home", "on"],
            "confidence": 0.90,
            "typical_correlation": 5000,
            "bidirectional": True,
            "default_hints": [
                {"state": "home", "implies": "arriving"},
                {"state": "away", "implies": "leaving"}
            ],
            "description": "Presence detection (device trackers, person entities)",
        },
        "temperature": {
            "domains": ["sensor", "climate"],
            "default_states": ["rising", "falling"],
            "confidence": 0.40,
            "typical_correlation": 30000,
            "bidirectional": False,
            "default_hints": [],
            "description": "Temperature sensors and climate devices",
        },
        "vibration": {
            "domains": ["binary_sensor"],
            "default_states": ["on", "detected"],
            "confidence": 0.70,
            "typical_correlation": 500,
            "bidirectional": False,
            "default_hints": [],
            "description": "Vibration sensors (door knock, floor vibration)",
        },
        "power": {
            "domains": ["sensor", "switch"],
            "default_states": ["rising"],
            "confidence": 0.55,
            "typical_correlation": 3000,
            "bidirectional": False,
            "default_hints": [],
            "description": "Power consumption sensors",
        },
        "media": {
            "domains": ["media_player"],
            "default_states": ["playing", "on"],
            "confidence": 0.50,
            "typical_correlation": 5000,
            "bidirectional": False,
            "default_hints": [
                {"state": "playing", "implies": "present"}
            ],
            "description": "Media players (TV, speakers, etc.)",
        },
    }
    
    @classmethod
    def get_cue_config(cls, cue_type: str) -> dict[str, Any]:
        """
        Get configuration for a specific cue type.
        
        Args:
            cue_type: The cue type name (e.g., "door", "light").
            
        Returns:
            Dictionary containing cue type configuration, or empty dict if not found.
            
        Example:
            >>> config = CueTypeRegistry.get_cue_config("door")
            >>> print(config["confidence"])
            0.85
        """
        config = cls.CUE_TYPES.get(cue_type, {})
        if not config and cue_type:
            _LOGGER.warning("Unknown cue type: %s", cue_type)
        return config.copy()  # Return copy to prevent mutation
    
    @classmethod
    def is_valid_cue_type(cls, cue_type: str) -> bool:
        """
        Check if a cue type is supported.
        
        Args:
            cue_type: The cue type name to validate.
            
        Returns:
            True if the cue type is registered, False otherwise.
            
        Example:
            >>> CueTypeRegistry.is_valid_cue_type("door")
            True
            >>> CueTypeRegistry.is_valid_cue_type("invalid")
            False
        """
        return cue_type in cls.CUE_TYPES
    
    @classmethod
    def get_all_types(cls) -> list[str]:
        """
        Get a list of all registered cue types.
        
        Returns:
            List of cue type names.
            
        Example:
            >>> types = CueTypeRegistry.get_all_types()
            >>> "door" in types
            True
        """
        return list(cls.CUE_TYPES.keys())
    
    @classmethod
    def get_types_for_domain(cls, domain: str) -> list[str]:
        """
        Get all cue types that support a given Home Assistant domain.
        
        Args:
            domain: Home Assistant domain (e.g., "binary_sensor", "light").
            
        Returns:
            List of cue type names that support this domain.
            
        Example:
            >>> types = CueTypeRegistry.get_types_for_domain("binary_sensor")
            >>> "door" in types
            True
        """
        matching_types = []
        for cue_type, config in cls.CUE_TYPES.items():
            if domain in config.get("domains", []):
                matching_types.append(cue_type)
        return matching_types
    
    @classmethod
    def register_custom_type(
        cls,
        cue_type: str,
        config: dict[str, Any],
        override: bool = False
    ) -> bool:
        """
        Register a custom cue type.
        
        This allows users to extend the registry with custom cue types
        for specialized hardware or use cases.
        
        Args:
            cue_type: Unique name for the custom cue type.
            config: Configuration dictionary matching the standard format.
            override: Allow overriding existing types (default False).
            
        Returns:
            True if registration successful, False if type exists and override=False.
            
        Raises:
            ValueError: If config is missing required fields.
            
        Example:
            >>> config = {
            ...     "domains": ["sensor"],
            ...     "default_states": ["on"],
            ...     "confidence": 0.5,
            ...     "typical_correlation": 1000,
            ...     "bidirectional": False,
            ...     "default_hints": [],
            ...     "description": "Custom sensor type"
            ... }
            >>> CueTypeRegistry.register_custom_type("custom", config)
            True
        """
        # Check if type already exists
        if cue_type in cls.CUE_TYPES and not override:
            _LOGGER.warning(
                "Cue type '%s' already exists. Use override=True to replace.",
                cue_type
            )
            return False
        
        # Validate required fields
        required_fields = [
            "domains", "default_states", "confidence",
            "typical_correlation", "bidirectional", "default_hints"
        ]
        missing_fields = [f for f in required_fields if f not in config]
        if missing_fields:
            raise ValueError(
                f"Config missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate field types and ranges
        if not isinstance(config["domains"], list):
            raise ValueError("'domains' must be a list")
        if not isinstance(config["default_states"], list):
            raise ValueError("'default_states' must be a list")
        if not (0.0 <= config["confidence"] <= 1.0):
            raise ValueError("'confidence' must be between 0.0 and 1.0")
        if not isinstance(config["typical_correlation"], int) or config["typical_correlation"] < 0:
            raise ValueError("'typical_correlation' must be a positive integer")
        if not isinstance(config["bidirectional"], bool):
            raise ValueError("'bidirectional' must be a boolean")
        if not isinstance(config["default_hints"], list):
            raise ValueError("'default_hints' must be a list")
        
        # Register the type
        cls.CUE_TYPES[cue_type] = config.copy()
        _LOGGER.info("Registered custom cue type: %s", cue_type)
        return True
    
    @classmethod
    def get_default_confidence(cls, cue_type: str) -> float:
        """
        Get default confidence boost for a cue type.
        
        Args:
            cue_type: The cue type name.
            
        Returns:
            Confidence value (0.0-1.0), or 0.5 if type unknown.
        """
        config = cls.get_cue_config(cue_type)
        return config.get("confidence", 0.5)
    
    @classmethod
    def get_correlation_window(cls, cue_type: str) -> int:
        """
        Get typical correlation time window for a cue type.
        
        Args:
            cue_type: The cue type name.
            
        Returns:
            Time window in milliseconds, or 2000 if type unknown.
        """
        config = cls.get_cue_config(cue_type)
        return config.get("typical_correlation", 2000)
    
    @classmethod
    def is_bidirectional(cls, cue_type: str) -> bool:
        """
        Check if a cue type provides bidirectional hints (entering/exiting).
        
        Args:
            cue_type: The cue type name.
            
        Returns:
            True if bidirectional, False otherwise.
        """
        config = cls.get_cue_config(cue_type)
        return config.get("bidirectional", False)
    
    @classmethod
    def get_default_hints(cls, cue_type: str) -> list[dict[str, str]]:
        """
        Get default directional hints for a cue type.
        
        Args:
            cue_type: The cue type name.
            
        Returns:
            List of hint dictionaries with 'state' and 'implies' keys.
        """
        config = cls.get_cue_config(cue_type)
        return config.get("default_hints", []).copy()
