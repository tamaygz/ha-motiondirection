# Motion Direction - Installation Guide

## Quick Start

After installing the Motion Direction integration, follow these steps to enable the custom dashboard cards.

## Automatic Setup ✨

The integration automatically:
- ✅ Registers frontend resources at `/hacsfiles/ha-motiondirection/`
- ✅ Makes all 9 custom cards available
- ✅ Creates a notification with setup instructions
- ✅ Serves files with proper caching headers

**No manual file copying required!**

### Enable the Cards (One-Time Setup)

After installing the integration, you only need to register the card loader **once**:

1. **Go to Settings → Dashboards → Resources** (or click the link in the notification)

2. **Click "Add Resource"**

3. **Enter the following:**
   - **URL:** `/hacsfiles/ha-motiondirection/card-loader.js`
   - **Resource Type:** JavaScript Module

4. **Click "Create"**

5. **Hard refresh your browser:**
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

6. **Verify installation:**
   - Go to your dashboard
   - Click "Add Card"
   - Search for "MotionDirection"
   - You should see all 9 cards available

## Available Cards

After registration, these cards are available:

1. **MotionDirection Motion Status** - Current direction and confidence
2. **MotionDirection Floorplan Editor** - Interactive sensor placement
3. **MotionDirection Motion Visualizer** - Trails and heatmaps
4. **MotionDirection Zone Status** - Zone occupancy and stats
5. **MotionDirection Zone Editor** - Zone configuration
6. **MotionDirection Zone Flow Visualizer** - Inter-zone movement
7. **MotionDirection Cue Status** - Secondary cue monitoring
8. **MotionDirection Cue Editor** - Cue configuration
9. **MotionDirection Hybrid Visualizer** - Combined visualization

## Troubleshooting

### Cards Not Appearing

**Problem:** Cards don't appear in the card picker after adding resource

**Solutions:**
1. Verify resource URL is correct: `/hacsfiles/ha-motiondirection/card-loader.js`
2. Check resource type is set to "JavaScript Module"
3. Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R)
4. Clear browser cache
5. Check browser console for errors (F12 → Console)
6. Check Home Assistant logs for frontend registration success message
7. Restart Home Assistant

### "Custom element doesn't exist" Error

**Problem:** Card shows error when trying to add

**Solutions:**
1. Check that JavaScript files are loading (F12 → Network tab)
2. Verify all files exist in `/config/www/motion-direction/`
3. Check for JavaScript errors in console
4. Ensure card-loader.js loaded successfully

### 404 Not Found Errors

**Problem:** Files return 404 errors

**Solutions:**
1. Verify integration is properly installed in `custom_components/motiondirection/`
2. Check frontend directory exists: `custom_components/motiondirection/frontend/`
3. Restart Home Assistant
4. Check Home Assistant logs for "Successfully registered frontend resources" message
5. Try accessing files directly: `http://your-ha-ip:8123/hacsfiles/ha-motiondirection/card-loader.js`

### CORS Errors

**Problem:** Cross-Origin Resource Sharing errors

**Solutions:**
1. Use the provided URL path: `/hacsfiles/ha-motiondirection/`
2. Don't use external URLs or file:// paths
3. Ensure you're accessing through Home Assistant's web interface

## Alternative Installation Methods

### Method 1: Individual Cards

If you only want specific cards, register them individually:

```yaml
# In Lovelace resources
- url: /hacsfiles/ha-motiondirection/motion-status-card.js
  type: module
- url: /hacsfiles/ha-motiondirection/floorplan-editor-card.js
  type: module
# ... etc
```

### Method 2: YAML Configuration

Add to `configuration.yaml` (if using YAML mode):

```yaml
lovelace:
  mode: yaml
  resources:
    - url: /hacsfiles/ha-motiondirection/card-loader.js
      type: module
```

### Method 3: Manual www/ Copy (Fallback)

If automatic registration fails for any reason:

```bash
# Copy frontend files to www directory
mkdir -p /config/www/motion-direction/
cp /config/custom_components/motiondirection/frontend/*.js /config/www/motion-direction/
```

Then use `/local/motion-direction/card-loader.js` as the resource URL.

## Verification

Check that everything is working:

```bash
# Check source files exist
ls -la /config/custom_components/motiondirection/frontend/

# Should see: card-loader.js and all *-card.js files
```

**Test direct access:**
- Open browser to: `http://your-ha-ip:8123/hacsfiles/ha-motiondirection/card-loader.js`
- Should download or display the JavaScript file
- If 404 error, check Home Assistant logs for registration errors

**Check Home Assistant logs:**
```bash
# Look for successful registration message
grep "Successfully registered frontend resources" /config/home-assistant.log
```

## HACS Installation

If using HACS:

1. HACS handles resource registration automatically
2. Files are available at `/hacsfiles/ha-motiondirection/`
3. Follow the same steps to add the resource
4. Updates are managed through HACS

## Support

If you continue to have issues:

1. **Check Home Assistant logs:**
   - Settings → System → Logs
   - Look for `motiondirection` entries

2. **Check browser console:**
   - Press F12
   - Go to Console tab
   - Look for errors related to MotionDirection

3. **Verify integration:**
   - Settings → Devices & Services
   - Check that Motion Direction is listed and active

4. **Report issues:**
   - GitHub: https://github.com/tamaygz/ha-motiondirection/issues
   - Include HA version, browser, and error messages

## Next Steps

After installation:

1. **Configure your floorplan:**
   - Use the Floorplan Editor card
   - Place your motion sensors
   - Draw zones if needed

2. **Add monitoring cards:**
   - Motion Status card for current direction
   - Zone Status card for zone occupancy

3. **Enable advanced features:**
   - Add secondary cues (lights, doors)
   - Configure trigger zones
   - Use the Hybrid Visualizer

4. **Explore visualizations:**
   - Motion Visualizer for trails
   - Zone Flow Visualizer for patterns

## Updates

When updating the integration:

1. Update via HACS or manually copy new files
2. Restart Home Assistant
3. Hard refresh your browser (Ctrl+Shift+R)
4. No need to re-register resources

## Uninstalling

To remove the cards:

1. Remove the integration (Settings → Devices & Services)
2. Remove the Lovelace resource (Settings → Dashboards → Resources)
3. Hard refresh browser

The frontend files are automatically removed when the integration is uninstalled.
