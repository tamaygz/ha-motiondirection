/**
 * Motion Direction Status Card
 * 
 * A custom Lovelace card for Home Assistant that displays the current motion
 * direction detection status, including confidence scores, active zones,
 * triggered sensors, and pattern information.
 * 
 * @version 1.0.0
 * @license MIT
 */

class MotionStatusCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._hass = null;
    this._config = null;
  }

  /**
   * Set the Home Assistant object
   * Called automatically when HA state changes
   */
  set hass(hass) {
    this._hass = hass;
    this._updateCard();
  }

  /**
   * Set the card configuration
   * Called when user configures the card
   */
  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity (sensor.motion_direction)');
    }

    this._config = {
      entity: config.entity,
      title: config.title || 'Motion Direction',
      show_confidence: config.show_confidence !== false,
      show_zones: config.show_zones !== false,
      show_sensors: config.show_sensors !== false,
      show_pattern: config.show_pattern !== false,
      show_cues: config.show_cues !== false,
      update_interval: config.update_interval || 1000,
      ...config
    };

    this._updateCard();
  }

  /**
   * Update the card content
   */
  _updateCard() {
    if (!this._hass || !this._config) {
      return;
    }

    const stateObj = this._hass.states[this._config.entity];
    
    if (!stateObj) {
      this.shadowRoot.innerHTML = this._renderError(`Entity ${this._config.entity} not found`);
      return;
    }

    this.shadowRoot.innerHTML = this._renderCard(stateObj);
  }

  /**
   * Render error message
   */
  _renderError(message) {
    return `
      <style>${this._getStyles()}</style>
      <ha-card>
        <div class="card-content error">
          <ha-icon icon="mdi:alert-circle"></ha-icon>
          <p>${message}</p>
        </div>
      </ha-card>
    `;
  }

  /**
   * Render the complete card
   */
  _renderCard(stateObj) {
    const direction = stateObj.state || 'unknown';
    const attributes = stateObj.attributes || {};
    
    return `
      <style>${this._getStyles()}</style>
      <ha-card>
        <div class="card-header">
          <div class="name">${this._config.title}</div>
        </div>
        <div class="card-content">
          ${this._renderDirection(direction, attributes)}
          ${this._config.show_confidence ? this._renderConfidence(attributes) : ''}
          ${this._config.show_pattern ? this._renderPattern(attributes) : ''}
          ${this._config.show_zones ? this._renderZones(attributes) : ''}
          ${this._config.show_sensors ? this._renderSensors(attributes) : ''}
          ${this._config.show_cues ? this._renderCues(attributes) : ''}
        </div>
      </ha-card>
    `;
  }

  /**
   * Render direction display
   */
  _renderDirection(direction, attributes) {
    const icon = this._getDirectionIcon(direction);
    const method = attributes.detection_method || 'unknown';
    
    return `
      <div class="direction-container">
        <div class="direction-icon">
          <ha-icon icon="${icon}"></ha-icon>
        </div>
        <div class="direction-info">
          <div class="direction-value">${this._formatDirection(direction)}</div>
          <div class="direction-method">${method}</div>
        </div>
      </div>
    `;
  }

  /**
   * Render confidence score
   */
  _renderConfidence(attributes) {
    const confidence = attributes.confidence || 0;
    const percentage = Math.round(confidence * 100);
    const confidenceClass = this._getConfidenceClass(confidence);
    
    return `
      <div class="info-row">
        <span class="info-label">Confidence:</span>
        <div class="confidence-bar">
          <div class="confidence-fill ${confidenceClass}" style="width: ${percentage}%"></div>
          <span class="confidence-text">${percentage}%</span>
        </div>
      </div>
    `;
  }

  /**
   * Render pattern information
   */
  _renderPattern(attributes) {
    if (!attributes.pattern_type) {
      return '';
    }
    
    const patternIcon = this._getPatternIcon(attributes.pattern_type);
    
    return `
      <div class="info-row">
        <span class="info-label">Pattern:</span>
        <div class="pattern-info">
          <ha-icon icon="${patternIcon}"></ha-icon>
          <span>${this._formatPattern(attributes.pattern_type)}</span>
        </div>
      </div>
    `;
  }

  /**
   * Render active zones
   */
  _renderZones(attributes) {
    const zones = attributes.active_zones || [];
    
    if (zones.length === 0) {
      return '';
    }
    
    return `
      <div class="info-section">
        <div class="section-header">Active Zones</div>
        <div class="zone-list">
          ${zones.map(zone => `
            <div class="zone-chip">
              <ha-icon icon="mdi:map-marker"></ha-icon>
              <span>${zone}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  /**
   * Render triggered sensors
   */
  _renderSensors(attributes) {
    const sensors = attributes.triggered_sensors || [];
    
    if (sensors.length === 0) {
      return '';
    }
    
    return `
      <div class="info-section">
        <div class="section-header">Triggered Sensors</div>
        <div class="sensor-list">
          ${sensors.map(sensor => `
            <div class="sensor-item">
              <ha-icon icon="mdi:motion-sensor"></ha-icon>
              <span>${this._formatEntityName(sensor)}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  /**
   * Render contributing cues
   */
  _renderCues(attributes) {
    const cues = attributes.contributing_cues || [];
    
    if (cues.length === 0) {
      return '';
    }
    
    return `
      <div class="info-section">
        <div class="section-header">Contributing Cues</div>
        <div class="cue-list">
          ${cues.map(cue => `
            <div class="cue-item">
              <ha-icon icon="mdi:lightbulb"></ha-icon>
              <span>${this._formatEntityName(cue)}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  /**
   * Get direction icon
   */
  _getDirectionIcon(direction) {
    const icons = {
      'north': 'mdi:arrow-up',
      'south': 'mdi:arrow-down',
      'east': 'mdi:arrow-right',
      'west': 'mdi:arrow-left',
      'north_east': 'mdi:arrow-top-right',
      'north_west': 'mdi:arrow-top-left',
      'south_east': 'mdi:arrow-bottom-right',
      'south_west': 'mdi:arrow-bottom-left',
      'entering': 'mdi:home-import-outline',
      'exiting': 'mdi:home-export-outline',
      'unknown': 'mdi:help-circle',
      'none': 'mdi:minus-circle'
    };
    return icons[direction] || 'mdi:help-circle';
  }

  /**
   * Get pattern icon
   */
  _getPatternIcon(pattern) {
    const icons = {
      'linear': 'mdi:arrow-right-bold',
      'circular': 'mdi:sync',
      'zone_transition': 'mdi:transit-transfer',
      'stationary': 'mdi:stop-circle',
      'random': 'mdi:shuffle',
      'anomaly': 'mdi:alert'
    };
    return icons[pattern] || 'mdi:help-circle';
  }

  /**
   * Get confidence class for styling
   */
  _getConfidenceClass(confidence) {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.5) return 'medium';
    return 'low';
  }

  /**
   * Format direction for display
   */
  _formatDirection(direction) {
    return direction
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }

  /**
   * Format pattern for display
   */
  _formatPattern(pattern) {
    return pattern
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }

  /**
   * Format entity name (remove domain and underscores)
   */
  _formatEntityName(entityId) {
    return entityId
      .split('.')[1]
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase());
  }

  /**
   * Get card size for masonry layout
   */
  getCardSize() {
    return 4;
  }

  /**
   * Get grid options for sections layout
   */
  getGridOptions() {
    return {
      rows: 4,
      columns: 6,
      min_rows: 3,
      max_rows: 6,
    };
  }

  /**
   * Get card styles
   */
  _getStyles() {
    return `
      ha-card {
        padding: 16px;
      }
      
      .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
      }
      
      .name {
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      
      .card-content {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
      
      .error {
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--error-color);
      }
      
      .direction-container {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 16px;
        background: var(--secondary-background-color);
        border-radius: 8px;
      }
      
      .direction-icon {
        font-size: 48px;
        color: var(--primary-color);
      }
      
      .direction-icon ha-icon {
        width: 48px;
        height: 48px;
      }
      
      .direction-info {
        flex: 1;
      }
      
      .direction-value {
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      
      .direction-method {
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        margin-top: 4px;
      }
      
      .info-row {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      
      .info-label {
        font-weight: 500;
        color: var(--secondary-text-color);
        min-width: 100px;
      }
      
      .confidence-bar {
        flex: 1;
        height: 24px;
        background: var(--secondary-background-color);
        border-radius: 12px;
        position: relative;
        overflow: hidden;
      }
      
      .confidence-fill {
        height: 100%;
        border-radius: 12px;
        transition: width 0.3s ease;
      }
      
      .confidence-fill.high {
        background: var(--success-color);
      }
      
      .confidence-fill.medium {
        background: var(--warning-color);
      }
      
      .confidence-fill.low {
        background: var(--error-color);
      }
      
      .confidence-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--primary-text-color);
      }
      
      .pattern-info {
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--primary-text-color);
      }
      
      .info-section {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      
      .section-header {
        font-weight: 500;
        font-size: 0.875rem;
        color: var(--secondary-text-color);
        text-transform: uppercase;
      }
      
      .zone-list, .sensor-list, .cue-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
      }
      
      .zone-chip {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: var(--primary-color);
        color: var(--text-primary-color);
        border-radius: 16px;
        font-size: 0.875rem;
      }
      
      .zone-chip ha-icon {
        width: 16px;
        height: 16px;
      }
      
      .sensor-item, .cue-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: var(--secondary-background-color);
        border-radius: 8px;
        font-size: 0.875rem;
        color: var(--primary-text-color);
      }
      
      .sensor-item ha-icon, .cue-item ha-icon {
        width: 18px;
        height: 18px;
        color: var(--secondary-text-color);
      }
    `;
  }
}

// Register the custom card
customElements.define('motion-status-card', MotionStatusCard);

// Register with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'motion-status-card',
  name: 'Motion Direction Status',
  description: 'Display current motion direction detection status with confidence, zones, and sensors',
  preview: true,
  documentationURL: 'https://github.com/tamaygz/ha-motiondirection#motion-status-card',
});

console.info(
  '%c MOTION-STATUS-CARD %c 1.0.0 ',
  'color: white; background: #039be5; font-weight: 700;',
  'color: #039be5; background: white; font-weight: 700;'
);
