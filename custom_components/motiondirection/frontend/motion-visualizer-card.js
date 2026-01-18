/**
 * MotionDirection Motion Visualizer Card
 * 
 * Real-time and historical motion visualization with Canvas-based rendering.
 * Displays motion trails, heat maps, direction arrows, and confidence overlays.
 * 
 * Features:
 * - Real-time motion display with trails
 * - Historical playback with timeline control
 * - Heat map visualization
 * - Direction arrows
 * - Confidence overlay
 * - Animation speed control
 * - Floorplan integration
 * 
 * @example
 * type: custom:motiondirection-visualizer
 * floorplan_id: ground_floor
 * show_realtime: true
 * show_history: true
 * history_duration: 3600
 * animation_speed: 1.0
 * heat_map: true
 * show_direction_arrows: true
 * show_confidence_overlay: true
 */

class MotionDirectionVisualizerCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = null;
    this._hass = null;
    this._animationFrame = null;
    this._canvas = null;
    this._ctx = null;
    this._motionTrails = [];
    this._heatMapData = [];
    this._historicalData = [];
    this._playbackTime = null;
    this._isPlaying = false;
    this._animationSpeed = 1.0;
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
      show_realtime: config.show_realtime !== false,
      show_history: config.show_history !== false,
      history_duration: config.history_duration || 3600,
      animation_speed: config.animation_speed || 1.0,
      heat_map: config.heat_map !== false,
      show_direction_arrows: config.show_direction_arrows !== false,
      show_confidence_overlay: config.show_confidence_overlay !== false,
      trail_length: config.trail_length || 50,
      trail_decay: config.trail_decay || 0.95,
      heat_radius: config.heat_radius || 30,
      title: config.title || 'Motion Visualizer',
    };

    this._animationSpeed = this._config.animation_speed;
    this.render();
  }

  /**
   * Set Home Assistant instance
   */
  set hass(hass) {
    const oldHass = this._hass;
    this._hass = hass;

    // Update motion data when motion events occur
    if (this._config?.show_realtime) {
      this.updateMotionData();
    }

    // Start animation loop if not already running
    if (!this._animationFrame && this._canvas) {
      this.startAnimation();
    }
  }

  /**
   * Get card size for layout
   */
  getCardSize() {
    return 6;
  }

  /**
   * Called when element is connected to DOM
   */
  connectedCallback() {
    if (this._canvas && this._config?.show_realtime) {
      this.startAnimation();
    }
  }

  /**
   * Called when element is disconnected from DOM
   */
  disconnectedCallback() {
    this.stopAnimation();
  }

  /**
   * Start animation loop
   */
  startAnimation() {
    this.stopAnimation();
    
    const animate = () => {
      this.updateVisualization();
      this._animationFrame = requestAnimationFrame(animate);
    };
    
    this._animationFrame = requestAnimationFrame(animate);
  }

  /**
   * Stop animation loop
   */
  stopAnimation() {
    if (this._animationFrame) {
      cancelAnimationFrame(this._animationFrame);
      this._animationFrame = null;
    }
  }

  /**
   * Update motion data from Home Assistant
   */
  updateMotionData() {
    if (!this._hass || !this._config) return;

    // Get motion events from the sensor
    const sensorId = `sensor.motiondirection_${this._config.floorplan_id}_motion`;
    const entity = this._hass.states[sensorId];

    if (!entity) return;

    // Extract motion events from attributes
    const motionEvents = entity.attributes.recent_motion_events || [];
    
    // Add new motion events to trails
    motionEvents.forEach(event => {
      if (!this.isEventInTrails(event)) {
        this.addMotionTrail(event);
      }
    });

    // Update heat map data
    if (this._config.heat_map) {
      this.updateHeatMapData(motionEvents);
    }

    // Load historical data if requested
    if (this._config.show_history) {
      this.loadHistoricalData();
    }
  }

  /**
   * Check if event is already in trails
   */
  isEventInTrails(event) {
    return this._motionTrails.some(trail => 
      trail.id === event.id || 
      (trail.timestamp === event.timestamp && trail.sensor === event.sensor)
    );
  }

  /**
   * Add motion trail
   */
  addMotionTrail(event) {
    const trail = {
      id: event.id || `${event.sensor}_${event.timestamp}`,
      sensor: event.sensor,
      timestamp: new Date(event.timestamp),
      position: event.position || this.getSensorPosition(event.sensor),
      direction: event.direction,
      confidence: event.confidence || 1.0,
      alpha: 1.0,
      points: [event.position || this.getSensorPosition(event.sensor)],
    };

    this._motionTrails.push(trail);

    // Limit trail count
    if (this._motionTrails.length > this._config.trail_length) {
      this._motionTrails.shift();
    }
  }

  /**
   * Get sensor position from floorplan
   */
  getSensorPosition(sensorId) {
    // Try to get sensor position from floorplan entity
    const floorplanEntity = this._hass?.states[`sensor.motiondirection_floorplan_${this._config.floorplan_id}`];
    
    if (floorplanEntity?.attributes?.sensors) {
      const sensor = floorplanEntity.attributes.sensors.find(s => s.id === sensorId);
      if (sensor) {
        return { x: sensor.x, y: sensor.y };
      }
    }

    // Default to center if not found
    return { x: 0.5, y: 0.5 };
  }

  /**
   * Update heat map data
   */
  updateHeatMapData(events) {
    const now = Date.now();
    const maxAge = this._config.history_duration * 1000;

    // Add new events
    events.forEach(event => {
      const position = event.position || this.getSensorPosition(event.sensor);
      this._heatMapData.push({
        x: position.x,
        y: position.y,
        intensity: event.confidence || 1.0,
        timestamp: new Date(event.timestamp).getTime(),
      });
    });

    // Remove old data
    this._heatMapData = this._heatMapData.filter(point => 
      (now - point.timestamp) < maxAge
    );
  }

  /**
   * Load historical data
   */
  async loadHistoricalData() {
    // In a real implementation, this would fetch from Home Assistant history
    // For now, we'll use the current motion data
    const sensorId = `sensor.motiondirection_${this._config.floorplan_id}_motion`;
    const entity = this._hass?.states[sensorId];

    if (entity?.attributes?.historical_events) {
      this._historicalData = entity.attributes.historical_events;
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
          padding: 0;
          overflow: hidden;
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

        .canvas-container {
          position: relative;
          width: 100%;
          height: 500px;
          background: var(--primary-background-color);
        }

        canvas {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
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
          padding: 16px;
          background: var(--card-background-color);
          border-top: 1px solid var(--divider-color);
        }

        .timeline {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .timeline-slider {
          flex: 1;
          height: 4px;
          background: var(--divider-color);
          border-radius: 2px;
          position: relative;
          cursor: pointer;
        }

        .timeline-progress {
          height: 100%;
          background: var(--primary-color);
          border-radius: 2px;
          transition: width 0.1s linear;
        }

        .timeline-time {
          font-size: 12px;
          color: var(--secondary-text-color);
          min-width: 80px;
          text-align: right;
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
      </style>

      <ha-card>
        <div class="card-header">
          <h2 class="card-title">${this._config.title}</h2>
          <div class="controls">
            <button class="control-btn ${this._config.heat_map ? 'active' : ''}" id="toggleHeatMap">
              Heat Map
            </button>
            <button class="control-btn ${this._config.show_direction_arrows ? 'active' : ''}" id="toggleArrows">
              Arrows
            </button>
            <button class="control-btn ${this._config.show_confidence_overlay ? 'active' : ''}" id="toggleConfidence">
              Confidence
            </button>
            <button class="control-btn" id="clearTrails">Clear</button>
          </div>
        </div>

        <div class="canvas-container">
          <canvas id="mainCanvas"></canvas>
          
          <div class="legend">
            <div class="legend-item">
              <div class="legend-color" style="background: rgba(255, 0, 0, 0.5);"></div>
              <span class="legend-label">High Motion</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background: rgba(255, 255, 0, 0.5);"></div>
              <span class="legend-label">Medium Motion</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background: rgba(0, 255, 0, 0.5);"></div>
              <span class="legend-label">Low Motion</span>
            </div>
          </div>
        </div>

        ${this._config.show_history ? `
          <div class="timeline-container">
            <div class="timeline">
              <button class="control-btn" id="playPause">▶️</button>
              <div class="timeline-slider" id="timelineSlider">
                <div class="timeline-progress" id="timelineProgress"></div>
              </div>
              <div class="timeline-time" id="timelineTime">00:00:00</div>
            </div>
          </div>
        ` : ''}

        <div class="stats">
          <div class="stat-item">
            <div class="stat-value" id="statMotionEvents">0</div>
            <div class="stat-label">Motion Events</div>
          </div>
          <div class="stat-item">
            <div class="stat-value" id="statAvgConfidence">0%</div>
            <div class="stat-label">Avg Confidence</div>
          </div>
          <div class="stat-item">
            <div class="stat-value" id="statActiveZones">0</div>
            <div class="stat-label">Active Zones</div>
          </div>
        </div>
      </ha-card>
    `;

    // Setup canvas
    this.setupCanvas();

    // Setup event listeners
    this.setupEventListeners();

    // Initial update
    this.updateMotionData();
  }

  /**
   * Setup canvas
   */
  setupCanvas() {
    this._canvas = this.shadowRoot.getElementById('mainCanvas');
    if (!this._canvas) return;

    this._ctx = this._canvas.getContext('2d');

    // Set canvas size
    const container = this.shadowRoot.querySelector('.canvas-container');
    this._canvas.width = container.clientWidth;
    this._canvas.height = container.clientHeight;

    // Handle resize
    window.addEventListener('resize', () => {
      this._canvas.width = container.clientWidth;
      this._canvas.height = container.clientHeight;
    });
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    const toggleHeatMapBtn = this.shadowRoot.getElementById('toggleHeatMap');
    const toggleArrowsBtn = this.shadowRoot.getElementById('toggleArrows');
    const toggleConfidenceBtn = this.shadowRoot.getElementById('toggleConfidence');
    const clearTrailsBtn = this.shadowRoot.getElementById('clearTrails');
    const playPauseBtn = this.shadowRoot.getElementById('playPause');
    const timelineSlider = this.shadowRoot.getElementById('timelineSlider');

    if (toggleHeatMapBtn) {
      toggleHeatMapBtn.addEventListener('click', () => {
        this._config.heat_map = !this._config.heat_map;
        toggleHeatMapBtn.classList.toggle('active');
      });
    }

    if (toggleArrowsBtn) {
      toggleArrowsBtn.addEventListener('click', () => {
        this._config.show_direction_arrows = !this._config.show_direction_arrows;
        toggleArrowsBtn.classList.toggle('active');
      });
    }

    if (toggleConfidenceBtn) {
      toggleConfidenceBtn.addEventListener('click', () => {
        this._config.show_confidence_overlay = !this._config.show_confidence_overlay;
        toggleConfidenceBtn.classList.toggle('active');
      });
    }

    if (clearTrailsBtn) {
      clearTrailsBtn.addEventListener('click', () => {
        this._motionTrails = [];
        this._heatMapData = [];
      });
    }

    if (playPauseBtn) {
      playPauseBtn.addEventListener('click', () => {
        this._isPlaying = !this._isPlaying;
        playPauseBtn.textContent = this._isPlaying ? '⏸️' : '▶️';
      });
    }

    if (timelineSlider) {
      timelineSlider.addEventListener('click', (e) => {
        const rect = timelineSlider.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const percentage = x / rect.width;
        this._playbackTime = percentage * this._config.history_duration;
        this.updateTimelineDisplay();
      });
    }
  }

  /**
   * Update visualization
   */
  updateVisualization() {
    if (!this._ctx || !this._canvas) return;

    const { width, height } = this._canvas;

    // Clear canvas
    this._ctx.clearRect(0, 0, width, height);

    // Draw heat map
    if (this._config.heat_map) {
      this.drawHeatMap();
    }

    // Draw motion trails
    this.drawMotionTrails();

    // Draw direction arrows
    if (this._config.show_direction_arrows) {
      this.drawDirectionArrows();
    }

    // Draw confidence overlay
    if (this._config.show_confidence_overlay) {
      this.drawConfidenceOverlay();
    }

    // Update statistics
    this.updateStatistics();

    // Update trails (decay alpha)
    this.updateTrails();
  }

  /**
   * Draw heat map
   */
  drawHeatMap() {
    const { width, height } = this._canvas;
    const radius = this._config.heat_radius;

    this._heatMapData.forEach(point => {
      const x = point.x * width;
      const y = point.y * height;

      // Create radial gradient
      const gradient = this._ctx.createRadialGradient(x, y, 0, x, y, radius);
      
      // Color based on intensity and age
      const now = Date.now();
      const age = (now - point.timestamp) / 1000; // seconds
      const ageFactor = Math.max(0, 1 - (age / this._config.history_duration));
      const alpha = point.intensity * ageFactor * 0.3;

      // Red for high intensity, yellow for medium, green for low
      if (point.intensity > 0.7) {
        gradient.addColorStop(0, `rgba(255, 0, 0, ${alpha})`);
        gradient.addColorStop(1, 'rgba(255, 0, 0, 0)');
      } else if (point.intensity > 0.4) {
        gradient.addColorStop(0, `rgba(255, 255, 0, ${alpha})`);
        gradient.addColorStop(1, 'rgba(255, 255, 0, 0)');
      } else {
        gradient.addColorStop(0, `rgba(0, 255, 0, ${alpha})`);
        gradient.addColorStop(1, 'rgba(0, 255, 0, 0)');
      }

      this._ctx.fillStyle = gradient;
      this._ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
    });
  }

  /**
   * Draw motion trails
   */
  drawMotionTrails() {
    const { width, height } = this._canvas;

    this._motionTrails.forEach(trail => {
      if (trail.points.length < 2) return;

      this._ctx.beginPath();
      this._ctx.strokeStyle = `rgba(0, 150, 255, ${trail.alpha})`;
      this._ctx.lineWidth = 3;
      this._ctx.lineCap = 'round';
      this._ctx.lineJoin = 'round';

      trail.points.forEach((point, index) => {
        const x = point.x * width;
        const y = point.y * height;

        if (index === 0) {
          this._ctx.moveTo(x, y);
        } else {
          this._ctx.lineTo(x, y);
        }
      });

      this._ctx.stroke();

      // Draw point at current position
      const currentPos = trail.points[trail.points.length - 1];
      const x = currentPos.x * width;
      const y = currentPos.y * height;

      this._ctx.beginPath();
      this._ctx.arc(x, y, 5, 0, Math.PI * 2);
      this._ctx.fillStyle = `rgba(0, 150, 255, ${trail.alpha})`;
      this._ctx.fill();
    });
  }

  /**
   * Draw direction arrows
   */
  drawDirectionArrows() {
    const { width, height } = this._canvas;

    this._motionTrails.forEach(trail => {
      if (!trail.direction || trail.alpha < 0.3) return;

      const pos = trail.points[trail.points.length - 1];
      const x = pos.x * width;
      const y = pos.y * height;

      // Calculate arrow angle based on direction
      const angle = this.getDirectionAngle(trail.direction);

      // Draw arrow
      this._ctx.save();
      this._ctx.translate(x, y);
      this._ctx.rotate(angle);

      this._ctx.beginPath();
      this._ctx.moveTo(15, 0);
      this._ctx.lineTo(-5, -8);
      this._ctx.lineTo(-5, 8);
      this._ctx.closePath();

      this._ctx.fillStyle = `rgba(255, 100, 0, ${trail.alpha * 0.8})`;
      this._ctx.fill();
      this._ctx.strokeStyle = `rgba(255, 255, 255, ${trail.alpha})`;
      this._ctx.lineWidth = 1;
      this._ctx.stroke();

      this._ctx.restore();
    });
  }

  /**
   * Get direction angle in radians
   */
  getDirectionAngle(direction) {
    const angles = {
      'north': -Math.PI / 2,
      'south': Math.PI / 2,
      'east': 0,
      'west': Math.PI,
      'northeast': -Math.PI / 4,
      'northwest': (-3 * Math.PI) / 4,
      'southeast': Math.PI / 4,
      'southwest': (3 * Math.PI) / 4,
    };
    return angles[direction?.toLowerCase()] || 0;
  }

  /**
   * Draw confidence overlay
   */
  drawConfidenceOverlay() {
    const { width, height } = this._canvas;

    this._motionTrails.forEach(trail => {
      const pos = trail.points[trail.points.length - 1];
      const x = pos.x * width;
      const y = pos.y * height;

      // Draw confidence circle
      const confidence = trail.confidence || 0;
      const radius = 15 + (confidence * 10);

      this._ctx.beginPath();
      this._ctx.arc(x, y, radius, 0, Math.PI * 2);
      this._ctx.strokeStyle = `rgba(0, 255, 150, ${trail.alpha * confidence})`;
      this._ctx.lineWidth = 2;
      this._ctx.stroke();

      // Draw confidence percentage
      this._ctx.font = '10px sans-serif';
      this._ctx.fillStyle = `rgba(255, 255, 255, ${trail.alpha})`;
      this._ctx.textAlign = 'center';
      this._ctx.textBaseline = 'middle';
      this._ctx.fillText(`${Math.round(confidence * 100)}%`, x, y - radius - 10);
    });
  }

  /**
   * Update trails (decay alpha)
   */
  updateTrails() {
    this._motionTrails = this._motionTrails.filter(trail => {
      trail.alpha *= this._config.trail_decay;
      return trail.alpha > 0.05;
    });
  }

  /**
   * Update statistics display
   */
  updateStatistics() {
    const statMotionEvents = this.shadowRoot.getElementById('statMotionEvents');
    const statAvgConfidence = this.shadowRoot.getElementById('statAvgConfidence');
    const statActiveZones = this.shadowRoot.getElementById('statActiveZones');

    if (statMotionEvents) {
      statMotionEvents.textContent = this._motionTrails.length;
    }

    if (statAvgConfidence) {
      const avgConfidence = this._motionTrails.length > 0
        ? this._motionTrails.reduce((sum, trail) => sum + (trail.confidence || 0), 0) / this._motionTrails.length
        : 0;
      statAvgConfidence.textContent = `${Math.round(avgConfidence * 100)}%`;
    }

    if (statActiveZones) {
      // Count unique zones (simplified)
      const zones = new Set(this._motionTrails.map(t => t.sensor));
      statActiveZones.textContent = zones.size;
    }
  }

  /**
   * Update timeline display
   */
  updateTimelineDisplay() {
    const timelineProgress = this.shadowRoot.getElementById('timelineProgress');
    const timelineTime = this.shadowRoot.getElementById('timelineTime');

    if (timelineProgress && this._playbackTime !== null) {
      const percentage = (this._playbackTime / this._config.history_duration) * 100;
      timelineProgress.style.width = `${percentage}%`;
    }

    if (timelineTime && this._playbackTime !== null) {
      const hours = Math.floor(this._playbackTime / 3600);
      const minutes = Math.floor((this._playbackTime % 3600) / 60);
      const seconds = Math.floor(this._playbackTime % 60);
      timelineTime.textContent = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
  }

  /**
   * Get editor configuration schema
   */
  static getConfigElement() {
    return document.createElement('motiondirection-visualizer-card-editor');
  }

  /**
   * Get stub configuration for card picker
   */
  static getStubConfig() {
    return {
      floorplan_id: 'ground_floor',
      show_realtime: true,
      show_history: true,
      history_duration: 3600,
      animation_speed: 1.0,
      heat_map: true,
      show_direction_arrows: true,
      show_confidence_overlay: true,
    };
  }
}

// Register custom element
customElements.define('motiondirection-motion-visualizer-card', MotionDirectionVisualizerCard);

// Register card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'motiondirection-motion-visualizer',
  name: 'MotionDirection Motion Visualizer',
  description: 'Real-time and historical motion visualization with trails, heat maps, and direction arrows',
  preview: true,
});

console.info(
  '%c MOTIONDIRECTION-VISUALIZER-CARD %c v1.0.0 ',
  'color: white; background: #4caf50; font-weight: 700;',
  'color: #4caf50; background: white; font-weight: 700;'
);
