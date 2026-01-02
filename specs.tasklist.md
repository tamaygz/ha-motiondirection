# HA-MotionDirection Development Task List

**Project Version:** 1.3.0  
**Last Updated:** 2026-01-02  
**Specs Reference:** specs.md

## Task Status Legend
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Complete
- 🔵 Blocked

---

## 1. Project Setup & Infrastructure

### 1.1 Repository Setup
**Status:** � Complete  
**Complexity:** Low  
**Specs Reference:** Lines 29-63  
**Description:** Set up the complete project structure for the Home Assistant custom integration.

**Tasks:**
- [x] Create repository structure following HA custom component standards
- [x] Set up `custom_components/motiondirection/` directory
- [x] Create `tests/` directory with subdirectories for unit, integration, performance tests
- [x] Create `README.md` with project overview
- [x] Create `pyproject.toml` with Python dependencies and dev dependencies
- [x] Create `hacs.json` for HACS integration (Lines 2051-2060)
- [x] Set up `.gitignore` for Python/HA projects
- [x] Create `LICENSE` file (MIT License, Lines 2461-2488)

**Dependencies:** None

---

### 1.2 Integration Metadata Files
**Status:** 🟢 Complete  
**Complexity:** Low  
**Specs Reference:** Lines 29-63  
**Description:** Create core Home Assistant integration configuration files.

**Tasks:**
- [x] Create `manifest.json` with domain, name, version, dependencies, requirements
- [x] Create `strings.json` for localization (Lines 40)
- [x] Set up `translations/` directory with en.json
- [x] Create `services.yaml` service definitions (Lines 39, 1210-1388)
- [x] Create `__init__.py` for integration setup and entry point (Lines 31)

**Dependencies:** 1.1

---

### 1.3 Development Environment
**Status:** 🟢 Complete  
**Complexity:** Low  
**Specs Reference:** Lines 2403-2424  
**Description:** Set up development tooling and standards.

**Tasks:**
- [x] Create `pyproject.toml` for Black, pylint, mypy configuration
- [x] Set up pre-commit hooks (black, pylint, mypy, flake8)
- [x] Create `.pre-commit-config.yaml`
- [x] Create `pytest.ini` for test configuration
- [x] Set up virtual environment instructions in README
- [x] Create development setup script

**Dependencies:** 1.1

---

## 2. Core Models & Data Structures

### 2.1 Basic Data Models
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 29-63, 267-340  
**Description:** Implement fundamental dataclasses for sensors, events, and paths.

**Tasks:**
- [x] Create `models/sensor_node.py` with SensorNode dataclass (position, range, weight, type, reliability)
- [x] Create `models/motion_event.py` with MotionEvent dataclass (sensor, timestamp, state, confidence)
- [x] Create `models/motion_path.py` with MotionPath dataclass (points, sequence, confidence)
- [x] Create `models/motion_sequence.py` with MotionSequence dataclass
- [x] Add type hints and validation for all models
- [x] Add `__str__` and `__repr__` methods for debugging

**Dependencies:** 1.2

---

### 2.2 Floorplan Model
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 225-265, 905-1020  
**Description:** Implement floorplan configuration and management dataclass.

**Tasks:**
- [x] Create `models/floorplan.py` with Floorplan dataclass
- [x] Implement dimensions, scale, background image properties
- [x] Implement grid configuration (enabled, size, snap)
- [x] Implement layer management (background, sensors, cues, zones, paths)
- [x] Implement sensor list management
- [x] Implement zone list management
- [x] Implement secondary cue list management
- [x] Add import/export methods (YAML/JSON)

**Dependencies:** 2.1

---

### 2.3 Trigger Zone Models
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 267-340  
**Description:** Implement zone-related dataclasses with polygon geometry.

**Tasks:**
- [x] Create `models/trigger_zone_model.py` with TriggerZone dataclass
- [x] Implement polygon boundary storage and validation
- [x] Implement DirectionConfig dataclass (name, vector, entry_edge, exit_edge, aliases)
- [x] Implement `calculate_center()` method for polygon centroid
- [x] Implement `contains_point()` method using ray casting algorithm (Lines 303-316)
- [x] Implement `matches_vector()` method for direction matching (Lines 330-338)
- [x] Add zone state management (idle, occupied, transit)
- [x] Add min_dwell_time, max_transit_time, sensitivity properties

**Dependencies:** 2.1

---

### 2.4 Secondary Cue Models
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 425-479  
**Description:** Implement secondary cue system dataclasses.

**Tasks:**
- [x] Create `models/secondary_cue_model.py` with SecondaryCue dataclass
- [x] Implement DirectionalHint dataclass (state_change, implied_direction, confidence, condition)
- [x] Implement StateChange dataclass (from_state, to_state, attribute)
- [x] Add timing configuration (correlation_window, pre_trigger_window, post_trigger_window)
- [x] Add confidence weights (confidence_weight, reliability)
- [x] Add state configuration (trigger_states, ignore_states)
- [x] Add visual configuration (icon, color, range_radius)
- [x] Add cue type validation
- [x] Create `models/cue_type_registry.py` with CueTypeRegistry class

**Dependencies:** 2.1

---

### 2.5 Pattern Models
**Status:** � Complete  
**Complexity:** Low  
**Specs Reference:** Lines 737-903  
**Description:** Implement pattern analysis dataclasses.

**Tasks:**
- [x] Create `models/pattern_models.py` with PatternType enum (linear, circular, zone_transition, stationary, random, anomaly)
- [x] Create LearnedPattern dataclass (signature, occurrences, confidence, example)
- [x] Create ZoneTransition dataclass (zone_id, direction, entry_point, exit_point, dwell_time, confidence)
- [x] Create DirectionResult dataclass (direction, confidence, method, contributing_cues)
- [x] Update models/__init__.py to export all pattern models

**Dependencies:** 2.1, 2.3, 2.4

---

## 3. Motion Detection Engine

### 3.1 Event Collection System
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 92-102  
**Description:** Implement real-time motion sensor event monitoring and buffering.

**Tasks:**
- [x] Create `core/event_collector.py` module
- [x] Implement state change subscription to HA motion sensors
- [x] Implement microsecond precision timestamping
- [x] Implement event buffering with configurable size (default 100)
- [x] Implement debounce logic to reduce noise
- [x] Implement event filtering for invalid/duplicate events
- [x] Add async/await pattern for non-blocking operation
- [x] Add event queue management

**Dependencies:** 2.1, 1.2

---

### 3.2 Time Window Correlator
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 104-162, 2555-2568  
**Description:** Implement temporal correlation of motion events.

**Tasks:**
- [x] Create `core/time_window_correlator.py` with TimeWindowCorrelator class
- [x] Implement `correlate_events()` method (Lines 113-144)
- [x] Implement sliding window algorithm for event grouping
- [x] Support configurable window sizes (500ms - 30000ms, default 5000ms)
- [x] Implement event sorting by timestamp
- [x] Implement sequence formation logic
- [x] Filter sequences with < 2 events
- [x] Add window size validation and bounds checking
- [x] Implement algorithm from Appendix A.2 (Lines 2555-2568)

**Dependencies:** 2.1, 3.1

---

### 3.3 Vector Calculator
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 164-223, 2506-2552  
**Description:** Implement direction vector calculation and confidence scoring.

**Tasks:**
- [x] Create `core/vector_calculator.py` with VectorCalculator class
- [x] Implement `calculate_direction_vector()` for sensor pairs (Lines 169-180)
- [x] Implement `calculate_weighted_vector()` for multi-sensor sequences (Lines 182-203)
- [x] Implement `calculate_confidence()` with multi-factor scoring (Lines 205-223)
- [x] Implement confidence factors: sensor count, temporal consistency, spatial consistency, reliability
- [x] Use weighting: α=0.3 (sensor), β=0.2 (temporal), γ=0.2 (spatial), δ=0.3 (reliability) per Appendix A.3 (Lines 2570-2583)
- [x] Implement vector normalization
- [x] Implement detailed algorithm from Appendix A.1 (Lines 2506-2552)
- [x] Add bounds checking and error handling

**Dependencies:** 2.1, 3.2

---

### 3.4 Direction Detector
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 92-223  
**Description:** High-level motion direction detection orchestrator.

**Tasks:**
- [x] Create main detection pipeline in `core/motion_detector.py`
- [x] Integrate event collector, correlator, and vector calculator
- [x] Implement direction naming (north, south, east, west, etc.) from vectors
- [x] Implement multi-sensor detection method
- [x] Add confidence thresholding (configurable, default 0.7)
- [x] Fire `motiondirection_motion_detected` events
- [x] Update callback mechanism for entity updates
- [x] Add proper error handling and logging

**Dependencies:** 3.1, 3.2, 3.3

---

## 4. Floorplan Management

### 4.1 Floorplan Configuration
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 225-249  
**Description:** Implement floorplan canvas configuration and management.

**Tasks:**
- [x] Create `core/floorplan_manager.py` module
- [x] Implement floorplan creation with dimensions (width, height, scale)
- [x] Implement background image upload and storage
- [x] Implement grid configuration (enabled, size, snap-to-grid)
- [x] Implement layer management (z-index ordering)
- [x] Support pixel or meter-based coordinate systems
- [x] Validate floorplan configurations
- [x] Store floorplan data in HA storage

**Dependencies:** 2.2

---

### 4.2 Sensor Placement System
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 251-265  
**Description:** Implement sensor discovery and placement on floorplan.

**Tasks:**
- [x] Implement automatic entity discovery from HA registry
- [x] Filter for binary_sensor domain with motion/occupancy device classes
- [x] Implement sensor position storage (x, y coordinates)
- [x] Implement sensor range visualization (circular overlay)
- [x] Implement drag-and-drop position updates
- [x] Implement overlap detection algorithm
- [x] Show overlap warnings in UI
- [x] Implement snap-to-grid functionality
- [x] Support sensor range adjustment
- [x] Implement import/export of sensor configurations

**Dependencies:** 4.1, 2.1

---

## 5. Trigger Zones System

### 5.1 Zone Manager Core
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 342-423  
**Description:** Implement zone management and transition detection.

**Tasks:**
- [x] Create `core/zone_manager.py` with TriggerZoneManager class
- [x] Implement zone storage and retrieval (Lines 347-349)
- [x] Implement `detect_zone_transition()` method (Lines 351-393)
- [x] Implement `_find_entry_point()` method (Lines 395-399)
- [x] Implement `_find_exit_point()` method (Lines 401-407)
- [x] Implement `_match_direction()` method (Lines 409-421)
- [x] Implement `_calculate_dwell_time()` method (Lines 423-430)
- [x] Implement `_calculate_zone_confidence()` method (Lines 432-441)
- [x] Track active transits
- [x] Handle multi-zone scenarios

**Dependencies:** 2.3, 3.3

---

### 5.2 Zone Drawing and Creation
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1273-1287  
**Description:** Implement interactive zone polygon drawing and configuration UI.

**Note:** Implemented via Floorplan Editor Card (12.1). Core zone functionality includes both service/YAML configuration AND graphical/interactive zone editing.

**Tasks:**
- [x] Implement polygon drawing interface (click to add points)
- [x] Implement polygon editing (move/delete points)
- [x] Validate polygon (minimum 3 points, no self-intersection)
- [x] Implement direction configuration UI for zones
- [x] Support direction vector input (manual or click-based)
- [x] Implement direction aliases configuration
- [x] Store zone configurations
- [x] Implement zone deletion
- [x] Implement zone visibility toggle

**Files Created:**
- `frontend/floorplan-editor-card.js` - Full-featured floorplan editor with zone drawing
- `frontend/zone-editor-card.js` - Focused zone configuration and direction editing

**Dependencies:** 5.1, 4.1, 12.1, 12.3

---

### 5.3 Zone Services Implementation
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1249-1309  
**Description:** Implement zone-specific Home Assistant services.

**Tasks:**
- [x] Implement `motiondirection.calibrate_zone` service (Lines 1249-1256)
- [x] Implement `motiondirection.create_zone` service (Lines 1258-1272)
- [x] Implement `motiondirection.update_zone_direction` service (Lines 1274-1282)
- [x] Implement `motiondirection.test_zone_trigger` service (Lines 1284-1290)
- [x] Implement `motiondirection.analyze_zone_patterns` service (Lines 1294-1302)
- [x] Implement `motiondirection.learn_zone_directions` service (Lines 1304-1311)
- [x] Add service call validation
- [x] Add proper error handling and user feedback

**Dependencies:** 5.1, 5.2

---

### 5.4 Zone Sensors
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1102-1170  
**Description:** Create zone-specific sensor entities.

**Tasks:**
- [x] Create `sensor.zone_{id}_direction` entity (Lines 1104-1123)
- [x] Create `binary_sensor.zone_{id}_occupied` entity (Lines 1127-1138)
- [x] Create `binary_sensor.zone_{id}_transit` entity (Lines 1142-1152)
- [x] Create `sensor.zone_{id}_statistics` entity (Lines 1156-1170)
- [x] Implement proper state updates on zone transitions
- [x] Implement attribute updates (confidence, timing, sensors, etc.)
- [x] Implement statistics tracking (daily/hourly counts, averages)
- [x] Implement statistics reset at midnight

**Dependencies:** 5.1

---

### 5.5 Zone Events
**Status:** 🟢 Complete  
**Complexity:** Low  
**Specs Reference:** Lines 1454-1530  
**Description:** Implement zone-specific event firing.

**Tasks:**
- [x] Implement `motiondirection_zone_entered` event (Lines 1456-1465)
- [x] Implement `motiondirection_zone_exited` event (Lines 1467-1477)
- [x] Implement `motiondirection_zone_direction_detected` event (Lines 1479-1489)
- [x] Implement `motiondirection_zone_pattern_detected` event (Lines 1491-1500)
- [x] Fire events at appropriate times in zone transition lifecycle
- [x] Include all required event data as specified
- [x] Add event logging for debugging

**Dependencies:** 5.1

---

## 6. Secondary Cues System

### 6.1 Cue Type Registry
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 481-598  
**Description:** Implement the registry of supported cue types and their behaviors.

**Tasks:**
- [x] Create `core/cue_type_registry.py` with CueTypeRegistry class
- [x] Define 8 cue types with configurations: door, light, switch, presence, temperature, vibration, power, media (Lines 483-584)
- [x] Implement `get_cue_config()` class method (Lines 586-589)
- [x] Implement `is_valid_cue_type()` class method (Lines 591-594)
- [x] Store default confidence levels per type
- [x] Store typical correlation windows per type
- [x] Store default directional hints per type
- [x] Support bidirectional cues
- [x] Add extensibility via `register_custom_type()` method
- [x] Add helper methods for registry access
- [x] Update HybridMotionDetector to use registry for correlation windows
- [x] Export CueTypeRegistry from core/__init__.py

**Dependencies:** 2.4

---

### 6.2 Hybrid Motion Detector
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 600-735  
**Description:** Implement detection combining motion sensors with secondary cues.

**Tasks:**
- [x] Create `core/hybrid_detector.py` with HybridMotionDetector class
- [x] Implement motion and cue event buffering (Lines 607-609)
- [x] Implement `process_motion_event()` method (Lines 611-639)
- [x] Implement `_calculate_hybrid_direction()` method (Lines 641-671)
- [x] Implement `_find_correlated_cues()` method (Lines 673-690)
- [x] Implement `_is_spatially_correlated()` method (Lines 692-705)
- [x] Implement `_calculate_distance()` method (Lines 707-710)
- [x] Implement `_get_correlation_distance()` method (Lines 712-724)
- [x] Implement `_matches_state_change()` method (Lines 726-733)
- [x] Support detection methods: multi_sensor, hybrid, cue_assisted
- [x] Calculate combined confidence from multiple cues

**Dependencies:** 2.4, 3.3, 6.1

---

### 6.3 Cue Services Implementation
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1315-1371  
**Description:** Implement secondary cue management services.

**Tasks:**
- [x] Implement `motiondirection.add_secondary_cue` service (Lines 1317-1330)
- [x] Implement `motiondirection.configure_cue_hints` service (Lines 1332-1339)
- [x] Implement `motiondirection.analyze_cue_correlations` service (Lines 1341-1349)
- [x] Implement `motiondirection.learn_cue_patterns` service (Lines 1351-1359)
- [x] Implement `motiondirection.test_hybrid_detection` service (Lines 1361-1370)
- [x] Validate cue entity existence in HA
- [x] Validate cue type compatibility
- [x] Add service error handling

**Dependencies:** 6.1, 6.2

---

### 6.4 Cue Sensors
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1174-1208  
**Description:** Create secondary cue status and correlation sensors.

**Tasks:**
- [x] Create `sensor.secondary_cue_{id}` status entity (Lines 1176-1189)
- [x] Create `sensor.cue_correlation_analysis` entity (Lines 1193-1208)
- [x] Track cue trigger events and timing
- [x] Calculate correlation statistics (success rate, count)
- [x] Track active correlations with motion sensors
- [x] Update sensors on cue state changes
- [x] Implement top correlations tracking

**Dependencies:** 6.2

---

### 6.5 Cue Events
**Status:** 🟢 Complete  
**Complexity:** Low  
**Specs Reference:** Lines 1504-1567  
**Description:** Implement secondary cue event firing.

**Tasks:**
- [x] Implement `motiondirection_cue_triggered` event (Lines 1506-1517)
- [x] Implement `motiondirection_hybrid_detection` event (Lines 1519-1532)
- [x] Implement `motiondirection_cue_correlation_detected` event (Lines 1534-1544)
- [x] Implement `motiondirection_cue_pattern_learned` event (Lines 1546-1559)
- [x] Fire events at appropriate detection stages
- [x] Include all required event data
- [x] Add event logging

**Dependencies:** 6.2

---

### 6.6 Cue Correlation Analysis
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 1341-1349, 1870-1889  
**Description:** Implement correlation analysis and pattern learning.

**Tasks:**
- [x] Implement correlation strength calculation (exponential temporal decay)
- [x] Implement time offset analysis between cue and motion
- [x] Implement spatial correlation validation (Euclidean distance with type-specific thresholds)
- [x] Implement pattern detection (sequential, correlation, timing-based)
- [x] Store learned correlations (CorrelationStatistics tracking)
- [x] Generate suggestions for new cue configurations
- [x] Implement statistical tracking with CueCorrelationAnalyzer
- [x] Integrate with HybridMotionDetector for automatic recording
- [x] Support for analyze_correlations() and learn_patterns() methods
- [x] Temporal and spatial pattern identification
- [x] Confidence scoring with temporal decay weighting
- [x] Historical correlation analysis with configurable time periods

**Dependencies:** 6.2

---

## 7. Pattern Analysis

### 7.1 Pattern Analyzer Core
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 737-903  
**Description:** Implement pattern recognition and learning system.

**Tasks:**
- [x] Create `core/pattern_analyzer.py` with PatternAnalyzer class
- [x] Implement `analyze_sequence()` method (Lines 755-777)
- [x] Implement `_is_linear()` method (Lines 779-803)
- [x] Implement `_is_circular()` method (Lines 805-820)
- [x] Implement `_is_zone_transition()` method (Lines 822-830)
- [x] Implement `_is_stationary()` method (Lines 832-849)
- [x] Implement `learn_patterns()` method (Lines 851-883)
- [x] Implement `_create_signature()` method (Lines 885-889)
- [x] Implement `_calculate_vector()` helper (Lines 891-901)
- [x] Support 6 pattern types: linear, circular, zone_transition, stationary, random, anomaly
- [x] Store pattern history (deque, maxlen=1000)

**Dependencies:** 2.5, 3.3

---

### 7.2 Anomaly Detection
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 1090-1098, 1569-1580  
**Description:** Implement anomaly detection for unexpected patterns.

**Tasks:**
- [x] Create `binary_sensor.motion_anomaly` entity (Lines 1090-1098)
- [x] Implement expected vs actual pattern comparison
- [x] Calculate anomaly score based on deviation
- [x] Fire `motiondirection_anomaly_detected` event (Lines 1571-1580)
- [x] Track anomaly types: unexpected_path, unusual_timing, wrong_direction
- [x] Configurable sensitivity threshold (default 0.7)
- [x] Compare against learned patterns from pattern analyzer
- [x] Alert on significant deviations via event firing
- [x] Implement detect_anomaly method in coordinator
- [x] Implement pattern similarity calculation
- [x] Implement anomaly type determination
- [x] Update binary sensor _handle_coordinator_update to detect anomalies

**Dependencies:** 7.1

---

### 7.3 Pattern Learning
**Status:** 🟢 Complete  
**Complexity:** High  
**Specs Reference:** Lines 851-883, 1032-1044  
**Description:** Implement automatic pattern learning from historical data.

**Tasks:**
- [x] Implement pattern occurrence tracking (track_pattern_occurrence method)
- [x] Implement minimum samples threshold (default 10)
- [x] Implement confidence calculation for learned patterns (exponential moving average)
- [x] Store learned patterns with examples
- [x] Implement pattern suggestion system (suggest_patterns method)
- [x] Support learning periods (configurable, default 7 days)
- [x] Implement auto-apply vs manual review modes
- [x] Generate user-friendly pattern descriptions (_generate_pattern_description)
- [x] Implement apply_pattern method
- [x] Implement get_pattern_suggestions_formatted method
- [x] Enhance analyze_pattern service to support learning and auto-apply

**Dependencies:** 7.1

---

## 8. Configuration Management

### 8.1 Config Flow
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 2097-2139  
**Description:** Implement Home Assistant configuration flow UI.

**Tasks:**
- [x] Create `config_flow.py` with ConfigFlow class
- [x] Implement initial setup wizard (6 steps per Lines 2099-2139)
- [x] Step 1: Add integration entry point
- [x] Step 2: Floorplan creation (name, dimensions, background, scale)
- [x] Step 3: Sensor placement with auto-discovery
- [x] Step 4: Secondary cues addition (optional)
- [x] Step 5: Zone creation (optional)
- [x] Step 6: Calibration (optional but recommended)
- [x] Implement options flow for reconfiguration
- [x] Add validation for all inputs
- [x] Support background image upload

**Dependencies:** 1.2, 2.2

---

### 8.2 YAML Configuration Parser
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 905-1044  
**Description:** Implement YAML configuration schema validation and parsing.

**Tasks:**
- [x] Implement global settings parser (time_window, confidence_threshold, etc.)
- [x] Implement floorplan configuration parser
- [x] Implement sensors list parser with validation
- [x] Implement zones list parser with polygon validation
- [x] Implement secondary_cues list parser
- [x] Implement advanced settings parser (debounce, interpolation, sensitivity)
- [x] Implement per-sensor configuration parser (Lines 1022-1030)
- [x] Implement cue_learning configuration parser (Lines 1032-1044)
- [x] Add schema validation using voluptuous
- [x] Provide helpful error messages for invalid configs
- [x] Validate position coordinates within floorplan bounds
- [x] Validate polygon geometry (minimum 3 points)
- [x] Validate zone directions
- [x] Cross-reference validation (sensor_config vs actual sensors)

**Dependencies:** 2.2, 2.3, 2.4

---

### 8.3 Constants Definition
**Status:** � Complete  
**Complexity:** Low  
**Specs Reference:** Lines 104-113, 905-925  
**Description:** Define all constants used throughout the integration.

**Tasks:**
- [x] Create `const.py` with all constants
- [x] Define DOMAIN = "motiondirection"
- [x] Define default values: DEFAULT_WINDOW_SIZE = 5000, MIN_WINDOW_SIZE = 500, MAX_WINDOW_SIZE = 30000
- [x] Define confidence thresholds
- [x] Define entity name patterns
- [x] Define event types
- [x] Define service names
- [x] Define configuration keys
- [x] Define pattern types enum
- [x] Define cue types enum

**Dependencies:** None

---

## 9. Entity Implementation

### 9.1 Motion Direction Sensor
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1054-1069  
**Description:** Implement primary motion direction sensor entity.

**Tasks:**
- [x] Create `sensor.py` platform
- [x] Implement `sensor.motion_direction` entity
- [x] State: direction string (north, south, east, west, north_east, etc.)
- [x] Attributes: confidence, detection_method, vector, speed, path, triggered_sensors, contributing_cues, cue_confidence, active_zones, last_update
- [x] Update state on direction detection
- [x] Implement state restoration after HA restart
- [x] Add unit of measurement for speed (m/s)

**Dependencies:** 3.4, 8.3

---

### 9.2 Motion Pattern Sensor
**Status:** � Complete  
**Complexity:** Low  
**Specs Reference:** Lines 1073-1080  
**Description:** Implement motion pattern classification sensor.

**Tasks:**
- [x] Implement `sensor.motion_pattern` entity in sensor.py
- [x] State: pattern type (linear, circular, stationary, random, zone_transition)
- [x] Attributes: pattern_confidence, pattern_duration, pattern_history (last 10), zone_sequence
- [x] Update on pattern detection
- [x] Maintain pattern history buffer

**Dependencies:** 7.1, 9.1

---

### 9.3 Binary Sensors
**Status:** � Complete  
**Complexity:** Low  
**Specs Reference:** Lines 1084-1100  
**Description:** Implement motion detection and anomaly binary sensors.

**Tasks:**
- [x] Create `binary_sensor.py` platform
- [x] Implement `binary_sensor.motion_detected` entity
- [x] Implement `binary_sensor.motion_anomaly` entity (covered in 7.2)
- [x] Add appropriate device classes
- [x] Update states based on motion and anomaly detection
- [x] Include proper attributes

**Dependencies:** 3.4, 7.2

---

### 9.4 Coordinator
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 33, 65-90  
**Description:** Implement DataUpdateCoordinator for managing entity updates.

**Tasks:**
- [x] Create `coordinator.py` with MotionDirectionCoordinator class
- [x] Extend DataUpdateCoordinator from HA
- [x] Implement data update method
- [x] Manage motion event processing
- [x] Coordinate updates to all entities
- [x] Implement update intervals
- [x] Handle entity subscriptions
- [x] Implement error handling and recovery

**Dependencies:** 9.1, 9.2, 9.3, 5.4, 6.4

---

## 10. Service Implementation

### 10.1 Core Services
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1212-1247  
**Description:** Implement core integration services.

**Tasks:**
- [x] Implement `motiondirection.calibrate` service (Lines 1214-1221)
- [x] Implement `motiondirection.clear_history` service (Lines 1223-1229)
- [x] Implement `motiondirection.simulate` service (Lines 1231-1240)
- [x] Add service schema validation in services.yaml
- [x] Implement service handlers in __init__.py
- [x] Add proper async/await patterns
- [x] Add user notifications on completion
- [x] Add error handling

**Dependencies:** 3.4, 4.1

---

### 10.2 Analysis Services
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1375-1388  
**Description:** Implement pattern analysis and reporting services.

**Tasks:**
- [x] Implement `motiondirection.analyze_pattern` service (Lines 1377-1385)
- [x] Implement `motiondirection.generate_report` service (Lines 1387-1398)
- [x] Support multiple report formats (PDF, JSON, YAML)
- [x] Generate comprehensive statistics
- [x] Include zones, cues, patterns in reports
- [x] Store reports in accessible location
- [x] Add date range filtering

**Dependencies:** 7.1, 5.1, 6.2

---

### 10.3 Diagnostic Services
**Status:** � Complete  
**Complexity:** Low  
**Specs Reference:** Lines 2264-2286  
**Description:** Implement diagnostic and validation services.

**Tasks:**
- [x] Implement `motiondirection.get_status` service (Lines 2266-2269)
- [x] Implement `motiondirection.test_detection` service (Lines 2271-2277)
- [x] Implement `motiondirection.validate_config` service (Lines 2279-2282)
- [x] Return comprehensive system status
- [x] Test detection with specified duration
- [x] Validate all configuration parameters
- [x] Provide actionable error messages
- [x] Add service response support for get_status, test_detection, validate_config
- [x] Add coordinator diagnostic methods (get_detection_count, get_average_detection_time, etc.)
- [x] Add test mode enable/disable functionality in coordinator
- [x] Add INTEGRATION_VERSION constant

**Dependencies:** 3.4, 8.2

---

## 11. Event System

### 11.1 Event Bus Integration
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1390-1580  
**Description:** Implement event firing to Home Assistant event bus.

**Tasks:**
- [x] Create event firing wrapper in core module
- [x] Fire motion events (Lines 1392-1426)
- [x] Fire zone events (Lines 1430-1502)
- [x] Fire cue events (Lines 1506-1567)
- [x] Fire anomaly events (Lines 1571-1580)
- [x] Include all required event data fields
- [x] Add event data validation
- [x] Add event logging for debugging
- [x] Implement event throttling if needed

**Dependencies:** 3.4, 5.1, 6.2, 7.2

---

### 11.2 Event Data Structures
**Status:** � Complete  
**Complexity:** Low  
**Specs Reference:** Lines 1390-1580  
**Description:** Define event data schemas and validation.

**Tasks:**
- [x] Create event data dataclasses in models/
- [x] Define schema for each event type
- [x] Add validation for required fields
- [x] Add serialization methods
- [x] Ensure JSON-serializable output
- [x] Add event versioning support (EVENT_SCHEMA_VERSION = "1.0.0")

**Dependencies:** 2.1

---

## 12. Frontend Components

**Note:** A complete, working Motion Status Card has been implemented as a foundation. The architecture is documented in `/frontend/README.md` for future card development. The integration is fully functional via config flow, services, and entity states without requiring a visual editor.

### 12.0 Motion Status Card
**Status:** 🟢 Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1584-1602  
**Description:** Create motion direction status display card.

**Tasks:**
- [x] Create `frontend/motion-status-card.js` custom element
- [x] Display current motion direction with icon
- [x] Show confidence score with visual progress bar
- [x] Display detection method
- [x] Show active zones as chips
- [x] List triggered sensors
- [x] Display contributing cues
- [x] Show pattern type with icon
- [x] Implement configurable display options
- [x] Add HA theme support (light/dark)
- [x] Register as Lovelace card
- [x] Document architecture in frontend/README.md

**Dependencies:** 9.1, 9.2

---

### 12.1 Floorplan Editor Card
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 1584-1602  
**Description:** Create interactive floorplan editor Lovelace card.

**Tasks:**
- [x] Create `frontend/floorplan-editor-card.js` custom element
- [x] Implement SVG rendering with layers (background, grid, zones, sensors, cues, drawing)
- [x] Implement grid display with snap-to-grid
- [x] Implement sensor drag-and-drop
- [x] Implement sensor range visualization
- [x] Implement zone polygon drawing (point-by-point with preview)
- [x] Implement cue placement
- [x] Support editing mode toggle (view, edit, draw_zone, place_sensor)
- [x] Implement zoom and pan (mouse wheel + shift+drag)
- [x] Add save/load functionality via HA services
- [x] Register as Lovelace card
- [x] Add comprehensive toolbar with all editing tools
- [x] Support element selection and deletion
- [x] Implement keyboard shortcuts (Escape, Delete)

**Files Created:**
- `custom_components/motiondirection/frontend/floorplan-editor-card.js` - 1200+ lines, production-ready

**Dependencies:** 4.1, 4.2, 5.2

---

### 12.2 Motion Visualizer Card
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 1604-1615  
**Description:** Create real-time motion visualization card.

**Tasks:**
- [x] Create `frontend/motion-visualizer-card.js` custom element
- [x] Implement real-time motion display with trails
- [x] Implement historical motion playback with timeline
- [x] Implement heat map generation with alpha blending
- [x] Implement direction arrows with vector graphics
- [x] Implement confidence overlay (opacity based)
- [x] Support animation speed control
- [x] Use requestAnimationFrame for smooth animations
- [x] Implement time range selection with slider
- [x] Add playback controls (play/pause, clear)
- [x] Add toggle controls for heat map, arrows, confidence
- [x] Display real-time statistics (events, avg confidence, active zones)

**Files Created:**
- `custom_components/motiondirection/frontend/motion-visualizer-card.js` - 950+ lines, Canvas-based real-time visualization with trails, heat maps, direction arrows, confidence overlays, and historical playback

**Note:** Uses Canvas API with requestAnimationFrame for efficient rendering. Heat map uses radial gradients with alpha blending. Motion trails decay over time.

**Dependencies:** 12.1, 11.1

---

### 12.3 Zone Editor Card
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1617-1629  
**Description:** Create zone configuration and editing card.

**Tasks:**
- [x] Create `frontend/zone-editor-card.js` custom element
- [x] Implement view/edit modes
- [x] Show zone list with status indicators
- [x] Show direction arrows with rotation per vector
- [x] Implement zone selection with details panel
- [x] Implement direction configuration UI (add, edit, delete)
- [x] Show zone labels and statistics
- [x] Highlight active zones (real-time status)
- [x] Support color schemes (rainbow, monochrome, custom)
- [x] Integrate with zone services (calibrate, delete, update_direction)
- [x] Display confidence scores and transition statistics
- [x] Support direction aliases configuration
- [x] Implement zone calibration controls

**Files Created:**
- `custom_components/motiondirection/frontend/zone-editor-card.js` - 950+ lines, production-ready

**Dependencies:** 12.1, 5.2

---

### 12.4 Zone Status Card
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1631-1645  
**Description:** Create zone status monitoring card.

**Tasks:**
- [x] Create `frontend/zone-status-card.js` custom element
- [x] Display list of zones with active/inactive badges
- [x] Show current direction per zone with direction icons
- [x] Show occupancy status (occupied/vacant)
- [x] Show statistics (transitions, dwell time, last motion)
- [x] Support grid/list/compact layouts with toggle buttons
- [x] Update in real-time via hass property updates
- [x] Configurable update interval (default 1000ms)
- [x] Per-zone configuration (show_direction, show_occupancy, show_statistics)
- [x] Display confidence bars for direction certainty
- [x] Format timestamps and durations (human-readable)
- [x] Handle unavailable entities with error messages

**Files Created:**
- `custom_components/motiondirection/frontend/zone-status-card.js` - 700+ lines, comprehensive zone monitoring with three layout modes, direction indicators, occupancy tracking, and real-time statistics

**Note:** Zone states fetched from sensor.motiondirection_zone_{zone_id} entities. Updates via interval polling.

**Dependencies:** 5.4, 11.1

---

### 12.5 Zone Flow Visualizer
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 1647-1658  
**Description:** Create zone flow pattern visualization card.

**Tasks:**
- [x] Create `frontend/zone-flow-visualizer-card.js` custom element
- [x] Implement particle-based flow visualization with trails
- [x] Implement arrow-based flow visualization with gradients
- [x] Implement heat map visualization with color gradients
- [x] Show real-time zone transitions with animated particles
- [x] Load flow paths from floorplan and flow entities
- [x] Zone highlighting with configurable colors (active, idle, transit)
- [x] Support flow style switching (particles, arrows, heatmap)
- [x] Animate zone transitions with smooth interpolation
- [x] Display zone labels on floorplan
- [x] Show statistics (zones, paths, transitions)
- [x] Use requestAnimationFrame for smooth animations
- [x] Particle system with randomized speed and alpha
- [x] Automatic path selection and particle recycling

**Files Created:**
- `custom_components/motiondirection/frontend/zone-flow-visualizer-card.js` - 850+ lines, Canvas-based particle flow system with three visualization modes, zone highlighting, and real-time statistics

**Note:** Fetches zone data from sensor.motiondirection_floorplan_{floorplan_id} and flow data from sensor.motiondirection_{floorplan_id}_flow. Particles smoothly transition between zones.

**Dependencies:** 12.1, 5.1

---

### 12.6 Cue Editor Card
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1660-1673  
**Description:** Create secondary cue configuration card.

**Tasks:**
- [x] Create `frontend/cue-editor-card.js` custom element
- [x] Display available entities for cues with entity selector
- [x] Implement cue placement on floorplan with drag-and-drop
- [x] Show cue type selection (door, window, light, switch, lock, climate, media, appliance)
- [x] Configure directional hints UI with add/remove functionality
- [x] Show correlation lines to nearby sensors
- [x] Visualize cue states with multiple styles (icons/badges/circles)
- [x] Implement animations (pulse/glow/none)
- [x] Show confidence indicators
- [x] Integrate with cue services (update_cue, delete_cue)
- [x] Support view/edit/create modes
- [x] Entity filtering and domain categorization
- [x] Real-time state updates
- [x] Details panel for cue configuration

**Files Created:**
- `custom_components/motiondirection/frontend/cue-editor-card.js` - 900+ lines, full-featured cue editor with entity selection, drag-and-drop placement, directional hints configuration, correlation visualization, and service integration

**Note:** Similar architecture to Zone Editor Card but focused on secondary cues. Supports multiple visualization styles and animations. Entity selector filters available entities by domain.

**Dependencies:** 12.1, 6.3

---

### 12.7 Cue Status Card
**Status:** � Complete  
**Complexity:** Low  
**Specs Reference:** Lines 1675-1689  
**Description:** Create cue status monitoring card.

**Tasks:**
- [x] Create `frontend/cue-status-card.js` custom element
- [x] Display list of configured cues with type badges
- [x] Show cue states (on/off) with icons
- [x] Show correlation statistics (total, successful)
- [x] Show correlation success rates with gradient progress bars
- [x] Display active correlations with badges
- [x] Support list/grid/compact layouts with toggle buttons
- [x] Update in real-time via hass property updates
- [x] Configurable update interval (default 1000ms)
- [x] Per-cue configuration (show_state, show_correlations, show_statistics)
- [x] Display statistics (avg confidence, total triggers, 24h triggers)
- [x] Format last triggered timestamps (human-readable)
- [x] Cue type icons (door, window, light, switch, etc.)

**Files Created:**
- `custom_components/motiondirection/frontend/cue-status-card.js` - 650+ lines, comprehensive cue monitoring with three layout modes, correlation tracking, success rate visualization, and real-time statistics

**Note:** Cue states fetched from sensor.motiondirection_cue_{cue_id} entities. Updates via interval polling. Success rates visualized with gradient color bars.

**Dependencies:** 6.4, 11.1

---

### 12.8 Hybrid Detection Visualizer
**Status:** 🔴 Not Started  
**Complexity:** High  
**Specs Reference:** Lines 1691-1704  
**Description:** Create hybrid detection visualization showing motion+cues.

**Tasks:**
- [ ] Create `frontend/hybrid-visualizer.js` custom element
- [ ] Display motion sensors
- [ ] Display secondary cues
- [ ] Show correlation lines between motion and cues
- [ ] Color code by type (motion vs cue)
- [ ] Show detection method indicator
- [ ] Implement confidence-based opacity
- [ ] Show timeline of events
- [ ] Display correlation timing offsets

**Dependencies:** 12.1, 6.2, 11.1

---

### 12.9 Card Registration
**Status:** 🔴 Not Started  
**Complexity:** Low  
**Specs Reference:** Lines 2141-2149  
**Description:** Register all custom cards with Home Assistant.

**Tasks:**
- [ ] Create card registration code
- [ ] Add to resources in configuration.yaml
- [ ] Create card info definitions
- [ ] Add card previews/screenshots
- [ ] Document card configurations
- [ ] Add to HACS resources

**Dependencies:** 12.1-12.8

---

## 13. Performance Optimization

### 13.1 Event Batching
**Status:** 🔴 Not Started  
**Complexity:** Medium  
**Specs Reference:** Lines 1801-1807  
**Description:** Implement event batching for processing efficiency.

**Tasks:**
- [ ] Implement event queue with batch processing
- [ ] Configure batch size (default 10 events)
- [ ] Configure batch timeout (default 100ms)
- [ ] Process batches asynchronously
- [ ] Maintain event ordering within batches
- [ ] Add batch processing metrics

**Dependencies:** 3.1

---

### 13.2 Spatial Indexing
**Status:** 🔴 Not Started  
**Complexity:** High  
**Specs Reference:** Lines 1809-1824  
**Description:** Implement spatial indexing for efficient lookups.

**Tasks:**
- [ ] Implement R-tree or QuadTree for zone lookups
- [ ] Implement KD-tree for cue proximity searches
- [ ] Index sensor positions
- [ ] Index zone boundaries
- [ ] Index cue positions
- [ ] Update indexes on configuration changes
- [ ] Benchmark lookup performance
- [ ] Target <10ms lookup time

**Dependencies:** 5.1, 6.2

---

### 13.3 Caching System
**Status:** 🔴 Not Started  
**Complexity:** Medium  
**Specs Reference:** Lines 1801-1826  
**Description:** Implement caching for frequently accessed data.

**Tasks:**
- [ ] Implement correlation cache for cues
- [ ] Implement zone edge cache
- [ ] Implement direction vector cache
- [ ] Configure cache sizes (LRU eviction)
- [ ] Configure cache TTL
- [ ] Implement cache invalidation on config changes
- [ ] Add cache hit rate metrics

**Dependencies:** 5.1, 6.2

---

### 13.4 History Management
**Status:** 🔴 Not Started  
**Complexity:** Medium  
**Specs Reference:** Lines 1803, 1793  
**Description:** Implement efficient historical data storage and cleanup.

**Tasks:**
- [ ] Implement lazy loading of historical data
- [ ] Implement configurable retention (default 30 days)
- [ ] Implement automatic cleanup job (daily)
- [ ] Store compressed historical events
- [ ] Support partial history queries (time ranges)
- [ ] Target: 10MB per month storage
- [ ] Implement history export

**Dependencies:** 3.1

---

### 13.5 Performance Monitoring
**Status:** 🔴 Not Started  
**Complexity:** Low  
**Specs Reference:** Lines 1789-1796, 1828-1834  
**Description:** Implement performance metrics and monitoring.

**Tasks:**
- [ ] Track memory usage (target: <50MB base)
- [ ] Track CPU usage (target: <5% average, <15% peak)
- [ ] Track response times (target: <100ms)
- [ ] Track event processing rate (target: 1000/min)
- [ ] Add performance metrics to diagnostics service
- [ ] Log performance warnings
- [ ] Implement performance testing suite

**Dependencies:** 10.3

---

## 14. Security & Privacy

### 14.1 Data Protection
**Status:** 🔴 Not Started  
**Complexity:** Medium  
**Specs Reference:** Lines 1931-1937  
**Description:** Implement data protection and privacy features.

**Tasks:**
- [ ] Ensure local-only data storage
- [ ] Implement configurable retention policies
- [ ] Implement optional encryption at rest (AES-256)
- [ ] Support disabling history recording entirely
- [ ] Implement data anonymization for shared patterns
- [ ] Add GDPR compliance features
- [ ] Document data collection in privacy policy

**Dependencies:** 13.4

---

### 14.2 Access Control
**Status:** 🔴 Not Started  
**Complexity:** Medium  
**Specs Reference:** Lines 1939-1945  
**Description:** Implement access control and authorization.

**Tasks:**
- [ ] Integrate with HA user permissions
- [ ] Implement per-floorplan access control
- [ ] Restrict service call authorization
- [ ] Implement audit logging for sensitive operations
- [ ] Implement read-only mode for guests
- [ ] Log access attempts
- [ ] Add admin-only operations

**Dependencies:** 1.2

---

### 14.3 Privacy Options
**Status:** 🔴 Not Started  
**Complexity:** Low  
**Specs Reference:** Lines 1947-1953  
**Description:** Implement privacy-focused configuration options.

**Tasks:**
- [ ] Add option to exclude zones from learning
- [ ] Add notification for learning features
- [ ] Implement privacy mode (no history, no learning)
- [ ] Add encryption for sensitive zones
- [ ] Clear documentation of data usage
- [ ] User consent for pattern learning
- [ ] Implement data export for user access

**Dependencies:** 14.1, 7.3

---

## 15. Testing

### 15.1 Unit Test Suite
**Status:** � Complete  
**Complexity:** High  
**Specs Reference:** Lines 1957-1965  
**Description:** Create comprehensive unit tests.

**Tasks:**
- [x] Test TimeWindowCorrelator with various window sizes
- [x] Test VectorCalculator with edge cases (zero vectors, normalization)
- [x] Test confidence calculation formulas
- [x] Test pattern recognition algorithms
- [x] Test point-in-polygon (ray casting) algorithm
- [x] Test cue correlation logic
- [x] Test hybrid detection with various scenarios
- [x] Test configuration validation
- [x] Target: 80%+ code coverage
- [x] Use pytest framework
- [x] Create shared conftest.py with fixtures
- [x] Test models (all dataclasses)
- [x] Test motion detector with various scenarios
- [x] Test correlator with various event streams

**Files Created:**
- `tests/conftest.py` - Shared fixtures and helpers
- `tests/unit/test_models.py` - All data model tests
- `tests/unit/test_vector_calculator.py` - Vector calculation tests
- `tests/unit/test_correlator.py` - Time window correlation tests
- `tests/unit/test_motion_detector.py` - Motion detection tests

**Dependencies:** All core modules

---

### 15.2 Integration Test Suite
**Status:** 🟢 Complete  
**Complexity:** High  
**Specs Reference:** Lines 1967-1977  
**Description:** Create Home Assistant integration tests.

**Tasks:**
- [x] Test entity creation in HA
- [x] Test entity state updates
- [x] Test service calls and responses
- [x] Test event firing and handling
- [x] Test config flow wizard
- [x] Test zone sensor creation
- [x] Test cue event processing
- [x] Use HA test framework
- [x] Mock HA core dependencies
- [x] Test coordinator operations
- [x] Test all service handlers
- [x] Test concurrent service calls

**Files Created:**
- `tests/integration/test_coordinator.py` - Coordinator integration tests
- `tests/integration/test_services.py` - Service integration tests

**Dependencies:** All modules

---

### 15.3 Performance Test Suite
**Status:** 🟢 Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 1979-1987  
**Description:** Create performance and load tests.

**Tasks:**
- [x] Load test with 50 sensors
- [x] Load test with 50 zones (via 100-sensor grid)
- [x] Load test with large event streams
- [x] Test throughput with various event rates
- [x] Memory usage validation
- [x] Response time benchmarks
- [x] Concurrent event processing
- [x] Large dataset queries (correlation with 5000 events)
- [x] Use pytest-benchmark
- [x] Real-time requirement validation

**Files Created:**
- `tests/performance/test_detection_performance.py` - Comprehensive performance tests

**Dependencies:** All modules

---

### 15.4 End-to-End Test Suite
**Status:** 🔴 Not Started  
**Complexity:** High  
**Specs Reference:** Lines 1989-1997  
**Description:** Create user acceptance and E2E tests.

**Tasks:**
- [ ] Test complete setup workflow
- [ ] Test floorplan editor usability
- [ ] Test sensor placement workflow
- [ ] Test zone configuration workflow
- [ ] Test cue setup workflow
- [ ] Test direction detection accuracy with real scenarios
- [ ] Test automation triggering
- [ ] Create test scenarios document
- [ ] Use Selenium/Playwright for UI tests

**Dependencies:** All modules, frontend

---

## 16. API & WebSocket

### 16.1 Python API
**Status:** 🔴 Not Started  
**Complexity:** Medium  
**Specs Reference:** Lines 2290-2313  
**Description:** Implement Python API for programmatic access.

**Tasks:**
- [ ] Create `api/motion_direction_api.py` with MotionDirectionAPI class
- [ ] Implement `get_current_direction()` method
- [ ] Implement `get_direction_history()` method
- [ ] Implement `analyze_pattern()` method
- [ ] Implement `get_learned_patterns()` method
- [ ] Implement `get_floorplan()` method
- [ ] Implement `get_sensors()` method
- [ ] Add async/await patterns
- [ ] Add error handling
- [ ] Add API documentation

**Dependencies:** 3.4, 4.1, 7.1

---

### 16.2 Zone API
**Status:** 🔴 Not Started  
**Complexity:** Medium  
**Specs Reference:** Lines 2315-2331  
**Description:** Implement Zone management API.

**Tasks:**
- [ ] Create `api/zone_api.py` with ZoneAPI class
- [ ] Implement `create_zone()` method
- [ ] Implement `update_zone_direction()` method
- [ ] Implement `get_zones()` method
- [ ] Implement `get_zone_transitions()` method
- [ ] Implement `analyze_zone_patterns()` method
- [ ] Implement `get_zone_statistics()` method
- [ ] Implement `get_zone_state()` method
- [ ] Implement `trigger_zone_manually()` method

**Dependencies:** 5.1, 5.4

---

### 16.3 Secondary Cue API
**Status:** 🔴 Not Started  
**Complexity:** Medium  
**Specs Reference:** Lines 2333-2358  
**Description:** Implement Secondary Cue management API.

**Tasks:**
- [ ] Create `api/cue_api.py` with SecondaryCueAPI class
- [ ] Implement `add_cue()` method
- [ ] Implement `update_cue_hints()` method
- [ ] Implement `get_cues()` method
- [ ] Implement `analyze_correlations()` method
- [ ] Implement `detect_patterns()` method
- [ ] Implement `process_hybrid_detection()` method
- [ ] Implement `suggest_new_cues()` method
- [ ] Implement `apply_learned_patterns()` method

**Dependencies:** 6.2, 6.6

---

### 16.4 WebSocket API
**Status:** 🔴 Not Started  
**Complexity:** High  
**Specs Reference:** Lines 2360-2394  
**Description:** Implement WebSocket API for real-time communication.

**Tasks:**
- [ ] Create WebSocket command handlers in __init__.py
- [ ] Implement `motiondirection/get_state` command
- [ ] Implement `motiondirection/get_zone_states` command
- [ ] Implement `motiondirection/get_cue_correlations` command
- [ ] Implement `motiondirection/update_config` command
- [ ] Implement subscription to events
- [ ] Add command validation
- [ ] Add error responses
- [ ] Document WebSocket API
- [ ] Support authentication

**Dependencies:** 16.1, 16.2, 16.3

---

## 17. Documentation

### 17.1 User Documentation
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 2051-2170, 2585-2705  
**Description:** Create comprehensive user documentation.

**Tasks:**
- [x] Write README.md with overview and features
- [x] Document installation methods (HACS and manual)
- [x] Document setup wizard steps
- [x] Create configuration examples (Appendix B, Lines 2585-2632)
- [x] Document all services with examples
- [x] Document all events with examples
- [x] Document frontend cards with screenshots
- [x] Create troubleshooting guide (Lines 2172-2260)
- [x] Create FAQ (Appendix D, Lines 2666-2705)
- [x] Add best practices guide (Lines 1836-1927)
- [x] Create USER_GUIDE.md with step-by-step guidance
- [x] Add automation examples

**Dependencies:** All modules

---

### 17.2 API Reference Documentation
**Status:** 🟢 Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 16.1-16.4, Services, Events, Sensors  
**Description:** Create comprehensive API reference for services, events, and sensors.

**Tasks:**
- [x] Document all service schemas with examples
- [x] Document all event data structures with examples
- [x] Document all sensor entities with attributes
- [x] Document data models and types
- [x] Create API_REFERENCE.md
- [x] Add service usage examples
- [x] Add event listener examples
- [x] Document sensor states and attributes

**Dependencies:** All modules

---

### 17.3 Developer Documentation
**Status:** � Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 2396-2459  
**Description:** Create developer documentation and contribution guidelines.

**Tasks:**
- [x] Write CONTRIBUTING.md (Lines 2396-2452)
- [x] Document code standards (PEP 8, type hints)
- [x] Document development setup (Lines 2403-2417)
- [x] Document PR process (Lines 2419-2426)
- [x] Document commit message format (Lines 2428-2441)
- [x] Create code review checklist (Lines 2443-2449)
- [x] Document architecture and design patterns
- [x] Create DEVELOPER_GUIDE.md with comprehensive coverage
- [x] Document testing requirements
- [x] Add debugging tips and performance considerations
- [x] Document all core components in detail
- [x] Provide extension point examples

**Dependencies:** 1.3, 15.1-15.4

---

### 17.3 Algorithm Documentation
**Status:** 🔴 Not Started  
**Complexity:** Low  
**Specs Reference:** Lines 2502-2583  
**Description:** Document algorithms and mathematical models.

**Tasks:**
- [ ] Document vector calculation algorithm (Lines 2506-2552)
- [ ] Document time window correlation (Lines 2555-2568)
- [ ] Document confidence calculation formula (Lines 2570-2583)
- [ ] Add algorithm complexity analysis
- [ ] Add algorithm flowcharts
- [ ] Document optimization techniques

**Dependencies:** 3.2, 3.3

---

### 17.4 Integration Examples
**Status:** 🔴 Not Started  
**Complexity:** Low  
**Specs Reference:** Lines 1708-1787, 2585-2663  
**Description:** Create example configurations and automations.

**Tasks:**
- [ ] Create automation examples (Lines 1708-1787)
- [ ] Create simple hallway configuration (Lines 2589-2605)
- [ ] Create multi-room with zones configuration (Lines 2607-2636)
- [ ] Create hybrid detection with cues configuration (Lines 2638-2663)
- [ ] Create sample floorplan templates
- [ ] Create video tutorials (future)
- [ ] Create community showcase

**Dependencies:** All modules

---

## 18. Deployment & Distribution

### 18.1 HACS Integration
**Status:** � Complete  
**Complexity:** Low  
**Specs Reference:** Lines 2051-2060  
**Description:** Prepare integration for HACS distribution.

**Tasks:**
- [x] Create hacs.json with proper metadata
- [x] Set up GitHub repository
- [x] Validate manifest.json has all required fields
- [x] Verify repository structure (custom_components/motiondirection/)
- [x] Create HACS validation workflow
- [x] Prepare for HACS default repository submission
- [x] Create installation documentation

**Dependencies:** 1.1, 1.2, 17.1

---

### 18.2 Version Management
**Status:** 🟢 Complete  
**Complexity:** Low  
**Specs Reference:** Lines 2001-2049  
**Description:** Implement semantic versioning and changelog.

**Tasks:**
- [x] Create CHANGELOG.md following Keep a Changelog format
- [x] Document all changes for v1.3.0
- [x] Implement semantic versioning (MAJOR.MINOR.PATCH)
- [x] Group changes by type (Added, Changed, Fixed, etc.)
- [x] Link versions to git tags
- [x] Document breaking changes
- [x] Create version validation in release workflow

**Dependencies:** 18.1

---

### 18.3 CI/CD Pipeline
**Status:** 🟢 Complete  
**Complexity:** Medium  
**Specs Reference:** Lines 2396-2459  
**Description:** Set up continuous integration and deployment.

**Tasks:**
- [x] Create GitHub Actions workflow for hassfest validation
- [x] Create GitHub Actions workflow for tests (pytest, coverage)
- [x] Create GitHub Actions workflow for linting (black, pylint, mypy)
- [x] Create GitHub Actions workflow for HACS validation
- [x] Create GitHub Actions workflow for automated releases
- [x] Run tests on multiple Python versions (3.11, 3.12)
- [x] Integrate code coverage reporting (Codecov)
- [x] Validate version consistency across manifest.json and hacs.json
- [x] Extract and publish release notes from CHANGELOG.md
- [x] Run workflows on push and pull_request events

**Dependencies:** 15.1, 15.2, 18.1

---

## 19. Future Enhancements (Phase 3-4)

### 19.1 Machine Learning Integration
**Status:** 🔴 Not Started  
**Complexity:** Very High  
**Specs Reference:** Lines 2027-2035  
**Description:** Add ML-based prediction and learning (Phase 3).

**Tasks:**
- [ ] Research appropriate ML models (LSTM, transformer)
- [ ] Implement predictive motion paths
- [ ] Implement behavioral analysis
- [ ] Implement advanced anomaly detection
- [ ] Implement self-learning capabilities
- [ ] Train models on historical data
- [ ] Optimize for edge deployment
- [ ] Add optional cloud training

**Dependencies:** 7.1, 13.4

---

### 19.2 Camera Integration
**Status:** 🔴 Not Started  
**Complexity:** High  
**Specs Reference:** Lines 2037-2046  
**Description:** Integrate with camera person detection (Phase 4).

**Tasks:**
- [ ] Integrate with Frigate
- [ ] Integrate with UniFi Protect
- [ ] Person detection tracking
- [ ] Person identification (optional)
- [ ] Multi-person tracking
- [ ] Camera calibration for position mapping
- [ ] Privacy considerations

**Dependencies:** 3.1, 16.1

---

### 19.3 Multi-Floor Support
**Status:** 🔴 Not Started  
**Complexity:** High  
**Specs Reference:** Lines 2038  
**Description:** Add multi-floor 3D visualization.

**Tasks:**
- [ ] Extend floorplan model for multiple floors
- [ ] Implement floor-to-floor transitions (stairs, elevators)
- [ ] Create 3D visualization component
- [ ] Add z-axis to position tracking
- [ ] Update zone logic for 3D spaces

**Dependencies:** 4.1, 12.1

---

### 19.4 External API
**Status:** 🔴 Not Started  
**Complexity:** Medium  
**Specs Reference:** Lines 2039  
**Description:** Create external REST API for third-party integrations.

**Tasks:**
- [ ] Design RESTful API
- [ ] Implement authentication (API keys, OAuth)
- [ ] Implement rate limiting
- [ ] Create API documentation (OpenAPI/Swagger)
- [ ] Create client SDKs (Python, JavaScript)
- [ ] Add webhooks for events

**Dependencies:** 16.1, 16.2, 16.3

---

### 19.5 Mobile Companion App
**Status:** 🔴 Not Started  
**Complexity:** Very High  
**Specs Reference:** Lines 2040  
**Description:** Create native mobile app for iOS and Android.

**Tasks:**
- [ ] Design mobile UI/UX
- [ ] Implement with React Native or Flutter
- [ ] Real-time floorplan viewing
- [ ] Push notifications for events
- [ ] Zone configuration on mobile
- [ ] AR overlay for sensor placement (future)
- [ ] Publish to App Store and Play Store

**Dependencies:** 16.4, 18.1

---

## 20. Project Management

### 20.1 Documentation Tracking
**Status:** 🟡 In Progress  
**Complexity:** Low  
**Description:** Track documentation completion.

**Tasks:**
- [x] Create development_tasklist.md
- [ ] Regular task list updates
- [ ] Track completed tasks
- [ ] Update progress percentages
- [ ] Review and adjust priorities

**Dependencies:** None

---

### 20.2 Code Review Process
**Status:** 🔴 Not Started  
**Complexity:** Low  
**Description:** Establish code review workflow.

**Tasks:**
- [ ] Define review requirements
- [ ] Create review checklist
- [ ] Assign reviewers per area
- [ ] Track review feedback
- [ ] Enforce review before merge

**Dependencies:** 1.3

---

### 20.3 Issue Management
**Status:** 🔴 Not Started  
**Complexity:** Low  
**Description:** Set up issue tracking and management.

**Tasks:**
- [ ] Create issue templates (bug, feature, question)
- [ ] Label system setup
- [ ] Milestone planning
- [ ] Triage process
- [ ] Issue assignment workflow

**Dependencies:** 18.1

---

## Summary Statistics

**Total Task Categories:** 20  
**Total Major Tasks:** 110+  
**Estimated Total Sub-tasks:** 500+

### By Phase:
- **Phase 1 (Core - v1.0):** ~60% of tasks (Infrastructure, Core Detection, Basic UI)
- **Phase 2 (Advanced - v1.5):** ~30% of tasks (Zones, Cues, Patterns)
- **Phase 3-4 (Intelligence & Ecosystem - v2.0+):** ~10% of tasks (ML, Integrations)

### By Complexity:
- **Low:** ~30 tasks
- **Medium:** ~40 tasks
- **High:** ~30 tasks
- **Very High:** ~10 tasks

### Critical Path:
1. Project Setup (1.1-1.3) → 2. Core Models (2.1-2.5) → 3. Motion Detection (3.1-3.4) → 4. Floorplan (4.1-4.2) → 8. Config (8.1-8.2) → 9. Entities (9.1-9.4) → 12. Frontend (12.1) → 15. Testing (15.1-15.2)

---

**Next Steps:**
1. Begin with Section 1 (Project Setup & Infrastructure)
2. Complete Section 2 (Core Models & Data Structures)
3. Implement Section 3 (Motion Detection Engine)
4. Continue through sections in order

**Notes:**
- Line references in specs.md may shift if document is edited
- Dependencies should be followed for proper implementation order
- Testing should be ongoing throughout development, not just at end
- Documentation should be written alongside code
- Regular progress updates to this task list recommended

