/**
 * MotionDirection Cue Editor Card
 * 
 * Interactive editor for secondary cue configuration on floorplans.
 * Allows placement, configuration, and visualization of secondary cues.
 * 
 * Features:
 * - Entity selector for available cues
 * - Drag-and-drop placement on floorplan
 * - Cue type selection
 * - Directional hints configuration
 * - Correlation visualization
 * - State visualization with animations
 * - Multiple visualization styles
 * - Service integration
 * 
 * @example
 * type: custom:motiondirection-cue-editor
 * floorplan_id: ground_floor
 * mode: "edit"
 * show_cues: true
 * show_correlations: true
 * show_confidence: true
 * cue_visualization:
 *   style: "icons"
 *   show_state: true
 *   show_direction_hints: true
 *   animation: "pulse"
 */

class MotionDirectionCueEditorCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = null;
    this._hass = null;
    this._selectedCue = null;
    this._draggedCue = null;
    this._availableEntities = [];
    this._cues = [];
    this._sensors = [];
    this._correlations = [];
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
      mode: config.mode || 'view',
      show_cues: config.show_cues !== false,
      show_correlations: config.show_correlations !== false,
      show_confidence: config.show_confidence !== false,
      cue_visualization: {
        style: config.cue_visualization?.style || 'icons',
        show_state: config.cue_visualization?.show_state !== false,
        show_direction_hints: config.cue_visualization?.show_direction_hints !== false,
        animation: config.cue_visualization?.animation || 'pulse',
      },
      title: config.title || 'Cue Editor',
    };

    this.render();
  }

  /**
   * Set Home Assistant instance
   */
  set hass(hass) {
    this._hass = hass;
    this.loadFloorplanData();
    this.loadAvailableEntities();
    this.updateCueStates();
  }

  /**
   * Get card size for layout
   */
  getCardSize() {
    return 8;
  }

  /**
   * Load floorplan data
   */
  loadFloorplanData() {
    if (!this._hass || !this._config) return;

    const floorplanEntity = this._hass.states[`sensor.motiondirection_floorplan_${this._config.floorplan_id}`];
    
    if (floorplanEntity?.attributes) {
      this._sensors = floorplanEntity.attributes.sensors || [];
      this._cues = floorplanEntity.attributes.cues || [];
      this.renderFloorplan();
    }
  }

  /**
   * Load available entities
   */
  loadAvailableEntities() {
    if (!this._hass) return;

    // Get all entities that could be cues
    this._availableEntities = Object.keys(this._hass.states)
      .filter(entityId => {
        const domain = entityId.split('.')[0];
        return ['binary_sensor', 'switch', 'light', 'lock', 'cover', 'climate', 'media_player'].includes(domain);
      })
      .map(entityId => {
        const entity = this._hass.states[entityId];
        return {
          entity_id: entityId,
          name: entity.attributes.friendly_name || entityId,
          domain: entityId.split('.')[0],
          state: entity.state,
        };
      })
      .sort((a, b) => a.name.localeCompare(b.name));

    this.updateEntityList();
  }

  /**
   * Update cue states
   */
  updateCueStates() {
    if (!this._hass || !this._cues) return;

    this._cues.forEach(cue => {
      const entity = this._hass.states[cue.entity_id];
      if (entity) {
        cue.current_state = entity.state;
        cue.attributes = entity.attributes;
      }

      // Load correlation data
      const cueEntity = this._hass.states[`sensor.motiondirection_cue_${cue.id}`];
      if (cueEntity?.attributes) {
        cue.correlations = cueEntity.attributes.correlations || [];
        cue.confidence = cueEntity.attributes.average_confidence || 0;
      }
    });

    this.renderFloorplan();
  }

  /**
   * Render the card
   */
  render() {
    const mode = this._config?.mode || 'view';
    
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

        .mode-selector {
          display: flex;
          gap: 4px;
        }

        .mode-btn {
          padding: 6px 12px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
          cursor: pointer;
          border-radius: 4px;
          font-size: 12px;
        }

        .mode-btn:hover {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .mode-btn.active {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .content {
          display: flex;
          flex: 1;
          overflow: hidden;
        }

        .sidebar {
          width: 280px;
          border-right: 1px solid var(--divider-color);
          overflow-y: auto;
          background: var(--card-background-color);
        }

        .sidebar-section {
          padding: 16px;
          border-bottom: 1px solid var(--divider-color);
        }

        .sidebar-title {
          font-size: 14px;
          font-weight: 500;
          margin-bottom: 12px;
          color: var(--primary-text-color);
        }

        .entity-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .entity-item {
          padding: 8px 12px;
          background: var(--primary-background-color);
          border: 1px solid var(--divider-color);
          border-radius: 6px;
          cursor: grab;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: all 0.2s;
        }

        .entity-item:hover {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .entity-item.dragging {
          opacity: 0.5;
          cursor: grabbing;
        }

        .entity-icon {
          font-size: 16px;
        }

        .entity-name {
          flex: 1;
          font-size: 13px;
        }

        .entity-badge {
          padding: 2px 6px;
          background: var(--divider-color);
          border-radius: 3px;
          font-size: 10px;
        }

        .cue-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .cue-list-item {
          padding: 8px 12px;
          background: var(--primary-background-color);
          border: 1px solid var(--divider-color);
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .cue-list-item:hover, .cue-list-item.selected {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .cue-list-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 4px;
        }

        .cue-name {
          font-size: 13px;
          font-weight: 500;
        }

        .cue-actions {
          display: flex;
          gap: 4px;
        }

        .cue-action-btn {
          padding: 2px 6px;
          border: none;
          background: transparent;
          cursor: pointer;
          font-size: 12px;
          color: var(--primary-text-color);
        }

        .cue-action-btn:hover {
          color: var(--error-color);
        }

        .cue-info {
          font-size: 11px;
          color: var(--secondary-text-color);
        }

        .floorplan-container {
          flex: 1;
          position: relative;
          background: var(--primary-background-color);
          overflow: hidden;
        }

        svg {
          width: 100%;
          height: 100%;
        }

        .cue-marker {
          cursor: pointer;
          transition: all 0.2s;
        }

        .cue-marker:hover {
          transform: scale(1.2);
        }

        .cue-marker.selected {
          filter: drop-shadow(0 0 6px var(--primary-color));
        }

        .cue-marker.pulse {
          animation: pulse 2s infinite;
        }

        .cue-marker.glow {
          animation: glow 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @keyframes glow {
          0%, 100% { filter: drop-shadow(0 0 0 transparent); }
          50% { filter: drop-shadow(0 0 8px var(--primary-color)); }
        }

        .correlation-line {
          stroke: var(--primary-color);
          stroke-width: 1;
          stroke-dasharray: 4 2;
          opacity: 0.5;
        }

        .sensor-marker {
          fill: var(--success-color);
          opacity: 0.3;
        }

        .details-panel {
          width: 300px;
          border-left: 1px solid var(--divider-color);
          overflow-y: auto;
          background: var(--card-background-color);
          padding: 16px;
        }

        .details-title {
          font-size: 16px;
          font-weight: 500;
          margin-bottom: 16px;
          color: var(--primary-text-color);
        }

        .form-group {
          margin-bottom: 16px;
        }

        .form-label {
          display: block;
          font-size: 13px;
          font-weight: 500;
          margin-bottom: 6px;
          color: var(--primary-text-color);
        }

        .form-input, .form-select {
          width: 100%;
          padding: 8px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          background: var(--primary-background-color);
          color: var(--primary-text-color);
          font-size: 13px;
        }

        .direction-hints {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .direction-hint-item {
          display: flex;
          gap: 8px;
          align-items: center;
        }

        .hint-input {
          flex: 1;
          padding: 6px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          background: var(--primary-background-color);
          color: var(--primary-text-color);
          font-size: 12px;
        }

        .hint-remove-btn {
          padding: 4px 8px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--error-color);
          cursor: pointer;
          border-radius: 4px;
          font-size: 11px;
        }

        .add-hint-btn {
          padding: 6px 12px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
          cursor: pointer;
          border-radius: 4px;
          font-size: 12px;
          width: 100%;
        }

        .add-hint-btn:hover {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .correlation-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .correlation-item {
          padding: 8px;
          background: var(--primary-background-color);
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          font-size: 12px;
        }

        .correlation-sensor {
          font-weight: 500;
          color: var(--primary-text-color);
        }

        .correlation-confidence {
          color: var(--secondary-text-color);
          margin-top: 4px;
        }

        .save-btn {
          width: 100%;
          padding: 10px;
          border: none;
          background: var(--primary-color);
          color: var(--text-primary-color);
          cursor: pointer;
          border-radius: 4px;
          font-size: 14px;
          font-weight: 500;
          margin-top: 16px;
        }

        .save-btn:hover {
          opacity: 0.9;
        }

        .toolbar {
          display: flex;
          gap: 8px;
          padding: 12px 16px;
          background: var(--card-background-color);
          border-top: 1px solid var(--divider-color);
        }

        .toolbar-btn {
          padding: 6px 12px;
          border: 1px solid var(--divider-color);
          background: var(--card-background-color);
          color: var(--primary-text-color);
          cursor: pointer;
          border-radius: 4px;
          font-size: 12px;
        }

        .toolbar-btn:hover {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .toolbar-btn.active {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border-color: var(--primary-color);
        }

        .no-selection {
          text-align: center;
          color: var(--secondary-text-color);
          padding: 32px;
          font-size: 14px;
        }
      </style>

      <ha-card>
        <div class="card-header">
          <h2 class="card-title">${this._config.title}</h2>
          <div class="mode-selector">
            <button class="mode-btn ${mode === 'view' ? 'active' : ''}" data-mode="view">View</button>
            <button class="mode-btn ${mode === 'edit' ? 'active' : ''}" data-mode="edit">Edit</button>
            <button class="mode-btn ${mode === 'create' ? 'active' : ''}" data-mode="create">Create</button>
          </div>
        </div>

        <div class="content">
          ${mode !== 'view' ? `
            <div class="sidebar">
              ${mode === 'create' ? `
                <div class="sidebar-section">
                  <div class="sidebar-title">Available Entities</div>
                  <div class="entity-list" id="entityList"></div>
                </div>
              ` : ''}
              
              <div class="sidebar-section">
                <div class="sidebar-title">Configured Cues</div>
                <div class="cue-list" id="cueList"></div>
              </div>
            </div>
          ` : ''}

          <div class="floorplan-container" id="floorplanContainer">
            <svg id="floorplanSvg" viewBox="0 0 1000 1000"></svg>
          </div>

          ${mode !== 'view' && this._selectedCue ? `
            <div class="details-panel" id="detailsPanel"></div>
          ` : ''}
        </div>

        ${mode !== 'view' ? `
          <div class="toolbar">
            <button class="toolbar-btn ${this._config.show_correlations ? 'active' : ''}" id="toggleCorrelations">
              Correlations
            </button>
            <button class="toolbar-btn ${this._config.show_confidence ? 'active' : ''}" id="toggleConfidence">
              Confidence
            </button>
            <button class="toolbar-btn" id="saveAll">Save All</button>
          </div>
        ` : ''}
      </ha-card>
    `;

    this.setupEventListeners();
    this.loadFloorplanData();
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    const modeButtons = this.shadowRoot.querySelectorAll('.mode-btn');
    modeButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        this._config.mode = e.target.dataset.mode;
        this._selectedCue = null;
        this.render();
      });
    });

    const floorplanContainer = this.shadowRoot.getElementById('floorplanContainer');
    if (floorplanContainer && this._config.mode !== 'view') {
      floorplanContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
      });

      floorplanContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        this.handleDrop(e);
      });
    }

    const toggleCorrelations = this.shadowRoot.getElementById('toggleCorrelations');
    if (toggleCorrelations) {
      toggleCorrelations.addEventListener('click', () => {
        this._config.show_correlations = !this._config.show_correlations;
        toggleCorrelations.classList.toggle('active');
        this.renderFloorplan();
      });
    }

    const toggleConfidence = this.shadowRoot.getElementById('toggleConfidence');
    if (toggleConfidence) {
      toggleConfidence.addEventListener('click', () => {
        this._config.show_confidence = !this._config.show_confidence;
        toggleConfidence.classList.toggle('active');
        this.renderFloorplan();
      });
    }

    const saveAll = this.shadowRoot.getElementById('saveAll');
    if (saveAll) {
      saveAll.addEventListener('click', () => {
        this.saveAllCues();
      });
    }
  }

  /**
   * Update entity list
   */
  updateEntityList() {
    const entityList = this.shadowRoot.getElementById('entityList');
    if (!entityList || this._config.mode !== 'create') return;

    entityList.innerHTML = this._availableEntities
      .filter(entity => !this._cues.some(cue => cue.entity_id === entity.entity_id))
      .map(entity => `
        <div class="entity-item" draggable="true" data-entity="${entity.entity_id}">
          <span class="entity-icon">${this.getEntityIcon(entity.domain)}</span>
          <span class="entity-name">${entity.name}</span>
          <span class="entity-badge">${entity.domain}</span>
        </div>
      `).join('');

    // Add drag listeners
    entityList.querySelectorAll('.entity-item').forEach(item => {
      item.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', e.target.dataset.entity);
        e.target.classList.add('dragging');
      });

      item.addEventListener('dragend', (e) => {
        e.target.classList.remove('dragging');
      });
    });
  }

  /**
   * Update cue list
   */
  updateCueList() {
    const cueList = this.shadowRoot.getElementById('cueList');
    if (!cueList) return;

    cueList.innerHTML = this._cues.map(cue => `
      <div class="cue-list-item ${this._selectedCue?.id === cue.id ? 'selected' : ''}" data-cue-id="${cue.id}">
        <div class="cue-list-header">
          <span class="cue-name">${cue.name || cue.entity_id}</span>
          <div class="cue-actions">
            ${this._config.mode === 'edit' ? `<button class="cue-action-btn" data-action="delete" data-cue-id="${cue.id}">🗑️</button>` : ''}
          </div>
        </div>
        <div class="cue-info">
          Type: ${cue.cue_type || 'unknown'} | State: ${cue.current_state || 'unknown'}
        </div>
      </div>
    `).join('');

    // Add click listeners
    cueList.querySelectorAll('.cue-list-item').forEach(item => {
      item.addEventListener('click', (e) => {
        if (!e.target.classList.contains('cue-action-btn')) {
          const cueId = item.dataset.cueId;
          this.selectCue(cueId);
        }
      });
    });

    // Add delete listeners
    cueList.querySelectorAll('[data-action="delete"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const cueId = btn.dataset.cueId;
        this.deleteCue(cueId);
      });
    });
  }

  /**
   * Handle drop on floorplan
   */
  handleDrop(e) {
    const entityId = e.dataTransfer.getData('text/plain');
    if (!entityId) return;

    const svg = this.shadowRoot.getElementById('floorplanSvg');
    const rect = svg.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    this.addCue(entityId, x, y);
  }

  /**
   * Add cue
   */
  addCue(entityId, x, y) {
    const entity = this._hass.states[entityId];
    if (!entity) return;

    const cue = {
      id: `cue_${Date.now()}`,
      entity_id: entityId,
      name: entity.attributes.friendly_name || entityId,
      cue_type: this.inferCueType(entityId),
      position: { x, y },
      directional_hints: [],
      current_state: entity.state,
      attributes: entity.attributes,
    };

    this._cues.push(cue);
    this.updateEntityList();
    this.updateCueList();
    this.renderFloorplan();
    this.selectCue(cue.id);
  }

  /**
   * Select cue
   */
  selectCue(cueId) {
    this._selectedCue = this._cues.find(cue => cue.id === cueId);
    this.updateCueList();
    this.renderFloorplan();
    this.renderDetailsPanel();
  }

  /**
   * Delete cue
   */
  async deleteCue(cueId) {
    if (!confirm('Delete this cue?')) return;

    this._cues = this._cues.filter(cue => cue.id !== cueId);
    if (this._selectedCue?.id === cueId) {
      this._selectedCue = null;
    }

    this.updateEntityList();
    this.updateCueList();
    this.renderFloorplan();
    this.renderDetailsPanel();

    // Call delete service
    await this.callService('delete_cue', { cue_id: cueId });
  }

  /**
   * Render details panel
   */
  renderDetailsPanel() {
    const detailsPanel = this.shadowRoot.getElementById('detailsPanel');
    if (!detailsPanel) return;

    if (!this._selectedCue) {
      detailsPanel.innerHTML = '<div class="no-selection">Select a cue to edit</div>';
      return;
    }

    const cue = this._selectedCue;

    detailsPanel.innerHTML = `
      <div class="details-title">Edit Cue</div>
      
      <div class="form-group">
        <label class="form-label">Name</label>
        <input type="text" class="form-input" id="cueName" value="${cue.name || ''}" />
      </div>

      <div class="form-group">
        <label class="form-label">Entity</label>
        <input type="text" class="form-input" value="${cue.entity_id}" disabled />
      </div>

      <div class="form-group">
        <label class="form-label">Cue Type</label>
        <select class="form-select" id="cueType">
          <option value="door" ${cue.cue_type === 'door' ? 'selected' : ''}>Door</option>
          <option value="window" ${cue.cue_type === 'window' ? 'selected' : ''}>Window</option>
          <option value="light" ${cue.cue_type === 'light' ? 'selected' : ''}>Light</option>
          <option value="switch" ${cue.cue_type === 'switch' ? 'selected' : ''}>Switch</option>
          <option value="lock" ${cue.cue_type === 'lock' ? 'selected' : ''}>Lock</option>
          <option value="climate" ${cue.cue_type === 'climate' ? 'selected' : ''}>Climate</option>
          <option value="media" ${cue.cue_type === 'media' ? 'selected' : ''}>Media</option>
          <option value="appliance" ${cue.cue_type === 'appliance' ? 'selected' : ''}>Appliance</option>
        </select>
      </div>

      <div class="form-group">
        <label class="form-label">Directional Hints</label>
        <div class="direction-hints" id="directionHints">
          ${(cue.directional_hints || []).map((hint, idx) => `
            <div class="direction-hint-item">
              <input type="text" class="hint-input" value="${hint}" data-index="${idx}" />
              <button class="hint-remove-btn" data-index="${idx}">Remove</button>
            </div>
          `).join('')}
        </div>
        <button class="add-hint-btn" id="addHint">+ Add Hint</button>
      </div>

      ${this._config.show_correlations && cue.correlations ? `
        <div class="form-group">
          <label class="form-label">Correlations</label>
          <div class="correlation-list">
            ${cue.correlations.map(corr => `
              <div class="correlation-item">
                <div class="correlation-sensor">${corr.sensor}</div>
                <div class="correlation-confidence">Confidence: ${Math.round(corr.confidence * 100)}%</div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <button class="save-btn" id="saveCue">Save Cue</button>
    `;

    // Add event listeners
    const saveCue = detailsPanel.querySelector('#saveCue');
    if (saveCue) {
      saveCue.addEventListener('click', () => {
        this.saveCue();
      });
    }

    const cueName = detailsPanel.querySelector('#cueName');
    if (cueName) {
      cueName.addEventListener('input', (e) => {
        cue.name = e.target.value;
      });
    }

    const cueType = detailsPanel.querySelector('#cueType');
    if (cueType) {
      cueType.addEventListener('change', (e) => {
        cue.cue_type = e.target.value;
        this.renderFloorplan();
      });
    }

    const addHint = detailsPanel.querySelector('#addHint');
    if (addHint) {
      addHint.addEventListener('click', () => {
        if (!cue.directional_hints) cue.directional_hints = [];
        cue.directional_hints.push('');
        this.renderDetailsPanel();
      });
    }

    const hintInputs = detailsPanel.querySelectorAll('.hint-input');
    hintInputs.forEach(input => {
      input.addEventListener('input', (e) => {
        const idx = parseInt(e.target.dataset.index);
        cue.directional_hints[idx] = e.target.value;
      });
    });

    const removeButtons = detailsPanel.querySelectorAll('.hint-remove-btn');
    removeButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const idx = parseInt(e.target.dataset.index);
        cue.directional_hints.splice(idx, 1);
        this.renderDetailsPanel();
      });
    });
  }

  /**
   * Render floorplan
   */
  renderFloorplan() {
    const svg = this.shadowRoot.getElementById('floorplanSvg');
    if (!svg) return;

    let content = '';

    // Draw sensors if correlations are shown
    if (this._config.show_correlations && this._sensors.length > 0) {
      this._sensors.forEach(sensor => {
        content += `
          <circle
            class="sensor-marker"
            cx="${sensor.x * 1000}"
            cy="${sensor.y * 1000}"
            r="8"
          />
        `;
      });
    }

    // Draw correlation lines
    if (this._config.show_correlations && this._selectedCue) {
      const selectedCue = this._selectedCue;
      if (selectedCue.correlations) {
        selectedCue.correlations.forEach(corr => {
          const sensor = this._sensors.find(s => s.id === corr.sensor);
          if (sensor) {
            content += `
              <line
                class="correlation-line"
                x1="${selectedCue.position.x * 1000}"
                y1="${selectedCue.position.y * 1000}"
                x2="${sensor.x * 1000}"
                y2="${sensor.y * 1000}"
              />
            `;
          }
        });
      }
    }

    // Draw cues
    this._cues.forEach(cue => {
      const isSelected = this._selectedCue?.id === cue.id;
      const animation = this._config.cue_visualization.animation;
      const style = this._config.cue_visualization.style;
      
      const animClass = animation !== 'none' ? animation : '';
      
      if (style === 'icons') {
        const icon = this.getCueIcon(cue.cue_type);
        content += `
          <text
            class="cue-marker ${isSelected ? 'selected' : ''} ${animClass}"
            x="${cue.position.x * 1000}"
            y="${cue.position.y * 1000}"
            text-anchor="middle"
            dominant-baseline="middle"
            font-size="24"
            data-cue-id="${cue.id}"
          >${icon}</text>
        `;
      } else if (style === 'badges') {
        const color = this.getCueColor(cue.current_state);
        content += `
          <rect
            class="cue-marker ${isSelected ? 'selected' : ''} ${animClass}"
            x="${cue.position.x * 1000 - 15}"
            y="${cue.position.y * 1000 - 15}"
            width="30"
            height="30"
            rx="4"
            fill="${color}"
            data-cue-id="${cue.id}"
          />
        `;
      } else {
        const color = this.getCueColor(cue.current_state);
        content += `
          <circle
            class="cue-marker ${isSelected ? 'selected' : ''} ${animClass}"
            cx="${cue.position.x * 1000}"
            cy="${cue.position.y * 1000}"
            r="12"
            fill="${color}"
            data-cue-id="${cue.id}"
          />
        `;
      }

      // Show confidence if enabled
      if (this._config.show_confidence && cue.confidence) {
        content += `
          <text
            x="${cue.position.x * 1000}"
            y="${cue.position.y * 1000 + 25}"
            text-anchor="middle"
            font-size="10"
            fill="var(--primary-text-color)"
          >${Math.round(cue.confidence * 100)}%</text>
        `;
      }
    });

    svg.innerHTML = content;

    // Add click listeners to cue markers
    svg.querySelectorAll('.cue-marker').forEach(marker => {
      marker.addEventListener('click', (e) => {
        const cueId = e.target.dataset.cueId;
        if (cueId) {
          this.selectCue(cueId);
        }
      });
    });

    this.updateCueList();
  }

  /**
   * Get entity icon
   */
  getEntityIcon(domain) {
    const icons = {
      'binary_sensor': '📡',
      'switch': '🔌',
      'light': '💡',
      'lock': '🔒',
      'cover': '🪟',
      'climate': '🌡️',
      'media_player': '📺',
    };
    return icons[domain] || '❓';
  }

  /**
   * Get cue icon
   */
  getCueIcon(cueType) {
    const icons = {
      'door': '🚪',
      'window': '🪟',
      'light': '💡',
      'switch': '🔌',
      'lock': '🔒',
      'climate': '🌡️',
      'media': '📺',
      'appliance': '🏠',
    };
    return icons[cueType] || '❓';
  }

  /**
   * Get cue color based on state
   */
  getCueColor(state) {
    if (state === 'on' || state === 'open' || state === 'unlocked') {
      return 'var(--success-color)';
    } else if (state === 'off' || state === 'closed' || state === 'locked') {
      return 'var(--disabled-color)';
    }
    return 'var(--warning-color)';
  }

  /**
   * Infer cue type from entity ID
   */
  inferCueType(entityId) {
    if (entityId.includes('door')) return 'door';
    if (entityId.includes('window')) return 'window';
    if (entityId.includes('light')) return 'light';
    if (entityId.includes('switch')) return 'switch';
    if (entityId.includes('lock')) return 'lock';
    if (entityId.includes('climate') || entityId.includes('thermostat')) return 'climate';
    if (entityId.includes('media')) return 'media';
    
    const domain = entityId.split('.')[0];
    if (domain === 'light') return 'light';
    if (domain === 'switch') return 'switch';
    if (domain === 'lock') return 'lock';
    if (domain === 'cover') return 'window';
    if (domain === 'climate') return 'climate';
    if (domain === 'media_player') return 'media';
    
    return 'appliance';
  }

  /**
   * Save cue
   */
  async saveCue() {
    if (!this._selectedCue) return;

    await this.callService('update_cue', {
      cue_id: this._selectedCue.id,
      name: this._selectedCue.name,
      cue_type: this._selectedCue.cue_type,
      position: this._selectedCue.position,
      directional_hints: this._selectedCue.directional_hints,
    });

    alert('Cue saved successfully!');
  }

  /**
   * Save all cues
   */
  async saveAllCues() {
    for (const cue of this._cues) {
      await this.callService('update_cue', {
        cue_id: cue.id,
        name: cue.name,
        cue_type: cue.cue_type,
        position: cue.position,
        directional_hints: cue.directional_hints,
      });
    }

    alert('All cues saved successfully!');
  }

  /**
   * Call service
   */
  async callService(service, data) {
    if (!this._hass) return;

    try {
      await this._hass.callService('motiondirection', service, {
        floorplan_id: this._config.floorplan_id,
        ...data,
      });
    } catch (error) {
      console.error(`Failed to call service ${service}:`, error);
      alert(`Error: ${error.message}`);
    }
  }

  /**
   * Get editor configuration schema
   */
  static getConfigElement() {
    return document.createElement('motiondirection-cue-editor-card-editor');
  }

  /**
   * Get stub configuration for card picker
   */
  static getStubConfig() {
    return {
      floorplan_id: 'ground_floor',
      mode: 'edit',
      show_cues: true,
      show_correlations: true,
      show_confidence: true,
      cue_visualization: {
        style: 'icons',
        show_state: true,
        show_direction_hints: true,
        animation: 'pulse',
      },
    };
  }
}

// Register custom element
customElements.define('motiondirection-cue-editor-card', MotionDirectionCueEditorCard);

// Register card with Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'motiondirection-cue-editor',
  name: 'MotionDirection Cue Editor',
  description: 'Interactive editor for secondary cue configuration on floorplans',
  preview: true,
});

console.info(
  '%c MOTIONDIRECTION-CUE-EDITOR-CARD %c v1.0.0 ',
  'color: white; background: #ff5722; font-weight: 700;',
  'color: #ff5722; background: white; font-weight: 700;'
);
