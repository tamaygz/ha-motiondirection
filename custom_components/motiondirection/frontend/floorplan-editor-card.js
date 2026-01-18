/**
 * Floorplan Editor Card
 * 
 * A custom Lovelace card for Home Assistant that provides an interactive
 * floorplan editor for the MotionDirection integration. Supports sensor
 * placement, zone drawing, grid snapping, zoom/pan, and real-time visualization.
 * 
 * @version 1.0.0
 * @license MIT
 */

class FloorplanEditorCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // Core state
    this._hass = null;
    this._config = null;
    
    // Editor state
    this._mode = 'view'; // 'view' | 'edit' | 'draw_zone' | 'place_sensor'
    this._selectedElement = null;
    this._dragState = null;
    this._zoneDrawingPoints = [];
    
    // Transform state
    this._zoom = 1.0;
    this._panX = 0;
    this._panY = 0;
    this._isPanning = false;
    this._lastPanPoint = null;
    
    // Grid state
    this._gridEnabled = true;
    this._gridSize = 20;
    this._snapToGrid = true;
    
    // Floorplan data
    this._floorplanData = null;
    this._sensors = [];
    this._zones = [];
    this._cues = [];
  }

  /**
   * Set the Home Assistant object
   */
  set hass(hass) {
    this._hass = hass;
    this._loadFloorplanData();
    this._updateCard();
  }

  /**
   * Set the card configuration
   */
  setConfig(config) {
    if (!config.floorplan_id) {
      throw new Error('You need to define a floorplan_id');
    }

    this._config = {
      floorplan_id: config.floorplan_id,
      title: config.title || 'Floorplan Editor',
      mode: config.mode || 'view', // 'view', 'edit', 'create'
      show_grid: config.show_grid !== false,
      show_sensors: config.show_sensors !== false,
      show_zones: config.show_zones !== false,
      show_cues: config.show_cues !== false,
      show_paths: config.show_paths !== false,
      grid_size: config.grid_size || 20,
      snap_to_grid: config.snap_to_grid !== false,
      zoom_controls: config.zoom_controls !== false,
      ...config
    };

    this._mode = this._config.mode;
    this._gridEnabled = this._config.show_grid;
    this._gridSize = this._config.grid_size;
    this._snapToGrid = this._config.snap_to_grid;

    this._updateCard();
  }

  /**
   * Load floorplan data from Home Assistant
   */
  _loadFloorplanData() {
    if (!this._hass || !this._config) {
      return;
    }

    // Load floorplan configuration entity
    const floorplanEntity = `sensor.floorplan_${this._config.floorplan_id}`;
    const stateObj = this._hass.states[floorplanEntity];

    if (stateObj && stateObj.attributes) {
      this._floorplanData = stateObj.attributes;
      this._sensors = stateObj.attributes.sensors || [];
      this._zones = stateObj.attributes.zones || [];
      this._cues = stateObj.attributes.cues || [];
    }
  }

  /**
   * Update the card content
   */
  _updateCard() {
    if (!this._config) {
      return;
    }

    if (!this._floorplanData) {
      this.shadowRoot.innerHTML = this._renderPlaceholder();
      return;
    }

    this.shadowRoot.innerHTML = this._renderCard();
    this._attachEventListeners();
  }

  /**
   * Render placeholder when no floorplan data
   */
  _renderPlaceholder() {
    return `
      <style>${this._getStyles()}</style>
      <ha-card>
        <div class="card-content placeholder">
          <ha-icon icon="mdi:floor-plan"></ha-icon>
          <p>No floorplan data available</p>
          <p class="hint">Configure your floorplan using the config flow or YAML</p>
        </div>
      </ha-card>
    `;
  }

  /**
   * Render the complete card
   */
  _renderCard() {
    return `
      <style>${this._getStyles()}</style>
      <ha-card>
        ${this._renderHeader()}
        ${this._renderToolbar()}
        <div class="card-content">
          ${this._renderFloorplan()}
        </div>
        ${this._mode !== 'view' ? this._renderControls() : ''}
      </ha-card>
    `;
  }

  /**
   * Render card header
   */
  _renderHeader() {
    return `
      <div class="card-header">
        <div class="name">
          <ha-icon icon="mdi:floor-plan"></ha-icon>
          ${this._config.title}
        </div>
        <div class="mode-indicator mode-${this._mode}">
          ${this._formatMode(this._mode)}
        </div>
      </div>
    `;
  }

  /**
   * Render toolbar with mode buttons
   */
  _renderToolbar() {
    if (this._config.mode === 'view') {
      return '';
    }

    return `
      <div class="toolbar">
        <div class="toolbar-group">
          <button class="toolbar-btn ${this._mode === 'view' ? 'active' : ''}" 
                  data-action="mode-view" title="View Mode">
            <ha-icon icon="mdi:eye"></ha-icon>
          </button>
          <button class="toolbar-btn ${this._mode === 'edit' ? 'active' : ''}" 
                  data-action="mode-edit" title="Edit Mode">
            <ha-icon icon="mdi:cursor-move"></ha-icon>
          </button>
          <button class="toolbar-btn ${this._mode === 'draw_zone' ? 'active' : ''}" 
                  data-action="mode-draw-zone" title="Draw Zone">
            <ha-icon icon="mdi:vector-polygon"></ha-icon>
          </button>
          <button class="toolbar-btn ${this._mode === 'place_sensor' ? 'active' : ''}" 
                  data-action="mode-place-sensor" title="Place Sensor">
            <ha-icon icon="mdi:motion-sensor"></ha-icon>
          </button>
        </div>
        
        <div class="toolbar-group">
          <button class="toolbar-btn ${this._gridEnabled ? 'active' : ''}" 
                  data-action="toggle-grid" title="Toggle Grid">
            <ha-icon icon="mdi:grid"></ha-icon>
          </button>
          <button class="toolbar-btn ${this._snapToGrid ? 'active' : ''}" 
                  data-action="toggle-snap" title="Snap to Grid">
            <ha-icon icon="mdi:magnet"></ha-icon>
          </button>
        </div>
        
        <div class="toolbar-group">
          <button class="toolbar-btn" data-action="zoom-in" title="Zoom In">
            <ha-icon icon="mdi:magnify-plus"></ha-icon>
          </button>
          <button class="toolbar-btn" data-action="zoom-out" title="Zoom Out">
            <ha-icon icon="mdi:magnify-minus"></ha-icon>
          </button>
          <button class="toolbar-btn" data-action="zoom-fit" title="Fit to View">
            <ha-icon icon="mdi:fit-to-screen"></ha-icon>
          </button>
        </div>
        
        ${this._selectedElement ? `
          <div class="toolbar-group">
            <button class="toolbar-btn" data-action="delete-selected" title="Delete">
              <ha-icon icon="mdi:delete"></ha-icon>
            </button>
          </div>
        ` : ''}
      </div>
    `;
  }

  /**
   * Render floorplan SVG
   */
  _renderFloorplan() {
    const width = this._floorplanData.dimensions?.width || 1000;
    const height = this._floorplanData.dimensions?.height || 800;
    const backgroundImage = this._floorplanData.background_image || '';

    return `
      <div class="floorplan-container" id="floorplan-container">
        <svg id="floorplan-svg" 
             class="floorplan-svg"
             viewBox="0 0 ${width} ${height}"
             preserveAspectRatio="xMidYMid meet">
          
          <!-- Definitions for patterns and markers -->
          <defs>
            ${this._renderDefs()}
          </defs>
          
          <!-- Background layer -->
          <g id="layer-background" class="layer">
            ${this._renderBackground(width, height, backgroundImage)}
          </g>
          
          <!-- Grid layer -->
          ${this._gridEnabled ? this._renderGrid(width, height) : ''}
          
          <!-- Zones layer -->
          <g id="layer-zones" class="layer layer-zones">
            ${this._config.show_zones ? this._renderZones() : ''}
          </g>
          
          <!-- Sensors layer -->
          <g id="layer-sensors" class="layer layer-sensors">
            ${this._config.show_sensors ? this._renderSensors() : ''}
          </g>
          
          <!-- Cues layer -->
          <g id="layer-cues" class="layer layer-cues">
            ${this._config.show_cues ? this._renderCues() : ''}
          </g>
          
          <!-- Drawing layer (temporary shapes while drawing) -->
          <g id="layer-drawing" class="layer layer-drawing">
            ${this._mode === 'draw_zone' ? this._renderZoneDrawing() : ''}
          </g>
        </svg>
      </div>
    `;
  }

  /**
   * Render SVG definitions (gradients, patterns, markers)
   */
  _renderDefs() {
    return `
      <!-- Arrow marker for direction -->
      <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" 
              orient="auto" markerUnits="strokeWidth">
        <path d="M0,0 L0,6 L9,3 z" fill="var(--primary-color)" />
      </marker>
      
      <!-- Selection gradient -->
      <linearGradient id="selection-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color: var(--primary-color); stop-opacity: 0.3" />
        <stop offset="100%" style="stop-color: var(--primary-color); stop-opacity: 0.1" />
      </linearGradient>
      
      <!-- Sensor range gradient -->
      <radialGradient id="sensor-range-gradient">
        <stop offset="0%" style="stop-color: var(--info-color); stop-opacity: 0.4" />
        <stop offset="100%" style="stop-color: var(--info-color); stop-opacity: 0" />
      </radialGradient>
    `;
  }

  /**
   * Render background layer
   */
  _renderBackground(width, height, backgroundImage) {
    if (backgroundImage) {
      return `
        <image href="${backgroundImage}" 
               width="${width}" 
               height="${height}" 
               preserveAspectRatio="xMidYMid meet" />
      `;
    }
    return `
      <rect width="${width}" height="${height}" 
            fill="var(--secondary-background-color)" />
    `;
  }

  /**
   * Render grid overlay
   */
  _renderGrid(width, height) {
    const lines = [];
    
    // Vertical lines
    for (let x = 0; x <= width; x += this._gridSize) {
      lines.push(`<line x1="${x}" y1="0" x2="${x}" y2="${height}" 
                        class="grid-line" />`);
    }
    
    // Horizontal lines
    for (let y = 0; y <= height; y += this._gridSize) {
      lines.push(`<line x1="0" y1="${y}" x2="${width}" y2="${y}" 
                        class="grid-line" />`);
    }
    
    return `
      <g id="layer-grid" class="layer layer-grid">
        ${lines.join('\n')}
      </g>
    `;
  }

  /**
   * Render zones
   */
  _renderZones() {
    return this._zones.map((zone, index) => {
      const points = zone.polygon.map(p => `${p[0]},${p[1]}`).join(' ');
      const isSelected = this._selectedElement?.type === 'zone' && 
                        this._selectedElement?.id === zone.id;
      
      return `
        <g class="zone ${isSelected ? 'selected' : ''}" 
           data-type="zone" 
           data-id="${zone.id}">
          <polygon points="${points}" 
                   class="zone-polygon"
                   fill="url(#selection-gradient)" 
                   stroke="var(--primary-color)"
                   stroke-width="2"
                   opacity="0.6" />
          
          <!-- Zone center point -->
          <circle cx="${zone.center[0]}" 
                  cy="${zone.center[1]}" 
                  r="5" 
                  class="zone-center"
                  fill="var(--primary-color)" />
          
          <!-- Zone label -->
          <text x="${zone.center[0]}" 
                y="${zone.center[1] - 15}" 
                class="zone-label"
                text-anchor="middle"
                fill="var(--primary-text-color)">
            ${zone.name}
          </text>
          
          <!-- Direction arrows -->
          ${this._renderZoneDirections(zone)}
        </g>
      `;
    }).join('');
  }

  /**
   * Render zone direction arrows
   */
  _renderZoneDirections(zone) {
    if (!zone.known_directions || zone.known_directions.length === 0) {
      return '';
    }

    return zone.known_directions.map(dir => {
      const vector = dir.vector;
      const startX = zone.center[0];
      const startY = zone.center[1];
      const endX = startX + vector[0] * 50;
      const endY = startY + vector[1] * 50;

      return `
        <line x1="${startX}" y1="${startY}" 
              x2="${endX}" y2="${endY}"
              class="direction-arrow"
              stroke="var(--primary-color)"
              stroke-width="2"
              marker-end="url(#arrow)" />
        <text x="${endX + 10}" y="${endY}" 
              class="direction-label"
              fill="var(--secondary-text-color)"
              font-size="12">
          ${dir.name}
        </text>
      `;
    }).join('');
  }

  /**
   * Render sensors
   */
  _renderSensors() {
    return this._sensors.map((sensor, index) => {
      const isSelected = this._selectedElement?.type === 'sensor' && 
                        this._selectedElement?.id === sensor.entity_id;
      
      return `
        <g class="sensor ${isSelected ? 'selected' : ''}" 
           data-type="sensor" 
           data-id="${sensor.entity_id}">
          
          <!-- Sensor range -->
          <circle cx="${sensor.position[0]}" 
                  cy="${sensor.position[1]}" 
                  r="${sensor.range || 100}" 
                  class="sensor-range"
                  fill="url(#sensor-range-gradient)" 
                  stroke="none" />
          
          <!-- Sensor icon -->
          <circle cx="${sensor.position[0]}" 
                  cy="${sensor.position[1]}" 
                  r="12" 
                  class="sensor-icon"
                  fill="var(--info-color)"
                  stroke="var(--card-background-color)"
                  stroke-width="2" />
          
          <!-- Sensor label -->
          <text x="${sensor.position[0]}" 
                y="${sensor.position[1] + 25}" 
                class="sensor-label"
                text-anchor="middle"
                fill="var(--primary-text-color)"
                font-size="10">
            ${this._formatEntityName(sensor.entity_id)}
          </text>
        </g>
      `;
    }).join('');
  }

  /**
   * Render secondary cues
   */
  _renderCues() {
    return this._cues.map((cue, index) => {
      const isSelected = this._selectedElement?.type === 'cue' && 
                        this._selectedElement?.id === cue.entity_id;
      const icon = this._getCueIcon(cue.cue_type);
      
      return `
        <g class="cue ${isSelected ? 'selected' : ''}" 
           data-type="cue" 
           data-id="${cue.entity_id}">
          
          <!-- Cue range circle -->
          <circle cx="${cue.position[0]}" 
                  cy="${cue.position[1]}" 
                  r="${cue.range_radius || 50}" 
                  class="cue-range"
                  fill="none"
                  stroke="var(--warning-color)"
                  stroke-width="1"
                  stroke-dasharray="5,5"
                  opacity="0.5" />
          
          <!-- Cue icon placeholder -->
          <circle cx="${cue.position[0]}" 
                  cy="${cue.position[1]}" 
                  r="10" 
                  class="cue-icon"
                  fill="${cue.color || 'var(--warning-color)'}"
                  stroke="var(--card-background-color)"
                  stroke-width="2" />
          
          <!-- Cue label -->
          <text x="${cue.position[0]}" 
                y="${cue.position[1] + 20}" 
                class="cue-label"
                text-anchor="middle"
                fill="var(--primary-text-color)"
                font-size="10">
            ${cue.cue_type}
          </text>
        </g>
      `;
    }).join('');
  }

  /**
   * Render zone being drawn
   */
  _renderZoneDrawing() {
    if (this._zoneDrawingPoints.length === 0) {
      return '';
    }

    const points = this._zoneDrawingPoints.map(p => `${p[0]},${p[1]}`).join(' ');
    
    return `
      <!-- Preview polygon -->
      ${this._zoneDrawingPoints.length >= 3 ? `
        <polygon points="${points}" 
                 class="zone-preview"
                 fill="var(--primary-color)"
                 fill-opacity="0.2"
                 stroke="var(--primary-color)"
                 stroke-width="2"
                 stroke-dasharray="5,5" />
      ` : ''}
      
      <!-- Drawing points -->
      ${this._zoneDrawingPoints.map((point, index) => `
        <circle cx="${point[0]}" 
                cy="${point[1]}" 
                r="5" 
                class="drawing-point"
                fill="var(--primary-color)"
                stroke="var(--card-background-color)"
                stroke-width="2" />
        <text x="${point[0] + 10}" 
              y="${point[1] - 10}" 
              class="point-label"
              fill="var(--primary-text-color)"
              font-size="10">
          ${index + 1}
        </text>
      `).join('')}
      
      <!-- Lines between points -->
      ${this._zoneDrawingPoints.length > 1 ? this._zoneDrawingPoints.slice(0, -1).map((point, index) => {
        const nextPoint = this._zoneDrawingPoints[index + 1];
        return `
          <line x1="${point[0]}" y1="${point[1]}" 
                x2="${nextPoint[0]}" y2="${nextPoint[1]}"
                class="drawing-line"
                stroke="var(--primary-color)"
                stroke-width="2"
                stroke-dasharray="5,5" />
        `;
      }).join('') : ''}
    `;
  }

  /**
   * Render control panel
   */
  _renderControls() {
    return `
      <div class="controls">
        ${this._mode === 'draw_zone' ? this._renderZoneControls() : ''}
        ${this._mode === 'place_sensor' ? this._renderSensorControls() : ''}
      </div>
    `;
  }

  /**
   * Render zone drawing controls
   */
  _renderZoneControls() {
    return `
      <div class="control-panel">
        <div class="control-header">Drawing Zone</div>
        <div class="control-content">
          <p class="control-hint">Click on the floorplan to add points (min 3 points)</p>
          <p class="control-info">Points: ${this._zoneDrawingPoints.length}</p>
          <div class="control-buttons">
            <button class="control-btn" data-action="finish-zone" 
                    ${this._zoneDrawingPoints.length < 3 ? 'disabled' : ''}>
              <ha-icon icon="mdi:check"></ha-icon>
              Finish Zone
            </button>
            <button class="control-btn secondary" data-action="cancel-zone">
              <ha-icon icon="mdi:close"></ha-icon>
              Cancel
            </button>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Render sensor placement controls
   */
  _renderSensorControls() {
    return `
      <div class="control-panel">
        <div class="control-header">Place Sensor</div>
        <div class="control-content">
          <p class="control-hint">Click on the floorplan to place a sensor</p>
          <div class="control-buttons">
            <button class="control-btn secondary" data-action="cancel-sensor">
              <ha-icon icon="mdi:close"></ha-icon>
              Cancel
            </button>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Attach event listeners
   */
  _attachEventListeners() {
    const root = this.shadowRoot;

    // Toolbar button clicks
    root.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', (e) => this._handleAction(e.currentTarget.dataset.action));
    });

    // Floorplan interactions
    const svg = root.getElementById('floorplan-svg');
    if (svg) {
      svg.addEventListener('click', (e) => this._handleFloorplanClick(e));
      svg.addEventListener('mousedown', (e) => this._handleMouseDown(e));
      svg.addEventListener('mousemove', (e) => this._handleMouseMove(e));
      svg.addEventListener('mouseup', (e) => this._handleMouseUp(e));
      svg.addEventListener('wheel', (e) => this._handleWheel(e));
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => this._handleKeyDown(e));
  }

  /**
   * Handle toolbar action
   */
  _handleAction(action) {
    switch (action) {
      case 'mode-view':
        this._setMode('view');
        break;
      case 'mode-edit':
        this._setMode('edit');
        break;
      case 'mode-draw-zone':
        this._setMode('draw_zone');
        break;
      case 'mode-place-sensor':
        this._setMode('place_sensor');
        break;
      case 'toggle-grid':
        this._gridEnabled = !this._gridEnabled;
        this._updateCard();
        break;
      case 'toggle-snap':
        this._snapToGrid = !this._snapToGrid;
        this._updateCard();
        break;
      case 'zoom-in':
        this._zoom = Math.min(this._zoom * 1.2, 5.0);
        this._updateCard();
        break;
      case 'zoom-out':
        this._zoom = Math.max(this._zoom / 1.2, 0.2);
        this._updateCard();
        break;
      case 'zoom-fit':
        this._zoom = 1.0;
        this._panX = 0;
        this._panY = 0;
        this._updateCard();
        break;
      case 'delete-selected':
        this._deleteSelected();
        break;
      case 'finish-zone':
        this._finishZone();
        break;
      case 'cancel-zone':
        this._cancelZone();
        break;
      case 'cancel-sensor':
        this._setMode('edit');
        break;
    }
  }

  /**
   * Handle floorplan click
   */
  _handleFloorplanClick(e) {
    if (e.target.closest('[data-type]')) {
      // Clicked on an element
      const element = e.target.closest('[data-type]');
      const type = element.dataset.type;
      const id = element.dataset.id;
      
      if (this._mode === 'edit') {
        this._selectedElement = { type, id };
        this._updateCard();
      }
      return;
    }

    // Clicked on empty space
    const point = this._getSVGPoint(e);
    const snappedPoint = this._snapToGrid ? this._snapPoint(point) : point;

    if (this._mode === 'draw_zone') {
      this._zoneDrawingPoints.push(snappedPoint);
      this._updateCard();
    } else if (this._mode === 'place_sensor') {
      this._placeSensor(snappedPoint);
    } else if (this._mode === 'edit') {
      this._selectedElement = null;
      this._updateCard();
    }
  }

  /**
   * Handle mouse down (start drag or pan)
   */
  _handleMouseDown(e) {
    if (e.button === 1 || (e.button === 0 && e.shiftKey)) {
      // Middle mouse or shift+left = pan
      this._isPanning = true;
      this._lastPanPoint = { x: e.clientX, y: e.clientY };
      e.preventDefault();
    } else if (this._mode === 'edit' && e.target.closest('[data-type]')) {
      // Start dragging element
      const element = e.target.closest('[data-type]');
      this._dragState = {
        type: element.dataset.type,
        id: element.dataset.id,
        startPoint: this._getSVGPoint(e)
      };
    }
  }

  /**
   * Handle mouse move (drag or pan)
   */
  _handleMouseMove(e) {
    if (this._isPanning && this._lastPanPoint) {
      const dx = e.clientX - this._lastPanPoint.x;
      const dy = e.clientY - this._lastPanPoint.y;
      this._panX += dx;
      this._panY += dy;
      this._lastPanPoint = { x: e.clientX, y: e.clientY };
      this._updateTransform();
    } else if (this._dragState) {
      const currentPoint = this._getSVGPoint(e);
      const snappedPoint = this._snapToGrid ? this._snapPoint(currentPoint) : currentPoint;
      this._updateElementPosition(this._dragState.type, this._dragState.id, snappedPoint);
    }
  }

  /**
   * Handle mouse up (end drag or pan)
   */
  _handleMouseUp(e) {
    if (this._isPanning) {
      this._isPanning = false;
      this._lastPanPoint = null;
    } else if (this._dragState) {
      const currentPoint = this._getSVGPoint(e);
      const snappedPoint = this._snapToGrid ? this._snapPoint(currentPoint) : currentPoint;
      this._saveElementPosition(this._dragState.type, this._dragState.id, snappedPoint);
      this._dragState = null;
    }
  }

  /**
   * Handle mouse wheel (zoom)
   */
  _handleWheel(e) {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    this._zoom = Math.max(0.2, Math.min(5.0, this._zoom * delta));
    this._updateTransform();
  }

  /**
   * Handle keyboard shortcuts
   */
  _handleKeyDown(e) {
    if (e.key === 'Escape') {
      if (this._mode === 'draw_zone') {
        this._cancelZone();
      } else if (this._selectedElement) {
        this._selectedElement = null;
        this._updateCard();
      }
    } else if (e.key === 'Delete' && this._selectedElement) {
      this._deleteSelected();
    }
  }

  /**
   * Set editor mode
   */
  _setMode(mode) {
    this._mode = mode;
    this._selectedElement = null;
    this._zoneDrawingPoints = [];
    this._updateCard();
  }

  /**
   * Get SVG point from mouse event
   */
  _getSVGPoint(e) {
    const svg = this.shadowRoot.getElementById('floorplan-svg');
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());
    return [svgP.x, svgP.y];
  }

  /**
   * Snap point to grid
   */
  _snapPoint(point) {
    return [
      Math.round(point[0] / this._gridSize) * this._gridSize,
      Math.round(point[1] / this._gridSize) * this._gridSize
    ];
  }

  /**
   * Update element position during drag
   */
  _updateElementPosition(type, id, position) {
    // Update temporary position (visual feedback)
    const element = this.shadowRoot.querySelector(`[data-type="${type}"][data-id="${id}"]`);
    if (element) {
      element.style.transform = `translate(${position[0]}px, ${position[1]}px)`;
    }
  }

  /**
   * Save element position (call HA service)
   */
  async _saveElementPosition(type, id, position) {
    if (!this._hass) return;

    try {
      if (type === 'sensor') {
        await this._hass.callService('motiondirection', 'update_sensor_position', {
          sensor_id: id,
          position: position
        });
      } else if (type === 'cue') {
        await this._hass.callService('motiondirection', 'update_cue_position', {
          cue_id: id,
          position: position
        });
      }
      this._showNotification('Position updated successfully');
    } catch (error) {
      this._showNotification('Failed to update position: ' + error.message, 'error');
    }
  }

  /**
   * Finish zone drawing
   */
  async _finishZone() {
    if (this._zoneDrawingPoints.length < 3) {
      this._showNotification('Zone must have at least 3 points', 'warning');
      return;
    }

    try {
      // Prompt for zone name
      const zoneName = prompt('Enter zone name:');
      if (!zoneName) {
        return;
      }

      await this._hass.callService('motiondirection', 'create_zone', {
        name: zoneName,
        polygon: this._zoneDrawingPoints,
        floorplan_id: this._config.floorplan_id
      });

      this._showNotification('Zone created successfully');
      this._zoneDrawingPoints = [];
      this._setMode('edit');
      this._loadFloorplanData();
    } catch (error) {
      this._showNotification('Failed to create zone: ' + error.message, 'error');
    }
  }

  /**
   * Cancel zone drawing
   */
  _cancelZone() {
    this._zoneDrawingPoints = [];
    this._setMode('edit');
  }

  /**
   * Place sensor at position
   */
  async _placeSensor(position) {
    try {
      const sensorId = prompt('Enter sensor entity ID:');
      if (!sensorId) {
        return;
      }

      await this._hass.callService('motiondirection', 'add_sensor', {
        entity_id: sensorId,
        position: position,
        floorplan_id: this._config.floorplan_id
      });

      this._showNotification('Sensor placed successfully');
      this._setMode('edit');
      this._loadFloorplanData();
    } catch (error) {
      this._showNotification('Failed to place sensor: ' + error.message, 'error');
    }
  }

  /**
   * Delete selected element
   */
  async _deleteSelected() {
    if (!this._selectedElement) return;

    const confirmed = confirm(`Delete this ${this._selectedElement.type}?`);
    if (!confirmed) return;

    try {
      const service = `remove_${this._selectedElement.type}`;
      await this._hass.callService('motiondirection', service, {
        [`${this._selectedElement.type}_id`]: this._selectedElement.id
      });

      this._showNotification(`${this._selectedElement.type} deleted successfully`);
      this._selectedElement = null;
      this._loadFloorplanData();
    } catch (error) {
      this._showNotification(`Failed to delete: ${error.message}`, 'error');
    }
  }

  /**
   * Update transform (zoom/pan)
   */
  _updateTransform() {
    const svg = this.shadowRoot.getElementById('floorplan-svg');
    if (svg) {
      svg.style.transform = `scale(${this._zoom}) translate(${this._panX}px, ${this._panY}px)`;
    }
  }

  /**
   * Show notification
   */
  _showNotification(message, type = 'info') {
    if (this._hass) {
      this._hass.callService('persistent_notification', 'create', {
        message: message,
        title: 'Floorplan Editor',
        notification_id: `floorplan_editor_${Date.now()}`
      });
    }
  }

  /**
   * Format mode for display
   */
  _formatMode(mode) {
    return mode.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  }

  /**
   * Format entity name
   */
  _formatEntityName(entityId) {
    return entityId
      .split('.')[1]
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }

  /**
   * Get cue icon
   */
  _getCueIcon(cueType) {
    const icons = {
      'door': 'mdi:door',
      'light': 'mdi:lightbulb',
      'switch': 'mdi:light-switch',
      'presence': 'mdi:account',
      'temperature': 'mdi:thermometer',
      'vibration': 'mdi:vibrate',
      'power': 'mdi:power-plug',
      'media': 'mdi:speaker'
    };
    return icons[cueType] || 'mdi:help-circle';
  }

  /**
   * Get card size for masonry layout
   */
  getCardSize() {
    return 6;
  }

  /**
   * Get grid options for sections layout
   */
  getGridOptions() {
    return {
      rows: 6,
      columns: 12,
      min_rows: 4,
      max_rows: 10,
    };
  }

  /**
   * Get card styles
   */
  _getStyles() {
    return `
      ha-card {
        display: flex;
        flex-direction: column;
        height: 100%;
      }
      
      .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px;
        border-bottom: 1px solid var(--divider-color);
      }
      
      .name {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.25rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      
      .mode-indicator {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
      }
      
      .mode-view {
        background: var(--info-color);
        color: white;
      }
      
      .mode-edit {
        background: var(--warning-color);
        color: white;
      }
      
      .mode-draw_zone, .mode-place_sensor {
        background: var(--success-color);
        color: white;
      }
      
      .toolbar {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: var(--secondary-background-color);
        border-bottom: 1px solid var(--divider-color);
        flex-wrap: wrap;
      }
      
      .toolbar-group {
        display: flex;
        gap: 4px;
        padding: 0 8px;
        border-right: 1px solid var(--divider-color);
      }
      
      .toolbar-group:last-child {
        border-right: none;
      }
      
      .toolbar-btn {
        background: transparent;
        border: none;
        padding: 8px;
        cursor: pointer;
        border-radius: 4px;
        color: var(--primary-text-color);
        transition: background 0.2s;
      }
      
      .toolbar-btn:hover {
        background: var(--primary-color);
        color: var(--text-primary-color);
      }
      
      .toolbar-btn.active {
        background: var(--primary-color);
        color: var(--text-primary-color);
      }
      
      .toolbar-btn ha-icon {
        width: 20px;
        height: 20px;
        display: block;
      }
      
      .card-content {
        flex: 1;
        overflow: hidden;
        position: relative;
        background: var(--card-background-color);
      }
      
      .placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 16px;
        padding: 48px;
        color: var(--secondary-text-color);
        text-align: center;
      }
      
      .placeholder ha-icon {
        width: 64px;
        height: 64px;
        opacity: 0.5;
      }
      
      .hint {
        font-size: 0.875rem;
        color: var(--disabled-text-color);
      }
      
      .floorplan-container {
        width: 100%;
        height: 100%;
        overflow: hidden;
        position: relative;
      }
      
      .floorplan-svg {
        width: 100%;
        height: 100%;
        cursor: crosshair;
        transition: transform 0.1s ease-out;
      }
      
      .floorplan-svg.dragging {
        cursor: grabbing;
      }
      
      .layer {
        pointer-events: all;
      }
      
      .grid-line {
        stroke: var(--divider-color);
        stroke-width: 0.5;
        opacity: 0.3;
      }
      
      .zone-polygon {
        cursor: pointer;
        transition: opacity 0.2s;
      }
      
      .zone-polygon:hover {
        opacity: 0.8;
      }
      
      .zone.selected .zone-polygon {
        stroke-width: 3;
        filter: drop-shadow(0 0 5px var(--primary-color));
      }
      
      .zone-center {
        cursor: pointer;
      }
      
      .zone-label, .sensor-label, .cue-label, .direction-label {
        font-size: 12px;
        font-weight: 500;
        pointer-events: none;
        user-select: none;
      }
      
      .direction-arrow {
        pointer-events: none;
      }
      
      .sensor {
        cursor: pointer;
      }
      
      .sensor-range {
        pointer-events: none;
      }
      
      .sensor-icon {
        cursor: move;
        transition: transform 0.2s;
      }
      
      .sensor-icon:hover {
        transform: scale(1.2);
      }
      
      .sensor.selected .sensor-icon {
        filter: drop-shadow(0 0 5px var(--info-color));
      }
      
      .cue {
        cursor: pointer;
      }
      
      .cue-range {
        pointer-events: none;
      }
      
      .cue-icon {
        cursor: move;
        transition: transform 0.2s;
      }
      
      .cue-icon:hover {
        transform: scale(1.2);
      }
      
      .cue.selected .cue-icon {
        filter: drop-shadow(0 0 5px var(--warning-color));
      }
      
      .zone-preview {
        pointer-events: none;
      }
      
      .drawing-point {
        cursor: pointer;
      }
      
      .drawing-line {
        pointer-events: none;
      }
      
      .point-label {
        pointer-events: none;
      }
      
      .controls {
        position: absolute;
        bottom: 16px;
        left: 16px;
        right: 16px;
        pointer-events: none;
      }
      
      .control-panel {
        background: var(--card-background-color);
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        padding: 16px;
        pointer-events: all;
        max-width: 400px;
      }
      
      .control-header {
        font-size: 1rem;
        font-weight: 600;
        color: var(--primary-text-color);
        margin-bottom: 12px;
      }
      
      .control-content {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      
      .control-hint {
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        margin: 0;
      }
      
      .control-info {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--primary-text-color);
        margin: 0;
      }
      
      .control-buttons {
        display: flex;
        gap: 8px;
      }
      
      .control-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 10px 16px;
        background: var(--primary-color);
        color: var(--text-primary-color);
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 600;
        transition: background 0.2s;
      }
      
      .control-btn:hover {
        opacity: 0.9;
      }
      
      .control-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      .control-btn.secondary {
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
      }
      
      .control-btn ha-icon {
        width: 18px;
        height: 18px;
      }
    `;
  }

  /**
   * Get editor configuration element
   * Returns a custom element for UI configuration
   */
  static getConfigElement() {
    return document.createElement('motiondirection-floorplan-editor-card-editor');
  }

  /**
   * Get stub configuration for card picker
   * Provides default configuration when adding card
   */
  static getStubConfig() {
    return {
      floorplan_id: 'default',
      width: 800,
      height: 600,
      show_grid: true,
      grid_size: 50,
      show_sensors: true,
      show_zones: true,
      enable_editing: true,
    };
  }
}

// Register the custom card
customElements.define('motiondirection-floorplan-editor', FloorplanEditorCard);

// Register with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'motiondirection-floorplan-editor',
  name: 'MotionDirection Floorplan Editor',
  description: 'Interactive floorplan editor for MotionDirection integration with sensor placement, zone drawing, and real-time visualization',
  preview: true,
  documentationURL: 'https://github.com/tamaygz/ha-motiondirection#floorplan-editor-card',
});

console.info(
  '%c FLOORPLAN-EDITOR-CARD %c 1.0.0 ',
  'color: white; background: #4caf50; font-weight: 700;',
  'color: #4caf50; background: white; font-weight: 700;'
);
