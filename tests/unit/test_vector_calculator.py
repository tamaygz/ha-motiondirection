"""Unit tests for vector calculator."""
import math

import pytest

from custom_components.motiondirection.core.vector_calculator import VectorCalculator
from custom_components.motiondirection.models import PathPoint


# ===== Distance Calculation Tests =====


def test_calculate_distance_horizontal():
    """Test distance calculation for horizontal movement."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=0.0)
    p2 = PathPoint(x=5.0, y=0.0)
    
    distance = calculator.calculate_distance(p1, p2)
    assert distance == 5.0


def test_calculate_distance_vertical():
    """Test distance calculation for vertical movement."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=0.0)
    p2 = PathPoint(x=0.0, y=3.0)
    
    distance = calculator.calculate_distance(p1, p2)
    assert distance == 3.0


def test_calculate_distance_diagonal():
    """Test distance calculation for diagonal movement."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=0.0)
    p2 = PathPoint(x=3.0, y=4.0)
    
    distance = calculator.calculate_distance(p1, p2)
    assert distance == 5.0  # 3-4-5 triangle


def test_calculate_distance_same_point():
    """Test distance calculation for same point."""
    calculator = VectorCalculator()
    p = PathPoint(x=5.0, y=5.0)
    
    distance = calculator.calculate_distance(p, p)
    assert distance == 0.0


def test_calculate_distance_negative_coordinates():
    """Test distance calculation with negative coordinates."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=-5.0, y=-5.0)
    p2 = PathPoint(x=5.0, y=5.0)
    
    distance = calculator.calculate_distance(p1, p2)
    expected = math.sqrt(200)  # sqrt((10^2 + 10^2))
    assert abs(distance - expected) < 0.001


# ===== Angle Calculation Tests =====


def test_calculate_angle_east():
    """Test angle calculation for eastward movement."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=0.0)
    p2 = PathPoint(x=5.0, y=0.0)
    
    angle = calculator.calculate_angle(p1, p2)
    assert angle == 90.0  # East is 90° in our coordinate system


def test_calculate_angle_north():
    """Test angle calculation for northward movement."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=0.0)
    p2 = PathPoint(x=0.0, y=5.0)
    
    angle = calculator.calculate_angle(p1, p2)
    assert angle == 0.0  # North is 0°


def test_calculate_angle_west():
    """Test angle calculation for westward movement."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=5.0, y=0.0)
    p2 = PathPoint(x=0.0, y=0.0)
    
    angle = calculator.calculate_angle(p1, p2)
    assert angle == 270.0  # West is 270°


def test_calculate_angle_south():
    """Test angle calculation for southward movement."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=5.0)
    p2 = PathPoint(x=0.0, y=0.0)
    
    angle = calculator.calculate_angle(p1, p2)
    assert angle == 180.0  # South is 180°


def test_calculate_angle_northeast():
    """Test angle calculation for northeast movement."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=0.0)
    p2 = PathPoint(x=5.0, y=5.0)
    
    angle = calculator.calculate_angle(p1, p2)
    assert abs(angle - 45.0) < 0.1  # Northeast is approximately 45°


def test_calculate_angle_same_point():
    """Test angle calculation for same point."""
    calculator = VectorCalculator()
    p = PathPoint(x=5.0, y=5.0)
    
    angle = calculator.calculate_angle(p, p)
    assert angle == 0.0  # Default to north for zero vector


def test_calculate_angle_range():
    """Test that angle is always in [0, 360) range."""
    calculator = VectorCalculator()
    
    # Test all four quadrants
    angles = []
    for x, y in [(5, 5), (-5, 5), (-5, -5), (5, -5)]:
        p1 = PathPoint(x=0.0, y=0.0)
        p2 = PathPoint(x=float(x), y=float(y))
        angle = calculator.calculate_angle(p1, p2)
        angles.append(angle)
        assert 0.0 <= angle < 360.0


# ===== Velocity Calculation Tests =====


def test_calculate_velocity_constant_speed():
    """Test velocity calculation with constant speed."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=0.0)
    p2 = PathPoint(x=10.0, y=0.0)
    time_delta = 2.0  # seconds
    
    velocity = calculator.calculate_velocity(p1, p2, time_delta)
    assert velocity == 5.0  # 10 meters / 2 seconds


def test_calculate_velocity_zero_time():
    """Test velocity calculation with zero time delta."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=0.0)
    p2 = PathPoint(x=10.0, y=0.0)
    
    velocity = calculator.calculate_velocity(p1, p2, 0.0)
    assert velocity == 0.0  # Should handle division by zero gracefully


def test_calculate_velocity_no_movement():
    """Test velocity calculation with no movement."""
    calculator = VectorCalculator()
    p = PathPoint(x=5.0, y=5.0)
    
    velocity = calculator.calculate_velocity(p, p, 1.0)
    assert velocity == 0.0


def test_calculate_velocity_slow_movement():
    """Test velocity calculation with slow movement."""
    calculator = VectorCalculator()
    p1 = PathPoint(x=0.0, y=0.0)
    p2 = PathPoint(x=0.1, y=0.0)
    
    velocity = calculator.calculate_velocity(p1, p2, 10.0)
    assert abs(velocity - 0.01) < 0.001  # 0.1 meters / 10 seconds


# ===== Vector Normalization Tests =====


def test_normalize_vector_unit():
    """Test normalizing a unit vector."""
    calculator = VectorCalculator()
    vector = (1.0, 0.0)
    
    normalized = calculator.normalize_vector(vector)
    assert abs(normalized[0] - 1.0) < 0.001
    assert abs(normalized[1] - 0.0) < 0.001


def test_normalize_vector_arbitrary():
    """Test normalizing an arbitrary vector."""
    calculator = VectorCalculator()
    vector = (3.0, 4.0)
    
    normalized = calculator.normalize_vector(vector)
    # Should be (0.6, 0.8) for 3-4-5 triangle
    assert abs(normalized[0] - 0.6) < 0.001
    assert abs(normalized[1] - 0.8) < 0.001


def test_normalize_vector_magnitude():
    """Test that normalized vector has magnitude 1."""
    calculator = VectorCalculator()
    vector = (5.0, 12.0)
    
    normalized = calculator.normalize_vector(vector)
    magnitude = math.sqrt(normalized[0]**2 + normalized[1]**2)
    assert abs(magnitude - 1.0) < 0.001


def test_normalize_zero_vector():
    """Test normalizing a zero vector."""
    calculator = VectorCalculator()
    vector = (0.0, 0.0)
    
    normalized = calculator.normalize_vector(vector)
    assert normalized == (0.0, 0.0)  # Should return zero vector


def test_normalize_negative_components():
    """Test normalizing vector with negative components."""
    calculator = VectorCalculator()
    vector = (-3.0, -4.0)
    
    normalized = calculator.normalize_vector(vector)
    assert abs(normalized[0] - (-0.6)) < 0.001
    assert abs(normalized[1] - (-0.8)) < 0.001


# ===== Direction Name Tests =====


def test_angle_to_direction_cardinal():
    """Test converting cardinal direction angles to names."""
    calculator = VectorCalculator()
    
    assert calculator.angle_to_direction(0.0) == "north"
    assert calculator.angle_to_direction(90.0) == "east"
    assert calculator.angle_to_direction(180.0) == "south"
    assert calculator.angle_to_direction(270.0) == "west"


def test_angle_to_direction_intercardinal():
    """Test converting intercardinal direction angles to names."""
    calculator = VectorCalculator()
    
    assert calculator.angle_to_direction(45.0) == "northeast"
    assert calculator.angle_to_direction(135.0) == "southeast"
    assert calculator.angle_to_direction(225.0) == "southwest"
    assert calculator.angle_to_direction(315.0) == "northwest"


def test_angle_to_direction_tolerance():
    """Test direction conversion with angle tolerance."""
    calculator = VectorCalculator()
    
    # Slightly off from exact north should still be north
    assert calculator.angle_to_direction(5.0) == "north"
    assert calculator.angle_to_direction(355.0) == "north"
    
    # Slightly off from exact east
    assert calculator.angle_to_direction(85.0) == "east"
    assert calculator.angle_to_direction(95.0) == "east"


def test_angle_to_direction_wraparound():
    """Test direction conversion with angle wraparound."""
    calculator = VectorCalculator()
    
    # 360° should be same as 0° (north)
    assert calculator.angle_to_direction(360.0) == "north"
    
    # Negative angles should wrap around
    assert calculator.angle_to_direction(-90.0) == "west"


# ===== Vector Operations Tests =====


def test_dot_product():
    """Test vector dot product calculation."""
    calculator = VectorCalculator()
    v1 = (1.0, 0.0)
    v2 = (0.0, 1.0)
    
    dot = calculator.dot_product(v1, v2)
    assert dot == 0.0  # Perpendicular vectors


def test_dot_product_parallel():
    """Test dot product of parallel vectors."""
    calculator = VectorCalculator()
    v1 = (1.0, 0.0)
    v2 = (2.0, 0.0)
    
    dot = calculator.dot_product(v1, v2)
    assert dot == 2.0


def test_dot_product_opposite():
    """Test dot product of opposite vectors."""
    calculator = VectorCalculator()
    v1 = (1.0, 0.0)
    v2 = (-1.0, 0.0)
    
    dot = calculator.dot_product(v1, v2)
    assert dot == -1.0


def test_vector_magnitude():
    """Test vector magnitude calculation."""
    calculator = VectorCalculator()
    
    assert calculator.vector_magnitude((3.0, 4.0)) == 5.0
    assert calculator.vector_magnitude((1.0, 0.0)) == 1.0
    assert calculator.vector_magnitude((0.0, 0.0)) == 0.0


def test_vector_similarity():
    """Test vector similarity calculation."""
    calculator = VectorCalculator()
    
    # Same direction
    v1 = (1.0, 0.0)
    v2 = (1.0, 0.0)
    assert calculator.vector_similarity(v1, v2) == 1.0
    
    # Opposite directions
    v3 = (-1.0, 0.0)
    assert calculator.vector_similarity(v1, v3) == -1.0
    
    # Perpendicular
    v4 = (0.0, 1.0)
    assert abs(calculator.vector_similarity(v1, v4)) < 0.001
