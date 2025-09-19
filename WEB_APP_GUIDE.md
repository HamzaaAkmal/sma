# NSFW Video Filter - Web Application

🛡️ **Advanced real-time NSFW content detection and blurring for YouTube videos and uploads**

## 🚀 Quick Start

### Option 1: Double-click to start (Windows)
```
Double-click: start_webapp.bat
```

### Option 2: Command line
```bash
python launch_webapp.py
```

### Option 3: Direct Streamlit
```bash
streamlit run streamlit_app.py
```

## 📋 Features

### 🎬 Video Processing
- **YouTube Integration**: Paste any YouTube URL for instant processing
- **File Upload**: Support for MP4, AVI, MOV, MKV formats
- **Real-time Preview**: Watch the filtering process live
- **Multiple Quality Options**: 480p, 720p, 1080p processing

### 🤖 AI-Powered Detection
- **YOLOv8 Model**: State-of-the-art object detection
- **High Accuracy**: Trained specifically for NSFW content
- **Configurable Sensitivity**: Adjust detection confidence
- **Real-time Processing**: 20-45 FPS depending on hardware

### 🎨 Advanced Blurring
- **Multi-stage Blur**: Gaussian + Pixelation + Motion blur
- **Pixel-perfect Results**: Smooth edge blending
- **Privacy Protection**: Multiple blur layers ensure complete obscuring
- **Adaptive Intensity**: Blur strength adapts to content type

### ⚡ Performance Optimization
- **Hardware Auto-detection**: Automatically uses GPU when available
- **Multiple Presets**: Balance between speed and quality
- **Memory Efficient**: Optimized for long video processing
- **Progress Tracking**: Real-time processing statistics

## 🎯 Use Cases

### Content Creators
- **Safe Content Creation**: Ensure your videos are family-friendly
- **Platform Compliance**: Meet YouTube/Twitch content guidelines
- **Educational Content**: Create safe versions for educational use

### Platforms & Developers
- **Content Moderation**: Automated NSFW filtering for user uploads
- **API Integration**: Embed into existing video processing pipelines
- **Batch Processing**: Handle multiple videos efficiently

### Personal Use
- **Privacy Protection**: Blur sensitive content in personal videos
- **Family Safety**: Create kid-safe versions of content
- **Social Media**: Safe sharing of video content

## 🔧 Configuration Guide

### Performance Presets

| Preset | Speed | Quality | Best For |
|--------|-------|---------|----------|
| **Maximum Quality** | 5-10 FPS | Excellent | Static images, final output |
| **Balanced** ⭐ | 15-25 FPS | High | Most video processing |
| **Maximum Speed** | 25-35 FPS | Good | Large batches, testing |
| **Real-time Streaming** | 30+ FPS | Good | Live streams, webcams |

⭐ *Recommended for most users*

### Hardware Requirements

| Component | Minimum | Recommended | Optimal |
|-----------|---------|-------------|---------|
| **CPU** | 4 cores | 8 cores | 16+ cores |
| **RAM** | 8GB | 16GB | 32GB+ |
| **GPU** | Integrated | GTX 1060 / RTX 2060 | RTX 3070+ |
| **Storage** | 5GB free | 20GB free | 100GB+ SSD |

### Quality Settings

| Video Quality | Resolution | Processing Speed | Use Case |
|---------------|------------|------------------|----------|
| **480p** | 854×480 | Fastest | Quick previews, mobile |
| **720p** ⭐ | 1280×720 | Balanced | Most YouTube content |
| **1080p** | 1920×1080 | Slower | High-quality output |

⭐ *Recommended for balance of speed and quality*

## 📊 Performance Benchmarks

### Test System: RTX 3070, i7-10700K, 32GB RAM

| Video Type | Resolution | Preset | FPS | Quality |
|------------|------------|--------|-----|---------|
| YouTube Video | 720p | Maximum Speed | 35 FPS | Good |
| YouTube Video | 720p | Balanced | 22 FPS | High |
| YouTube Video | 1080p | Balanced | 18 FPS | High |
| Uploaded File | 480p | Real-time | 45 FPS | Good |

### Processing Time Examples

| Video Length | Resolution | Preset | Processing Time |
|--------------|------------|--------|-----------------|
| 1 minute | 720p | Balanced | ~3 minutes |
| 5 minutes | 720p | Balanced | ~15 minutes |
| 10 minutes | 1080p | Maximum Quality | ~45 minutes |
| 30 minutes | 480p | Maximum Speed | ~20 minutes |

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Setup
```bash
python test_setup.py
```

### 3. Launch Application
```bash
python launch_webapp.py
```

### Manual Installation
```bash
# Core dependencies
pip install streamlit ultralytics yt-dlp opencv-python torch

# Optional for enhanced UI
pip install plotly pandas pillow
```

## 🌐 Web Interface Guide

### 1. Configuration Panel (Sidebar)
- **Performance Preset**: Choose speed vs quality balance
- **Video Quality**: Select download resolution
- **Detection Confidence**: Adjust sensitivity (0.1-0.9)
- **Advanced Settings**: View current configuration details

### 2. Video Input Area
- **YouTube URL**: Paste any public YouTube video link
- **File Upload**: Drag & drop or browse for video files
- **Supported Formats**: MP4, AVI, MOV, MKV

### 3. Processing Monitor
- **Real-time Preview**: Live view of processing
- **Progress Tracking**: Percentage and frame counters
- **Performance Metrics**: FPS, detections, blur count
- **Processing Statistics**: Real-time performance data

### 4. Output & Download
- **Processed Video**: Downloadable filtered video
- **File Information**: Size, format, processing stats
- **Quality Metrics**: Detection accuracy, processing time

## 🔍 Detection Classes

The AI model detects and blurs these NSFW content types:

| Content Type | Action | Confidence Threshold |
|--------------|--------|---------------------|
| **Exposed Genitalia** | Always Blur | > 0.3 |
| **Exposed Breasts** | Always Blur | > 0.3 |
| **Exposed Buttocks** | Always Blur | > 0.3 |
| **Exposed Anus** | Always Blur | > 0.3 |
| **Covered Areas** | No Action | N/A |
| **Faces** | No Action | N/A |

## 🛡️ Privacy & Security

### Local Processing
- **No Cloud Upload**: All processing happens on your device
- **Privacy Protected**: Videos never leave your computer
- **Offline Capable**: Works without internet after download
- **Temporary Files**: Auto-cleanup of downloaded content

### Data Handling
- **No Data Collection**: No personal information stored
- **No Analytics**: No usage tracking or reporting
- **Local Storage Only**: Session data stays on your device
- **Secure Processing**: Encrypted temporary file handling

## 🐛 Troubleshooting

### Common Issues

#### Slow Processing
**Problem**: Processing is too slow for real-time use
**Solutions**:
- Use "Maximum Speed" preset
- Lower video quality (480p)
- Increase confidence threshold to 0.6+
- Close other applications
- Update GPU drivers

#### High Memory Usage
**Problem**: System runs out of memory
**Solutions**:
- Process shorter video segments
- Lower video resolution
- Reduce video quality setting
- Close browser tabs and other apps

#### Download Failures
**Problem**: YouTube videos won't download
**Solutions**:
- Verify URL is correct and video is public
- Try different video quality
- Check internet connection
- Some videos may be region-restricted

#### Poor Blur Quality
**Problem**: Blurring doesn't adequately hide content
**Solutions**:
- Use "Maximum Quality" preset
- Lower confidence threshold to 0.3
- Increase blur kernel size in config
- Ensure good source video quality

#### Model Loading Errors
**Problem**: AI model fails to load
**Solutions**:
- Verify `best.pt` file exists
- Check file isn't corrupted
- Ensure sufficient disk space
- Reinstall ultralytics package

### Performance Optimization

#### For Real-time Processing (30+ FPS)
1. Use "Real-time Streaming" preset
2. Set confidence threshold to 0.5+
3. Use 480p or 720p quality
4. Ensure GPU acceleration is available
5. Close unnecessary applications

#### For Maximum Quality
1. Use "Maximum Quality" preset
2. Set confidence threshold to 0.3
3. Use 1080p quality
4. Allow longer processing time
5. Ensure sufficient RAM available

## 🔄 API Integration

### Embedding in Other Applications

```python
from realtime_video_processor import VideoStreamProcessor

# Initialize processor
processor = VideoStreamProcessor("best.pt")
processor.initialize_model()

# Process video file
success = processor.process_video_file(
    "input.mp4", 
    "output.mp4", 
    confidence_threshold=0.4
)
```

### Batch Processing Script

```python
import os
from realtime_video_processor import create_youtube_compatible_processor

processor = create_youtube_compatible_processor()

# Process all videos in directory
for filename in os.listdir("input_videos"):
    if filename.endswith('.mp4'):
        input_path = f"input_videos/{filename}"
        output_path = f"output_videos/filtered_{filename}"
        processor.process_video_file(input_path, output_path)
```

## 📈 Analytics & Monitoring

### Built-in Analytics
- **Processing History**: Track all processed videos
- **Performance Metrics**: Monitor FPS and processing times
- **Detection Statistics**: Count of filtered content
- **System Performance**: Hardware utilization tracking

### Session Data
- **Automatic Logging**: Processing sessions auto-saved
- **Performance Trends**: Track improvements over time
- **Usage Statistics**: Understand processing patterns
- **Export Capability**: JSON format for external analysis

## 🤝 Support & Contributing

### Getting Help
1. Check the troubleshooting section
2. Run the system test: `python test_setup.py`
3. Review the FAQ in the web interface
4. Check hardware requirements

### Contributing
1. Fork the repository
2. Create feature branch
3. Add comprehensive tests
4. Submit pull request with detailed description

### Reporting Issues
- Provide system specifications
- Include error messages
- Describe steps to reproduce
- Attach relevant log files

## 📄 Legal & Compliance

### Content Moderation Use
- Comply with local laws and regulations
- Follow platform-specific content policies
- Ensure appropriate use permissions
- Consider cultural and regional differences

### Model Accuracy
- AI detection is not 100% accurate
- Manual review may be required for critical applications
- Adjust confidence thresholds based on use case
- Regular model updates recommended

### Privacy Considerations
- Process only content you have rights to modify
- Inform users about automated content filtering
- Ensure compliance with privacy regulations
- Implement appropriate data handling procedures

---

**Version**: 2.0
**Last Updated**: September 2025
**License**: Educational and Research Use
**Platform Support**: Windows, macOS, Linux
