"""Pattern analysis and learning for motion sequences."""
from __future__ import annotations

import logging
import math
from collections import deque
from typing import Any, Dict, List, Tuple

from ..models import LearnedPattern, MotionSequence

_LOGGER = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analyzes motion patterns and learns common behaviors.
    
    Identifies pattern types including linear motion, circular patterns,
    zone transitions, stationary presence, and learns from historical data.
    
    Attributes:
        pattern_history: Recent patterns for analysis
        learned_patterns: Dictionary of learned pattern signatures
    """
    
    def __init__(self) -> None:
        """Initialize pattern analyzer."""
        self.pattern_history: deque = deque(maxlen=1000)
        self.learned_patterns: Dict[str, LearnedPattern] = {}
        
        _LOGGER.info("PatternAnalyzer initialized")
    
    def analyze_sequence(self, motion_sequence: MotionSequence) -> str:
        """Determine pattern type from motion sequence.
        
        Args:
            motion_sequence: Sequence to analyze
        
        Returns:
            Pattern type: linear, circular, zone_transition, stationary, or random
        """
        if len(motion_sequence.events) < 2:
            return "insufficient_data"
        
        # Check for linear pattern
        if self._is_linear(motion_sequence):
            return "linear"
        
        # Check for circular pattern
        if self._is_circular(motion_sequence):
            return "circular"
        
        # Check for zone transition
        if self._is_zone_transition(motion_sequence):
            return "zone_transition"
        
        # Check for stationary
        if self._is_stationary(motion_sequence):
            return "stationary"
        
        return "random"
    
    def _is_linear(self, sequence: MotionSequence) -> bool:
        """Check if motion follows a linear path.
        
        Args:
            sequence: Motion sequence
        
        Returns:
            True if linear
        """
        if len(sequence.events) < 3:
            return True  # Assume linear for short sequences
        
        # Calculate vectors between consecutive sensors
        vectors = []
        for i in range(len(sequence.events) - 1):
            v = self._calculate_vector(
                sequence.events[i].sensor.position,
                sequence.events[i + 1].sensor.position,
            )
            vectors.append(v)
        
        # Check if all vectors point in similar direction
        if not vectors:
            return False
        
        reference = vectors[0]
        for v in vectors[1:]:
            dot_product = reference[0] * v[0] + reference[1] * v[1]
            if dot_product < 0.7:  # Less than ~45 degree difference
                return False
        
        return True
    
    def _is_circular(self, sequence: MotionSequence) -> bool:
        """Check if motion follows a circular/loop pattern.
        
        Args:
            sequence: Motion sequence
        
        Returns:
            True if circular
        """
        if len(sequence.events) < 4:
            return False
        
        # Check if path returns to starting position
        start_pos = sequence.events[0].sensor.position
        end_pos = sequence.events[-1].sensor.position
        
        distance = math.sqrt(
            (end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2
        )
        
        # If end is close to start, likely circular
        return distance < 50  # Within 50 units
    
    def _is_zone_transition(self, sequence: MotionSequence) -> bool:
        """Check if motion represents zone-to-zone transition.
        
        Args:
            sequence: Motion sequence
        
        Returns:
            True if zone transition
        """
        # Check if events span multiple zones
        zones = set()
        for event in sequence.events:
            if hasattr(event.sensor, "zone"):
                zones.add(event.sensor.zone)
        
        return len(zones) >= 2
    
    def _is_stationary(self, sequence: MotionSequence) -> bool:
        """Check if motion is stationary (repeated triggers in same area).
        
        Args:
            sequence: Motion sequence
        
        Returns:
            True if stationary
        """
        if len(sequence.events) < 3:
            return False
        
        # Check if all events from same or very close sensors
        positions = [e.sensor.position for e in sequence.events]
        max_distance = 0.0
        
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                dist = math.sqrt(
                    (positions[j][0] - positions[i][0]) ** 2
                    + (positions[j][1] - positions[i][1]) ** 2
                )
                max_distance = max(max_distance, dist)
        
        return max_distance < 30  # Within 30 units
    
    def learn_patterns(
        self,
        historical_data: List[MotionSequence],
        min_occurrences: int = 5,
    ) -> List[LearnedPattern]:
        """Learn common patterns from historical data.
        
        Args:
            historical_data: List of historical sequences
            min_occurrences: Minimum occurrences to consider pattern
        
        Returns:
            List of learned patterns
        """
        pattern_counts: Dict[str, Dict] = {}
        
        for sequence in historical_data:
            # Create pattern signature
            signature = self._create_signature(sequence)
            
            if signature not in pattern_counts:
                pattern_counts[signature] = {
                    "count": 0,
                    "example": sequence,
                    "confidence_sum": 0.0,
                }
            
            pattern_counts[signature]["count"] += 1
            pattern_counts[signature]["confidence_sum"] += sequence.confidence
        
        # Filter patterns by minimum occurrences
        learned = []
        for signature, data in pattern_counts.items():
            if data["count"] >= min_occurrences:
                avg_confidence = data["confidence_sum"] / data["count"]
                learned.append(
                    LearnedPattern(
                        signature=signature,
                        occurrences=data["count"],
                        confidence=avg_confidence,
                        example=data["example"],
                    )
                )
        
        # Store learned patterns
        for pattern in learned:
            self.learned_patterns[pattern.signature] = pattern
        
        _LOGGER.info("Learned %d patterns from %d sequences", len(learned), len(historical_data))
        
        return learned
    
    def _create_signature(self, sequence: MotionSequence) -> str:
        """Create a unique signature for a motion pattern.
        
        Args:
            sequence: Motion sequence
        
        Returns:
            Pattern signature
        """
        # Use sensor IDs and approximate timing
        sensors = [e.sensor.entity_id for e in sequence.events]
        return "->".join(sensors)
    
    def _calculate_vector(
        self,
        pos1: Tuple[float, float],
        pos2: Tuple[float, float],
    ) -> Tuple[float, float]:
        """Calculate normalized vector between positions.
        
        Args:
            pos1: First position
            pos2: Second position
        
        Returns:
            Normalized vector
        """
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        magnitude = math.sqrt(dx**2 + dy**2)
        
        if magnitude == 0:
            return (0.0, 0.0)
        
        return (dx / magnitude, dy / magnitude)
    
    def add_to_history(self, sequence: MotionSequence) -> None:
        """Add sequence to pattern history.
        
        Args:
            sequence: Motion sequence to add
        """
        self.pattern_history.append(sequence)
    
    def get_pattern_statistics(self) -> Dict[str, int]:
        """Get statistics on learned patterns.
        
        Returns:
            Dictionary of pattern type counts
        """
        pattern_types: Dict[str, int] = {
            "linear": 0,
            "circular": 0,
            "zone_transition": 0,
            "stationary": 0,
            "random": 0,
        }
        
        for sequence in self.pattern_history:
            pattern_type = self.analyze_sequence(sequence)
            if pattern_type in pattern_types:
                pattern_types[pattern_type] += 1
        
        return pattern_types
    
    def clear_history(self) -> None:
        """Clear pattern history."""
        self.pattern_history.clear()
        _LOGGER.info("Pattern history cleared")
    
    def clear_learned_patterns(self) -> None:
        """Clear learned patterns."""
        self.learned_patterns.clear()
        _LOGGER.info("Learned patterns cleared")
    
    def suggest_patterns(
        self,
        min_confidence: float = 0.7,
        max_suggestions: int = 10,
    ) -> List[LearnedPattern]:
        """Suggest learned patterns for user review.
        
        Args:
            min_confidence: Minimum confidence threshold for suggestions
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of learned patterns sorted by confidence
        """
        # Filter patterns by confidence
        suggestions = [
            pattern
            for pattern in self.learned_patterns.values()
            if pattern.confidence >= min_confidence
        ]
        
        # Sort by occurrences * confidence (relevance score)
        suggestions.sort(
            key=lambda p: p.occurrences * p.confidence,
            reverse=True,
        )
        
        # Limit to max suggestions
        return suggestions[:max_suggestions]
    
    def apply_pattern(
        self,
        pattern_signature: str,
        auto_apply: bool = False,
    ) -> bool:
        """Apply a learned pattern to the system.
        
        Args:
            pattern_signature: Signature of pattern to apply
            auto_apply: Whether to automatically apply without confirmation
            
        Returns:
            True if pattern was applied successfully
        """
        if pattern_signature not in self.learned_patterns:
            _LOGGER.warning("Pattern %s not found in learned patterns", pattern_signature)
            return False
        
        pattern = self.learned_patterns[pattern_signature]
        
        # In a full implementation, this would update zone definitions,
        # add new directional hints, or configure automation rules
        _LOGGER.info(
            "Applied pattern: %s (occurrences=%d, confidence=%.2f, auto=%s)",
            pattern_signature,
            pattern.occurrences,
            pattern.confidence,
            auto_apply,
        )
        
        return True
    
    def track_pattern_occurrence(
        self,
        sequence: MotionSequence,
    ) -> None:
        """Track occurrence of a pattern.
        
        Updates the occurrence count for matching learned patterns.
        
        Args:
            sequence: Motion sequence to track
        """
        signature = self._create_signature(sequence)
        
        if signature in self.learned_patterns:
            # Update existing pattern
            pattern = self.learned_patterns[signature]
            pattern.occurrences += 1
            
            # Update confidence with exponential moving average
            alpha = 0.1  # Smoothing factor
            pattern.confidence = (
                alpha * sequence.confidence + (1 - alpha) * pattern.confidence
            )
            
            _LOGGER.debug(
                "Updated pattern occurrence: %s (count=%d, confidence=%.2f)",
                signature,
                pattern.occurrences,
                pattern.confidence,
            )
    
    def get_pattern_suggestions_formatted(
        self,
        min_confidence: float = 0.7,
        max_suggestions: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get formatted pattern suggestions for user display.
        
        Args:
            min_confidence: Minimum confidence threshold
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of formatted suggestion dictionaries
        """
        suggestions = self.suggest_patterns(min_confidence, max_suggestions)
        
        formatted = []
        for pattern in suggestions:
            formatted.append({
                "signature": pattern.signature,
                "description": self._generate_pattern_description(pattern),
                "occurrences": pattern.occurrences,
                "confidence": round(pattern.confidence, 2),
                "relevance_score": round(pattern.occurrences * pattern.confidence, 2),
                "example_sensors": pattern.example.get_sensor_ids() if pattern.example else [],
            })
        
        return formatted
    
    def _generate_pattern_description(self, pattern: LearnedPattern) -> str:
        """Generate human-readable description of a pattern.
        
        Args:
            pattern: Learned pattern
            
        Returns:
            Description string
        """
        if not pattern.example:
            return "Unknown pattern"
        
        sensors = pattern.example.get_sensor_ids()
        
        # Generate description based on sensor count and pattern
        if len(sensors) == 1:
            return f"Single sensor motion at {sensors[0]}"
        elif len(sensors) == 2:
            return f"Motion from {sensors[0]} to {sensors[1]}"
        else:
            return f"Motion path: {' → '.join(sensors)}"
