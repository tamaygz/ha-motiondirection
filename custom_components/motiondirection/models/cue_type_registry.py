"""Registry of secondary cue types and their behaviors."""
from typing import Any, Dict, List, Optional


class CueTypeRegistry:
    """Registry of secondary cue types and their default configurations.
    
    This registry defines the characteristics and behaviors of different
    types of secondary cues (doors, lights, switches, etc.).
    """
    
    # Registry of cue types with their configurations
    CUE_TYPES: Dict[str, Dict[str, Any]] = {
        "door": {
            "domains": ["binary_sensor", "cover"],
            "default_states": ["open", "opening", "on"],
            "confidence": 0.85,
            "typical_correlation": 1000,  # ms
            "bidirectional": True,
            "default_hints": [
                {"state": "open", "implies": "entering"},
                {"state": "closed", "implies": "exiting"}
            ],
            "icon": "mdi:door",
            "color": "#2196F3",
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
            "icon": "mdi:lightbulb",
            "color": "#FFC107",
        },
        "switch": {
            "domains": ["switch", "input_boolean"],
            "default_states": ["on"],
            "confidence": 0.60,
            "typical_correlation": 1500,
            "bidirectional": True,
            "default_hints": [],  # User-defined
            "icon": "mdi:light-switch",
            "color": "#9E9E9E",
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
            "icon": "mdi:account",
            "color": "#4CAF50",
        },
        "temperature": {
            "domains": ["sensor", "climate"],
            "default_states": ["rising", "falling"],
            "confidence": 0.40,
            "typical_correlation": 30000,
            "bidirectional": False,
            "default_hints": [],
            "icon": "mdi:thermometer",
            "color": "#FF5722",
        },
        "vibration": {
            "domains": ["binary_sensor"],
            "default_states": ["on", "detected"],
            "confidence": 0.70,
            "typical_correlation": 500,
            "bidirectional": False,
            "default_hints": [],
            "icon": "mdi:vibrate",
            "color": "#9C27B0",
        },
        "power": {
            "domains": ["sensor", "switch"],
            "default_states": ["rising"],
            "confidence": 0.55,
            "typical_correlation": 3000,
            "bidirectional": False,
            "default_hints": [],
            "icon": "mdi:power-plug",
            "color": "#FF9800",
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
            "icon": "mdi:play-circle",
            "color": "#E91E63",
        },
    }
    
    @classmethod
    def get_cue_config(cls, cue_type: str) -> Dict[str, Any]:
        """Get configuration for a cue type.
        
        Args:
            cue_type: Type of cue
            
        Returns:
            Configuration dictionary
        """
        return cls.CUE_TYPES.get(cue_type, {})
    
    @classmethod
    def is_valid_cue_type(cls, cue_type: str) -> bool:
        """Check if cue type is supported.
        
        Args:
            cue_type: Type to check
            
        Returns:
            True if valid cue type
        """
        return cue_type in cls.CUE_TYPES
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get list of all cue types.
        
        Returns:
            List of cue type names
        """
        return list(cls.CUE_TYPES.keys())
    
    @classmethod
    def get_types_for_domain(cls, domain: str) -> List[str]:
        """Get cue types that support a specific domain.
        
        Args:
            domain: Home Assistant domain (e.g., 'binary_sensor')
            
        Returns:
            List of compatible cue types
        """
        compatible = []
        for cue_type, config in cls.CUE_TYPES.items():
            if domain in config.get("domains", []):
                compatible.append(cue_type)
        return compatible
    
    @classmethod
    def get_default_confidence(cls, cue_type: str) -> float:
        """Get default confidence for a cue type.
        
        Args:
            cue_type: Type of cue
            
        Returns:
            Default confidence value (0-1)
        """
        config = cls.get_cue_config(cue_type)
        return config.get("confidence", 0.5)
    
    @classmethod
    def get_typical_correlation_window(cls, cue_type: str) -> int:
        """Get typical correlation window for a cue type.
        
        Args:
            cue_type: Type of cue
            
        Returns:
            Typical correlation window in milliseconds
        """
        config = cls.get_cue_config(cue_type)
        return config.get("typical_correlation", 3000)
    
    @classmethod
    def is_bidirectional(cls, cue_type: str) -> bool:
        """Check if cue type supports bidirectional detection.
        
        Args:
            cue_type: Type of cue
            
        Returns:
            True if bidirectional
        """
        config = cls.get_cue_config(cue_type)
        return config.get("bidirectional", False)
    
    @classmethod
    def get_default_icon(cls, cue_type: str) -> str:
        """Get default MDI icon for a cue type.
        
        Args:
            cue_type: Type of cue
            
        Returns:
            MDI icon name
        """
        config = cls.get_cue_config(cue_type)
        return config.get("icon", "mdi:help-circle")
    
    @classmethod
    def get_default_color(cls, cue_type: str) -> str:
        """Get default color for a cue type.
        
        Args:
            cue_type: Type of cue
            
        Returns:
            Color hex code
        """
        config = cls.get_cue_config(cue_type)
        return config.get("color", "#808080")
    
    @classmethod
    def get_default_hints(cls, cue_type: str) -> List[Dict[str, str]]:
        """Get default directional hints for a cue type.
        
        Args:
            cue_type: Type of cue
            
        Returns:
            List of hint configurations
        """
        config = cls.get_cue_config(cue_type)
        return config.get("default_hints", [])
    
    @classmethod
    def suggest_cue_type(cls, entity_id: str) -> Optional[str]:
        """Suggest a cue type based on entity ID.
        
        Args:
            entity_id: Home Assistant entity ID
            
        Returns:
            Suggested cue type or None
        """
        # Extract domain from entity_id
        if "." not in entity_id:
            return None
        
        domain = entity_id.split(".")[0]
        
        # Get compatible types
        compatible = cls.get_types_for_domain(domain)
        
        if not compatible:
            return None
        
        # Check entity ID for keywords
        entity_lower = entity_id.lower()
        
        if any(keyword in entity_lower for keyword in ["door", "gate", "garage"]):
            return "door"
        elif any(keyword in entity_lower for keyword in ["light", "lamp"]):
            return "light"
        elif any(keyword in entity_lower for keyword in ["switch"]):
            return "switch"
        elif any(keyword in entity_lower for keyword in ["person", "device_tracker"]):
            return "presence"
        elif any(keyword in entity_lower for keyword in ["temperature", "temp"]):
            return "temperature"
        elif any(keyword in entity_lower for keyword in ["vibration", "shake"]):
            return "vibration"
        elif any(keyword in entity_lower for keyword in ["power", "watt"]):
            return "power"
        elif any(keyword in entity_lower for keyword in ["media", "player", "tv"]):
            return "media"
        
        # Return first compatible type if no keyword match
        return compatible[0] if compatible else None
