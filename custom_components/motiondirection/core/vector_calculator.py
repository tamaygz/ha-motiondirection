"""Vector calculation for motion direction detection."""
import logging
import math
from typing import List, Tuple

from ..models import MotionSequence, SensorNode

_LOGGER = logging.getLogger(__name__)


class VectorCalculator:
    """Calculates motion vectors between sensor triggers.
    
    Implements vector calculation algorithms for direction detection,
    including normalization, weighted averaging, and confidence scoring.
    
    Confidence calculation uses multiple factors (see Appendix A.3):
    - Sensor count confidence (α = 0.3)
    - Temporal consistency (β = 0.2)
    - Spatial consistency (γ = 0.2)
    - Sensor reliability (δ = 0.3)
    
    Attributes:
        alpha: Weight for sensor count confidence
        beta: Weight for temporal consistency
        gamma: Weight for spatial consistency
        delta: Weight for sensor reliability
    """
    
    # Confidence calculation weights (Appendix A.3)
    ALPHA = 0.3  # Sensor count
    BETA = 0.2   # Temporal consistency
    GAMMA = 0.2  # Spatial consistency
    DELTA = 0.3  # Sensor reliability
    
    def __init__(
        self,
        alpha: float = ALPHA,
        beta: float = BETA,
        gamma: float = GAMMA,
        delta: float = DELTA,
    ) -> None:
        """Initialize vector calculator.
        
        Args:
            alpha: Weight for sensor count confidence
            beta: Weight for temporal consistency
            gamma: Weight for spatial consistency
            delta: Weight for sensor reliability
        
        Raises:
            ValueError: If weights don't sum to approximately 1.0
        """
        total = alpha + beta + gamma + delta
        if not 0.99 <= total <= 1.01:
            raise ValueError(
                f"Confidence weights must sum to 1.0 (got {total})"
            )
        
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        
        _LOGGER.info(
            "VectorCalculator initialized (α=%.2f, β=%.2f, γ=%.2f, δ=%.2f)",
            alpha,
            beta,
            gamma,
            delta,
        )
    
    def calculate_direction_vector(
        self,
        sensor1: SensorNode,
        sensor2: SensorNode,
    ) -> Tuple[float, float]:
        """Calculate normalized direction vector from sensor1 to sensor2.
        
        Args:
            sensor1: Starting sensor
            sensor2: Ending sensor
        
        Returns:
            Normalized direction vector (dx, dy)
        """
        dx = sensor2.position[0] - sensor1.position[0]
        dy = sensor2.position[1] - sensor1.position[1]
        
        magnitude = math.sqrt(dx**2 + dy**2)
        
        if magnitude == 0:
            _LOGGER.warning(
                "Zero magnitude vector between sensors %s and %s",
                sensor1.entity_id,
                sensor2.entity_id,
            )
            return (0.0, 0.0)
        
        return (dx / magnitude, dy / magnitude)
    
    def calculate_weighted_vector(
        self,
        vectors: List[Tuple[float, float, float]],
    ) -> Tuple[float, float]:
        """Calculate weighted average of multiple direction vectors.
        
        Args:
            vectors: List of (x, y, weight) tuples
        
        Returns:
            Normalized weighted direction vector
        """
        if not vectors:
            _LOGGER.warning("No vectors provided for weighted calculation")
            return (0.0, 0.0)
        
        total_weight = sum(v[2] for v in vectors)
        
        if total_weight == 0:
            _LOGGER.warning("Total weight is zero")
            return (0.0, 0.0)
        
        # Calculate weighted average
        weighted_x = sum(v[0] * v[2] for v in vectors) / total_weight
        weighted_y = sum(v[1] * v[2] for v in vectors) / total_weight
        
        # Normalize result
        magnitude = math.sqrt(weighted_x**2 + weighted_y**2)
        
        if magnitude == 0:
            return (0.0, 0.0)
        
        return (weighted_x / magnitude, weighted_y / magnitude)
    
    def calculate_sequence_vector(
        self,
        sequence: MotionSequence,
    ) -> Tuple[float, float]:
        """Calculate direction vector for entire motion sequence.
        
        Uses time-based and reliability-based weighting for sensor pairs
        (see Appendix A.1).
        
        Args:
            sequence: Motion sequence to analyze
        
        Returns:
            Normalized weighted direction vector
        """
        if len(sequence.events) < 2:
            _LOGGER.debug("Sequence has less than 2 events")
            return (0.0, 0.0)
        
        vectors = []
        weights = []
        
        # Calculate vectors between consecutive sensor pairs
        for i in range(len(sequence.events) - 1):
            s1 = sequence.events[i]
            s2 = sequence.events[i + 1]
            
            # Skip if same sensor
            if s1.sensor.entity_id == s2.sensor.entity_id:
                continue
            
            # Calculate direction vector
            dx = s2.sensor.position[0] - s1.sensor.position[0]
            dy = s2.sensor.position[1] - s1.sensor.position[1]
            
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude > 0:
                vectors.append((dx / magnitude, dy / magnitude))
            else:
                continue
            
            # Calculate weight based on time and reliability
            time_diff = (s2.timestamp - s1.timestamp).total_seconds()
            time_weight = 1.0 / (1.0 + time_diff)  # Prefer closer events
            reliability_weight = (s1.sensor.reliability + s2.sensor.reliability) / 2
            
            weights.append(time_weight * reliability_weight)
        
        if not vectors:
            _LOGGER.debug("No valid vectors in sequence")
            return (0.0, 0.0)
        
        # Weighted average
        total_weight = sum(weights)
        weighted_x = sum(v[0] * w for v, w in zip(vectors, weights)) / total_weight
        weighted_y = sum(v[1] * w for v, w in zip(vectors, weights)) / total_weight
        
        # Final normalization
        final_magnitude = math.sqrt(weighted_x**2 + weighted_y**2)
        if final_magnitude > 0:
            normalized_vector = (
                weighted_x / final_magnitude,
                weighted_y / final_magnitude,
            )
            _LOGGER.debug(
                "Sequence vector: (%.3f, %.3f) from %d events",
                normalized_vector[0],
                normalized_vector[1],
                len(sequence.events),
            )
            return normalized_vector
        
        return (0.0, 0.0)
    
    def calculate_confidence(self, sequence: MotionSequence) -> float:
        """Calculate confidence score for direction detection.
        
        Combines multiple factors using weighted formula (Appendix A.3):
        C = α·Cs + β·Ct + γ·Csp + δ·Cr
        
        Args:
            sequence: Motion sequence to analyze
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if len(sequence.events) < 2:
            return 0.0
        
        # Factor 1: Sensor count confidence (more sensors = better)
        sensor_confidence = min(len(sequence.events) / 5.0, 1.0)
        
        # Factor 2: Temporal consistency (regular intervals = better)
        time_diffs = []
        for i in range(1, len(sequence.events)):
            diff = (
                sequence.events[i].timestamp - sequence.events[i - 1].timestamp
            ).total_seconds()
            time_diffs.append(diff)
        
        if time_diffs:
            avg_diff = sum(time_diffs) / len(time_diffs)
            if avg_diff == 0:
                temporal_confidence = 0.5
            else:
                variance = sum((d - avg_diff) ** 2 for d in time_diffs) / len(time_diffs)
                # Lower variance = higher confidence
                temporal_confidence = 1.0 / (1.0 + variance)
        else:
            temporal_confidence = 0.5
        
        # Factor 3: Spatial consistency (linear path = better)
        spatial_confidence = self._calculate_spatial_consistency(sequence)
        
        # Factor 4: Sensor reliability (average of all sensors)
        reliability_confidence = sum(
            event.sensor.reliability for event in sequence.events
        ) / len(sequence.events)
        
        # Combine using weights
        confidence = (
            self.alpha * sensor_confidence
            + self.beta * temporal_confidence
            + self.gamma * spatial_confidence
            + self.delta * reliability_confidence
        )
        
        # Clamp to [0, 1]
        confidence = max(0.0, min(confidence, 1.0))
        
        _LOGGER.debug(
            "Confidence: %.3f (sensors=%.3f, temporal=%.3f, spatial=%.3f, reliability=%.3f)",
            confidence,
            sensor_confidence,
            temporal_confidence,
            spatial_confidence,
            reliability_confidence,
        )
        
        return confidence
    
    def _calculate_spatial_consistency(self, sequence: MotionSequence) -> float:
        """Calculate spatial consistency of motion path.
        
        Measures how linear the path is by comparing individual vectors
        to the overall direction vector.
        
        Args:
            sequence: Motion sequence to analyze
        
        Returns:
            Spatial consistency score between 0.0 and 1.0
        """
        if len(sequence.events) < 3:
            return 0.8  # Assume reasonable consistency for 2 sensors
        
        # Get overall direction vector
        overall_vector = self.calculate_sequence_vector(sequence)
        
        if overall_vector == (0.0, 0.0):
            return 0.0
        
        # Calculate individual vectors and compare to overall
        deviations = []
        
        for i in range(len(sequence.events) - 1):
            s1 = sequence.events[i]
            s2 = sequence.events[i + 1]
            
            if s1.sensor.entity_id == s2.sensor.entity_id:
                continue
            
            # Calculate individual vector
            dx = s2.sensor.position[0] - s1.sensor.position[0]
            dy = s2.sensor.position[1] - s1.sensor.position[1]
            
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude == 0:
                continue
            
            individual_vector = (dx / magnitude, dy / magnitude)
            
            # Calculate dot product (cosine similarity)
            dot_product = (
                individual_vector[0] * overall_vector[0]
                + individual_vector[1] * overall_vector[1]
            )
            
            # Deviation from overall direction (0 = same, 2 = opposite)
            deviation = 1.0 - dot_product
            deviations.append(deviation)
        
        if not deviations:
            return 0.8
        
        # Lower average deviation = higher consistency
        avg_deviation = sum(deviations) / len(deviations)
        consistency = 1.0 - (avg_deviation / 2.0)  # Normalize to [0, 1]
        
        return max(0.0, min(consistency, 1.0))
    
    @staticmethod
    def angle_to_direction(angle_degrees: float) -> str:
        """Convert angle in degrees to direction name.
        
        Args:
            angle_degrees: Angle in degrees (0 = East, 90 = North)
        
        Returns:
            Direction name (e.g., "north", "east", "north_east")
        """
        # Normalize angle to [0, 360)
        angle = angle_degrees % 360
        
        # Define direction ranges (centered on cardinal/intercardinal directions)
        directions = [
            (337.5, 22.5, "east"),
            (22.5, 67.5, "north_east"),
            (67.5, 112.5, "north"),
            (112.5, 157.5, "north_west"),
            (157.5, 202.5, "west"),
            (202.5, 247.5, "south_west"),
            (247.5, 292.5, "south"),
            (292.5, 337.5, "south_east"),
        ]
        
        for start, end, direction_name in directions:
            if start > end:  # Wrap around 0
                if angle >= start or angle < end:
                    return direction_name
            elif start <= angle < end:
                return direction_name
        
        return "unknown"
    
    @staticmethod
    def vector_to_angle(vector: Tuple[float, float]) -> float:
        """Convert direction vector to angle in degrees.
        
        Args:
            vector: Direction vector (dx, dy)
        
        Returns:
            Angle in degrees (0 = East, 90 = North, 180 = West, 270 = South)
        """
        if vector == (0.0, 0.0):
            return 0.0
        
        angle_rad = math.atan2(vector[1], vector[0])
        angle_deg = math.degrees(angle_rad)
        
        # Convert to standard compass format (0 = North)
        # atan2 gives: 0 = East, 90 = North, -90 = South
        compass_angle = (90 - angle_deg) % 360
        
        return compass_angle
