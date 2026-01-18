/**
 * MotionDirection Card Loader
 * 
 * Automatically registers all custom cards with Home Assistant.
 * This file is loaded by __init__.py during integration setup.
 */

/**
 * Card definitions for all MotionDirection cards
 */
const MOTIONDIRECTION_CARDS = [
  {
    type: 'custom:motiondirection-motion-status',
    name: 'MotionDirection Motion Status',
    description: 'Display motion direction, confidence, detection method, and active zones',
    preview: true,
    module: '/hacsfiles/ha-motiondirection/motion-status-card.js',
  },
  {
    type: 'custom:motiondirection-floorplan-editor',
    name: 'MotionDirection Floorplan Editor',
    description: 'Interactive floorplan editor for sensor and zone placement',
    preview: true,
    module: '/hacsfiles/ha-motiondirection/floorplan-editor-card.js',
  },
  {
    type: 'custom:motiondirection-motion-visualizer',
    name: 'MotionDirection Motion Visualizer',
    description: 'Visualize motion trails, heat maps, direction arrows, and historical playback',
    preview: true,
    module: '/hacsfiles/ha-motiondirection/motion-visualizer-card.js',
  },
  {
    type: 'custom:motiondirection-zone-editor',
    name: 'MotionDirection Zone Editor',
    description: 'Edit zones with polygon drawing, naming, and direction configuration',
    preview: true,
    module: '/hacsfiles/ha-motiondirection/zone-editor-card.js',
  },
  {
    type: 'custom:motiondirection-zone-status',
    name: 'MotionDirection Zone Status',
    description: 'Display zone occupancy, direction statistics, and real-time updates',
    preview: true,
    module: '/hacsfiles/ha-motiondirection/zone-status-card.js',
  },
  {
    type: 'custom:motiondirection-zone-flow-visualizer',
    name: 'MotionDirection Zone Flow Visualizer',
    description: 'Visualize flow between zones with particles, arrows, and heat maps',
    preview: true,
    module: '/hacsfiles/ha-motiondirection/zone-flow-visualizer-card.js',
  },
  {
    type: 'custom:motiondirection-cue-editor',
    name: 'MotionDirection Cue Editor',
    description: 'Edit secondary cues with entity selection, placement, and directional hints',
    preview: true,
    module: '/hacsfiles/ha-motiondirection/cue-editor-card.js',
  },
  {
    type: 'custom:motiondirection-cue-status',
    name: 'MotionDirection Cue Status',
    description: 'Display secondary cue states, correlations, and success rates',
    preview: true,
    module: '/hacsfiles/ha-motiondirection/cue-status-card.js',
  },
  {
    type: 'custom:motiondirection-hybrid-visualizer',
    name: 'MotionDirection Hybrid Detection Visualizer',
    description: 'Visualize hybrid detection with motion sensors, secondary cues, correlations, and timeline',
    preview: true,
    module: '/hacsfiles/ha-motiondirection/hybrid-visualizer-card.js',
  },
];

/**
 * Register all cards with Home Assistant
 */
function registerCards() {
  // Initialize custom cards registry
  window.customCards = window.customCards || [];

  // Register each card
  MOTIONDIRECTION_CARDS.forEach(card => {
    // Check if card is already registered
    const existing = window.customCards.find(c => c.type === card.type);
    
    if (!existing) {
      window.customCards.push(card);
      console.info(`[MotionDirection] Registered card: ${card.type}`);
    }
  });

  console.info(
    '%c MOTIONDIRECTION-CARDS %c Registered ' + MOTIONDIRECTION_CARDS.length + ' cards ',
    'color: white; background: #e91e63; font-weight: 700;',
    'color: #e91e63; background: white; font-weight: 700;'
  );
}

/**
 * Load card modules dynamically
 */
async function loadCardModules() {
  const loadPromises = MOTIONDIRECTION_CARDS.map(async card => {
    try {
      // Check if module is already loaded
      // Extract element name from type (e.g., 'custom:motiondirection-motion-status' -> 'motiondirection-motion-status')
      const elementName = card.type.replace('custom:', '');
      if (customElements.get(elementName)) {
        console.debug(`[MotionDirection] Card already loaded: ${card.type}`);
        return;
      }

      // Load module
      await import(card.module);
      console.debug(`[MotionDirection] Loaded card module: ${card.type}`);
    } catch (error) {
      console.error(`[MotionDirection] Failed to load card ${card.type}:`, error);
    }
  });

  await Promise.all(loadPromises);
}

/**
 * Get card resource URLs for configuration.yaml
 */
function getResourceUrls() {
  return MOTIONDIRECTION_CARDS.map(card => ({
    url: card.module,
    type: 'module',
  }));
}

/**
 * Get card configuration examples for documentation
 */
function getCardExamples() {
  return {
    'motion-status': {
      type: 'custom:motiondirection-motion-status',
      floorplan_id: 'ground_floor',
      show_confidence: true,
      show_detection_method: true,
      show_active_zones: true,
      show_triggered_sensors: true,
      show_contributing_cues: true,
    },
    'floorplan-editor': {
      type: 'custom:motiondirection-floorplan-editor',
      floorplan_id: 'ground_floor',
      width: 1000,
      height: 1000,
      background_image: '/local/floorplan.png',
      show_grid: true,
    },
    'motion-visualizer': {
      type: 'custom:motiondirection-motion-visualizer',
      floorplan_id: 'ground_floor',
      visualization_mode: 'trails',
      show_sensors: true,
      show_direction_arrows: true,
      trail_length: 50,
      playback_speed: 1.0,
    },
    'zone-editor': {
      type: 'custom:motiondirection-zone-editor',
      floorplan_id: 'ground_floor',
      show_existing_zones: true,
      enable_zone_editing: true,
    },
    'zone-status': {
      type: 'custom:motiondirection-zone-status',
      floorplan_id: 'ground_floor',
      layout: 'grid',
      show_occupancy: true,
      show_direction: true,
      show_statistics: true,
    },
    'zone-flow-visualizer': {
      type: 'custom:motiondirection-zone-flow-visualizer',
      floorplan_id: 'ground_floor',
      visualization_mode: 'particles',
      particle_count: 100,
      show_statistics: true,
    },
    'cue-editor': {
      type: 'custom:motiondirection-cue-editor',
      floorplan_id: 'ground_floor',
      show_available_entities: true,
      entity_types: ['light', 'switch', 'media_player', 'climate'],
      enable_drag_drop: true,
    },
    'cue-status': {
      type: 'custom:motiondirection-cue-status',
      floorplan_id: 'ground_floor',
      layout: 'grid',
      show_state: true,
      show_correlation: true,
      show_success_rate: true,
    },
    'hybrid-visualizer': {
      type: 'custom:motiondirection-hybrid-visualizer',
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
    },
  };
}

/**
 * Initialize card loader
 */
function init() {
  // Register cards immediately
  registerCards();

  // Load card modules when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadCardModules);
  } else {
    loadCardModules();
  }
}

// Export for use in Python integration
export {
  MOTIONDIRECTION_CARDS,
  registerCards,
  loadCardModules,
  getResourceUrls,
  getCardExamples,
};

// Auto-initialize
init();
