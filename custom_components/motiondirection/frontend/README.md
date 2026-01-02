# Frontend Components

This directory contains custom Lovelace cards for the Motion Direction integration.

## Overview

The Motion Direction integration provides custom cards for visualizing and interacting with motion detection data in Home Assistant dashboards.

## Available Cards

### 1. Motion Status Card (`motion-status-card.js`) ✅ COMPLETE

A comprehensive status card that displays:
- Current motion direction with icon
- Confidence score with visual bar
- Detection method (multi-sensor, hybrid, cue-assisted)
- Active zones
- Triggered sensors
- Contributing secondary cues
- Pattern type

**Configuration:**
```yaml
type: custom:motion-status-card
entity: sensor.motion_direction
title: "Motion Direction"  # Optional
show_confidence: true       # Optional, default: true
show_zones: true           # Optional, default: true
show_sensors: true         # Optional, default: true
show_pattern: true         # Optional, default: true
show_cues: true            # Optional, default: true
```

**Installation:**
1. Copy `motion-status-card.js` to `/config/www/motion-direction/`
2. Add resource in Home Assistant:
   - Go to Settings → Dashboards → Resources
   - Click "Add Resource"
   - URL: `/local/motion-direction/motion-status-card.js`
   - Resource type: JavaScript Module

### 2. Floorplan Editor Card (Planned)

An interactive floorplan editor for:
- Placing and positioning sensors
- Drawing zone polygons
- Adding secondary cues
- Configuring trigger zones
- Real-time motion visualization

**Status:** Architecture documented, ready for implementation

### 3. Motion Visualizer Card (Planned)

Real-time motion visualization with:
- Motion path animation
- Heat map generation
- Historical playback
- Confidence overlays

**Status:** Architecture documented, ready for implementation

### 4. Zone Status Card (Planned)

Zone monitoring card showing:
- Zone occupancy states
- Direction per zone
- Statistics (transitions, dwell time)
- Zone filtering and sorting

**Status:** Architecture documented, ready for implementation

## Architecture

### Base Card Pattern

All cards follow the Home Assistant custom card pattern:

```javascript
class MyCustomCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  // Called when HA state changes
  set hass(hass) {
    this._hass = hass;
    this._updateCard();
  }

  // Called when user configures card
  setConfig(config) {
    if (!config.entity) {
      throw new Error('Entity required');
    }
    this._config = config;
    this._updateCard();
  }

  // For masonry layout
  getCardSize() {
    return 3;
  }

  // For sections layout
  getGridOptions() {
    return {
      rows: 3,
      columns: 6,
      min_rows: 2,
      max_rows: 6,
    };
  }
}

customElements.define('my-custom-card', MyCustomCard);
```

### Styling Guidelines

1. **Use HA CSS Variables:**
   - `--primary-color`
   - `--primary-text-color`
   - `--secondary-text-color`
   - `--secondary-background-color`
   - `--success-color`, `--warning-color`, `--error-color`

2. **Follow Material Design principles:**
   - 8px grid system
   - Elevation shadows for depth
   - Smooth transitions (0.3s ease)

3. **Ensure theme compatibility:**
   - Test with light and dark themes
   - Use relative colors, not hardcoded values

### Real-Time Updates

Cards receive updates via the `hass` property setter:

```javascript
set hass(hass) {
  this._hass = hass;
  
  // Access entity state
  const entity = hass.states[this._config.entity];
  
  // Update card content
  this._updateCard();
}
```

For WebSocket subscriptions (advanced):

```javascript
// Subscribe to events
this._hass.connection.subscribeEvents((event) => {
  if (event.event_type === 'motiondirection_motion_detected') {
    this._handleMotionEvent(event.data);
  }
}, 'motiondirection_motion_detected');
```

## Development

### Prerequisites

- Node.js and npm (for development builds)
- Home Assistant instance for testing
- Basic knowledge of JavaScript/TypeScript
- Understanding of Web Components and Shadow DOM

### Development Workflow

1. **Create card file:**
   ```bash
   touch custom_components/motiondirection/frontend/my-card.js
   ```

2. **Implement card:**
   - Extend `HTMLElement`
   - Implement required methods
   - Add styles using shadow DOM

3. **Test locally:**
   - Copy to `/config/www/motion-direction/`
   - Add as resource in HA
   - Add card to dashboard
   - Test with different configurations

4. **Debug:**
   - Use browser DevTools Console
   - Check for errors in HA logs
   - Validate with `hass.states` in console

### Building for Production

For TypeScript/bundled builds:

```bash
# Install dependencies
npm install

# Development build with watch
npm run dev

# Production build
npm run build
```

## Testing Cards

### Quick Test Setup

```yaml
# In your dashboard
views:
  - title: Motion Test
    cards:
      - type: custom:motion-status-card
        entity: sensor.motion_direction
```

### Testing Checklist

- [ ] Card loads without errors
- [ ] Configuration validation works
- [ ] Updates reflect state changes
- [ ] Styling works in light/dark themes
- [ ] Responsive on mobile devices
- [ ] No console errors
- [ ] Performance is acceptable

## Best Practices

### Performance

1. **Throttle updates:** Don't update on every tiny state change
2. **Use shadow DOM:** Encapsulate styles
3. **Minimize DOM operations:** Batch updates
4. **Lazy load resources:** Only load what's needed

### Accessibility

1. **Use semantic HTML:** Proper heading structure
2. **ARIA labels:** For screen readers
3. **Keyboard navigation:** Ensure all features accessible
4. **Color contrast:** Meet WCAG AA standards

### Error Handling

```javascript
setConfig(config) {
  if (!config.entity) {
    throw new Error('You need to define an entity');
  }
  
  // Validate entity exists in next hass update
}

set hass(hass) {
  const entity = hass.states[this._config.entity];
  
  if (!entity) {
    this._showError('Entity not found');
    return;
  }
  
  // Normal update
}
```

## Contributing

When adding new cards:

1. Follow the architecture patterns established
2. Use meaningful variable names
3. Add comprehensive configuration options
4. Document all features
5. Include usage examples
6. Test with multiple themes
7. Update this README

## Resources

- [Home Assistant Developer Docs - Custom Cards](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/)
- [Web Components MDN](https://developer.mozilla.org/en-US/docs/Web/Web_Components)
- [Lit Element](https://lit.dev/)
- [Material Design](https://material.io/design)

## License

MIT License - See project LICENSE file
