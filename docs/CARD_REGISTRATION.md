# MotionDirection Custom Cards Registration

This document describes how to register and configure MotionDirection custom cards in Home Assistant.

## Automatic Registration

The MotionDirection integration automatically registers all custom cards when loaded. No manual registration is required.

## Available Cards

### 1. Motion Status Card
**Type:** `custom:motiondirection-motion-status`

Displays current motion direction, confidence, detection method, and active zones.

```yaml
type: custom:motiondirection-motion-status
floorplan_id: ground_floor
show_confidence: true
show_detection_method: true
show_active_zones: true
show_triggered_sensors: true
show_contributing_cues: true
```

### 2. Floorplan Editor Card
**Type:** `custom:motiondirection-floorplan-editor`

Interactive floorplan editor for sensor and zone placement.

```yaml
type: custom:motiondirection-floorplan-editor
floorplan_id: ground_floor
width: 1000
height: 1000
background_image: /local/floorplan.png
show_grid: true
grid_size: 50
snap_to_grid: true
```

### 3. Motion Visualizer Card
**Type:** `custom:motiondirection-motion-visualizer`

Visualizes motion trails, heat maps, direction arrows, and historical playback.

```yaml
type: custom:motiondirection-motion-visualizer
floorplan_id: ground_floor
visualization_mode: trails  # trails, heatmap, arrows
show_sensors: true
show_direction_arrows: true
trail_length: 50
trail_fade_time: 5000
playback_speed: 1.0
show_playback_controls: true
show_statistics: true
```

### 4. Zone Editor Card
**Type:** `custom:motiondirection-zone-editor`

Edit zones with polygon drawing, naming, and direction configuration.

```yaml
type: custom:motiondirection-zone-editor
floorplan_id: ground_floor
show_existing_zones: true
enable_zone_editing: true
enable_zone_creation: true
enable_zone_deletion: true
```

### 5. Zone Status Card
**Type:** `custom:motiondirection-zone-status`

Displays zone occupancy, direction statistics, and real-time updates.

```yaml
type: custom:motiondirection-zone-status
floorplan_id: ground_floor
layout: grid  # grid, list, compact
show_occupancy: true
show_direction: true
show_statistics: true
show_confidence: true
max_zones_displayed: 10
```

### 6. Zone Flow Visualizer Card
**Type:** `custom:motiondirection-zone-flow-visualizer`

Visualizes flow between zones with particles, arrows, and heat maps.

```yaml
type: custom:motiondirection-zone-flow-visualizer
floorplan_id: ground_floor
visualization_mode: particles  # particles, arrows, heatmap
particle_count: 100
show_statistics: true
highlight_active_zones: true
```

### 7. Cue Editor Card
**Type:** `custom:motiondirection-cue-editor`

Edit secondary cues with entity selection, placement, and directional hints.

```yaml
type: custom:motiondirection-cue-editor
floorplan_id: ground_floor
show_available_entities: true
entity_types:
  - light
  - switch
  - media_player
  - climate
enable_drag_drop: true
show_directional_hints: true
show_correlation_visualization: true
```

### 8. Cue Status Card
**Type:** `custom:motiondirection-cue-status`

Displays secondary cue states, correlations, and success rates.

```yaml
type: custom:motiondirection-cue-status
floorplan_id: ground_floor
layout: grid  # grid, list, compact
show_state: true
show_correlation: true
show_success_rate: true
show_confidence: true
max_cues_displayed: 10
```

### 9. Hybrid Detection Visualizer Card
**Type:** `custom:motiondirection-hybrid-visualizer`

Visualizes hybrid detection with motion sensors, secondary cues, correlations, and timeline.

```yaml
type: custom:motiondirection-hybrid-visualizer
floorplan_id: ground_floor
show_motion_sensors: true
show_secondary_cues: true
show_detection_method: true
visualization_options:
  motion_color: '#00FF00'
  cue_color: '#FFA500'
  correlation_lines: true
  confidence_opacity: true
  show_timeline: true
timeline_duration: 300  # seconds
```

## Manual Resource Registration

If automatic registration fails, you can manually add the cards to your `configuration.yaml`:

```yaml
lovelace:
  mode: yaml
  resources:
    - url: /hacsfiles/ha-motiondirection/motion-status-card.js
      type: module
    - url: /hacsfiles/ha-motiondirection/floorplan-editor-card.js
      type: module
    - url: /hacsfiles/ha-motiondirection/motion-visualizer-card.js
      type: module
    - url: /hacsfiles/ha-motiondirection/zone-editor-card.js
      type: module
    - url: /hacsfiles/ha-motiondirection/zone-status-card.js
      type: module
    - url: /hacsfiles/ha-motiondirection/zone-flow-visualizer-card.js
      type: module
    - url: /hacsfiles/ha-motiondirection/cue-editor-card.js
      type: module
    - url: /hacsfiles/ha-motiondirection/cue-status-card.js
      type: module
    - url: /hacsfiles/ha-motiondirection/hybrid-visualizer-card.js
      type: module
```

## Adding Cards to Dashboard

### Method 1: Visual Editor
1. Enter edit mode in your dashboard
2. Click "Add Card"
3. Search for "MotionDirection"
4. Select the desired card
5. Configure using the visual editor

### Method 2: YAML Mode
1. Enter edit mode in your dashboard
2. Click "Show Code Editor"
3. Add the card YAML configuration
4. Click "Save"

## Card Organization

### Recommended Dashboard Layout

```yaml
title: MotionDirection
views:
  - title: Overview
    cards:
      - type: custom:motiondirection-motion-status
        floorplan_id: ground_floor
      - type: custom:motiondirection-hybrid-visualizer
        floorplan_id: ground_floor

  - title: Configuration
    cards:
      - type: custom:motiondirection-floorplan-editor
        floorplan_id: ground_floor
      - type: custom:motiondirection-zone-editor
        floorplan_id: ground_floor
      - type: custom:motiondirection-cue-editor
        floorplan_id: ground_floor

  - title: Monitoring
    cards:
      - type: custom:motiondirection-zone-status
        floorplan_id: ground_floor
      - type: custom:motiondirection-cue-status
        floorplan_id: ground_floor
      - type: custom:motiondirection-zone-flow-visualizer
        floorplan_id: ground_floor

  - title: Analysis
    cards:
      - type: custom:motiondirection-motion-visualizer
        floorplan_id: ground_floor
```

## Troubleshooting

### Cards Not Appearing
1. Verify integration is loaded: Developer Tools → Info → Check integrations
2. Check browser console for errors (F12)
3. Clear browser cache and refresh
4. Verify HACS installation is complete
5. Restart Home Assistant

### Cards Not Loading
1. Check `configuration.yaml` for resource URLs
2. Verify files exist in `/config/custom_components/motiondirection/frontend/`
3. Check file permissions
4. Verify network connectivity
5. Check Home Assistant logs for errors

### Visual Issues
1. Clear browser cache
2. Try different browser
3. Disable browser extensions
4. Check for theme conflicts
5. Verify card configuration is valid

### Performance Issues
1. Reduce particle count in visualizers
2. Disable unnecessary features (timeline, statistics)
3. Reduce update frequency
4. Use compact layout mode
5. Limit number of zones/cues displayed

## Development

### Creating Custom Card Variations

You can extend the base cards to create custom variations:

```javascript
import { MotionDirectionMotionStatusCard } from '/hacsfiles/ha-motiondirection/motion-status-card.js';

class CustomMotionStatusCard extends MotionDirectionMotionStatusCard {
  // Override methods to customize behavior
  render() {
    super.render();
    // Add custom styling or elements
  }
}

customElements.define('custom-motion-status-card', CustomMotionStatusCard);
```

### Card Events

Cards emit custom events that can be listened to:

```javascript
// Listen for card events
document.addEventListener('motiondirection-card-update', (event) => {
  console.log('Card updated:', event.detail);
});

// Available events:
// - motiondirection-card-update: Card data updated
// - motiondirection-card-error: Card error occurred
// - motiondirection-zone-selected: Zone selected in editor
// - motiondirection-cue-selected: Cue selected in editor
// - motiondirection-sensor-clicked: Sensor clicked in visualizer
```

## Additional Resources

- [MotionDirection Documentation](../../../docs/README.md)
- [Configuration Guide](../../../docs/CONFIGURATION.md)
- [API Reference](../../../docs/API.md)
- [Troubleshooting Guide](../../../docs/TROUBLESHOOTING.md)
