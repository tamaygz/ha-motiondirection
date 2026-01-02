# Frontend Components

This directory contains custom Lovelace cards for the Motion Direction integration.

## Overview

The Motion Direction integration provides **9 fully-implemented custom cards** for visualizing and interacting with motion detection data in Home Assistant dashboards. All cards support automatic installation, real-time updates, and work seamlessly with both light and dark themes.

### Key Features

- **✅ All 9 Cards Fully Implemented** - Complete functionality ready to use
- **🔄 Automatic Registration** - Cards auto-register via card-loader.js
- **🎨 Theme Compatible** - Works with light/dark themes and custom themes
- **📱 Responsive Design** - Optimized for desktop, tablet, and mobile
- **⚡ Real-time Updates** - Smooth updates via Home Assistant state changes
- **🛠️ Configuration UI** - All cards configurable through the dashboard UI
- **📊 Multiple Visualization Modes** - Trails, heatmaps, particles, arrows, and more
- **🔌 HACS Compatible** - Easy installation and updates via HACS

### Card Categories

**Status & Monitoring (3 cards):**
- Motion Status Card - Current direction, confidence, detection method
- Zone Status Card - Zone occupancy, direction, statistics
- Cue Status Card - Secondary cue states and correlations

**Visualization (3 cards):**
- Motion Visualizer Card - Motion paths, heatmaps, historical playback
- Hybrid Visualizer Card - Combined motion and cue visualization
- Zone Flow Visualizer Card - Inter-zone movement flow

**Configuration & Editing (3 cards):**
- Floorplan Editor Card - Interactive sensor and zone placement
- Zone Editor Card - Polygon drawing and zone configuration
- Cue Editor Card - Secondary cue placement and configuration

## Available Cards

### 1. Motion Status Card (`motion-status-card.js`) ✅ IMPLEMENTED

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
type: custom:motiondirection-motion-status
entity: sensor.motion_direction
title: "Motion Direction"  # Optional
show_confidence: true       # Optional, default: true
show_zones: true           # Optional, default: true
show_sensors: true         # Optional, default: true
show_pattern: true         # Optional, default: true
show_cues: true            # Optional, default: true
```

### 2. Floorplan Editor Card (`floorplan-editor-card.js`) ✅ IMPLEMENTED

An interactive floorplan editor for:
- Placing and positioning sensors
- Drawing zone polygons
- Adding secondary cues
- Configuring trigger zones
- Real-time motion visualization

**Configuration:**
```yaml
type: custom:motiondirection-floorplan-editor
floorplan_id: ground_floor
width: 1000
height: 1000
background_image: /local/floorplan.png
show_grid: true
```

### 3. Motion Visualizer Card (`motion-visualizer-card.js`) ✅ IMPLEMENTED

Real-time motion visualization with:
- Motion path animation (trails, arrows, particles)
- Heat map generation
- Historical playback
- Confidence overlays

**Configuration:**
```yaml
type: custom:motiondirection-motion-visualizer
floorplan_id: ground_floor
visualization_mode: trails  # trails, arrows, particles, heatmap
show_sensors: true
show_direction_arrows: true
trail_length: 50
playback_speed: 1.0
```

### 4. Zone Status Card (`zone-status-card.js`) ✅ IMPLEMENTED

Zone monitoring card showing:
- Zone occupancy states
- Direction per zone
- Statistics (transitions, dwell time)
- Zone filtering and sorting

**Configuration:**
```yaml
type: custom:motiondirection-zone-status
floorplan_id: ground_floor
layout: grid  # grid, list, compact
show_occupancy: true
show_direction: true
show_statistics: true
```

### 5. Zone Editor Card (`zone-editor-card.js`) ✅ IMPLEMENTED

Interactive zone editing interface:
- Polygon drawing tools
- Zone naming and configuration
- Direction configuration
- Trigger zone setup

**Configuration:**
```yaml
type: custom:motiondirection-zone-editor
floorplan_id: ground_floor
show_existing_zones: true
enable_zone_editing: true
```

### 6. Zone Flow Visualizer Card (`zone-flow-visualizer-card.js`) ✅ IMPLEMENTED

Visualize movement flow between zones:
- Particle flow animation
- Direction arrows between zones
- Heat map overlays
- Flow statistics

**Configuration:**
```yaml
type: custom:motiondirection-zone-flow-visualizer
floorplan_id: ground_floor
visualization_mode: particles  # particles, arrows, heatmap
particle_count: 100
show_statistics: true
```

### 7. Cue Editor Card (`cue-editor-card.js`) ✅ IMPLEMENTED

Configure secondary cues (lights, doors, switches):
- Entity selection and placement
- Directional hint configuration
- Drag-and-drop positioning
- Cue type assignment

**Configuration:**
```yaml
type: custom:motiondirection-cue-editor
floorplan_id: ground_floor
show_available_entities: true
entity_types: [light, switch, media_player, climate]
enable_drag_drop: true
```

### 8. Cue Status Card (`cue-status-card.js`) ✅ IMPLEMENTED

Monitor secondary cue performance:
- Current cue states
- Correlation with motion events
- Success rates
- Contributing patterns

**Configuration:**
```yaml
type: custom:motiondirection-cue-status
floorplan_id: ground_floor
layout: grid  # grid, list, compact
show_state: true
show_correlation: true
show_success_rate: true
```

### 9. Hybrid Visualizer Card (`hybrid-visualizer-card.js`) ✅ IMPLEMENTED

Comprehensive hybrid detection visualization:
- Motion sensors and secondary cues overlay
- Detection method indicators
- Correlation lines
- Confidence-based opacity
- Timeline view

**Configuration:**
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
```

## Installation

### Automatic Installation (Recommended)

The Motion Direction integration automatically registers all custom cards when installed. No manual steps required!

**How it works:**
1. The integration includes a `card-loader.js` that auto-registers all 9 cards
2. Cards are served directly from the integration's frontend directory
3. Resources are automatically available at `/hacsfiles/ha-motiondirection/`
4. The card loader registers cards with Home Assistant's custom cards registry

**To verify installation:**
1. Go to Settings → Dashboards → Add Card
2. Search for "MotionDirection" in the card picker
3. You should see all 9 cards available

### HACS Installation

If you're using HACS (Home Assistant Community Store):

1. **Add this repository to HACS:**
   - HACS → Integrations → Custom Repositories
   - URL: `https://github.com/tamaygz/ha-motiondirection`
   - Category: Integration

2. **Install via HACS:**
   - HACS → Integrations → Explore & Download Repositories
   - Search for "Motion Direction"
   - Click "Download"

3. **Restart Home Assistant**

4. **Add the integration:**
   - Settings → Devices & Services → Add Integration
   - Search for "Motion Direction"

### Manual Installation

If automatic registration doesn't work, you can manually register the resources:

1. **Copy files to www directory:**
   ```bash
   mkdir -p /config/www/motion-direction/
   cp custom_components/motiondirection/frontend/*.js /config/www/motion-direction/
   ```

2. **Add resources via UI:**
   - Settings → Dashboards → Resources
   - Click "Add Resource"
   - For each card, add:
     - URL: `/local/motion-direction/<card-name>.js`
     - Resource type: JavaScript Module

3. **Or add to configuration.yaml:**
   ```yaml
   lovelace:
     mode: yaml
     resources:
       - url: /local/motion-direction/card-loader.js
         type: module
       # Or add each card individually
       - url: /local/motion-direction/motion-status-card.js
         type: module
       - url: /local/motion-direction/floorplan-editor-card.js
         type: module
       # ... etc
   ```

### Integration-Served Resources (Advanced)

For custom integrations, Home Assistant supports serving frontend resources directly from the integration:

**Method 1: Frontend Panel Registration**
The integration can register a frontend panel that serves the cards:

```python
# In __init__.py
hass.http.register_static_path(
    "/hacsfiles/ha-motiondirection",
    hass.config.path("custom_components/motiondirection/frontend"),
    cache_headers=False
)
```

**Method 2: Lovelace Resource Registration**
Programmatically register resources during setup:

```python
# In __init__.py
from homeassistant.components.lovelace import dashboard

async def async_setup(hass, config):
    # Register custom cards as resources
    await dashboard.async_register_resource(
        hass,
        "/hacsfiles/ha-motiondirection/card-loader.js",
        resource_type="module"
    )
```

**Method 3: Frontend Extra Module URL**
Register cards as extra modules loaded on every page:

```python
# In manifest.json
{
  "frontend": {
    "extra_module_url": [
      "/hacsfiles/ha-motiondirection/card-loader.js"
    ]
  }
}
```

### Troubleshooting Installation

**Cards not appearing:**
1. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
2. Clear browser cache
3. Check browser console for errors (F12 → Console)
4. Verify files exist in the frontend directory
5. Restart Home Assistant

**Cards showing as "Custom element doesn't exist":**
1. Check that JavaScript files are loading (Network tab in DevTools)
2. Verify resource URLs are correct
3. Check for JavaScript errors in console
4. Ensure all cards are properly registered

**CORS or 404 errors:**
1. Verify the integration is properly installed
2. Check file permissions on the frontend directory
3. Ensure www directory is accessible
4. Restart Home Assistant after moving files

### Comparing Installation Methods

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Automatic (card-loader.js)** | No manual steps, updates automatically with integration | Requires integration restart to update cards | Most users |
| **HACS** | Easy updates, community trusted, automatic resource registration | Requires HACS installed | Users with HACS |
| **Manual www/** | Full control, works without integration | Must manually copy files, update URLs | Development, testing |
| **Frontend Panel** | Professional, integrated with HA | Requires Python code changes | Integration developers |
| **Extra Module URL** | Loads on every page, always available | Loads even when not needed (performance) | System-wide cards |

**Recommendation:** Use automatic installation via card-loader.js (default) or HACS for production use. Use manual www/ method for development and testing custom modifications.

## Architecture

### Card Registration System

All cards are automatically registered through the `card-loader.js` system:

```javascript
// Cards register themselves with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'custom:motiondirection-motion-status',
  name: 'MotionDirection Motion Status',
  description: 'Display motion direction, confidence, and active zones',
  preview: true,
  module: '/hacsfiles/ha-motiondirection/motion-status-card.js',
});
```

**Benefits of this approach:**
- Cards are discoverable in the UI card picker
- Automatically loaded when needed (lazy loading)
- Properly documented with name and description
- Compatible with visual card editors
- Single entry point for all cards

**Card Registration Flow:**
1. Integration loads `card-loader.js` on startup
2. Card loader registers all 9 cards in `window.customCards` array
3. Each card module is dynamically imported when first used
4. Home Assistant's frontend discovers cards and shows them in the picker

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

### Current Implementation Status

All 9 cards have been implemented with full functionality:

| Card | File | Status | Features |
|------|------|--------|----------|
| Motion Status | `motion-status-card.js` | ✅ Complete | Direction, confidence, zones, sensors, cues |
| Floorplan Editor | `floorplan-editor-card.js` | ✅ Complete | Interactive editing, sensor placement, zones |
| Motion Visualizer | `motion-visualizer-card.js` | ✅ Complete | Trails, heatmaps, playback, multiple modes |
| Zone Status | `zone-status-card.js` | ✅ Complete | Occupancy, direction, statistics, layouts |
| Zone Editor | `zone-editor-card.js` | ✅ Complete | Polygon drawing, zone configuration |
| Zone Flow Visualizer | `zone-flow-visualizer-card.js` | ✅ Complete | Particle flow, arrows, zone transitions |
| Cue Editor | `cue-editor-card.js` | ✅ Complete | Entity selection, drag-drop, placement |
| Cue Status | `cue-status-card.js` | ✅ Complete | State, correlation, success rates |
| Hybrid Visualizer | `hybrid-visualizer-card.js` | ✅ Complete | Combined visualization, timeline, methods |

### Card Loader Implementation

The `card-loader.js` serves as the registration hub:

**Key Functions:**
- `registerCards()` - Registers all 9 cards with Home Assistant
- `loadCardModules()` - Dynamically imports card modules
- `getResourceUrls()` - Returns resource URLs for configuration
- `getCardExamples()` - Provides example configurations

**Adding a New Card:**

1. **Create the card file:**
   ```bash
   touch custom_components/motiondirection/frontend/new-card.js
   ```

2. **Implement the card** (see Base Card Pattern below)

3. **Register in card-loader.js:**
   ```javascript
   const MOTIONDIRECTION_CARDS = [
     // ... existing cards
     {
       type: 'custom:motiondirection-new-card',
       name: 'MotionDirection New Card',
       description: 'Description of new card',
       preview: true,
       module: '/hacsfiles/ha-motiondirection/new-card.js',
     },
   ];
   ```

4. **Test the card:**
   - Restart Home Assistant
   - Hard refresh browser
   - Check card appears in picker

### Prerequisites

- Node.js and npm (optional, for TypeScript builds)
- Home Assistant instance for testing
- Basic knowledge of JavaScript ES6+
- Understanding of Web Components and Shadow DOM
- Familiarity with Home Assistant state objects

### Development Workflow

1. **Create card file:**
   ```bash
   touch custom_components/motiondirection/frontend/my-card.js
   ```

2. **Implement card:**
   - Extend `HTMLElement`
   - Implement required methods (`setConfig`, `set hass`)
   - Add styles using shadow DOM
   - Implement `getCardSize()` and `getGridOptions()`

3. **Register in card-loader.js**

4. **Test locally:**
   - Restart Home Assistant (to reload card-loader)
   - Hard refresh browser (Ctrl+Shift+R)
   - Add card to dashboard via UI
   - Test with different configurations
   - Check console for errors

5. **Debug:**
   - Use browser DevTools Console (F12)
   - Check for errors in HA logs
   - Validate with `hass.states` in console
   - Use `console.log()` for debugging
   - Inspect shadow DOM in Elements tab

6. **Iterate:**
   - Make changes to card
   - Restart HA or reload resource
   - Hard refresh browser
   - Test changes

### Building for Production

For TypeScript/bundled builds (optional):

```bash
# Install dependencies
npm install

# Development build with watch
npm run dev

# Production build (minified)
npm run build

# Run linter
npm run lint

# Run tests
npm test
```

**Note:** Currently all cards are plain JavaScript and don't require a build step. TypeScript support can be added if needed.

## Testing Cards

### Quick Test Dashboard

Create a test dashboard with all cards:

```yaml
# In your dashboard (Settings → Dashboards → Add Dashboard)
title: Motion Direction Test
views:
  - title: Status & Monitoring
    cards:
      # Motion Status Card
      - type: custom:motiondirection-motion-status
        entity: sensor.motion_direction
        show_confidence: true
        show_zones: true
        show_sensors: true
        
      # Zone Status Card
      - type: custom:motiondirection-zone-status
        floorplan_id: ground_floor
        layout: grid
        show_occupancy: true
        show_direction: true
        
      # Cue Status Card
      - type: custom:motiondirection-cue-status
        floorplan_id: ground_floor
        layout: grid
        show_correlation: true
        
  - title: Visualization
    cards:
      # Motion Visualizer
      - type: custom:motiondirection-motion-visualizer
        floorplan_id: ground_floor
        visualization_mode: trails
        show_sensors: true
        trail_length: 50
        
      # Hybrid Visualizer
      - type: custom:motiondirection-hybrid-visualizer
        floorplan_id: ground_floor
        show_motion_sensors: true
        show_secondary_cues: true
        
      # Zone Flow Visualizer
      - type: custom:motiondirection-zone-flow-visualizer
        floorplan_id: ground_floor
        visualization_mode: particles
        particle_count: 100
        
  - title: Configuration
    cards:
      # Floorplan Editor
      - type: custom:motiondirection-floorplan-editor
        floorplan_id: ground_floor
        width: 1000
        height: 800
        show_grid: true
        
      # Zone Editor
      - type: custom:motiondirection-zone-editor
        floorplan_id: ground_floor
        show_existing_zones: true
        
      # Cue Editor
      - type: custom:motiondirection-cue-editor
        floorplan_id: ground_floor
        show_available_entities: true
        enable_drag_drop: true
```

### Testing Checklist

**Initial Load:**
- [ ] Card loads without errors
- [ ] No console errors or warnings
- [ ] Card appears with expected layout
- [ ] All configured options are respected

**Functionality:**
- [ ] Configuration validation works (try invalid configs)
- [ ] Updates reflect state changes
- [ ] Interactive elements work (buttons, sliders, etc.)
- [ ] Real-time updates are smooth
- [ ] Card persists configuration across reloads

**Visual & UX:**
- [ ] Styling works in light theme
- [ ] Styling works in dark theme
- [ ] Responsive on desktop (various sizes)
- [ ] Responsive on mobile devices
- [ ] Responsive on tablet devices
- [ ] Icons and images load properly
- [ ] Animations are smooth (60fps)
- [ ] Loading states are shown appropriately

**Performance:**
- [ ] Card loads quickly (<1 second)
- [ ] No memory leaks on long-running pages
- [ ] Updates don't cause lag
- [ ] Multiple instances don't slow down page
- [ ] Browser DevTools Performance tab shows good scores

**Accessibility:**
- [ ] Keyboard navigation works
- [ ] Screen reader announces changes
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators are visible
- [ ] Interactive elements have proper ARIA labels

**Browser Compatibility:**
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Home Assistant mobile app

### Testing Checklist

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

1. **Follow established patterns** - Use the same structure as existing cards
2. **Register in card-loader.js** - Add card definition to MOTIONDIRECTION_CARDS array
3. **Use meaningful variable names** - Follow JavaScript naming conventions
4. **Add comprehensive configuration options** - Make cards flexible and customizable
5. **Document all features** - Update this README with usage examples
6. **Include usage examples** - Provide YAML configuration examples
7. **Test thoroughly** - Use the testing checklist above
8. **Test with multiple themes** - Verify light/dark theme compatibility
9. **Update this README** - Keep documentation current
10. **Submit pull request** - Include description of changes and screenshots

### Contribution Guidelines

**Code Style:**
- Use ES6+ features (const/let, arrow functions, template literals)
- Follow existing code formatting
- Add JSDoc comments for functions
- Use meaningful commit messages

**Testing:**
- Test on latest Home Assistant version
- Verify on Chrome, Firefox, and Safari
- Test on mobile devices
- Check browser console for errors

**Documentation:**
- Update README with new features
- Include configuration examples
- Document all options
- Add troubleshooting tips if needed

## Resources

### Home Assistant Documentation
- [Custom Cards Guide](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/) - Official HA custom card documentation
- [Registering Resources](https://developers.home-assistant.io/docs/frontend/custom-ui/registering-resources) - How to register frontend resources
- [Integration Manifest](https://developers.home-assistant.io/docs/creating_integration_manifest) - Manifest.json configuration
- [Frontend Data](https://developers.home-assistant.io/docs/frontend/data/) - Understanding the `hass` object
- [Lovelace Cards](https://www.home-assistant.io/dashboards/cards/) - Built-in card documentation

### Web Technologies
- [Web Components](https://developer.mozilla.org/en-US/docs/Web/Web_Components) - MDN Web Components guide
- [Shadow DOM](https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_shadow_DOM) - Encapsulation guide
- [Custom Elements](https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_custom_elements) - Custom element API
- [HTML5 Canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) - For visualization cards
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties) - CSS variables for theming

### UI/UX Design
- [Material Design](https://material.io/design) - Google's design system (used by HA)
- [Material Design Colors](https://materialui.co/colors) - Color palettes
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Accessibility standards

### Build Tools & Libraries (Optional)
- [Lit Element](https://lit.dev/) - Lightweight web components library
- [Rollup](https://rollupjs.org/) - Module bundler
- [TypeScript](https://www.typescriptlang.org/) - Type-safe JavaScript
- [ESLint](https://eslint.org/) - JavaScript linting

### Community Resources
- [HACS](https://hacs.xyz/) - Home Assistant Community Store
- [Home Assistant Community](https://community.home-assistant.io/) - Forums
- [Awesome Home Assistant](https://www.awesome-ha.com/) - Custom card examples
- [GitHub - thomasloven/lovelace-card-tools](https://github.com/thomasloven/lovelace-card-tools) - Helper library for card development

### Visualization Libraries (For Reference)
- [Chart.js](https://www.chartjs.org/) - Simple charting library
- [D3.js](https://d3js.org/) - Advanced data visualization
- [Particles.js](https://vincentgarreau.com/particles.js/) - Particle effects
- [Leaflet](https://leafletjs.com/) - Interactive maps (for floorplans)

## License

MIT License - See project LICENSE file
