# HA-MotionDirection Developer Guide

Comprehensive guide for developers contributing to or extending the HA-MotionDirection integration.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Extension Points](#extension-points)
5. [Development Setup](#development-setup)
6. [Code Standards](#code-standards)
7. [Testing Strategy](#testing-strategy)
8. [Contribution Guidelines](#contribution-guidelines)
9. [Debugging Tips](#debugging-tips)
10. [Performance Considerations](#performance-considerations)

---

## Architecture Overview

### High-Level Design

HA-MotionDirection uses a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                   Home Assistant                    │
│              (Event Bus, State Machine)             │
└─────────────────────┬───────────────────────────────┘
                      │
                      ├── Config Flow
                      │   └── Setup & Configuration
                      │
┌─────────────────────▼───────────────────────────────┐
│              Coordinator (async)                    │
│  - Orchestrates detection lifecycle                 │
│  - Manages entity updates                           │
│  - Handles service calls                            │
└─────────────────────┬───────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
┌─────────▼──┐  ┌────▼────┐  ┌──▼──────────┐
│  Entities  │  │Managers │  │   Storage   │
│  - Sensors │  │- Floor  │  │ (JSON/HA)   │
│  - Binary  │  │- Zone   │  └─────────────┘
│  - Status  │  │- Hybrid │
└────────────┘  └────┬────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼───┐  ┌────▼─────┐  ┌──▼──────────┐
│ Detection │  │ Pattern  │  │  Event Bus  │
│ - Vector  │  │ Analyzer │  │  - Motion   │
│ - Zone    │  │ - Learn  │  │  - Zone     │
│ - Hybrid  │  │ - Anomaly│  │  - Cue      │
└───────────┘  └──────────┘  └─────────────┘
```

### Data Flow

**1. Motion Event Detection:**

```
Sensor State Change → EventCollector → TimeWindowCorrelator → 
VectorCalculator → MotionDetector → Coordinator → Entity Update
```

**2. Zone-Based Detection:**

```
Motion Path → TriggerZoneManager → Zone Matching → Direction Config → 
Zone Transition Event → Zone Sensor Update
```

**3. Hybrid Detection (Motion + Cues):**

```
Motion Event + Cue State Change → HybridMotionDetector → 
Correlation Analysis → Confidence Boost → Direction Result
```

**4. Pattern Learning:**

```
Historical Events → PatternAnalyzer → Signature Matching → 
Pattern Storage → Anomaly Detection → User Notifications
```

### Component Relationships

```
┌──────────────┐     uses      ┌──────────────────┐
│ Coordinator  │ ───────────────▶│ MotionDetector  │
└──────┬───────┘                └─────────┬────────┘
       │                                  │
       │ manages                          │ uses
       │                                  │
┌──────▼───────┐                ┌────────▼────────┐
│   Entities   │                │ VectorCalculator│
│  (Sensors)   │                └────────┬────────┘
└──────────────┘                         │
                                         │ uses
                                         │
                               ┌─────────▼──────────┐
                               │TimeWindowCorrelator│
                               └─────────┬──────────┘
                                         │
                                         │ uses
                                         │
                                ┌────────▼──────────┐
                                │  EventCollector   │
                                └───────────────────┘
```

---

## Project Structure

```
ha-motiondirection/
├── custom_components/
│   └── motiondirection/
│       ├── __init__.py           # Integration entry point, setup, services
│       ├── manifest.json         # Integration metadata
│       ├── strings.json          # User-facing strings
│       ├── services.yaml         # Service definitions
│       ├── config_flow.py        # Configuration UI
│       ├── config_schema.py      # YAML config validation
│       ├── const.py              # Constants and enums
│       ├── coordinator.py        # DataUpdateCoordinator
│       ├── sensor.py             # Sensor entities
│       ├── binary_sensor.py      # Binary sensor entities
│       ├── event_data.py         # Event data models
│       ├── event_bus.py          # Event firing utility
│       │
│       ├── models/               # Data models (dataclasses)
│       │   ├── __init__.py
│       │   ├── sensor_node.py
│       │   ├── motion_event.py
│       │   ├── motion_path.py
│       │   ├── motion_sequence.py
│       │   ├── floorplan.py
│       │   ├── trigger_zone_model.py
│       │   ├── secondary_cue_model.py
│       │   ├── pattern_models.py
│       │   └── cue_type_registry.py
│       │
│       ├── core/                 # Core logic (algorithms)
│       │   ├── __init__.py
│       │   ├── event_collector.py
│       │   ├── time_window_correlator.py
│       │   ├── vector_calculator.py
│       │   ├── motion_detector.py
│       │   ├── floorplan_manager.py
│       │   ├── trigger_zone_manager.py
│       │   ├── hybrid_detector.py
│       │   └── pattern_analyzer.py
│       │
│       ├── frontend/             # Frontend components
│       │   ├── motion-status-card.js
│       │   └── README.md
│       │
│       └── translations/         # Localization files
│           └── en.json
│
├── tests/                        # Test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_vector_calculator.py
│   │   ├── test_correlator.py
│   │   └── test_motion_detector.py
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   ├── test_coordinator.py
│   │   └── test_services.py
│   └── performance/             # Performance tests
│       ├── __init__.py
│       └── test_detection_performance.py
│
├── docs/                        # Documentation
│   ├── USER_GUIDE.md
│   ├── API_REFERENCE.md
│   └── DEVELOPER_GUIDE.md (this file)
│
├── README.md                    # Project overview
├── pyproject.toml              # Python dependencies, tool configs
├── pytest.ini                  # Pytest configuration
├── .pre-commit-config.yaml     # Pre-commit hooks
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── hacs.json                   # HACS metadata
└── specs.md                    # Original specifications
```

### Module Responsibilities

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `__init__.py` | Integration setup, service registration | `async_setup_entry()` |
| `coordinator.py` | Orchestration, data updates | `MotionDirectionCoordinator` |
| `sensor.py` | Sensor entity platform | `MotionDirectionSensor`, `MotionPatternSensor` |
| `binary_sensor.py` | Binary sensor platform | `MotionDetectedBinarySensor`, `MotionAnomalyBinarySensor` |
| `models/*` | Data structures | All dataclasses |
| `core/*` | Detection algorithms | Detectors, calculators, managers |
| `event_data.py` | Event schemas | Event dataclasses |
| `event_bus.py` | Event firing | `EventBus` utility |
| `config_flow.py` | UI configuration | `MotionDirectionConfigFlow` |
| `config_schema.py` | YAML validation | Voluptuous schemas |

---

## Core Components

### 1. MotionDirectionCoordinator

**Location:** `coordinator.py`

**Purpose:** Central orchestrator for all motion detection activities. Extends `DataUpdateCoordinator` from Home Assistant.

**Key Responsibilities:**
- Manage motion event processing lifecycle
- Coordinate updates to all entities
- Handle service calls
- Manage storage operations
- Fire custom events

**Key Methods:**

```python
async def _async_update_data(self) -> dict:
    """Fetch data from detection systems."""
    # Called periodically to update entity states
    
async def async_process_motion_event(self, event: Event):
    """Process a motion sensor state change."""
    # Main entry point for motion events
    
async def async_detect_direction(self):
    """Perform direction detection."""
    # Calls motion detector, updates entities
    
async def track_pattern_occurrence(self, signature: str):
    """Track a pattern occurrence for learning."""
    
async def detect_anomaly(self, current_result: DirectionResult):
    """Check for anomalies in current detection."""
```

**Extension Points:**
- Override `_async_update_data()` for custom update logic
- Add new event handlers via `async_track_state_change_event()`
- Extend storage schema in `_async_load_data()`

---

### 2. MotionDetector

**Location:** `core/motion_detector.py`

**Purpose:** High-level motion direction detection using vector-based analysis.

**Key Methods:**

```python
async def detect_direction(self, events: list[MotionEvent]) -> DirectionResult | None:
    """Detect motion direction from event sequence."""
    # Uses correlator → vector calculator → confidence scoring
    
def _calculate_direction_name(self, vector: tuple[float, float]) -> str:
    """Convert vector to compass direction."""
    # Maps (x, y) to "north", "northeast", etc.
```

**Algorithm:**
1. Correlate events within time window
2. Calculate weighted direction vector
3. Compute multi-factor confidence score
4. Map vector to direction name

---

### 3. VectorCalculator

**Location:** `core/vector_calculator.py`

**Purpose:** Calculate direction vectors and confidence scores with mathematical precision.

**Key Methods:**

```python
def calculate_direction_vector(
    self,
    sensor1: SensorNode,
    sensor2: SensorNode
) -> tuple[float, float]:
    """Calculate normalized direction vector between two sensors."""
    
def calculate_weighted_vector(
    self,
    sequence: MotionSequence
) -> tuple[tuple[float, float], float]:
    """Calculate weighted average vector for entire sequence."""
    
def calculate_confidence(
    self,
    sequence: MotionSequence,
    vector: tuple[float, float]
) -> float:
    """Calculate multi-factor confidence score (0.0-1.0)."""
```

**Confidence Factors:**
- **Sensor Count** (α=0.3): More sensors = higher confidence
- **Temporal Consistency** (β=0.2): Consistent timing = higher confidence
- **Spatial Consistency** (γ=0.2): Alignment with vector = higher confidence
- **Sensor Reliability** (δ=0.3): Reliable sensors = higher confidence

**Formula:**

$$
C_{total} = α·C_{count} + β·C_{temporal} + γ·C_{spatial} + δ·C_{reliability}
$$

---

### 4. TriggerZoneManager

**Location:** `core/trigger_zone_manager.py`

**Purpose:** Manage trigger zones and detect zone-based direction transitions.

**Key Methods:**

```python
async def detect_zone_transition(
    self,
    path: MotionPath
) -> ZoneTransition | None:
    """Detect zone transition from motion path."""
    # Returns transition with direction, confidence, timing
    
def _find_entry_point(self, zone: TriggerZone, path: MotionPath) -> PathPoint:
    """Find where path entered zone."""
    
def _find_exit_point(self, zone: TriggerZone, path: MotionPath) -> PathPoint:
    """Find where path exited zone."""
    
def _match_direction(
    self,
    zone: TriggerZone,
    entry: PathPoint,
    exit: PathPoint
) -> DirectionConfig | None:
    """Match entry/exit to configured direction."""
```

**Zone Detection Algorithm:**
1. Check path points against zone polygons (ray casting)
2. Identify entry and exit points
3. Calculate entry→exit vector
4. Match vector against configured directions
5. Calculate zone-specific confidence

---

### 5. HybridMotionDetector

**Location:** `core/hybrid_detector.py`

**Purpose:** Combine motion sensor data with secondary cues for enhanced detection.

**Key Methods:**

```python
async def process_motion_event(
    self,
    motion_event: MotionEvent,
    motion_sequence: MotionSequence
) -> DirectionResult:
    """Process motion with cue correlation."""
    
async def _find_correlated_cues(
    self,
    motion_time: datetime,
    motion_location: PathPoint
) -> list[tuple[SecondaryCue, StateChange]]:
    """Find cues that correlate with motion."""
    # Temporal + spatial correlation
    
def _calculate_hybrid_direction(
    self,
    base_result: DirectionResult,
    correlated_cues: list
) -> DirectionResult:
    """Combine base detection with cue hints."""
    # Confidence boosting, direction refinement
```

**Cue Correlation:**
- **Temporal Window:** ±5 seconds by default (configurable per cue type)
- **Spatial Radius:** Distance-based weighting
- **State Changes:** Match configured state transitions
- **Confidence Boost:** 0.15 default (configurable)

---

### 6. PatternAnalyzer

**Location:** `core/pattern_analyzer.py`

**Purpose:** Analyze motion sequences for patterns and learn from historical data.

**Key Methods:**

```python
async def analyze_sequence(
    self,
    sequence: MotionSequence
) -> PatternType:
    """Classify sequence into pattern type."""
    # Returns: linear, circular, zone_transition, stationary, random, anomaly
    
async def learn_patterns(
    self,
    history: deque[MotionSequence]
) -> list[LearnedPattern]:
    """Extract learned patterns from historical data."""
    # Signature matching, occurrence counting
    
def _create_signature(self, sequence: MotionSequence) -> str:
    """Create unique signature for sequence."""
    # E.g., "sensor1→sensor2→sensor3"
```

**Pattern Types:**

| Type | Detection Criteria |
|------|-------------------|
| **Linear** | Consistent direction, straight path |
| **Circular** | Returns to origin, enclosed area |
| **Zone Transition** | Clear zone entry/exit |
| **Stationary** | Single location, repeated triggers |
| **Random** | No discernible pattern |
| **Anomaly** | Deviates from learned patterns |

---

### 7. EventBus

**Location:** `event_bus.py`

**Purpose:** Centralized event firing utility for consistent event handling.

**Key Methods:**

```python
def fire_direction_detected(
    hass: HomeAssistant,
    result: DirectionResult
):
    """Fire motiondirection_direction_detected event."""
    
def fire_zone_transition(
    hass: HomeAssistant,
    transition: ZoneTransition
):
    """Fire motiondirection_zone_transition event."""
```

**Event Naming Convention:** `motiondirection_<event_type>`

---

## Extension Points

### Adding a New Detection Method

**1. Create detector class in `core/`:**

```python
# core/my_new_detector.py
from typing import Optional
from ..models import MotionEvent, DirectionResult

class MyNewDetector:
    """Custom detection algorithm."""
    
    async def detect(self, events: list[MotionEvent]) -> Optional[DirectionResult]:
        # Your algorithm here
        return DirectionResult(
            direction="north",
            confidence=0.85,
            method="my_new_method",
            contributing_sensors=["sensor.test"]
        )
```

**2. Integrate into coordinator:**

```python
# coordinator.py
from .core.my_new_detector import MyNewDetector

class MotionDirectionCoordinator(DataUpdateCoordinator):
    def __init__(self, ...):
        # ... existing code ...
        self.my_detector = MyNewDetector()
    
    async def async_detect_direction(self):
        # Try your detector
        result = await self.my_detector.detect(self.motion_events)
        if result and result.confidence > self.confidence_threshold:
            return result
        
        # Fall back to existing detectors
        # ...
```

---

### Adding a New Cue Type

**1. Register cue type in `models/cue_type_registry.py`:**

```python
CUE_TYPES = {
    # ... existing types ...
    "custom_type": {
        "default_confidence": 0.20,
        "correlation_window": timedelta(seconds=10),
        "bidirectional": True,
        "typical_hints": [
            {
                "state_change": {"from_state": "off", "to_state": "on"},
                "implied_direction": "custom_direction",
                "confidence_weight": 0.8
            }
        ]
    }
}
```

**2. Use in secondary cue configuration:**

```yaml
secondary_cues:
  - entity_id: sensor.my_custom_sensor
    cue_type: "custom_type"
    location: {x: 10.0, y: 5.0}
```

---

### Adding a New Pattern Type

**1. Add to `PatternType` enum in `models/pattern_models.py`:**

```python
class PatternType(str, Enum):
    # ... existing types ...
    MY_PATTERN = "my_pattern"
```

**2. Add detection logic in `PatternAnalyzer`:**

```python
# core/pattern_analyzer.py

async def analyze_sequence(self, sequence: MotionSequence) -> PatternType:
    # ... existing checks ...
    
    if self._is_my_pattern(sequence):
        return PatternType.MY_PATTERN
    
    # ... rest of logic ...

def _is_my_pattern(self, sequence: MotionSequence) -> bool:
    """Check if sequence matches my custom pattern."""
    # Your pattern detection logic
    return True  # or False
```

---

### Adding a New Service

**1. Define in `services.yaml`:**

```yaml
my_custom_service:
  name: My Custom Service
  description: Does something cool
  fields:
    param1:
      description: First parameter
      required: true
      selector:
        text:
```

**2. Implement handler in `__init__.py`:**

```python
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # ... existing code ...
    
    async def handle_my_custom_service(call: ServiceCall):
        """Handle my custom service."""
        param1 = call.data.get("param1")
        
        # Your service logic here
        _LOGGER.info("Custom service called with: %s", param1)
        
        # Update entities if needed
        coordinator.async_set_updated_data({...})
    
    # Register service
    hass.services.async_register(
        DOMAIN,
        "my_custom_service",
        handle_my_custom_service,
        schema=vol.Schema({
            vol.Required("param1"): cv.string,
        })
    )
```

---

### Adding a New Sensor Entity

**1. Create sensor class in `sensor.py`:**

```python
class MyCustomSensor(CoordinatorEntity, SensorEntity):
    """My custom sensor."""
    
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._attr_name = "My Custom Sensor"
        self._attr_unique_id = f"{config_entry.entry_id}_my_custom"
        self._attr_native_unit_of_measurement = "custom_unit"
    
    @property
    def native_value(self):
        """Return sensor value."""
        return self.coordinator.data.get("my_custom_value", "unknown")
    
    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        return {
            "custom_attr1": "value1",
            "custom_attr2": "value2",
        }
```

**2. Add to entity setup:**

```python
async def async_setup_entry(...):
    # ... existing sensors ...
    entities.append(MyCustomSensor(coordinator, config_entry))
```

---

## Development Setup

### Prerequisites

- **Python 3.12+** (matching Home Assistant requirements)
- **Home Assistant Core** (for testing)
- **Git** (for version control)
- **VS Code** (recommended IDE)

### Initial Setup

**1. Clone the repository:**

```bash
git clone https://github.com/tamaygz/ha-motiondirection.git
cd ha-motiondirection
```

**2. Create virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install dependencies:**

```bash
pip install -e .
pip install -r requirements-dev.txt
```

**4. Install pre-commit hooks:**

```bash
pre-commit install
```

### Development Dependencies

Defined in `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-homeassistant-custom-component>=0.13.0",
    "pytest-asyncio>=0.21.0",
    "pytest-benchmark>=4.0.0",
    "black>=23.0.0",
    "pylint>=2.17.0",
    "mypy>=1.4.0",
    "pre-commit>=3.3.0",
]
```

### IDE Setup (VS Code)

**Recommended extensions:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- Pylint (ms-python.pylint)
- Home Assistant Config Helper (keesschollaart.vscode-home-assistant)

**Settings (`.vscode/settings.json`):**

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "editor.formatOnSave": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/.pytest_cache": true
    }
}
```

### Running Tests

**All tests:**

```bash
pytest
```

**Unit tests only:**

```bash
pytest tests/unit/
```

**Integration tests:**

```bash
pytest tests/integration/
```

**Performance tests:**

```bash
pytest tests/performance/ --benchmark-only
```

**With coverage:**

```bash
pytest --cov=custom_components.motiondirection --cov-report=html
```

---

## Code Standards

### Python Style Guide

We follow **PEP 8** with these specific guidelines:

**Line Length:**
- **88 characters** (Black default)
- Docstrings: **72 characters**

**Naming Conventions:**

```python
# Constants: UPPER_CASE
DEFAULT_TIME_WINDOW = 5000

# Classes: PascalCase
class MotionDetector:
    pass

# Functions/methods: snake_case
async def async_setup_entry():
    pass

# Private methods: _leading_underscore
def _calculate_confidence():
    pass

# Variables: snake_case
motion_event = MotionEvent(...)
```

### Type Hints

**Always use type hints** for function signatures:

```python
from typing import Optional, List, Tuple
from datetime import datetime

async def detect_direction(
    self,
    events: list[MotionEvent],
    time_window: float = 5.0
) -> Optional[DirectionResult]:
    """Detect motion direction from events."""
    ...
```

**For complex types:**

```python
from typing import Dict, Any, Callable

ConfigDict = Dict[str, Any]
CallbackType = Callable[[DirectionResult], None]
```

### Docstrings

Use **Google-style docstrings**:

```python
async def correlate_events(
    self,
    events: list[MotionEvent],
    window_size_ms: int = 5000
) -> list[MotionSequence]:
    """Correlate motion events within time windows.
    
    Groups events that occur within the specified time window into
    motion sequences. Events are sorted chronologically before processing.
    
    Args:
        events: List of motion events to correlate.
        window_size_ms: Time window size in milliseconds. Must be between
            MIN_WINDOW_SIZE and MAX_WINDOW_SIZE.
    
    Returns:
        List of motion sequences, each containing temporally correlated events.
        Empty list if no correlations found or fewer than 2 events provided.
    
    Raises:
        ValueError: If window_size_ms is outside valid range.
    
    Example:
        >>> events = [event1, event2, event3]
        >>> sequences = await correlator.correlate_events(events, 5000)
        >>> print(len(sequences))
        1
    """
    ...
```

### Async/Await Patterns

**Always use async for I/O operations:**

```python
# ✅ Correct
async def async_process_event(self, event: MotionEvent):
    await self.storage.async_save(event)
    await self.hass.async_add_executor_job(self._sync_operation)

# ❌ Incorrect
def process_event(self, event: MotionEvent):
    self.storage.save(event)  # Blocking!
```

**Use `async_add_executor_job` for CPU-intensive tasks:**

```python
result = await self.hass.async_add_executor_job(
    self._calculate_complex_pattern,
    large_dataset
)
```

### Logging

Use the standard logging pattern:

```python
import logging

_LOGGER = logging.getLogger(__name__)

# Log levels:
_LOGGER.debug("Detailed diagnostic: %s", data)
_LOGGER.info("Normal operation: %s", result)
_LOGGER.warning("Unexpected but handled: %s", issue)
_LOGGER.error("Error occurred: %s", error)
_LOGGER.exception("Exception with traceback")
```

**Logging best practices:**
- Use lazy formatting: `_LOGGER.info("Value: %s", value)` not `f"Value: {value}"`
- Don't log sensitive information (user data, credentials)
- Use appropriate log levels
- Include context in error messages

### Error Handling

**Always handle exceptions gracefully:**

```python
try:
    result = await self.async_detect_direction()
except ValueError as err:
    _LOGGER.error("Invalid configuration: %s", err)
    return None
except Exception as err:
    _LOGGER.exception("Unexpected error during detection: %s", err)
    raise HomeAssistantError(f"Detection failed: {err}") from err
```

---

## Testing Strategy

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Fast, isolated tests
│   ├── test_models.py       # Dataclass tests
│   ├── test_vector_calculator.py
│   └── test_correlator.py
├── integration/             # HA integration tests
│   ├── test_coordinator.py
│   └── test_services.py
└── performance/             # Benchmark tests
    └── test_detection_performance.py
```

### Unit Test Example

```python
# tests/unit/test_vector_calculator.py
import pytest
from custom_components.motiondirection.core.vector_calculator import VectorCalculator
from custom_components.motiondirection.models import SensorNode

@pytest.fixture
def calculator():
    """Fixture for vector calculator."""
    return VectorCalculator()

@pytest.fixture
def sensor1():
    """First test sensor."""
    return SensorNode("sensor.test1", x=0.0, y=0.0, range_meters=3.0)

@pytest.fixture
def sensor2():
    """Second test sensor."""
    return SensorNode("sensor.test2", x=5.0, y=0.0, range_meters=3.0)

def test_calculate_direction_vector_east(calculator, sensor1, sensor2):
    """Test eastward vector calculation."""
    vector = calculator.calculate_direction_vector(sensor1, sensor2)
    
    assert vector == (1.0, 0.0), "Should return normalized east vector"

def test_calculate_direction_vector_zero_distance(calculator, sensor1):
    """Test handling of zero-distance sensors."""
    with pytest.raises(ValueError, match="same position"):
        calculator.calculate_direction_vector(sensor1, sensor1)
```

### Integration Test Example

```python
# tests/integration/test_services.py
import pytest
from homeassistant.core import HomeAssistant
from custom_components.motiondirection.const import DOMAIN

@pytest.mark.asyncio
async def test_update_floorplan_service(hass: HomeAssistant, coordinator):
    """Test update_floorplan service call."""
    # Arrange
    service_data = {
        "floorplan_id": "test_floor",
        "width": 10.0,
        "height": 10.0,
        "sensors": [
            {"entity_id": "binary_sensor.test1", "x": 5.0, "y": 5.0, "range_meters": 3.0}
        ]
    }
    
    # Act
    await hass.services.async_call(
        DOMAIN,
        "update_floorplan",
        service_data,
        blocking=True
    )
    
    # Assert
    assert coordinator.floorplan_manager.floorplans.get("test_floor") is not None
    assert coordinator.floorplan_manager.floorplans["test_floor"].width == 10.0
```

### Performance Test Example

```python
# tests/performance/test_detection_performance.py
import pytest
from custom_components.motiondirection.models import MotionEvent
from datetime import datetime

@pytest.mark.benchmark(group="detection")
def test_detection_performance_50_sensors(benchmark, motion_detector, sensors_50):
    """Benchmark detection with 50 sensors."""
    events = [
        MotionEvent(s.entity_id, datetime.now(), "on")
        for s in sensors_50[:10]
    ]
    
    result = benchmark(motion_detector.detect_direction, events)
    
    assert result is not None
    # Should complete in < 100ms
```

### Coverage Requirements

- **Minimum coverage:** 80%
- **Critical paths:** 95% (detection, correlation, vector calculation)
- **Models:** 100% (dataclasses are simple)

**Check coverage:**

```bash
pytest --cov=custom_components.motiondirection --cov-report=term-missing
```

---

## Contribution Guidelines

### Workflow

**1. Fork and clone:**

```bash
git clone https://github.com/your-username/ha-motiondirection.git
cd ha-motiondirection
git remote add upstream https://github.com/tamaygz/ha-motiondirection.git
```

**2. Create feature branch:**

```bash
git checkout -b feature/my-new-feature
```

**3. Make changes:**
- Write code following style guide
- Add tests for new functionality
- Update documentation

**4. Run checks:**

```bash
# Format code
black custom_components/ tests/

# Run linter
pylint custom_components/

# Run type checker
mypy custom_components/

# Run tests
pytest

# Pre-commit hooks
pre-commit run --all-files
```

**5. Commit with conventional commits:**

```bash
git commit -m "feat: add new detection method"
git commit -m "fix: resolve zone boundary calculation"
git commit -m "docs: update API reference"
```

**6. Push and create PR:**

```bash
git push origin feature/my-new-feature
```

Then create a pull request on GitHub.

### Commit Message Format

Use **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

**Examples:**

```
feat(zones): add multi-zone transition detection

Implement detection for transitions involving multiple zones.
Adds new ZoneTransitionChain class to track sequences.

Closes #123
```

```
fix(vector): handle zero-magnitude vectors

Division by zero when normalizing vectors with no magnitude.
Now returns (0, 0) and logs warning.

Fixes #456
```

### Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows PEP 8 and project style guide
- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Tests added for new functionality
- [ ] All tests pass (`pytest`)
- [ ] Code coverage maintained or improved
- [ ] Pre-commit hooks pass
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (for user-facing changes)
- [ ] Commit messages follow conventional commits
- [ ] PR description explains changes clearly

### Code Review Process

**Reviewers will check:**
1. **Functionality:** Does it work as intended?
2. **Tests:** Are there adequate tests?
3. **Code Quality:** Is it maintainable and readable?
4. **Performance:** Are there any bottlenecks?
5. **Security:** Are there any vulnerabilities?
6. **Documentation:** Is it well-documented?

**Review turnaround:** Aim for 2-3 business days.

---

## Debugging Tips

### Enable Debug Logging

**In `configuration.yaml`:**

```yaml
logger:
  default: info
  logs:
    custom_components.motiondirection: debug
```

### Common Issues

**1. "Integration not found"**
- Check `manifest.json` is valid JSON
- Ensure `domain` matches folder name
- Restart Home Assistant

**2. "Service not found"**
- Check service registration in `__init__.py`
- Verify `services.yaml` syntax
- Check logs for registration errors

**3. "Entity not updating"**
- Verify coordinator `async_set_updated_data()` is called
- Check entity's `_handle_coordinator_update()` method
- Ensure `available` property returns `True`

**4. "Events not firing"**
- Check `event_bus.fire_*()` calls
- Verify event data is JSON-serializable
- Use Developer Tools > Events to listen

### Using Debugger

**VS Code `launch.json`:**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Home Assistant",
            "type": "python",
            "request": "attach",
            "port": 5678,
            "host": "localhost",
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/custom_components/motiondirection",
                    "remoteRoot": "/config/custom_components/motiondirection"
                }
            ]
        }
    ]
}
```

**In code:**

```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```

### Diagnostic Service

Use the `motiondirection.get_status` service to get diagnostic information:

```yaml
service: motiondirection.get_status
```

Returns:
- Version information
- Coordinator status
- Detection statistics
- Configuration summary
- Entity states

---

## Performance Considerations

### Optimization Tips

**1. Event Batching**

Avoid processing events one by one:

```python
# ❌ Slow
for event in events:
    await self.async_process_event(event)

# ✅ Fast
await self.async_process_batch(events)
```

**2. Caching**

Cache expensive calculations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
```

**3. Lazy Loading**

Don't load historical data unless needed:

```python
# ❌ Loads all history on startup
self.history = await self.storage.async_load_all()

# ✅ Loads on demand
async def get_history(self):
    if self._history is None:
        self._history = await self.storage.async_load_all()
    return self._history
```

**4. Efficient Data Structures**

Use appropriate structures for the use case:

```python
# For quick lookups: dict
self.sensors = {s.entity_id: s for s in sensors}

# For ordered iteration: list
self.events = [e1, e2, e3]

# For fixed-size buffers: deque
from collections import deque
self.history = deque(maxlen=1000)
```

### Performance Targets

| Metric | Target |
|--------|--------|
| **Event Processing** | < 50ms per event |
| **Direction Detection** | < 100ms |
| **Zone Matching** | < 10ms |
| **Pattern Analysis** | < 200ms |
| **Memory Usage** | < 50MB base, < 100MB with history |
| **CPU Usage** | < 5% average, < 15% peak |

### Profiling

**Use cProfile for detailed profiling:**

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
await self.async_detect_direction()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

**Or use pytest-benchmark:**

```bash
pytest tests/performance/ --benchmark-only --benchmark-autosave
```

---

## Additional Resources

- [Home Assistant Developer Documentation](https://developers.home-assistant.io/)
- [User Guide](USER_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Project Specifications](../specs.md)
- [GitHub Issues](https://github.com/tamaygz/ha-motiondirection/issues)

---

**Questions or need help?** Open an issue on GitHub or join the discussion!
