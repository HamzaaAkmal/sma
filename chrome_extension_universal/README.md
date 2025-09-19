# Universal NSFW Filter Chrome Extension

## 🌐 Universal Website Support
This Chrome extension now works on **ALL websites** with video content, providing real-time NSFW detection and blurring across the entire web.

## 🚀 Features

### ✅ Universal Compatibility
- **All Websites**: Works on every website that contains video content
- **Adaptive Processing**: Automatically optimizes settings based on website type
- **Smart Detection**: Identifies video content across different frameworks and platforms
- **SPA Support**: Handles Single Page Applications and dynamic content loading

### ⚡ Ultra-Fast Performance
- **Sub-10ms Latency**: GPU-accelerated processing for real-time filtering
- **Adaptive Frame Rate**: Automatically adjusts based on website and content type
- **Queue Management**: Intelligent frame processing queue with overflow protection
- **Background Processing**: Non-blocking processing that doesn't affect browsing

### 🎯 Advanced AI Detection
- **YOLOv8 Model**: 18-category NSFW content detection
- **Multi-stage Blurring**: Gaussian blur + pixelation for maximum privacy
- **Confidence Tuning**: Adjustable sensitivity for different content types
- **Context Awareness**: Website-specific optimization profiles

### 🔧 Smart Configuration
- **Website Profiles**: Pre-configured settings for popular platforms
- **Real-time Adjustment**: Change settings without page reload
- **Performance Monitoring**: Live statistics and latency tracking
- **Error Recovery**: Automatic fallback and reconnection handling

## 📋 Installation

### From Source (Development)
1. Clone or download this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked" and select the `chrome_extension_universal` folder
5. The extension will appear in your toolbar

### Production Deployment
```bash
# Zip the extension for Chrome Web Store
cd chrome_extension_universal
zip -r universal-nsfw-filter.zip . -x "*.DS_Store" "node_modules/*" ".git/*"
```

## 🌍 Supported Websites

### Popular Platforms (Optimized)
- **YouTube** - 20fps, high quality processing
- **TikTok** - 25fps, optimized for short videos  
- **Instagram** - 15fps, balanced performance
- **Twitch** - 30fps, high-frequency processing
- **Twitter/X** - 12fps, efficient processing
- **Facebook** - 15fps, adaptive quality
- **Reddit** - 10fps, battery-friendly
- **LinkedIn** - 10fps, professional content focus

### Universal Support
- **News Websites** - All video content automatically detected
- **Adult Content Sites** - Enhanced processing with higher frame rates
- **Educational Platforms** - Balanced processing for learning content
- **E-commerce Sites** - Product video monitoring
- **Social Media** - Real-time feed content protection
- **Video Hosting** - Universal video player support
- **Live Streaming** - Real-time stream monitoring
- **Any Website** - Automatic video content detection

## ⚙️ Configuration

### Basic Settings
```javascript
{
  "enabled": true,                    // Global enable/disable
  "apiEndpoint": "https://server.superioruniversity.app/process-frame-stream",
  "frameRate": 15,                   // Frames per second to process
  "compressionQuality": 0.7,         // Image compression (0.1-1.0)
  "sensitivity": 0.5                 // Detection sensitivity (0.1-1.0)
}
```

### Website-Specific Profiles
The extension automatically applies optimized settings based on the current website:

```javascript
// Example: YouTube optimization
{
  frameRate: 20,
  quality: 0.8,
  queueSize: 5
}

// Example: Adult site optimization  
{
  frameRate: 30,
  quality: 0.9,
  queueSize: 8
}
```

## 🔧 API Integration

### Server Endpoint
The extension connects to your local Flask server for testing:
- **Endpoint**: `http://localhost:5000/process-frame-stream`
- **Method**: POST
- **Content-Type**: application/json

### Request Format
```json
{
  "frame": "base64_encoded_image",
  "frame_id": "unique_frame_identifier", 
  "confidence": 0.5,
  "website": "hostname.com"
}
```

### Response Format
```json
{
  "frame": "base64_encoded_blurred_image",
  "detections": [
    {
      "class": "explicit",
      "confidence": 0.87,
      "bbox": [x, y, width, height]
    }
  ],
  "time": 8.5,
  "processed": true
}
```

## 📊 Performance Monitoring

### Real-time Statistics
- **Active Tabs**: Number of tabs currently being monitored
- **Frames Processed**: Total frames processed since startup
- **Average Latency**: Rolling average of processing time
- **Success Rate**: Percentage of successfully processed frames
- **Error Count**: Failed processing attempts
- **Website Analysis**: Current site compatibility status

### Performance Optimization
The extension includes several optimization features:

1. **Adaptive Frame Rate**: Reduces processing during high latency
2. **Queue Management**: Prevents memory overflow during peak processing
3. **Error Recovery**: Exponential backoff for network issues
4. **Canvas Optimization**: Efficient frame capture and rendering
5. **Memory Management**: Automatic cleanup of processed frames

## 🛠️ Development

### File Structure
```
chrome_extension_universal/
├── manifest.json           # Extension configuration (Universal permissions)
├── background.js          # Service worker for extension lifecycle
├── content_script.js      # Universal video processing logic
├── popup.html            # Extension settings interface
├── popup.js              # Popup functionality and stats
├── welcome.html          # First-run welcome page
└── README.md            # This documentation
```

### Key Components

#### Universal Content Script (`content_script.js`)
- **Universal Video Detection**: Finds video elements on any website
- **Adaptive Processing**: Website-specific optimization
- **Real-time Monitoring**: Continuous frame capture and processing
- **Overlay Management**: Blurred content application
- **Performance Tracking**: Statistics and error handling

#### Background Service (`background.js`)
- **Global State Management**: Extension-wide settings and statistics
- **Tab Management**: Multi-tab processing coordination
- **API Communication**: Server connectivity and error handling
- **Performance Monitoring**: Cross-tab statistics aggregation

#### Popup Interface (`popup.html/js`)
- **Real-time Dashboard**: Live statistics and status
- **Quick Settings**: Frame rate, sensitivity, quality adjustment
- **Website Analysis**: Current site compatibility and video detection
- **Control Panel**: Enable/disable, refresh, and help access

### Adding New Websites
The extension automatically works on all websites, but you can add specific optimizations:

```javascript
// In content_script.js - detectWebsiteSettings()
if (hostname.includes('newsite.com')) {
    return { 
        frameRate: 25, 
        quality: 0.8, 
        queueSize: 4 
    };
}
```

## 🔒 Privacy & Security

### Data Handling
- **Local Processing**: Frame capture and preparation done locally
- **Encrypted Transport**: HTTPS communication with AI server
- **No Storage**: Frames are processed and immediately discarded
- **No Tracking**: No user behavior or personal data collection
- **Anonymous Processing**: Frames sent without identifying information

### Permissions
The extension uses minimal required permissions:
- **`<all_urls>`**: Access to all websites for universal video monitoring
- **`storage`**: Save user preferences locally
- **`scripting`**: Inject content scripts for video processing
- **`activeTab`**: Access current tab for settings management

## 🚀 Deployment

### VPS Server Setup
The extension requires the companion API server. See the `vps_deployment/` folder for:
- Docker deployment configuration
- GPU optimization settings
- SSL certificate setup
- Performance monitoring
- Auto-scaling configuration

### Production Checklist
- [ ] API server deployed and accessible
- [ ] SSL certificate configured
- [ ] Performance monitoring active
- [ ] Error logging enabled
- [ ] Extension permissions validated
- [ ] Cross-browser compatibility tested
- [ ] Performance benchmarks verified

## 📈 Analytics & Monitoring

### Extension Metrics
- **Processing Speed**: Target <10ms per frame
- **Success Rate**: Target >95% successful processing
- **Memory Usage**: Optimized for <50MB per tab
- **CPU Impact**: Minimal impact on browsing performance
- **Network Usage**: Efficient frame compression and transmission

### Server Integration
The extension integrates with your local Flask server for testing:
- **Real-time Dashboards**: Processing statistics and performance
- **Alert System**: Automatic notifications for issues
- **Performance Analytics**: Detailed latency and success metrics
- **Usage Statistics**: Anonymous usage patterns and optimization insights

## 🆘 Troubleshooting

### Common Issues

#### Extension Not Working
1. Check if extension is enabled in popup
2. Verify API server connectivity
3. Refresh the current tab
4. Check browser console for errors

#### Slow Performance
1. Reduce frame rate in settings
2. Lower image quality setting
3. Check internet connection speed
4. Verify GPU acceleration is enabled

#### Video Not Detected
1. Ensure page has finished loading
2. Check if videos are in iframes (limited access)
3. Try refreshing the extension
4. Verify website isn't in skip list

### Debug Mode
Enable debug logging in the browser console:
```javascript
// Open developer tools and run:
window.UniversalNSFWFilter.getProcessor().debug = true;
```

## 🤝 Support

### Getting Help
- **Documentation**: http://localhost:5000/help
- **API Status**: http://localhost:5000/health
- **Performance Dashboard**: Available in extension popup

### Reporting Issues
When reporting issues, please include:
1. Browser version and OS
2. Website where issue occurred
3. Extension settings in use
4. Console error messages
5. Steps to reproduce

---

**Superior University AI Research Division**  
Universal NSFW Detection and Content Protection Technology  
Version: 1.0.0 | Universal Website Support
