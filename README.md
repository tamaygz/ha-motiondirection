# HA-MotionDirection

![Version](https://img.shields.io/badge/version-1.3.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1%2B-blue.svg)

A Home Assistant custom integration that intelligently detects the direction of motion through a space by analyzing the sequential triggering patterns of multiple motion sensors.

## Features

- 🗺️ **Visual Floorplan Editor**: Intuitive 2D canvas for sensor placement
- 🧭 **Direction Detection**: Automatic calculation of motion direction vectors
- 🎯 **Trigger Zones**: Configurable zones with directional entry/exit detection
- 💡 **Secondary Cues**: Enhanced detection using doors, lights, and other sensors
- 📊 **Pattern Analysis**: Learn and recognize common motion patterns
- 📈 **Real-time Visualization**: Live motion tracking and historical playback
- 🤖 **Smart Automation**: Trigger actions based on direction and zones

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL
6. Select "Integration" as the category
7. Click "Add"
8. Search for "Motion Direction" and install

### Manual Installation

1. Download the latest release
2. Extract the `motiondirection` folder to your `config/custom_components/` directory
3. Restart Home Assistant

## Quick Start

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Motion Direction"
4. Follow the setup wizard:
   - Create a floorplan
   - Place motion sensors
   - (Optional) Add secondary cues
   - (Optional) Define trigger zones
   - Calibrate the system

## Documentation

- [Full Documentation](https://github.com/tamaygz/ha-motiondirection/wiki)
- [Configuration Guide](https://github.com/tamaygz/ha-motiondirection/wiki/Configuration)
- [Automation Examples](https://github.com/tamaygz/ha-motiondirection/wiki/Automations)
- [Troubleshooting](https://github.com/tamaygz/ha-motiondirection/wiki/Troubleshooting)

## Example Configuration

```yaml
sensor:
  - platform: motiondirection
    floorplan_id: ground_floor
    sensors:
      - entity_id: binary_sensor.hallway_motion
        position: {x: 100, y: 400}
      - entity_id: binary_sensor.kitchen_motion
        position: {x: 300, y: 400}
    zones:
      - id: hallway
        polygon: [[50,350], [150,350], [150,450], [50,450]]
        known_directions:
          - name: "east"
            vector: [1, 0]
```

## Use Cases

- **Directional Lighting**: Turn on lights ahead of motion direction
- **Security**: Detect unusual movement patterns
- **Energy Savings**: Optimize HVAC based on room transitions
- **Presence Detection**: Know which rooms are occupied
- **Smart Scenes**: Activate different scenes based on direction

## Requirements

- Home Assistant 2024.1.0 or later
- Python 3.12 or later
- At least 2 motion sensors for direction detection

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [Issue Tracker](https://github.com/tamaygz/ha-motiondirection/issues)
- [Discussion Forum](https://github.com/tamaygz/ha-motiondirection/discussions)
- [Home Assistant Community](https://community.home-assistant.io/)

## Acknowledgments

- Home Assistant community for inspiration and support
- Contributors and testers who helped improve this integration

---

**Note**: This integration is under active development. Please report any issues or feature requests through the GitHub issue tracker.
