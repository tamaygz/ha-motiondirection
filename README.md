# HA-MotionDirection

**Intelligent Motion Direction Detection for Home Assistant**

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)](https://www.home-assistant.io/)

HA-MotionDirection is a powerful Home Assistant custom integration that intelligently detects motion direction by analyzing patterns from multiple motion sensors. Perfect for presence detection, room-to-room tracking, and advanced automation scenarios.

## ✨ Key Features

- **🎯 Multi-Sensor Direction Detection**: Analyzes motion patterns across multiple sensors using vector-based algorithms
- **🗺️ Visual Floorplan Editor**: Interactive canvas-based editor for sensor placement and zone configuration
- **🏠 Trigger Zones**: Define specific zones with directional rules (e.g., "entering kitchen from living room")
- **💡 Secondary Cues**: Enhance accuracy using door sensors, lights, and other state changes
- **🧠 Pattern Learning**: Automatically learns common motion patterns over time
- **⚠️ Anomaly Detection**: Identifies unusual motion patterns for security or health monitoring
- **📊 Rich Sensors**: Motion direction, zone transitions, confidence scores, and pattern insights
- **🎨 Custom Lovelace Cards**: Beautiful status cards showing real-time motion visualization
- **🔌 Comprehensive Services**: Full API for automation and integration
- **🔒 Privacy-First**: All processing happens locally—no cloud required

## 📋 Requirements

- Home Assistant 2024.1.0 or newer
- Python 3.12 or newer
- At least 3 motion sensors for reliable direction detection
- HACS (Home Assistant Community Store) for easy installation

## 🚀 Quick Start

### Installation via HACS

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/tamaygz/ha-motiondirection`
6. Select category "Integration"
7. Click "Add"
8. Search for "Motion Direction" in HACS
9. Click "Download" and restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/tamaygz/ha-motiondirection/releases)
2. Extract the `custom_components/motiondirection` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

### First-Time Setup

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Motion Direction"
4. Follow the configuration wizard:
   - Set your update interval (default: 5 seconds)
   - Configure confidence threshold (default: 0.7)
   - Set time window for correlation (default: 5 seconds)

### Configure Your Floorplan

After installation, configure your sensors and floorplan:

```yaml
# Example service call to set up floorplan
service: motiondirection.update_floorplan
data:
  floorplan_id: "main"
  width: 20.0
  height: 15.0
  sensors:
    - entity_id: binary_sensor.living_room_motion
      x: 5.0
      y: 5.0
      range_meters: 3.0
    - entity_id: binary_sensor.kitchen_motion
      x: 15.0
      y: 5.0
      range_meters: 3.0
    - entity_id: binary_sensor.hallway_motion
      x: 10.0
      y: 10.0
      range_meters: 3.0
```

### Create Your First Trigger Zone

```yaml
service: motiondirection.create_trigger_zone
data:
  zone_id: "living_room"
  polygon:
    - x: 0.0
      y: 0.0
    - x: 10.0
      y: 0.0
    - x: 10.0
      y: 10.0
    - x: 0.0
      y: 10.0
  directions:
    - name: "to_kitchen"
      vector: [1.0, 0.0]
      entry_side: "right"
      confidence_threshold: 0.7
```

### Add to Your Dashboard

Add the motion status card to your dashboard:

```yaml
type: custom:motion-status-card
entity: sensor.motion_direction
show_confidence: true
show_zones: true
show_sensors: true
show_cues: true
```

## 📖 Documentation

- **[User Guide](docs/USER_GUIDE.md)**: Detailed configuration and usage instructions
- **[API Reference](docs/API_REFERENCE.md)**: Complete service and event documentation
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: Architecture and contribution guidelines

## 🎬 Example Automations

### Turn on lights based on direction

```yaml
automation:
  - alias: "Kitchen Light - Motion Direction"
    trigger:
      - platform: event
        event_type: motiondirection_direction_detected
        event_data:
          direction: "to_kitchen"
    condition:
      - condition: numeric_state
        entity_id: sensor.motion_direction_confidence
        above: 0.7
    action:
      - service: light.turn_on
        target:
          entity_id: light.kitchen
```

### Alert on unusual patterns

```yaml
automation:
  - alias: "Alert - Unusual Motion Pattern"
    trigger:
      - platform: event
        event_type: motiondirection_anomaly_detected
        event_data:
          severity: "high"
    action:
      - service: notify.mobile_app
        data:
          message: "Unusual motion pattern detected: {{ trigger.event.data.description }}"
```

## 🛠️ Services

| Service | Description |
|---------|-------------|
| `update_floorplan` | Update floorplan configuration with sensors |
| `create_trigger_zone` | Create a new trigger zone with directions |
| `update_trigger_zone` | Modify an existing trigger zone |
| `delete_trigger_zone` | Remove a trigger zone |
| `register_secondary_cue` | Add a secondary cue (door, light, etc.) |
| `analyze_pattern` | Manually trigger pattern analysis |

See [API Reference](docs/API_REFERENCE.md) for detailed service documentation.

## 📊 Sensors

The integration provides the following sensors:

- `sensor.motion_direction` - Current detected direction
- `sensor.motion_direction_confidence` - Detection confidence (0-1)
- `sensor.motion_direction_method` - Detection method used
- `sensor.zone_<zone_id>` - Per-zone direction sensors
- `sensor.cue_<cue_id>` - Secondary cue state sensors

## 🎯 Events

Listen to these events in your automations:

- `motiondirection_direction_detected` - Direction was detected
- `motiondirection_zone_transition` - Movement between zones
- `motiondirection_pattern_learned` - New pattern learned
- `motiondirection_anomaly_detected` - Unusual pattern detected

## 🐛 Troubleshooting

### Direction detection not working

1. Ensure you have at least 3 motion sensors configured
2. Verify sensor coordinates are correct (check floorplan)
3. Check sensor range (should overlap for best results)
4. Lower confidence threshold if too strict
5. Increase time window if sensors trigger slowly

### Low confidence scores

- Add more sensors for better coverage
- Register secondary cues (doors, lights)
- Adjust time window to match your space
- Check for sensor dead zones

### Zones not triggering

- Verify zone polygon contains sensor locations
- Check entry_side configuration matches expected direction
- Ensure confidence_threshold isn't too high

## 💬 Support & Community

- **Issues**: [GitHub Issues](https://github.com/tamaygz/ha-motiondirection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tamaygz/ha-motiondirection/discussions)
- **Home Assistant Community**: [Forum Thread](https://community.home-assistant.io)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Home Assistant community for inspiration and support
- Contributors who helped improve this integration
- HACS for making custom integration distribution easy

---

**Made with ❤️ for the Home Assistant community**
