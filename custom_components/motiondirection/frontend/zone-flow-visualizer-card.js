/**
 * MotionDirection Zone Flow Visualizer Card
 * 
 * Particle-based flow visualization showing zone transitions and motion flow patterns.
 * Displays real-time and historical flow data with animated particles.
 * 
 * Features:
 * - Particle flow animation
 * - Zone transition tracking
 * - Multiple flow styles (particles, arrows, heatmap)
 * - Zone state highlighting
 * - Historical playback
 * - Smooth animations
 * 
 * @example
 * type: custom:motiondirection-zone-flow
 * floorplan_id: ground_floor
 * show_realtime: true
 * show_history: true
 * history_duration: 3600
 * flow_style: "particles"
 * zone_highlights:
 *   active: "#00ff00"
 *   idle: "#808080"
 *   transit: "#ffff00"
 */

class MotionDirectionZoneFlowCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = null;
    this._hass = null;
    this._animationFrame = null;
    this._canvas = null;
    this._ctx = null;
    this._particles = [];
    this._zones = [];
    this._flowPaths = [];
    this._transitionMatrix = new Map();
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
      flow_style: config.flow_style || 'particles',
      zone_highlights: config.zone_highlights || {
        active: '#00ff00',
        idle: '#808080',
        transit: '#ffff00',
      },
      particle_count: config.particle_count || 50,
      particle_speed: config.particle_speed || 1.0,
      particle_size: config.particle_size || 3,
      show_zone_labels: config.show_zone_labels !== false,
      title: config.title || 'Zone Flow Visualizer',
    };

    this.render();
  }

  /**
   * Set Home Assistant instance
   */
  set hass(hass) {
    this._hass = hass;
    this.updateFlowData();

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
    if (this._canvas) {
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
   * Update flow data from Home Assistant
   */
  updateFlowData() {
    if (!this._hass || !this._config) return;

    // Load zones
    this.loadZones();

    // Load flow paths
    this.loadFlowPaths();

    // Update transition matrix
    this.updateTransitionMatrix();

    // Initialize particles if needed
    if (this._particles.length === 0 && this._flowPaths.length > 0) {
      this.initializeParticles();
    }
  }

  /**
   * Load zones from floorplan
   */
  loadZones() {
    const floorplanEntity = this._hass?.states[`sensor.motiondirection_floorplan_${this._config.floorplan_id}`];
    
    if (floorplanEntity?.attributes?.zones) {
      this._zones = floorplanEntity.attributes.zones.map(zone => ({
        id: zone.id,
        name: zone.name,
        bounds: zone.bounds,
        center: this.calculateZoneCenter(zone.bounds),
        state: 'idle',
        lastActivity: null,
      }));
    }

    // Update zone states from individual zone entities
    this._zones.forEach(zone => {
      const zoneEntity = this._hass?.states[`sensor.motiondirection_zone_${zone.id}`];
      if (zoneEntity) {
        zone.state = zoneEntity.state || 'idle';
        zone.lastActivity = zoneEntity.attributes.last_motion_time;
      }
    });
  }

  /**
   * Calculate zone center
   */
  calculateZoneCenter(bounds) {
    if (!bounds || bounds.length < 3) {
      return { x: 0.5, y: 0.5 };
    }

    const sumX = bounds.reduce((sum, point) => sum + point.x, 0);
    const sumY = bounds.reduce((sum, point) => sum + point.y, 0);

    return {
      x: sumX / bounds.length,
      y: sumY / bounds.length,
    };
  }

  /**
   * Load flow paths
   */
  loadFlowPaths() {
    const flowEntity = this._hass?.states[`sensor.motiondirection_${this._config.floorplan_id}_flow`];
    
    if (flowEntity?.attributes?.flow_paths) {
      this._flowPaths = flowEntity.attributes.flow_paths.map(path => ({
        from: path.from,
        to: path.to,
        strength: path.strength || 1.0,
        frequency: path.frequency || 0,
        avgTime: path.avg_time || 0,
      }));
    }

    // If no flow paths, create default paths between adjacent zones
    if (this._flowPaths.length === 0 && this._zones.length > 1) {
      this.generateDefaultPaths();
    }
  }

  /**
   * Generate default flow paths
   */
  generateDefaultPaths() {
    for (let i = 0; i < this._zones.length - 1; i++) {
      this._flowPaths.push({
        from: this._zones[i].id,
        to: this._zones[i + 1].id,
        strength: 0.5,
        frequency: 0,
        avgTime: 0,
      });
    }
  }

  /**
   * Update transition matrix
   */
  updateTransitionMatrix() {
    this._transitionMatrix.clear();

    this._flowPaths.forEach(path => {
      const key = `${path.from}_${path.to}`;
      this._transitionMatrix.set(key, {
        strength: path.strength,
        frequency: path.frequency,
        avgTime: path.avgTime,
      });
    });
  }

  /**
   * Initialize particles
   */
  initializeParticles() {
    this._particles = [];

    for (let i = 0; i < this._config.particle_count; i++) {
      // Select a random flow path
      if (this._flowPaths.length === 0) continue;

      const path = this._flowPaths[Math.floor(Math.random() * this._flowPaths.length)];
      const fromZone = this._zones.find(z => z.id === path.from);
      const toZone = this._zones.find(z => z.id === path.to);

      if (!fromZone || !toZone) continue;

      this._particles.push({
        id: i,
        path: path,
        fromZone: fromZone,
        toZone: toZone,
        position: { ...fromZone.center },
        progress: Math.random(),
        speed: this._config.particle_speed * (0.5 + Math.random() * 0.5),
        size: this._config.particle_size,
        alpha: 0.3 + (path.strength * 0.7),
      });
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
          max-width: 150px;
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
          font-size: 10px;
        }

        .stats {
          padding: 12px 16px;
          background: var(--card-background-color);
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
            <button class="control-btn ${this._config.flow_style === 'particles' ? 'active' : ''}" data-style="particles">
              Particles
            </button>
            <button class="control-btn ${this._config.flow_style === 'arrows' ? 'active' : ''}" data-style="arrows">
              Arrows
            </button>
            <button class="control-btn ${this._config.flow_style === 'heatmap' ? 'active' : ''}" data-style="heatmap">
              Heatmap
            </button>
          </div>
        </div>

        <div class="canvas-container">
          <canvas id="mainCanvas"></canvas>
          
          <div class="legend">
            <div class="legend-item">
              <div class="legend-color" style="background: ${this._config.zone_highlights.active};"></div>
              <span class="legend-label">Active Zone</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background: ${this._config.zone_highlights.transit};"></div>
              <span class="legend-label">Transit Zone</span>
            </div>
            <div class="legend-item">
              <div class="legend-color" style="background: ${this._config.zone_highlights.idle};"></div>
              <span class="legend-label">Idle Zone</span>
            </div>
          </div>
        </div>

        <div class="stats">
          <div class="stat-item">
            <div class="stat-value" id="statZones">0</div>
            <div class="stat-label">Zones</div>
          </div>
          <div class="stat-item">
            <div class="stat-value" id="statPaths">0</div>
            <div class="stat-label">Flow Paths</div>
          </div>
          <div class="stat-item">
            <div class="stat-value" id="statTransitions">0</div>
            <div class="stat-label">Transitions</div>
          </div>
        </div>
      </ha-card>
    `;

    // Setup canvas
    this.setupCanvas();

    // Setup event listeners
    this.setupEventListeners();

    // Initial update
    this.updateFlowData();
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
    const styleButtons = this.shadowRoot.querySelectorAll('[data-style]');
    
    styleButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const style = e.target.dataset.style;
        this._config.flow_style = style;
        
        // Update active state
        styleButtons.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
      });
    });
  }

  /**
   * Update visualization
   */
  updateVisualization() {
    if (!this._ctx || !this._canvas) return;

    const { width, height } = this._canvas;

    // Clear canvas
    this._ctx.clearRect(0, 0, width, height);

    // Draw zones
    this.drawZones();

    // Draw flow based on style
    switch (this._config.flow_style) {
      case 'particles':
        this.drawParticleFlow();
        break;
      case 'arrows':
        this.drawArrowFlow();
        break;
      case 'heatmap':
        this.drawHeatmapFlow();
        break;
    }

    // Update particles
    this.updateParticles();

    // Update statistics
    this.updateStatistics();
  }

  /**
   * Draw zones
   */
  drawZones() {
    const { width, height } = this._canvas;

    this._zones.forEach(zone => {
      if (!zone.bounds || zone.bounds.length < 3) return;

      // Determine zone color based on state
      let color = this._config.zone_highlights.idle;
      if (zone.state === 'active' || zone.state === 'occupied') {
        color = this._config.zone_highlights.active;
      } else if (zone.state === 'transit') {
        color = this._config.zone_highlights.transit;
      }

      // Draw zone polygon
      this._ctx.beginPath();
      zone.bounds.forEach((point, index) => {
        const x = point.x * width;
        const y = point.y * height;
        if (index === 0) {
          this._ctx.moveTo(x, y);
        } else {
          this._ctx.lineTo(x, y);
        }
      });
      this._ctx.closePath();

      this._ctx.fillStyle = `${color}22`;
      this._ctx.fill();
      this._ctx.strokeStyle = color;
      this._ctx.lineWidth = 2;
      this._ctx.stroke();

      // Draw zone label if enabled
      if (this._config.show_zone_labels) {
        const centerX = zone.center.x * width;
        const centerY = zone.center.y * height;

        this._ctx.font = '12px sans-serif';
        this._ctx.fillStyle = color;
        this._ctx.textAlign = 'center';
        this._ctx.textBaseline = 'middle';
        this._ctx.fillText(zone.name || zone.id, centerX, centerY);
      }
    });
  }

  /**
   * Draw particle flow
   */
  drawParticleFlow() {
    this._particles.forEach(particle => {
      const x = particle.position.x * this._canvas.width;
      const y = particle.position.y * this._canvas.height;

      this._ctx.beginPath();
      this._ctx.arc(x, y, particle.size, 0, Math.PI * 2);
      this._ctx.fillStyle = `rgba(0, 150, 255, ${particle.alpha})`;
      this._ctx.fill();

      // Draw trail
      const trailLength = 5;
      const dx = (particle.toZone.center.x - particle.fromZone.center.x) * -0.02;
      const dy = (particle.toZone.center.y - particle.fromZone.center.y) * -0.02;

      for (let i = 1; i <= trailLength; i++) {
        const trailX = (particle.position.x + dx * i) * this._canvas.width;
        const trailY = (particle.position.y + dy * i) * this._canvas.height;
        const trailAlpha = particle.alpha * (1 - i / trailLength);

        this._ctx.beginPath();
        this._ctx.arc(trailX, trailY, particle.size * 0.7, 0, Math.PI * 2);
        this._ctx.fillStyle = `rgba(0, 150, 255, ${trailAlpha})`;
        this._ctx.fill();
      }
    });
  }

  /**
   * Draw arrow flow
   */
  drawArrowFlow() {
    const { width, height } = this._canvas;

    this._flowPaths.forEach(path => {
      const fromZone = this._zones.find(z => z.id === path.from);
      const toZone = this._zones.find(z => z.id === path.to);

      if (!fromZone || !toZone) return;

      const fromX = fromZone.center.x * width;
      const fromY = fromZone.center.y * height;
      const toX = toZone.center.x * width;
      const toY = toZone.center.y * height;

      // Draw line
      this._ctx.beginPath();
      this._ctx.moveTo(fromX, fromY);
      this._ctx.lineTo(toX, toY);
      this._ctx.strokeStyle = `rgba(0, 150, 255, ${path.strength * 0.6})`;
      this._ctx.lineWidth = 2 + (path.strength * 3);
      this._ctx.stroke();

      // Draw arrowhead
      const angle = Math.atan2(toY - fromY, toX - fromX);
      const arrowSize = 10;

      this._ctx.save();
      this._ctx.translate(toX, toY);
      this._ctx.rotate(angle);

      this._ctx.beginPath();
      this._ctx.moveTo(0, 0);
      this._ctx.lineTo(-arrowSize, -arrowSize / 2);
      this._ctx.lineTo(-arrowSize, arrowSize / 2);
      this._ctx.closePath();

      this._ctx.fillStyle = `rgba(0, 150, 255, ${path.strength})`;
      this._ctx.fill();

      this._ctx.restore();
    });
  }

  /**
   * Draw heatmap flow
   */
  drawHeatmapFlow() {
    const { width, height } = this._canvas;

    this._flowPaths.forEach(path => {
      const fromZone = this._zones.find(z => z.id === path.from);
      const toZone = this._zones.find(z => z.id === path.to);

      if (!fromZone || !toZone) return;

      const fromX = fromZone.center.x * width;
      const fromY = fromZone.center.y * height;
      const toX = toZone.center.x * width;
      const toY = toZone.center.y * height;

      // Create gradient along path
      const gradient = this._ctx.createLinearGradient(fromX, fromY, toX, toY);
      
      const intensity = path.strength;
      if (intensity > 0.7) {
        gradient.addColorStop(0, 'rgba(255, 0, 0, 0.3)');
        gradient.addColorStop(1, 'rgba(255, 0, 0, 0.1)');
      } else if (intensity > 0.4) {
        gradient.addColorStop(0, 'rgba(255, 255, 0, 0.3)');
        gradient.addColorStop(1, 'rgba(255, 255, 0, 0.1)');
      } else {
        gradient.addColorStop(0, 'rgba(0, 255, 0, 0.3)');
        gradient.addColorStop(1, 'rgba(0, 255, 0, 0.1)');
      }

      // Draw thick line with gradient
      this._ctx.beginPath();
      this._ctx.moveTo(fromX, fromY);
      this._ctx.lineTo(toX, toY);
      this._ctx.strokeStyle = gradient;
      this._ctx.lineWidth = 15 + (intensity * 10);
      this._ctx.lineCap = 'round';
      this._ctx.stroke();
    });
  }

  /**
   * Update particles
   */
  updateParticles() {
    this._particles.forEach(particle => {
      // Update progress
      particle.progress += 0.01 * particle.speed;

      // Reset if reached destination
      if (particle.progress >= 1) {
        particle.progress = 0;
        
        // Optionally select a new random path
        if (Math.random() > 0.7 && this._flowPaths.length > 0) {
          const newPath = this._flowPaths[Math.floor(Math.random() * this._flowPaths.length)];
          const fromZone = this._zones.find(z => z.id === newPath.from);
          const toZone = this._zones.find(z => z.id === newPath.to);

          if (fromZone && toZone) {
            particle.path = newPath;
            particle.fromZone = fromZone;
            particle.toZone = toZone;
            particle.alpha = 0.3 + (newPath.strength * 0.7);
          }
        }
      }

      // Update position (linear interpolation)
      particle.position.x = particle.fromZone.center.x + 
        (particle.toZone.center.x - particle.fromZone.center.x) * particle.progress;
      particle.position.y = particle.fromZone.center.y + 
        (particle.toZone.center.y - particle.fromZone.center.y) * particle.progress;
    });
  }

  /**
   * Update statistics display
   */
  updateStatistics() {
    const statZones = this.shadowRoot.getElementById('statZones');
    const statPaths = this.shadowRoot.getElementById('statPaths');
    const statTransitions = this.shadowRoot.getElementById('statTransitions');

    if (statZones) {
      statZones.textContent = this._zones.length;
    }

    if (statPaths) {
      statPaths.textContent = this._flowPaths.length;
    }

    if (statTransitions) {
      const totalTransitions = this._flowPaths.reduce((sum, path) => sum + (path.frequency || 0), 0);
      statTransitions.textContent = totalTransitions;
    }
  }

  /**
   * Get editor configuration schema
   */
  static getConfigElement() {
    return document.createElement('motiondirection-zone-flow-card-editor');
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
      flow_style: 'particles',
      zone_highlights: {
        active: '#00ff00',
        idle: '#808080',
        transit: '#ffff00',
      },
    };
  }
}

// Register custom element
customElements.define('motiondirection-zone-flow-visualizer-card', MotionDirectionZoneFlowCard);

// Register card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'motiondirection-zone-flow-visualizer',
  name: 'MotionDirection Zone Flow Visualizer',
  description: 'Particle-based flow visualization showing zone transitions and motion patterns',
  preview: true,
});

console.info(
  '%c MOTIONDIRECTION-ZONE-FLOW-CARD %c v1.0.0 ',
  'color: white; background: #9c27b0; font-weight: 700;',
  'color: #9c27b0; background: white; font-weight: 700;'
);
