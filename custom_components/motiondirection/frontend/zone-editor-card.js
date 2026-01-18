/**
 * Zone Editor Card
 * 
 * A custom Lovelace card for Home Assistant that provides a focused interface
 * for viewing and editing zone configurations in the MotionDirection integration.
 * This card complements the Floorplan Editor with zone-specific controls.
 * 
 * @version 1.0.0
 * @license MIT
 */

class ZoneEditorCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // Core state
    this._hass = null;
    this._config = null;
    
    // Editor state
    this._mode = 'view'; // 'view' | 'edit'
    this._selectedZone = null;
    this._editingDirection = null;
    
    // Zones data
    this._zones = [];
  }

  /**
   * Set the Home Assistant object
   */
  set hass(hass) {
    this._hass = hass;
    this._loadZones();
    this._updateCard();
  }

  /**
   * Set the card configuration
   */
  setConfig(config) {
    this._config = {
      floorplan_id: config.floorplan_id,
      title: config.title || 'Zone Configuration',
      mode: config.mode || 'view', // 'view' | 'edit'
      show_directions: config.show_directions !== false,
      show_labels: config.show_labels !== false,
      show_statistics: config.show_statistics !== false,
      color_scheme: config.color_scheme || 'rainbow', // 'rainbow' | 'monochrome' | 'custom'
      update_interval: config.update_interval || 2000,
      ...config
    };

    this._mode = this._config.mode;
    this._updateCard();
  }

  /**
   * Load zones from Home Assistant
   */
  _loadZones() {
    if (!this._hass || !this._config) {
      return;
    }

    // Load zones from floorplan entity or zone sensors
    this._zones = [];
    
    // Try loading from floorplan entity
    if (this._config.floorplan_id) {
      const floorplanEntity = `sensor.floorplan_${this._config.floorplan_id}`;
      const stateObj = this._hass.states[floorplanEntity];
      if (stateObj && stateObj.attributes && stateObj.attributes.zones) {
        this._zones = stateObj.attributes.zones;
      }
    }

    // Also load individual zone sensors for real-time status
    Object.keys(this._hass.states).forEach(entityId => {
      if (entityId.startsWith('sensor.zone_') && entityId.endsWith('_direction')) {
        const zoneId = entityId.replace('sensor.zone_', '').replace('_direction', '');
        const zoneData = this._hass.states[entityId];
        
        // Find corresponding zone in floorplan data
        const existingZone = this._zones.find(z => z.id === zoneId);
        if (existingZone && zoneData) {
          existingZone.current_direction = zoneData.state;
          existingZone.confidence = zoneData.attributes.confidence;
          existingZone.last_trigger = zoneData.attributes.last_trigger;
        }
      }
    });
  }

  /**
   * Update the card content
   */
  _updateCard() {
    if (!this._config) {
      return;
    }

    this.shadowRoot.innerHTML = this._renderCard();
    this._attachEventListeners();
  }

  /**
   * Render the complete card
   */
  _renderCard() {
    return `
      <style>${this._getStyles()}</style>
      <ha-card>
        ${this._renderHeader()}
        <div class="card-content">
          ${this._zones.length === 0 ? this._renderEmptyState() : this._renderZoneList()}
        </div>
        ${this._selectedZone ? this._renderZoneDetails() : ''}
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
          <ha-icon icon="mdi:map-marker-multiple"></ha-icon>
          ${this._config.title}
        </div>
        ${this._mode === 'edit' ? `
          <button class="header-btn" data-action="add-zone">
            <ha-icon icon="mdi:plus"></ha-icon>
            Add Zone
          </button>
        ` : ''}
      </div>
    `;
  }

  /**
   * Render empty state
   */
  _renderEmptyState() {
    return `
      <div class="empty-state">
        <ha-icon icon="mdi:map-marker-off"></ha-icon>
        <p>No zones configured</p>
        <p class="hint">Create zones using the Floorplan Editor or config flow</p>
      </div>
    `;
  }

  /**
   * Render list of zones
   */
  _renderZoneList() {
    return `
      <div class="zone-list">
        ${this._zones.map((zone, index) => this._renderZoneCard(zone, index)).join('')}
      </div>
    `;
  }

  /**
   * Render individual zone card
   */
  _renderZoneCard(zone, index) {
    const isSelected = this._selectedZone?.id === zone.id;
    const color = this._getZoneColor(index);
    const isActive = zone.current_direction && zone.current_direction !== 'none';

    return `
      <div class="zone-card ${isSelected ? 'selected' : ''} ${isActive ? 'active' : ''}"
           data-zone-id="${zone.id}"
           style="border-left-color: ${color}">
        
        <div class="zone-card-header" data-action="select-zone">
          <div class="zone-name">
            <ha-icon icon="mdi:map-marker" style="color: ${color}"></ha-icon>
            <span>${zone.name}</span>
          </div>
          <div class="zone-status">
            ${isActive ? `
              <span class="status-badge active">
                <ha-icon icon="mdi:motion"></ha-icon>
                Active
              </span>
            ` : `
              <span class="status-badge">Idle</span>
            `}
          </div>
        </div>

        ${this._config.show_directions ? `
          <div class="zone-directions">
            <div class="directions-header">
              <span class="label">Configured Directions:</span>
              ${this._mode === 'edit' ? `
                <button class="icon-btn" data-action="add-direction" data-zone-id="${zone.id}">
                  <ha-icon icon="mdi:plus-circle-outline"></ha-icon>
                </button>
              ` : ''}
            </div>
            <div class="direction-list">
              ${zone.known_directions && zone.known_directions.length > 0 ? 
                zone.known_directions.map(dir => this._renderDirection(zone.id, dir)).join('') :
                '<span class="no-data">No directions configured</span>'
              }
            </div>
          </div>
        ` : ''}

        ${zone.current_direction ? `
          <div class="zone-current">
            <div class="current-direction">
              <ha-icon icon="mdi:arrow-right-bold"></ha-icon>
              <span class="label">Current:</span>
              <span class="value">${this._formatDirection(zone.current_direction)}</span>
              ${zone.confidence ? `
                <span class="confidence ${this._getConfidenceClass(zone.confidence)}">
                  ${Math.round(zone.confidence * 100)}%
                </span>
              ` : ''}
            </div>
          </div>
        ` : ''}

        ${this._config.show_statistics && zone.statistics ? `
          <div class="zone-stats">
            <div class="stat-item">
              <span class="stat-label">Transitions:</span>
              <span class="stat-value">${zone.statistics.transition_count || 0}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Avg Dwell:</span>
              <span class="stat-value">${this._formatDuration(zone.statistics.avg_dwell_time)}</span>
            </div>
          </div>
        ` : ''}

        ${this._mode === 'edit' ? `
          <div class="zone-actions">
            <button class="action-btn" data-action="edit-zone" data-zone-id="${zone.id}">
              <ha-icon icon="mdi:pencil"></ha-icon>
              Edit
            </button>
            <button class="action-btn" data-action="calibrate-zone" data-zone-id="${zone.id}">
              <ha-icon icon="mdi:tune"></ha-icon>
              Calibrate
            </button>
            <button class="action-btn danger" data-action="delete-zone" data-zone-id="${zone.id}">
              <ha-icon icon="mdi:delete"></ha-icon>
              Delete
            </button>
          </div>
        ` : ''}
      </div>
    `;
  }

  /**
   * Render direction item
   */
  _renderDirection(zoneId, direction) {
    const angle = this._vectorToAngle(direction.vector);
    const arrowRotation = angle - 90; // Adjust for icon orientation

    return `
      <div class="direction-item">
        <div class="direction-info">
          <div class="direction-arrow" style="transform: rotate(${arrowRotation}deg)">
            <ha-icon icon="mdi:arrow-up-bold"></ha-icon>
          </div>
          <div class="direction-details">
            <span class="direction-name">${direction.name}</span>
            ${direction.aliases && direction.aliases.length > 0 ? `
              <span class="direction-aliases">(${direction.aliases.join(', ')})</span>
            ` : ''}
          </div>
        </div>
        ${this._mode === 'edit' ? `
          <div class="direction-actions">
            <button class="icon-btn" data-action="edit-direction" 
                    data-zone-id="${zoneId}" data-direction="${direction.name}">
              <ha-icon icon="mdi:pencil"></ha-icon>
            </button>
            <button class="icon-btn danger" data-action="delete-direction" 
                    data-zone-id="${zoneId}" data-direction="${direction.name}">
              <ha-icon icon="mdi:delete"></ha-icon>
            </button>
          </div>
        ` : ''}
      </div>
    `;
  }

  /**
   * Render zone details panel (when selected)
   */
  _renderZoneDetails() {
    const zone = this._selectedZone;
    if (!zone) return '';

    return `
      <div class="details-panel">
        <div class="details-header">
          <h3>${zone.name}</h3>
          <button class="icon-btn" data-action="close-details">
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        </div>
        
        <div class="details-content">
          <div class="detail-section">
            <h4>Zone Information</h4>
            <div class="detail-row">
              <span class="detail-label">ID:</span>
              <span class="detail-value">${zone.id}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Points:</span>
              <span class="detail-value">${zone.polygon ? zone.polygon.length : 0}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Center:</span>
              <span class="detail-value">(${zone.center ? zone.center.join(', ') : 'N/A'})</span>
            </div>
          </div>

          <div class="detail-section">
            <h4>Detection Settings</h4>
            <div class="detail-row">
              <span class="detail-label">Min Dwell Time:</span>
              <span class="detail-value">${zone.min_dwell_time || 500}ms</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Max Transit Time:</span>
              <span class="detail-value">${zone.max_transit_time || 10000}ms</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Sensitivity:</span>
              <span class="detail-value">${zone.sensitivity || 0.7}</span>
            </div>
          </div>

          ${zone.statistics ? `
            <div class="detail-section">
              <h4>Statistics</h4>
              <div class="detail-row">
                <span class="detail-label">Total Transitions:</span>
                <span class="detail-value">${zone.statistics.transition_count || 0}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Average Dwell Time:</span>
                <span class="detail-value">${this._formatDuration(zone.statistics.avg_dwell_time)}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Last Trigger:</span>
                <span class="detail-value">${zone.last_trigger ? new Date(zone.last_trigger).toLocaleString() : 'Never'}</span>
              </div>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }

  /**
   * Attach event listeners
   */
  _attachEventListeners() {
    const root = this.shadowRoot;

    // Action button clicks
    root.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = e.currentTarget.dataset.action;
        const zoneId = e.currentTarget.dataset.zoneId;
        const direction = e.currentTarget.dataset.direction;
        this._handleAction(action, zoneId, direction);
      });
    });
  }

  /**
   * Handle action
   */
  _handleAction(action, zoneId, direction) {
    switch (action) {
      case 'add-zone':
        this._showNotification('Use Floorplan Editor to add new zones', 'info');
        break;
      case 'select-zone':
        this._selectedZone = this._zones.find(z => z.id === zoneId);
        this._updateCard();
        break;
      case 'close-details':
        this._selectedZone = null;
        this._updateCard();
        break;
      case 'edit-zone':
        this._editZone(zoneId);
        break;
      case 'calibrate-zone':
        this._calibrateZone(zoneId);
        break;
      case 'delete-zone':
        this._deleteZone(zoneId);
        break;
      case 'add-direction':
        this._addDirection(zoneId);
        break;
      case 'edit-direction':
        this._editDirection(zoneId, direction);
        break;
      case 'delete-direction':
        this._deleteDirection(zoneId, direction);
        break;
    }
  }

  /**
   * Edit zone
   */
  async _editZone(zoneId) {
    const zone = this._zones.find(z => z.id === zoneId);
    if (!zone) return;

    // For now, redirect to Floorplan Editor
    this._showNotification('Use Floorplan Editor to edit zone geometry', 'info');
  }

  /**
   * Calibrate zone
   */
  async _calibrateZone(zoneId) {
    try {
      await this._hass.callService('motiondirection', 'calibrate_zone', {
        zone_id: zoneId
      });
      this._showNotification('Zone calibration started', 'success');
    } catch (error) {
      this._showNotification('Failed to calibrate zone: ' + error.message, 'error');
    }
  }

  /**
   * Delete zone
   */
  async _deleteZone(zoneId) {
    const confirmed = confirm('Are you sure you want to delete this zone?');
    if (!confirmed) return;

    try {
      await this._hass.callService('motiondirection', 'remove_zone', {
        zone_id: zoneId
      });
      this._showNotification('Zone deleted successfully', 'success');
      this._loadZones();
    } catch (error) {
      this._showNotification('Failed to delete zone: ' + error.message, 'error');
    }
  }

  /**
   * Add direction to zone
   */
  async _addDirection(zoneId) {
    const directionName = prompt('Enter direction name (e.g., "north", "entrance", "exit"):');
    if (!directionName) return;

    const vectorX = parseFloat(prompt('Enter X component of direction vector (-1 to 1):') || '0');
    const vectorY = parseFloat(prompt('Enter Y component of direction vector (-1 to 1):') || '0');

    // Normalize vector
    const magnitude = Math.sqrt(vectorX * vectorX + vectorY * vectorY);
    const normalizedVector = magnitude > 0 ? 
      [vectorX / magnitude, vectorY / magnitude] : 
      [1, 0];

    try {
      await this._hass.callService('motiondirection', 'update_zone_direction', {
        zone_id: zoneId,
        direction_name: directionName,
        vector: normalizedVector
      });
      this._showNotification('Direction added successfully', 'success');
      this._loadZones();
    } catch (error) {
      this._showNotification('Failed to add direction: ' + error.message, 'error');
    }
  }

  /**
   * Edit direction
   */
  async _editDirection(zoneId, directionName) {
    const zone = this._zones.find(z => z.id === zoneId);
    if (!zone) return;

    const direction = zone.known_directions.find(d => d.name === directionName);
    if (!direction) return;

    const newName = prompt('Enter new direction name:', direction.name);
    if (!newName || newName === direction.name) return;

    try {
      await this._hass.callService('motiondirection', 'update_zone_direction', {
        zone_id: zoneId,
        direction_name: newName,
        vector: direction.vector,
        old_direction_name: directionName
      });
      this._showNotification('Direction updated successfully', 'success');
      this._loadZones();
    } catch (error) {
      this._showNotification('Failed to update direction: ' + error.message, 'error');
    }
  }

  /**
   * Delete direction
   */
  async _deleteDirection(zoneId, directionName) {
    const confirmed = confirm(`Delete direction "${directionName}"?`);
    if (!confirmed) return;

    try {
      await this._hass.callService('motiondirection', 'remove_zone_direction', {
        zone_id: zoneId,
        direction_name: directionName
      });
      this._showNotification('Direction deleted successfully', 'success');
      this._loadZones();
    } catch (error) {
      this._showNotification('Failed to delete direction: ' + error.message, 'error');
    }
  }

  /**
   * Get zone color based on index and color scheme
   */
  _getZoneColor(index) {
    switch (this._config.color_scheme) {
      case 'rainbow':
        const hue = (index * 360 / Math.max(this._zones.length, 1)) % 360;
        return `hsl(${hue}, 70%, 50%)`;
      case 'monochrome':
        return 'var(--primary-color)';
      case 'custom':
        return this._config.custom_colors?.[index] || 'var(--primary-color)';
      default:
        return 'var(--primary-color)';
    }
  }

  /**
   * Convert vector to angle (degrees)
   */
  _vectorToAngle(vector) {
    const [x, y] = vector;
    return Math.atan2(y, x) * 180 / Math.PI;
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
   * Format duration (milliseconds to readable format)
   */
  _formatDuration(ms) {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}min`;
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
   * Show notification
   */
  _showNotification(message, type = 'info') {
    if (this._hass) {
      this._hass.callService('persistent_notification', 'create', {
        message: message,
        title: 'Zone Editor',
        notification_id: `zone_editor_${Date.now()}`
      });
    }
  }

  /**
   * Get card size for masonry layout
   */
  getCardSize() {
    return Math.max(3, this._zones.length * 2);
  }

  /**
   * Get grid options for sections layout
   */
  getGridOptions() {
    return {
      rows: Math.max(4, Math.ceil(this._zones.length / 2) * 2),
      columns: 6,
      min_rows: 3,
      max_rows: 12,
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
      
      .header-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        background: var(--primary-color);
        color: var(--text-primary-color);
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 500;
      }
      
      .header-btn:hover {
        opacity: 0.9;
      }
      
      .card-content {
        padding: 16px;
        overflow-y: auto;
        max-height: 600px;
      }
      
      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 48px 16px;
        color: var(--secondary-text-color);
        text-align: center;
      }
      
      .empty-state ha-icon {
        width: 48px;
        height: 48px;
        opacity: 0.5;
      }
      
      .hint {
        font-size: 0.875rem;
        color: var(--disabled-text-color);
      }
      
      .zone-list {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
      
      .zone-card {
        background: var(--card-background-color);
        border: 1px solid var(--divider-color);
        border-left-width: 4px;
        border-radius: 8px;
        padding: 16px;
        transition: all 0.2s;
      }
      
      .zone-card:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      
      .zone-card.selected {
        border-color: var(--primary-color);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }
      
      .zone-card.active {
        background: var(--secondary-background-color);
      }
      
      .zone-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        cursor: pointer;
      }
      
      .zone-name {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.125rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      
      .zone-status {
        display: flex;
        gap: 8px;
      }
      
      .status-badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        background: var(--secondary-background-color);
        color: var(--secondary-text-color);
      }
      
      .status-badge.active {
        background: var(--success-color);
        color: white;
      }
      
      .status-badge ha-icon {
        width: 12px;
        height: 12px;
        margin-right: 4px;
      }
      
      .zone-directions {
        margin-bottom: 12px;
        padding: 12px;
        background: var(--secondary-background-color);
        border-radius: 6px;
      }
      
      .directions-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
      }
      
      .label {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--secondary-text-color);
      }
      
      .direction-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      
      .direction-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px;
        background: var(--card-background-color);
        border-radius: 4px;
      }
      
      .direction-info {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      
      .direction-arrow {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--primary-color);
        color: var(--text-primary-color);
        border-radius: 50%;
      }
      
      .direction-arrow ha-icon {
        width: 20px;
        height: 20px;
      }
      
      .direction-details {
        display: flex;
        flex-direction: column;
      }
      
      .direction-name {
        font-size: 0.9375rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      
      .direction-aliases {
        font-size: 0.8125rem;
        color: var(--secondary-text-color);
      }
      
      .direction-actions {
        display: flex;
        gap: 4px;
      }
      
      .icon-btn {
        background: transparent;
        border: none;
        padding: 6px;
        cursor: pointer;
        border-radius: 4px;
        color: var(--secondary-text-color);
        transition: all 0.2s;
      }
      
      .icon-btn:hover {
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
      }
      
      .icon-btn.danger:hover {
        background: var(--error-color);
        color: white;
      }
      
      .icon-btn ha-icon {
        width: 18px;
        height: 18px;
        display: block;
      }
      
      .no-data {
        font-size: 0.875rem;
        color: var(--disabled-text-color);
        font-style: italic;
      }
      
      .zone-current {
        margin-bottom: 12px;
        padding: 12px;
        background: var(--info-color);
        color: white;
        border-radius: 6px;
      }
      
      .current-direction {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.9375rem;
      }
      
      .current-direction ha-icon {
        width: 18px;
        height: 18px;
      }
      
      .current-direction .value {
        font-weight: 600;
      }
      
      .confidence {
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.3);
      }
      
      .confidence.high {
        background: rgba(76, 175, 80, 0.3);
      }
      
      .confidence.medium {
        background: rgba(255, 152, 0, 0.3);
      }
      
      .confidence.low {
        background: rgba(244, 67, 54, 0.3);
      }
      
      .zone-stats {
        display: flex;
        gap: 16px;
        padding: 8px 0;
        border-top: 1px solid var(--divider-color);
        margin-top: 8px;
      }
      
      .stat-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }
      
      .stat-label {
        font-size: 0.75rem;
        color: var(--secondary-text-color);
        text-transform: uppercase;
      }
      
      .stat-value {
        font-size: 1rem;
        font-weight: 600;
        color: var(--primary-text-color);
      }
      
      .zone-actions {
        display: flex;
        gap: 8px;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid var(--divider-color);
      }
      
      .action-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 8px;
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.8125rem;
        font-weight: 500;
        transition: all 0.2s;
      }
      
      .action-btn:hover {
        background: var(--primary-color);
        color: var(--text-primary-color);
      }
      
      .action-btn.danger:hover {
        background: var(--error-color);
        color: white;
      }
      
      .action-btn ha-icon {
        width: 16px;
        height: 16px;
      }
      
      .details-panel {
        position: fixed;
        right: 0;
        top: 0;
        bottom: 0;
        width: 400px;
        max-width: 90vw;
        background: var(--card-background-color);
        box-shadow: -2px 0 16px rgba(0, 0, 0, 0.2);
        display: flex;
        flex-direction: column;
        z-index: 10;
      }
      
      .details-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px;
        border-bottom: 1px solid var(--divider-color);
      }
      
      .details-header h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }
      
      .details-content {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
      }
      
      .detail-section {
        margin-bottom: 24px;
      }
      
      .detail-section h4 {
        margin: 0 0 12px 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--primary-text-color);
      }
      
      .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid var(--divider-color);
      }
      
      .detail-row:last-child {
        border-bottom: none;
      }
      
      .detail-label {
        font-size: 0.875rem;
        color: var(--secondary-text-color);
      }
      
      .detail-value {
        font-size: 0.875rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }
    `;
  }

  /**
   * Get editor configuration element
   * Returns a custom element for UI configuration
   */
  static getConfigElement() {
    return document.createElement('motiondirection-zone-editor-card-editor');
  }

  /**
   * Get stub configuration for card picker
   * Provides default configuration when adding card
   */
  static getStubConfig() {
    return {
      floorplan_id: 'default',
      zone_id: '',
      show_existing_zones: true,
      enable_zone_editing: true,
      enable_direction_config: true,
      width: 800,
      height: 600,
    };
  }
}

// Register the custom card
customElements.define('motiondirection-zone-editor', ZoneEditorCard);

// Register with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'motiondirection-zone-editor',
  name: 'MotionDirection Zone Editor',
  description: 'Focused zone configuration and direction editor for MotionDirection integration',
  preview: true,
  documentationURL: 'https://github.com/tamaygz/ha-motiondirection#zone-editor-card',
});

console.info(
  '%c ZONE-EDITOR-CARD %c 1.0.0 ',
  'color: white; background: #ff9800; font-weight: 700;',
  'color: #ff9800; background: white; font-weight: 700;'
);
