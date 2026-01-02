"""Data models for secondary cues."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass
class StateChange:
    """Represents a state transition for a secondary cue.
    
    Attributes:
        from_state: Previous state (None means any state)
        to_state: New state
        attribute: Optional attribute to track instead of main state
    """
    
    to_state: str
    from_state: Optional[str] = None
    attribute: Optional[str] = None
    
    def matches(self, old_state: Optional[str], new_state: str) -> bool:
        """Check if this state change matches actual state transition.
        
        Args:
            old_state: Previous state
            new_state: New state
            
        Returns:
            True if matches
        """
        if self.from_state is not None and old_state != self.from_state:
            return False
        return new_state == self.to_state
    
    def __str__(self) -> str:
        """String representation."""
        from_str = self.from_state or "any"
        return f"StateChange({from_str} -> {self.to_state})"
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()


@dataclass
class DirectionalHint:
    """Defines how a cue state change implies a direction.
    
    Attributes:
        state_change: The state transition that triggers this hint
        implied_direction: Direction name or vector implied by this change
        confidence: Confidence of this implication (0-1)
        condition: Optional template condition for additional filtering
    """
    
    state_change: StateChange
    implied_direction: str
    confidence: float = 0.7
    condition: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate directional hint."""
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
    
    def matches_transition(
        self, 
        old_state: Optional[str], 
        new_state: str
    ) -> bool:
        """Check if this hint matches a state transition.
        
        Args:
            old_state: Previous state
            new_state: New state
            
        Returns:
            True if hint applies to this transition
        """
        return self.state_change.matches(old_state, new_state)
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"DirectionalHint({self.state_change} -> "
            f"{self.implied_direction}, conf={self.confidence:.2f})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()


@dataclass
class SecondaryCue:
    """Represents a secondary cue device on the floorplan.
    
    Secondary cues are non-motion sensors (doors, lights, etc.) that
    provide additional context for direction detection.
    
    Attributes:
        id: Unique cue identifier
        name: Display name
        entity_id: Home Assistant entity ID to monitor
        position: (x, y) position on floorplan
        cue_type: Type of cue (door, light, switch, presence, etc.)
        directional_hints: List of hints for direction inference
        correlation_window: Max time before/after motion (milliseconds)
        pre_trigger_window: Max time cue can precede motion (milliseconds)
        post_trigger_window: Max time cue can follow motion (milliseconds)
        confidence_weight: Weight for confidence calculation (0-1)
        reliability: Device reliability factor (0-1)
        trigger_states: States that trigger this cue (None = use defaults)
        ignore_states: States to ignore (None = use defaults)
        icon: MDI icon for visualization
        color: Color for visualization (hex)
        range_radius: Visual range radius (0 for no range)
        last_triggered: Timestamp of last trigger
        trigger_count: Number of times triggered
    """
    
    id: str
    name: str
    entity_id: str
    position: Tuple[float, float]
    cue_type: str
    directional_hints: List[DirectionalHint] = field(default_factory=list)
    correlation_window: int = 3000
    pre_trigger_window: int = 2000
    post_trigger_window: int = 2000
    confidence_weight: float = 0.6
    reliability: float = 0.8
    trigger_states: Optional[List[str]] = None
    ignore_states: Optional[List[str]] = None
    icon: str = "mdi:lightbulb"
    color: str = "#FFA500"
    range_radius: float = 0.0
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def __post_init__(self) -> None:
        """Validate secondary cue configuration."""
        if not 0 <= self.confidence_weight <= 1:
            raise ValueError("confidence_weight must be between 0 and 1")
        if not 0 <= self.reliability <= 1:
            raise ValueError("reliability must be between 0 and 1")
        if self.correlation_window < 0:
            raise ValueError("correlation_window must be non-negative")
        if self.pre_trigger_window < 0:
            raise ValueError("pre_trigger_window must be non-negative")
        if self.post_trigger_window < 0:
            raise ValueError("post_trigger_window must be non-negative")
        if self.range_radius < 0:
            raise ValueError("range_radius must be non-negative")
    
    def is_trigger_state(self, state: str) -> bool:
        """Check if state is a trigger state for this cue.
        
        Args:
            state: State to check
            
        Returns:
            True if this state should trigger the cue
        """
        if self.trigger_states is not None:
            return state in self.trigger_states
        
        # Use defaults based on cue type (will be enhanced with registry)
        default_triggers = {
            "door": ["open", "opening", "on"],
            "light": ["on"],
            "switch": ["on"],
            "presence": ["home", "on"],
            "temperature": ["rising", "falling"],
            "vibration": ["on", "detected"],
            "power": ["rising"],
            "media": ["playing", "on"],
        }
        
        return state in default_triggers.get(self.cue_type, ["on"])
    
    def should_ignore_state(self, state: str) -> bool:
        """Check if state should be ignored.
        
        Args:
            state: State to check
            
        Returns:
            True if this state should be ignored
        """
        if self.ignore_states is not None:
            return state in self.ignore_states
        
        return state in ["unavailable", "unknown"]
    
    def get_hint_for_transition(
        self, 
        old_state: Optional[str], 
        new_state: str
    ) -> Optional[DirectionalHint]:
        """Get directional hint for a state transition.
        
        Args:
            old_state: Previous state
            new_state: New state
            
        Returns:
            DirectionalHint if transition matches, None otherwise
        """
        for hint in self.directional_hints:
            if hint.matches_transition(old_state, new_state):
                return hint
        
        return None
    
    def add_hint(self, hint: DirectionalHint) -> None:
        """Add a directional hint to this cue.
        
        Args:
            hint: DirectionalHint to add
        """
        self.directional_hints.append(hint)
    
    def update_trigger(self, timestamp: datetime) -> None:
        """Update trigger information.
        
        Args:
            timestamp: Time of trigger
        """
        self.last_triggered = timestamp
        self.trigger_count += 1
    
    def distance_to(self, position: Tuple[float, float]) -> float:
        """Calculate distance to a position.
        
        Args:
            position: (x, y) coordinates
            
        Returns:
            Distance in floorplan units
        """
        dx = position[0] - self.position[0]
        dy = position[1] - self.position[1]
        return (dx**2 + dy**2) ** 0.5
    
    def __str__(self) -> str:
        """String representation."""
        return (
            f"SecondaryCue(id={self.id}, entity_id={self.entity_id}, "
            f"type={self.cue_type}, hints={len(self.directional_hints)})"
        )
    
    def __repr__(self) -> str:
        """Debug representation."""
        return self.__str__()
