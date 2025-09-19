# Universal NSFW Filter - Installation & Troubleshooting Guide

## 🔧 Installation Steps

### 1. Install Extension in Developer Mode
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" toggle (top right)
3. Click "Load unpacked"
4. Select the `chrome_extension_universal` folder
5. Extension should appear with a puzzle piece icon

### 2. Grant Permissions
- Extension needs access to "All sites" for universal support
- Click "Allow" when prompted for permissions
- Check that extension has `<all_urls>` permission

### 3. Test Installation
1. Open the included `test.html` file in Chrome
2. Click the extension icon in toolbar
3. Verify popup opens with settings
4. Check browser console for any errors

## 🐛 Troubleshooting Common Issues

### Service Worker Registration Failed (Status Code 15)
**Cause**: Missing permissions or invalid manifest
**Solution**:
1. Check `manifest.json` has all required permissions
2. Ensure service worker file exists and is valid
3. Try reloading the extension
4. Check Chrome DevTools > Application > Service Workers

### Context Menu Errors (onClicked undefined)
**Cause**: Missing `contextMenus` permission or initialization timing
**Solution**:
1. Verify `contextMenus` is in permissions array
2. Check background script loads without errors
3. Context menus are created in `chrome.runtime.onInstalled`

### Extension Not Working on Websites
**Cause**: Content script injection failures
**Solution**:
1. Check `<all_urls>` permission is granted
2. Verify content script runs (check console logs)
3. Some sites block content scripts (CSP restrictions)
4. Try refreshing the page after extension installation

### API Connection Issues
**Cause**: Server not reachable or CORS issues
**Solution**:
1. Check API endpoint: `http://localhost:5000/process-frame-stream`
2. Verify Flask server is running on localhost:5000
3. Check network connectivity
4. Look for CORS errors in browser console

## 🔍 Debug Mode

### Enable Debug Logging
Open browser console and run:
```javascript
// Enable debug mode
window.UniversalNSFWFilter?.getProcessor().debug = true;

// Get current stats
window.UniversalNSFWFilter?.getStats();

// Check if processor is running
window.UniversalNSFWFilter?.getProcessor();
```

### Check Extension Status
```javascript
// Check if extension is loaded
chrome.runtime.getManifest();

// Check active permissions
chrome.permissions.getAll();

// Check storage
chrome.storage.sync.get();
```

### Monitor Processing
```javascript
// Watch for processing activity
setInterval(() => {
    const stats = window.UniversalNSFWFilter?.getStats();
    if (stats) console.log('Stats:', stats);
}, 5000);
```

## 📊 Expected Console Output

### Successful Loading
```
🌐 Universal NSFW Filter content script loaded for [hostname]
🚀 Universal NSFW Filter Background Service started
🎬 Universal NSFW Filter started for [hostname]
⚙️ Settings: 15fps, quality: 0.7, queue: 3
🎯 Attached to video: 640x360 on [hostname]
```

### During Processing
```
📊 Frames processed: 5/10, Success: 100%
✅ Frame processed in 8ms
🔞 NSFW content detected and blurred
```

### Error Indicators
```
❌ API request failed: 500 Internal Server Error
⚠️ Content script not available for current tab
🛑 Extension disabled
```

## 🔄 Quick Fixes

### Reset Extension
1. Go to `chrome://extensions/`
2. Click "Remove" on Universal NSFW Filter
3. Reload the unpacked extension
4. Test on `test.html` page

### Clear Storage
```javascript
chrome.storage.sync.clear();
chrome.storage.local.clear();
```

### Force Refresh
```javascript
// Restart the processor
window.UniversalNSFWFilter?.restart();
```

## 📁 File Checklist

Ensure all files are present:
- ✅ `manifest.json` - Extension configuration
- ✅ `background.js` - Service worker
- ✅ `content_script.js` - Universal video processing
- ✅ `popup.html` - Settings interface
- ✅ `popup.js` - Popup functionality
- ✅ `welcome.html` - Welcome page
- ✅ `test.html` - Test environment
- ✅ `README.md` - Documentation

## 🆘 Still Having Issues?

1. **Check Chrome Version**: Ensure Chrome 88+ for Manifest V3 support
2. **Disable Other Extensions**: Test with only NSFW Filter enabled
3. **Incognito Mode**: Test in incognito to rule out conflicts
4. **Server Status**: Verify `localhost:5000` is accessible
5. **Firewall/Antivirus**: Check if blocking extension or API requests

## 📞 Getting Help

If issues persist:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Copy any error messages
4. Note the website where issue occurs
5. Check extension popup for status info

The extension should work on ALL websites with video content automatically!
