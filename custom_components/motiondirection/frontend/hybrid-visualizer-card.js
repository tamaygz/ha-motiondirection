/**
 * MotionDirection Hybrid Detection Visualizer Card
 * 
 * Visualizes hybrid detection showing motion sensors and secondary cues together.
 * Displays correlation lines, detection methods, and timeline of events.
 * 
 * Features:
 * - Motion sensor visualization
 * - Secondary cue visualization
 * - Correlation lines between motion and cues
 * - Color coding by type
 * - Detection method indicators
 * - Confidence-based opacity
 * - Event timeline
 * - Correlation timing offsets
 * 
 * @example
 * type: custom:motiondirection-hybrid-visualizer
 * floorplan_id: ground_floor
 * show_motion_sensors: true
 * show_secondary_cues: true
 * show_detection_method: true
 * visualization_options:
 *   motion_color: "#00FF00"
 *   cue_color: "#FFA500"
 *   correlation_lines: true
 *   confidence_opacity: true
 *   show_timeline: true
 */

class MotionDirectionHybridVisualizerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = null;
    this._hass = null;
    this._sensors = [];
    this._cues = [];
    this._events = [];
    this._correlations = [];
    this._timelineStart = null;
    this._timelineEnd = null;
  }

  /**
   * Set card configuration
   */
  setConfig(config) {
    if (!config.floorplan_id) {
      throw new Error('You need to define a floorplan_id');
    }

    this._config = {
      floorplan_id: config.floorplan_id,
      show_motion_sensors: config.show_motion_sensors !== false,
      show_secondary_cues: config.show_secondary_cues !== false,
      show_detection_method: config.show_detection_method !== false,
      visualization_options: {
        motion_color: config.visualization_options?.motion_color || '#00FF00',
        cue_color: config.visualization_options?.cue_color || '#FFA500',
        correlation_lines: config.visualization_options?.correlation_lines !== false,
        confidence_opacity: config.visualization_options?.confidence_opacity !== false,
        show_timeline: config.visualization_options?.show_timeline !== false,
      },
      timeline_duration: config.timeline_duration || 300, // 5 minutes
      title: config.title || 'Hybrid Detection Visualizer',
    };

    this.render();
  }

  /**
   * Set Home Assistant instance
   */
  set hass(hass) {
    this._hass = hass;
    this.loadData();
  }

  /**
   * Get card size for layout
   */
  getCardSize() {
    return this._config?.visualization_options?.show_timeline ? 10 : 8;
  }

  /**
   * Load data
   */
  loadData() {
    if (!this._hass || !this._config) return;

    this.loadFloorplanData();
    this.loadEvents();
    this.loadCorrelations();
    this.renderVisualization();
  }

  /**
   * Load floorplan data
   */
  loadFloorplanData() {
    const floorplanEntity = this._hass?.states[`sensor.motiondirection_floorplan_${this._config.floorplan_id}`];
    
    if (floorplanEntity?.attributes) {
      this._sensors = floorplanEntity.attributes.sensors || [];
      this._cues = floorplanEntity.attributes.cues || [];
    }

    // Update sensor states
    this._sensors.forEach(sensor => {
      const entity = this._hass?.states[sensor.entity_id];
      if (entity) {
        sensor.state = entity.state;
        sensor.attributes = entity.attributes;
      }
    });

    // Update cue states
    this._cues.forEach(cue => {
      const entity = this._hass?.states[cue.entity_id];
      if (entity) {
        cue.state = entity.state;
        cue.attributes = entity.attributes;
      }
    });
  }

  /**
   * Load events
   */
  loadEvents() {
    const detectorEntity = this._hass?.states[`sensor.motiondirection_${this._config.floorplan_id}_detector`];
    
    if (detectorEntity?.attributes?.recent_events) {
      this._events = detectorEntity.attributes.recent_events
        .map(event => ({
          ...event,
          timestamp: new Date(event.timestamp),
        }))
        .sort((a, b) => b.timestamp - a.timestamp)
        .slice(0, 100);

      // Calculate timeline bounds
      if (this._events.length > 0) {
        this._timelineEnd = this._events[0].timestamp;
        this._timelineStart = new Date(this._timelineEnd.getTime() - (this._config.timeline_duration * 1000));
      }
    }
  }

  /**
   * Load correlations
   */
  loadCorrelations() {
    const correlationEntity = this._hass?.states[`sensor.motiondirection_${this._config.floorplan_id}_correlations`];
    
    if (correlationEntity?.attributes?.active_correlations) {
      this._correlations = correlationEntity.attributes.active_correlations;
    }
  }

  /**
   * Render the card
   */
  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }

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
          background: var(--card-background-color);
          border-bottom: 1px solid var(--divider-color);
        }

        .card-title {
          font-size: 18px;
          font-weight: 500;
          margin: 0;
        }

        .controls {
          display: flex;
          gap: 8px;
          align-items: center;
        }

        .control-btn {
          padding: 6px 12px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
          cursor: pointer;
          border-radius: 4px;
          font-size: 12px;
        }

        .control-btn:hover {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .control-btn.active {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .content {
          display: flex;
          flex-direction: column;
          flex: 1;
        }

        .visualization-container {
          flex: 1;
          position: relative;
          background: var(--primary-background-color);
          overflow: hidden;
          min-height: 400px;
        }

        svg {
          width: 100%;
          height: 100%;
        }

        .sensor-marker {
          cursor: pointer;
          transition: all 0.2s;
        }

        .sensor-marker:hover {
          transform: scale(1.2);
        }

        .cue-marker {
          cursor: pointer;
          transition: all 0.2s;
        }

        .cue-marker:hover {
          transform: scale(1.2);
        }

        .correlation-line {
          stroke-width: 2;
          stroke-dasharray: 5 3;
          animation: dash 1s linear infinite;
        }

        @keyframes dash {
          to {
            stroke-dashoffset: -8;
          }
        }

        .detection-badge {
          font-size: 10px;
          font-weight: 500;
        }

        .legend {
          position: absolute;
          top: 16px;
          right: 16px;
          background: var(--card-background-color);
          padding: 12px;
          border-radius: 8px;
          border: 1px solid var(--divider-color);
          font-size: 11px;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 6px;
        }

        .legend-item:last-child {
          margin-bottom: 0;
        }

        .legend-color {
          width: 16px;
          height: 16px;
          border-radius: 3px;
          border: 1px solid var(--divider-color);
        }

        .legend-label {
          color: var(--primary-text-color);
        }

        .timeline-container {
          height: 200px;
          background: var(--card-background-color);
          border-top: 1px solid var(--divider-color);
          padding: 16px;
          overflow-x: auto;
          overflow-y: hidden;
        }

        .timeline {
          position: relative;
          height: 100%;
          min-width: 100%;
        }

        .timeline-axis {
          position: absolute;
          bottom: 30px;
          left: 0;
          right: 0;
          height: 2px;
          background: var(--divider-color);
        }

        .timeline-label {
          position: absolute;
          bottom: 5px;
          font-size: 10px;
          color: var(--secondary-text-color);
          transform: translateX(-50%);
        }

        .timeline-event {
          position: absolute;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2px solid;
          background: var(--card-background-color);
          cursor: pointer;
          transition: all 0.2s;
        }

        .timeline-event:hover {
          transform: scale(1.3);
        }

        .timeline-event.motion {
          border-color: ${this._config?.visualization_options?.motion_color || '#00FF00'};
        }

        .timeline-event.cue {
          border-color: ${this._config?.visualization_options?.cue_color || '#FFA500'};
        }

        .timeline-event.hybrid {
          border-color: var(--primary-color);
          background: var(--primary-color);
        }

        .timeline-connector {
          position: absolute;
          height: 2px;
          background: var(--divider-color);
          top: 50%;
        }

        .stats {
          padding: 12px 16px;
          background: var(--primary-background-color);
          border-top: 1px solid var(--divider-color);
          display: flex;
          justify-content: space-around;
          font-size: 12px;
        }

        .stat-item {
          text-align: center;
        }

        .stat-value {
          font-size: 18px;
          font-weight: 500;
          color: var(--primary-text-color);
        }

        .stat-label {
          color: var(--secondary-text-color);
          margin-top: 4px;
        }

        .tooltip {
          position: absolute;
          background: var(--card-background-color);
          border: 1px solid var(--divider-color);
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 12px;
          pointer-events: none;
          z-index: 1000;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }

        .tooltip-hidden {
          display: none;
        }
      </style>

      <ha-card>
        <div class="card-header">
          <h2 class="card-title">${this._config.title}</h2>
          <div class="controls">
            <button class="control-btn ${this._config.show_motion_sensors ? 'active' : ''}" id="toggleMotion">
              Motion Sensors
            </button>
            <button class="control-btn ${this._config.show_secondary_cues ? 'active' : ''}" id="toggleCues">
              Cues
            </button>
            <button class="control-btn ${this._config.visualization_options.correlation_lines ? 'active' : ''}" id="toggleCorrelations">
              Correlations
            </button>
          </div>
        </div>

        <div class="content">
          <div class="visualization-container">
            <svg id="mainSvg" viewBox="0 0 1000 1000"></svg>
            
            <div class="legend">
              <div class="legend-item">
                <div class="legend-color" style="background: ${this._config.visualization_options.motion_color};"></div>
                <span class="legend-label">Motion Sensor</span>
              </div>
              <div class="legend-item">
                <div class="legend-color" style="background: ${this._config.visualization_options.cue_color};"></div>
                <span class="legend-label">Secondary Cue</span>
              </div>
              <div class="legend-item">
                <div class="legend-color" style="background: var(--primary-color);"></div>
                <span class="legend-label">Hybrid Detection</span>
              </div>
            </div>

            <div id="tooltip" class="tooltip tooltip-hidden"></div>
          </div>

          ${this._config.visualization_options.show_timeline ? `
            <div class="timeline-container">
              <div class="timeline" id="timeline"></div>
            </div>
          ` : ''}

          <div class="stats">
            <div class="stat-item">
              <div class="stat-value" id="statMotionEvents">0</div>
              <div class="stat-label">Motion Events</div>
            </div>
            <div class="stat-item">
              <div class="stat-value" id="statCueEvents">0</div>
              <div class="stat-label">Cue Events</div>
            </div>
            <div class="stat-item">
              <div class="stat-value" id="statHybridEvents">0</div>
              <div class="stat-label">Hybrid Detections</div>
            </div>
            <div class="stat-item">
              <div class="stat-value" id="statCorrelations">0</div>
              <div class="stat-label">Active Correlations</div>
            </div>
          </div>
        </div>
      </ha-card>
    `;

    this.setupEventListeners();
    this.loadData();
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    const toggleMotion = this.shadowRoot.getElementById('toggleMotion');
    if (toggleMotion) {
      toggleMotion.addEventListener('click', () => {
        this._config.show_motion_sensors = !this._config.show_motion_sensors;
        toggleMotion.classList.toggle('active');
        this.renderVisualization();
      });
    }

    const toggleCues = this.shadowRoot.getElementById('toggleCues');
    if (toggleCues) {
      toggleCues.addEventListener('click', () => {
        this._config.show_secondary_cues = !this._config.show_secondary_cues;
        toggleCues.classList.toggle('active');
        this.renderVisualization();
      });
    }

    const toggleCorrelations = this.shadowRoot.getElementById('toggleCorrelations');
    if (toggleCorrelations) {
      toggleCorrelations.addEventListener('click', () => {
        this._config.visualization_options.correlation_lines = !this._config.visualization_options.correlation_lines;
        toggleCorrelations.classList.toggle('active');
        this.renderVisualization();
      });
    }
  }

  /**
   * Render visualization
   */
  renderVisualization() {
    this.renderFloorplan();
    if (this._config.visualization_options.show_timeline) {
      this.renderTimeline();
    }
    this.updateStatistics();
  }

  /**
   * Render floorplan
   */
  renderFloorplan() {
    const svg = this.shadowRoot.getElementById('mainSvg');
    if (!svg) return;

    let content = '';

    // Draw correlation lines first (so they're behind markers)
    if (this._config.visualization_options.correlation_lines) {
      this._correlations.forEach(corr => {
        const sensor = this._sensors.find(s => s.id === corr.sensor_id);
        const cue = this._cues.find(c => c.id === corr.cue_id);

        if (sensor && cue) {
          const opacity = this._config.visualization_options.confidence_opacity 
            ? corr.confidence * 0.8 
            : 0.5;

          content += `
            <line
              class="correlation-line"
              x1="${sensor.x * 1000}"
              y1="${sensor.y * 1000}"
              x2="${cue.position.x * 1000}"
              y2="${cue.position.y * 1000}"
              stroke="var(--primary-color)"
              opacity="${opacity}"
            />
          `;
        }
      });
    }

    // Draw motion sensors
    if (this._config.show_motion_sensors) {
      this._sensors.forEach(sensor => {
        const isActive = sensor.state === 'on';
        const opacity = this._config.visualization_options.confidence_opacity && !isActive ? 0.3 : 1.0;
        const color = this._config.visualization_options.motion_color;

        content += `
          <g class="sensor-marker" data-sensor-id="${sensor.id}" opacity="${opacity}">
            <circle
              cx="${sensor.x * 1000}"
              cy="${sensor.y * 1000}"
              r="12"
              fill="${color}"
            />
            ${this._config.show_detection_method ? `
              <text
                x="${sensor.x * 1000}"
                y="${sensor.y * 1000 - 18}"
                text-anchor="middle"
                class="detection-badge"
                fill="var(--primary-text-color)"
              >M</text>
            ` : ''}
          </g>
        `;
      });
    }

    // Draw secondary cues
    if (this._config.show_secondary_cues) {
      this._cues.forEach(cue => {
        const isActive = cue.state === 'on';
        const opacity = this._config.visualization_options.confidence_opacity && !isActive ? 0.3 : 1.0;
        const color = this._config.visualization_options.cue_color;

        content += `
          <g class="cue-marker" data-cue-id="${cue.id}" opacity="${opacity}">
            <rect
              x="${cue.position.x * 1000 - 10}"
              y="${cue.position.y * 1000 - 10}"
              width="20"
              height="20"
              rx="3"
              fill="${color}"
            />
            ${this._config.show_detection_method ? `
              <text
                x="${cue.position.x * 1000}"
                y="${cue.position.y * 1000 - 18}"
                text-anchor="middle"
                class="detection-badge"
                fill="var(--primary-text-color)"
              >C</text>
            ` : ''}
          </g>
        `;
      });
    }

    // Draw hybrid detection indicators
    if (this._config.show_detection_method) {
      this._correlations.forEach(corr => {
        if (corr.detection_method === 'hybrid') {
          const sensor = this._sensors.find(s => s.id === corr.sensor_id);
          const cue = this._cues.find(c => c.id === corr.cue_id);

          if (sensor && cue) {
            const midX = (sensor.x + cue.position.x) / 2 * 1000;
            const midY = (sensor.y + cue.position.y) / 2 * 1000;

            content += `
              <circle
                cx="${midX}"
                cy="${midY}"
                r="8"
                fill="var(--primary-color)"
                opacity="0.8"
              />
              <text
                x="${midX}"
                y="${midY + 18}"
                text-anchor="middle"
                class="detection-badge"
                fill="var(--primary-text-color)"
              >H</text>
            `;
          }
        }
      });
    }

    svg.innerHTML = content;

    // Add hover tooltips
    this.setupTooltips();
  }

  /**
   * Setup tooltips
   */
  setupTooltips() {
    const tooltip = this.shadowRoot.getElementById('tooltip');
    const svg = this.shadowRoot.getElementById('mainSvg');

    if (!tooltip || !svg) return;

    svg.querySelectorAll('.sensor-marker, .cue-marker').forEach(marker => {
      marker.addEventListener('mouseenter', (e) => {
        const sensorId = marker.dataset.sensorId;
        const cueId = marker.dataset.cueId;

        let content = '';

        if (sensorId) {
          const sensor = this._sensors.find(s => s.id === sensorId);
          if (sensor) {
            content = `
              <strong>Motion Sensor</strong><br>
              ${sensor.name || sensor.id}<br>
              State: ${sensor.state || 'unknown'}
            `;
          }
        } else if (cueId) {
          const cue = this._cues.find(c => c.id === cueId);
          if (cue) {
            content = `
              <strong>Secondary Cue</strong><br>
              ${cue.name || cue.id}<br>
              Type: ${cue.cue_type || 'unknown'}<br>
              State: ${cue.state || 'unknown'}
            `;
          }
        }

        tooltip.innerHTML = content;
        tooltip.classList.remove('tooltip-hidden');
      });

      marker.addEventListener('mousemove', (e) => {
        tooltip.style.left = `${e.clientX + 10}px`;
        tooltip.style.top = `${e.clientY + 10}px`;
      });

      marker.addEventListener('mouseleave', () => {
        tooltip.classList.add('tooltip-hidden');
      });
    });
  }

  /**
   * Render timeline
   */
  renderTimeline() {
    const timeline = this.shadowRoot.getElementById('timeline');
    if (!timeline || !this._events.length) return;

    const width = timeline.clientWidth;
    const height = timeline.clientHeight;

    let content = '<div class="timeline-axis"></div>';

    // Add time labels
    const labelCount = 5;
    for (let i = 0; i <= labelCount; i++) {
      const time = new Date(this._timelineStart.getTime() + (this._timelineEnd - this._timelineStart) * (i / labelCount));
      const x = (i / labelCount) * 100;
      
      content += `
        <div class="timeline-label" style="left: ${x}%;">
          ${time.toLocaleTimeString()}
        </div>
      `;
    }

    // Add events
    this._events.forEach((event, index) => {
      const eventTime = event.timestamp.getTime();
      const x = ((eventTime - this._timelineStart.getTime()) / (this._timelineEnd - this._timelineStart)) * 100;
      
      if (x < 0 || x > 100) return;

      let eventClass = 'timeline-event';
      let title = '';

      if (event.detection_method === 'hybrid') {
        eventClass += ' hybrid';
        title = `Hybrid Detection\n${event.timestamp.toLocaleTimeString()}\nConfidence: ${Math.round(event.confidence * 100)}%`;
      } else if (event.type === 'motion') {
        eventClass += ' motion';
        title = `Motion Event\n${event.timestamp.toLocaleTimeString()}\nSensor: ${event.sensor}`;
      } else if (event.type === 'cue') {
        eventClass += ' cue';
        title = `Cue Event\n${event.timestamp.toLocaleTimeString()}\nCue: ${event.cue}`;
      }

      // Stagger events vertically to avoid overlap
      const yOffset = 35 + (index % 3) * 25;

      content += `
        <div
          class="${eventClass}"
          style="left: ${x}%; bottom: ${yOffset}px;"
          title="${title}"
        ></div>
      `;
    });

    timeline.innerHTML = content;
  }

  /**
   * Update statistics
   */
  updateStatistics() {
    const statMotionEvents = this.shadowRoot.getElementById('statMotionEvents');
    const statCueEvents = this.shadowRoot.getElementById('statCueEvents');
    const statHybridEvents = this.shadowRoot.getElementById('statHybridEvents');
    const statCorrelations = this.shadowRoot.getElementById('statCorrelations');

    if (statMotionEvents) {
      const motionEvents = this._events.filter(e => e.type === 'motion' && e.detection_method !== 'hybrid').length;
      statMotionEvents.textContent = motionEvents;
    }

    if (statCueEvents) {
      const cueEvents = this._events.filter(e => e.type === 'cue' && e.detection_method !== 'hybrid').length;
      statCueEvents.textContent = cueEvents;
    }

    if (statHybridEvents) {
      const hybridEvents = this._events.filter(e => e.detection_method === 'hybrid').length;
      statHybridEvents.textContent = hybridEvents;
    }

    if (statCorrelations) {
      statCorrelations.textContent = this._correlations.length;
    }
  }

  /**
   * Get editor configuration schema
   */
  static getConfigElement() {
    return document.createElement('motiondirection-hybrid-visualizer-card-editor');
  }

  /**
   * Get stub configuration for card picker
   */
  static getStubConfig() {
    return {
      floorplan_id: 'ground_floor',
      show_motion_sensors: true,
      show_secondary_cues: true,
      show_detection_method: true,
      visualization_options: {
        motion_color: '#00FF00',
        cue_color: '#FFA500',
        correlation_lines: true,
        confidence_opacity: true,
        show_timeline: true,
      },
    };
  }
}

// Register custom element
customElements.define('motiondirection-hybrid-visualizer-card', MotionDirectionHybridVisualizerCard);

// Register card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'motiondirection-hybrid-visualizer',
  name: 'MotionDirection Hybrid Detection Visualizer',
  description: 'Visualize hybrid detection with motion sensors, secondary cues, correlations, and timeline',
  preview: true,
});

console.info(
  '%c MOTIONDIRECTION-HYBRID-VISUALIZER-CARD %c v1.0.0 ',
  'color: white; background: #e91e63; font-weight: 700;',
  'color: #e91e63; background: white; font-weight: 700;'
);
