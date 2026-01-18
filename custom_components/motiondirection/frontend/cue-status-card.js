/**
 * MotionDirection Cue Status Card
 * 
 * Displays real-time status of secondary cues with correlation statistics.
 * Shows cue states, correlation success rates, and active correlations.
 * 
 * Features:
 * - Three layout modes: list, grid, compact
 * - Real-time updates
 * - Per-cue configuration
 * - State indicators
 * - Correlation statistics
 * - Success rate visualization
 * 
 * @example
 * type: custom:motiondirection-cue-status
 * cues:
 *   - cue_id: "front_door"
 *     show_state: true
 *     show_correlations: true
 *     show_statistics: true
 * layout: "list"
 * update_interval: 1000
 */

class MotionDirectionCueStatusCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = null;
    this._hass = null;
    this._updateInterval = null;
  }

  /**
   * Set card configuration
   */
  setConfig(config) {
    if (!config.cues || !Array.isArray(config.cues)) {
      throw new Error('You need to define cues');
    }

    this._config = {
      cues: config.cues,
      layout: config.layout || 'list',
      update_interval: config.update_interval || 1000,
      title: config.title || 'Cue Status',
      show_header: config.show_header !== false,
    };

    this.render();
  }

  /**
   * Set Home Assistant instance
   */
  set hass(hass) {
    this._hass = hass;
    this.updateCueData();
  }

  /**
   * Get card size for layout
   */
  getCardSize() {
    const cueCount = this._config?.cues?.length || 0;
    const layout = this._config?.layout || 'list';

    if (layout === 'compact') {
      return 1 + Math.ceil(cueCount / 4);
    } else if (layout === 'grid') {
      return 2 + Math.ceil(cueCount / 3);
    } else {
      return 1 + cueCount;
    }
  }

  /**
   * Called when element is connected to DOM
   */
  connectedCallback() {
    this.startUpdateInterval();
  }

  /**
   * Called when element is disconnected from DOM
   */
  disconnectedCallback() {
    this.stopUpdateInterval();
  }

  /**
   * Start update interval
   */
  startUpdateInterval() {
    this.stopUpdateInterval();
    if (this._config?.update_interval) {
      this._updateInterval = setInterval(() => {
        this.updateCueData();
      }, this._config.update_interval);
    }
  }

  /**
   * Stop update interval
   */
  stopUpdateInterval() {
    if (this._updateInterval) {
      clearInterval(this._updateInterval);
      this._updateInterval = null;
    }
  }

  /**
   * Update cue data from Home Assistant
   */
  updateCueData() {
    if (!this._hass || !this._config) return;

    const cueStates = this._config.cues.map(cueConfig => {
      const entityId = `sensor.motiondirection_cue_${cueConfig.cue_id}`;
      const entity = this._hass.states[entityId];

      if (!entity) {
        return {
          cue_id: cueConfig.cue_id,
          available: false,
          error: 'Entity not found',
          config: cueConfig,
        };
      }

      return {
        cue_id: cueConfig.cue_id,
        available: true,
        state: entity.state,
        cue_type: entity.attributes.cue_type || 'unknown',
        active: entity.attributes.active || false,
        last_triggered: entity.attributes.last_triggered || null,
        correlations: {
          total: entity.attributes.total_correlations || 0,
          successful: entity.attributes.successful_correlations || 0,
          success_rate: entity.attributes.correlation_success_rate || 0,
          active_correlations: entity.attributes.active_correlations || [],
        },
        statistics: {
          avg_confidence: entity.attributes.average_confidence || 0,
          total_triggers: entity.attributes.total_triggers || 0,
          last_24h_triggers: entity.attributes.triggers_last_24h || 0,
        },
        config: cueConfig,
      };
    });

    this.renderCues(cueStates);
  }

  /**
   * Render the card
   */
  render() {
    const layout = this._config?.layout || 'list';
    
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }

        ha-card {
          padding: 16px;
        }

        .card-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
        }

        .card-title {
          font-size: 18px;
          font-weight: 500;
          margin: 0;
        }

        .layout-toggle {
          display: flex;
          gap: 4px;
        }

        .layout-btn {
          padding: 4px 8px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
          cursor: pointer;
          border-radius: 4px;
          font-size: 12px;
        }

        .layout-btn.active {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .cues-container {
          display: ${layout === 'grid' ? 'grid' : 'flex'};
          ${layout === 'grid' ? 'grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));' : ''}
          ${layout === 'list' ? 'flex-direction: column;' : ''}
          ${layout === 'compact' ? 'flex-wrap: wrap;' : ''}
          gap: 12px;
        }

        .cue-item {
          background: var(--card-background-color);
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          padding: ${layout === 'compact' ? '8px' : '12px'};
          ${layout === 'compact' ? 'width: calc(25% - 9px);' : ''}
        }

        .cue-item.unavailable {
          opacity: 0.5;
        }

        .cue-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;
        }

        .cue-name {
          font-weight: 500;
          font-size: ${layout === 'compact' ? '12px' : '14px'};
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .cue-type-badge {
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 9px;
          font-weight: 500;
          text-transform: uppercase;
          background: var(--divider-color);
          color: var(--secondary-text-color);
        }

        .cue-status-badge {
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 10px;
          font-weight: 500;
          text-transform: uppercase;
        }

        .cue-status-badge.active {
          background: var(--success-color);
          color: white;
        }

        .cue-status-badge.inactive {
          background: var(--disabled-color);
          color: var(--secondary-text-color);
        }

        .cue-state {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 8px 0;
          padding: 8px;
          background: var(--primary-background-color);
          border-radius: 6px;
        }

        .state-icon {
          font-size: ${layout === 'compact' ? '18px' : '20px'};
        }

        .state-info {
          flex: 1;
        }

        .state-label {
          font-size: ${layout === 'compact' ? '11px' : '12px'};
          color: var(--secondary-text-color);
        }

        .state-value {
          font-size: ${layout === 'compact' ? '12px' : '14px'};
          font-weight: 500;
          color: var(--primary-text-color);
        }

        .cue-correlations {
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid var(--divider-color);
        }

        .correlation-header {
          font-size: 12px;
          font-weight: 500;
          color: var(--primary-text-color);
          margin-bottom: 6px;
        }

        .correlation-stats {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .stat-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 11px;
        }

        .stat-label {
          color: var(--secondary-text-color);
        }

        .stat-value {
          font-weight: 500;
          color: var(--primary-text-color);
        }

        .success-rate {
          margin-top: 8px;
        }

        .success-rate-bar {
          height: 6px;
          background: var(--divider-color);
          border-radius: 3px;
          overflow: hidden;
          margin-top: 4px;
        }

        .success-rate-fill {
          height: 100%;
          background: linear-gradient(to right, var(--error-color), var(--warning-color), var(--success-color));
          transition: width 0.3s ease;
        }

        .success-rate-label {
          display: flex;
          justify-content: space-between;
          font-size: 10px;
          margin-top: 2px;
        }

        .success-rate-percent {
          color: var(--primary-text-color);
          font-weight: 500;
        }

        .active-correlations {
          margin-top: 8px;
          display: ${layout === 'compact' ? 'none' : 'block'};
        }

        .active-correlation-item {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 0;
          font-size: 11px;
        }

        .correlation-badge {
          padding: 2px 4px;
          background: var(--primary-color);
          color: white;
          border-radius: 3px;
          font-size: 9px;
        }

        .cue-statistics {
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid var(--divider-color);
          display: ${layout === 'compact' ? 'none' : 'flex'};
          flex-direction: column;
          gap: 4px;
        }

        .last-triggered {
          font-size: 10px;
          color: var(--secondary-text-color);
          margin-top: 4px;
        }

        .error-message {
          color: var(--error-color);
          font-size: 12px;
          padding: 8px;
        }

        .no-cues {
          text-align: center;
          padding: 32px;
          color: var(--secondary-text-color);
        }
      </style>

      <ha-card>
        ${this._config.show_header ? `
          <div class="card-header">
            <h2 class="card-title">${this._config.title}</h2>
            <div class="layout-toggle">
              <button class="layout-btn ${layout === 'list' ? 'active' : ''}" data-layout="list">List</button>
              <button class="layout-btn ${layout === 'grid' ? 'active' : ''}" data-layout="grid">Grid</button>
              <button class="layout-btn ${layout === 'compact' ? 'active' : ''}" data-layout="compact">Compact</button>
            </div>
          </div>
        ` : ''}
        
        <div class="cues-container"></div>
      </ha-card>
    `;

    // Add event listeners to layout toggle buttons
    if (this._config.show_header) {
      this.shadowRoot.querySelectorAll('.layout-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const newLayout = e.target.dataset.layout;
          this._config.layout = newLayout;
          this.render();
          this.updateCueData();
        });
      });
    }

    // Initial data update
    this.updateCueData();
  }

  /**
   * Render cues with current state
   */
  renderCues(cueStates) {
    const container = this.shadowRoot.querySelector('.cues-container');
    if (!container) return;

    if (!cueStates || cueStates.length === 0) {
      container.innerHTML = '<div class="no-cues">No cues configured</div>';
      return;
    }

    container.innerHTML = cueStates.map(cue => this.renderCueItem(cue)).join('');
  }

  /**
   * Render a single cue item
   */
  renderCueItem(cue) {
    if (!cue.available) {
      return `
        <div class="cue-item unavailable">
          <div class="cue-header">
            <span class="cue-name">${cue.cue_id}</span>
            <span class="cue-status-badge inactive">Unavailable</span>
          </div>
          <div class="error-message">${cue.error}</div>
        </div>
      `;
    }

    const config = cue.config || {};
    const showState = config.show_state !== false;
    const showCorrelations = config.show_correlations !== false;
    const showStatistics = config.show_statistics !== false;
    const isActive = cue.active || cue.state === 'on';

    return `
      <div class="cue-item">
        <div class="cue-header">
          <span class="cue-name">
            ${cue.cue_id}
            <span class="cue-type-badge">${cue.cue_type}</span>
          </span>
          <span class="cue-status-badge ${isActive ? 'active' : 'inactive'}">
            ${isActive ? 'Active' : 'Inactive'}
          </span>
        </div>

        ${showState ? `
          <div class="cue-state">
            <span class="state-icon">${this.getCueTypeIcon(cue.cue_type)}</span>
            <div class="state-info">
              <div class="state-label">Current State</div>
              <div class="state-value">${this.formatState(cue.state)}</div>
            </div>
          </div>
        ` : ''}

        ${showCorrelations ? `
          <div class="cue-correlations">
            <div class="correlation-header">Correlations</div>
            <div class="correlation-stats">
              <div class="stat-row">
                <span class="stat-label">Total</span>
                <span class="stat-value">${cue.correlations.total}</span>
              </div>
              <div class="stat-row">
                <span class="stat-label">Successful</span>
                <span class="stat-value">${cue.correlations.successful}</span>
              </div>
            </div>
            
            <div class="success-rate">
              <div class="success-rate-bar">
                <div class="success-rate-fill" style="width: ${cue.correlations.success_rate * 100}%"></div>
              </div>
              <div class="success-rate-label">
                <span class="stat-label">Success Rate</span>
                <span class="success-rate-percent">${Math.round(cue.correlations.success_rate * 100)}%</span>
              </div>
            </div>

            ${cue.correlations.active_correlations && cue.correlations.active_correlations.length > 0 ? `
              <div class="active-correlations">
                ${cue.correlations.active_correlations.slice(0, 3).map(corr => `
                  <div class="active-correlation-item">
                    <span class="correlation-badge">Active</span>
                    <span>${corr.zone || corr.sensor || 'Unknown'}</span>
                  </div>
                `).join('')}
              </div>
            ` : ''}
          </div>
        ` : ''}

        ${showStatistics ? `
          <div class="cue-statistics">
            <div class="stat-row">
              <span class="stat-label">Avg Confidence</span>
              <span class="stat-value">${Math.round(cue.statistics.avg_confidence * 100)}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Total Triggers</span>
              <span class="stat-value">${cue.statistics.total_triggers}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Last 24h</span>
              <span class="stat-value">${cue.statistics.last_24h_triggers}</span>
            </div>
          </div>
        ` : ''}

        ${cue.last_triggered ? `
          <div class="last-triggered">
            Last triggered: ${this.formatLastTriggered(cue.last_triggered)}
          </div>
        ` : ''}
      </div>
    `;
  }

  /**
   * Get cue type icon
   */
  getCueTypeIcon(cueType) {
    const icons = {
      'door': '🚪',
      'window': '🪟',
      'light': '💡',
      'switch': '🔌',
      'lock': '🔒',
      'climate': '🌡️',
      'media': '📺',
      'appliance': '🏠',
      'sensor': '📡',
      'unknown': '❓',
    };
    return icons[cueType?.toLowerCase()] || icons['unknown'];
  }

  /**
   * Format state text
   */
  formatState(state) {
    if (!state) return 'Unknown';
    
    // Handle boolean states
    if (state === 'on' || state === true) return 'On';
    if (state === 'off' || state === false) return 'Off';
    
    // Capitalize first letter
    return state.charAt(0).toUpperCase() + state.slice(1);
  }

  /**
   * Format last triggered time
   */
  formatLastTriggered(timestamp) {
    if (!timestamp) return 'Never';
    
    const now = new Date();
    const lastTriggered = new Date(timestamp);
    const diffMs = now - lastTriggered;
    const diffSeconds = Math.floor(diffMs / 1000);

    if (diffSeconds < 60) {
      return 'Just now';
    } else if (diffSeconds < 3600) {
      const minutes = Math.floor(diffSeconds / 60);
      return `${minutes}m ago`;
    } else if (diffSeconds < 86400) {
      const hours = Math.floor(diffSeconds / 3600);
      return `${hours}h ago`;
    } else {
      const days = Math.floor(diffSeconds / 86400);
      return `${days}d ago`;
    }
  }

  /**
   * Get editor configuration schema
   */
  static getConfigElement() {
    return document.createElement('motiondirection-cue-status-card-editor');
  }

  /**
   * Get stub configuration for card picker
   */
  static getStubConfig() {
    return {
      cues: [
        {
          cue_id: 'front_door',
          show_state: true,
          show_correlations: true,
          show_statistics: true,
        },
      ],
      layout: 'list',
      update_interval: 1000,
    };
  }
}

// Register custom element
customElements.define('motiondirection-cue-status', MotionDirectionCueStatusCard);

// Register card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'motiondirection-cue-status',
  name: 'MotionDirection Cue Status',
  description: 'Display real-time status of secondary cues with correlation statistics',
  preview: true,
});

console.info(
  '%c MOTIONDIRECTION-CUE-STATUS-CARD %c v1.0.0 ',
  'color: white; background: #ff9800; font-weight: 700;',
  'color: #ff9800; background: white; font-weight: 700;'
);
