/**
 * MotionDirection Zone Status Card
 * 
 * Displays real-time status of motion zones with configurable layouts.
 * Shows direction, occupancy, and statistics for each zone.
 * 
 * Features:
 * - Three layout modes: grid, list, compact
 * - Real-time updates
 * - Per-zone configuration
 * - Direction indicators
 * - Occupancy status
 * - Statistics display
 * 
 * @example
 * type: custom:motiondirection-zone-status
 * zones:
 *   - zone_id: "living_room"
 *     show_direction: true
 *     show_occupancy: true
 *     show_statistics: true
 * layout: "grid"
 * update_interval: 1000
 */

class MotionDirectionZoneStatusCard extends HTMLElement {
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
    if (!config.zones || !Array.isArray(config.zones)) {
      throw new Error('You need to define zones');
    }

    this._config = {
      zones: config.zones,
      layout: config.layout || 'grid',
      update_interval: config.update_interval || 1000,
      title: config.title || 'Zone Status',
      show_header: config.show_header !== false,
    };

    this.render();
  }

  /**
   * Set Home Assistant instance
   */
  set hass(hass) {
    this._hass = hass;
    this.updateZoneData();
  }

  /**
   * Get card size for layout
   */
  getCardSize() {
    const zoneCount = this._config?.zones?.length || 0;
    const layout = this._config?.layout || 'grid';

    if (layout === 'compact') {
      return 1 + Math.ceil(zoneCount / 4);
    } else if (layout === 'grid') {
      return 2 + Math.ceil(zoneCount / 3);
    } else {
      return 1 + zoneCount;
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
        this.updateZoneData();
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
   * Update zone data from Home Assistant
   */
  updateZoneData() {
    if (!this._hass || !this._config) return;

    const zoneStates = this._config.zones.map(zoneConfig => {
      const entityId = `sensor.motiondirection_zone_${zoneConfig.zone_id}`;
      const entity = this._hass.states[entityId];

      if (!entity) {
        return {
          zone_id: zoneConfig.zone_id,
          available: false,
          error: 'Entity not found',
          config: zoneConfig,
        };
      }

      return {
        zone_id: zoneConfig.zone_id,
        available: true,
        state: entity.state,
        direction: entity.attributes.current_direction || 'unknown',
        occupancy: entity.attributes.occupancy || 'unknown',
        confidence: entity.attributes.confidence || 0,
        statistics: {
          transitions: entity.attributes.total_transitions || 0,
          dwell_time: entity.attributes.average_dwell_time || 0,
          last_motion: entity.attributes.last_motion_time || null,
        },
        config: zoneConfig,
      };
    });

    this.renderZones(zoneStates);
  }

  /**
   * Render the card
   */
  render() {
    const layout = this._config?.layout || 'grid';
    
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

        .zones-container {
          display: ${layout === 'grid' ? 'grid' : 'flex'};
          ${layout === 'grid' ? 'grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));' : ''}
          ${layout === 'list' ? 'flex-direction: column;' : ''}
          ${layout === 'compact' ? 'flex-wrap: wrap;' : ''}
          gap: 12px;
        }

        .zone-item {
          background: var(--card-background-color);
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          padding: ${layout === 'compact' ? '8px' : '12px'};
          ${layout === 'compact' ? 'width: calc(25% - 9px);' : ''}
        }

        .zone-item.unavailable {
          opacity: 0.5;
        }

        .zone-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;
        }

        .zone-name {
          font-weight: 500;
          font-size: ${layout === 'compact' ? '12px' : '14px'};
          color: var(--primary-text-color);
        }

        .zone-status-badge {
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 10px;
          font-weight: 500;
          text-transform: uppercase;
        }

        .zone-status-badge.active {
          background: var(--success-color);
          color: white;
        }

        .zone-status-badge.inactive {
          background: var(--disabled-color);
          color: var(--secondary-text-color);
        }

        .zone-direction {
          display: flex;
          align-items: center;
          gap: 8px;
          margin: 8px 0;
        }

        .direction-icon {
          font-size: ${layout === 'compact' ? '20px' : '24px'};
        }

        .direction-label {
          font-size: ${layout === 'compact' ? '11px' : '13px'};
          color: var(--secondary-text-color);
        }

        .direction-value {
          font-size: ${layout === 'compact' ? '12px' : '14px'};
          font-weight: 500;
          color: var(--primary-text-color);
        }

        .zone-occupancy {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 6px 0;
          border-top: 1px solid var(--divider-color);
          margin-top: 8px;
        }

        .occupancy-label {
          font-size: ${layout === 'compact' ? '11px' : '12px'};
          color: var(--secondary-text-color);
        }

        .occupancy-value {
          font-size: ${layout === 'compact' ? '11px' : '12px'};
          font-weight: 500;
        }

        .occupancy-value.occupied {
          color: var(--success-color);
        }

        .occupancy-value.vacant {
          color: var(--secondary-text-color);
        }

        .zone-statistics {
          margin-top: 8px;
          padding-top: 8px;
          border-top: 1px solid var(--divider-color);
          display: ${layout === 'compact' ? 'none' : 'flex'};
          flex-direction: column;
          gap: 4px;
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

        .confidence-bar {
          height: 4px;
          background: var(--divider-color);
          border-radius: 2px;
          margin-top: 8px;
          overflow: hidden;
        }

        .confidence-fill {
          height: 100%;
          background: var(--primary-color);
          transition: width 0.3s ease;
        }

        .error-message {
          color: var(--error-color);
          font-size: 12px;
          padding: 8px;
        }

        .no-zones {
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
              <button class="layout-btn ${layout === 'grid' ? 'active' : ''}" data-layout="grid">Grid</button>
              <button class="layout-btn ${layout === 'list' ? 'active' : ''}" data-layout="list">List</button>
              <button class="layout-btn ${layout === 'compact' ? 'active' : ''}" data-layout="compact">Compact</button>
            </div>
          </div>
        ` : ''}
        
        <div class="zones-container"></div>
      </ha-card>
    `;

    // Add event listeners to layout toggle buttons
    if (this._config.show_header) {
      this.shadowRoot.querySelectorAll('.layout-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const newLayout = e.target.dataset.layout;
          this._config.layout = newLayout;
          this.render();
          this.updateZoneData();
        });
      });
    }

    // Initial data update
    this.updateZoneData();
  }

  /**
   * Render zones with current state
   */
  renderZones(zoneStates) {
    const container = this.shadowRoot.querySelector('.zones-container');
    if (!container) return;

    if (!zoneStates || zoneStates.length === 0) {
      container.innerHTML = '<div class="no-zones">No zones configured</div>';
      return;
    }

    container.innerHTML = zoneStates.map(zone => this.renderZoneItem(zone)).join('');
  }

  /**
   * Render a single zone item
   */
  renderZoneItem(zone) {
    if (!zone.available) {
      return `
        <div class="zone-item unavailable">
          <div class="zone-header">
            <span class="zone-name">${zone.zone_id}</span>
            <span class="zone-status-badge inactive">Unavailable</span>
          </div>
          <div class="error-message">${zone.error}</div>
        </div>
      `;
    }

    const config = zone.config || {};
    const showDirection = config.show_direction !== false;
    const showOccupancy = config.show_occupancy !== false;
    const showStatistics = config.show_statistics !== false;
    const isActive = zone.state === 'active' || zone.occupancy === 'occupied';

    return `
      <div class="zone-item">
        <div class="zone-header">
          <span class="zone-name">${zone.zone_id}</span>
          <span class="zone-status-badge ${isActive ? 'active' : 'inactive'}">
            ${isActive ? 'Active' : 'Inactive'}
          </span>
        </div>

        ${showDirection ? `
          <div class="zone-direction">
            <span class="direction-icon">${this.getDirectionIcon(zone.direction)}</span>
            <div>
              <div class="direction-label">Direction</div>
              <div class="direction-value">${this.formatDirection(zone.direction)}</div>
            </div>
          </div>
        ` : ''}

        ${showDirection ? `
          <div class="confidence-bar">
            <div class="confidence-fill" style="width: ${zone.confidence * 100}%"></div>
          </div>
        ` : ''}

        ${showOccupancy ? `
          <div class="zone-occupancy">
            <span class="occupancy-label">Occupancy</span>
            <span class="occupancy-value ${zone.occupancy === 'occupied' ? 'occupied' : 'vacant'}">
              ${this.formatOccupancy(zone.occupancy)}
            </span>
          </div>
        ` : ''}

        ${showStatistics ? `
          <div class="zone-statistics">
            <div class="stat-row">
              <span class="stat-label">Transitions</span>
              <span class="stat-value">${zone.statistics.transitions}</span>
            </div>
            <div class="stat-row">
              <span class="stat-label">Avg Dwell Time</span>
              <span class="stat-value">${this.formatDwellTime(zone.statistics.dwell_time)}</span>
            </div>
            ${zone.statistics.last_motion ? `
              <div class="stat-row">
                <span class="stat-label">Last Motion</span>
                <span class="stat-value">${this.formatLastMotion(zone.statistics.last_motion)}</span>
              </div>
            ` : ''}
          </div>
        ` : ''}
      </div>
    `;
  }

  /**
   * Get direction icon
   */
  getDirectionIcon(direction) {
    const icons = {
      'north': '⬆️',
      'south': '⬇️',
      'east': '➡️',
      'west': '⬅️',
      'northeast': '↗️',
      'northwest': '↖️',
      'southeast': '↘️',
      'southwest': '↙️',
      'entering': '📥',
      'exiting': '📤',
      'unknown': '❓',
    };
    return icons[direction?.toLowerCase()] || icons['unknown'];
  }

  /**
   * Format direction text
   */
  formatDirection(direction) {
    if (!direction || direction === 'unknown') return 'Unknown';
    return direction.charAt(0).toUpperCase() + direction.slice(1);
  }

  /**
   * Format occupancy text
   */
  formatOccupancy(occupancy) {
    if (!occupancy || occupancy === 'unknown') return 'Unknown';
    return occupancy.charAt(0).toUpperCase() + occupancy.slice(1);
  }

  /**
   * Format dwell time
   */
  formatDwellTime(seconds) {
    if (!seconds || seconds === 0) return '0s';
    
    if (seconds < 60) {
      return `${Math.round(seconds)}s`;
    } else if (seconds < 3600) {
      return `${Math.round(seconds / 60)}m`;
    } else {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.round((seconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    }
  }

  /**
   * Format last motion time
   */
  formatLastMotion(timestamp) {
    if (!timestamp) return 'Never';
    
    const now = new Date();
    const lastMotion = new Date(timestamp);
    const diffMs = now - lastMotion;
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
    return document.createElement('motiondirection-zone-status-card-editor');
  }

  /**
   * Get stub configuration for card picker
   */
  static getStubConfig() {
    return {
      zones: [
        {
          zone_id: 'living_room',
          show_direction: true,
          show_occupancy: true,
          show_statistics: true,
        },
      ],
      layout: 'grid',
      update_interval: 1000,
    };
  }
}

// Register custom element
customElements.define('motiondirection-zone-status', MotionDirectionZoneStatusCard);

// Register card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'motiondirection-zone-status',
  name: 'MotionDirection Zone Status',
  description: 'Display real-time status of motion zones',
  preview: true,
});

console.info(
  '%c MOTIONDIRECTION-ZONE-STATUS-CARD %c v1.0.0 ',
  'color: white; background: #039be5; font-weight: 700;',
  'color: #039be5; background: white; font-weight: 700;'
);
