# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Zone drawing UI for polygon creation
- Additional frontend cards (Cue Editor, Cue Status, Hybrid Visualizer)
- Performance optimizations (event batching, spatial indexing, caching)
- Security features (data protection, access control, privacy options)
- Python/Zone/Cue/WebSocket APIs
- Machine learning integration
- Camera integration (Frigate, UniFi Protect)
- Multi-floor support

## [1.3.0] - 2026-01-02

### Added
- **Core Detection Engine**
  - Event collection system with debouncing and filtering
  - Time window correlator with configurable windows (500ms-30s)
  - Vector calculator with confidence scoring
  - Multi-sensor direction detection
- **Data Models**
  - Complete model hierarchy: SensorNode, MotionEvent, MotionPath, MotionSequence
  - Floorplan model with grid, layers, and configuration management
  - TriggerZone model with polygon geometry and ray casting
  - SecondaryCue model with DirectionalHint and StateChange
  - Pattern models: LearnedPattern, ZoneTransition, DirectionResult
- **Cue Type Registry**
  - Registry pattern for 8 cue types (door, light, switch, presence, temperature, vibration, power, media)
  - Type-specific correlation windows and distance thresholds
  - Dynamic configuration lookup
- **Hybrid Motion Detection**
  - Combines motion sensors with secondary cues
  - Spatial and temporal correlation
  - Type-specific correlation windows via registry
  - Multiple detection methods: multi_sensor, hybrid, cue_assisted
- **Cue Correlation Analysis**
  - Statistical tracking with CorrelationStatistics
  - Temporal decay functions for recency bias
  - Pattern learning (sequential, correlation, timing)
  - Historical analysis with configurable time periods
  - Confidence scoring with weighted decay
- **Zone Management**
  - Zone manager core with transition detection
  - Entry/exit point calculation
  - Direction matching and dwell time tracking
  - Zone confidence calculation
- **Pattern Analysis**
  - Pattern recognition: linear, circular, zone_transition, stationary, random, anomaly
  - Pattern learning with signature creation
  - Anomaly detection with deviation scoring
  - Pattern occurrence tracking and suggestions
- **Floorplan Management**
  - Floorplan configuration and storage
  - Sensor discovery and placement
  - Position tracking with overlap detection
  - Grid system with snap-to-grid
- **Configuration**
  - Config flow wizard (6 steps)
  - YAML configuration parser with voluptuous validation
  - Per-sensor and per-cue configuration
  - Cross-reference validation
- **Entities**
  - Primary sensors: motion_direction, motion_pattern
  - Binary sensors: motion_detected, motion_anomaly
  - Zone sensors: zone_{id}_direction, zone_{id}_occupied, zone_{id}_transit, zone_{id}_statistics
  - Cue sensors: secondary_cue_{id}, cue_correlation_analysis
  - Comprehensive attributes for all entities
- **Services**
  - Core: calibrate, clear_history, simulate
  - Zone: calibrate_zone, create_zone, update_zone_direction, test_zone_trigger, analyze_zone_patterns, learn_zone_directions
  - Cue: add_secondary_cue, configure_cue_hints, analyze_cue_correlations, learn_cue_patterns, test_hybrid_detection
  - Analysis: analyze_pattern, generate_report
  - Diagnostics: get_status, test_detection, validate_config
- **Events**
  - Motion: motiondirection_motion_detected, motiondirection_pattern_detected
  - Zone: zone_entered, zone_exited, zone_direction_detected, zone_pattern_detected
  - Cue: cue_triggered, hybrid_detection, cue_correlation_detected, cue_pattern_learned
  - Anomaly: anomaly_detected
  - Event versioning with schema_version field (1.0.0)
- **Frontend**
  - Motion Status Card with direction display, confidence, active zones, sensors, cues
  - Frontend architecture documented for future card development
- **Testing**
  - Comprehensive unit tests (80%+ coverage)
  - Integration tests for coordinator and services
  - Performance tests with benchmarks
  - Test fixtures and shared utilities
- **Documentation**
  - Complete README with features and installation
  - USER_GUIDE with step-by-step setup
  - API_REFERENCE for services, events, sensors
  - DEVELOPER_GUIDE with architecture and contribution guidelines
  - Troubleshooting guide and FAQ
  - Best practices guide

### Changed
- Updated all event dataclasses to include schema_version field for backward compatibility
- Improved correlation analysis with exponential temporal decay
- Enhanced pattern learning with confidence thresholds
- Optimized hybrid detector with registry-based correlation windows

### Fixed
- Correlation window calculations now use type-specific values
- Pattern confidence scoring uses exponential moving average
- Zone direction matching handles edge cases properly

## [1.2.0] - 2025-12-15

### Added
- Initial project structure
- Basic infrastructure setup
- Core model definitions

## [1.1.0] - 2025-12-01

### Added
- Project planning and specifications
- Development task list
- Architecture design

## [1.0.0] - 2025-11-15

### Added
- Initial repository setup
- License (MIT)
- Basic documentation structure

[Unreleased]: https://github.com/tamaygz/ha-motiondirection/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/tamaygz/ha-motiondirection/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/tamaygz/ha-motiondirection/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/tamaygz/ha-motiondirection/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/tamaygz/ha-motiondirection/releases/tag/v1.0.0
