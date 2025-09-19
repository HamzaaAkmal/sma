# Enhanced NSFW Content Filter

An advanced, real-time NSFW content detection and blurring system optimized for large-scale video processing and live streaming applications.

## 🚀 Key Enhancements

### Pixel-Perfect Blurring
- **Multi-stage blur algorithm**: Gaussian blur + Pixelation + Motion blur
- **Smooth edge blending**: Gradual transitions to avoid harsh edges
- **Adaptive blur intensity**: Different blur levels based on content type
- **Optimized privacy protection**: Multiple layers ensure complete obscuring

### Real-Time Performance
- **Optimized for 20+ FPS**: Real-time processing capabilities
- **Multi-threading support**: Parallel processing for better performance
- **Frame skipping options**: Skip frames when needed for speed
- **GPU acceleration**: CUDA support when available
- **Memory optimization**: Efficient memory usage for long sessions

### Large-Scale Video Processing
- **YouTube-compatible**: Optimized for common video resolutions
- **Batch processing**: Handle multiple videos efficiently
- **Progress tracking**: Real-time progress updates for long videos
- **Quality presets**: Choose between speed and quality
- **Hardware auto-optimization**: Automatically adjust settings based on your hardware

## 📁 File Structure

```
├── test_pytorch_model.py          # Enhanced main processing script
├── realtime_video_processor.py    # Real-time video processing class
├── config.py                      # Configuration and optimization settings
├── enhanced_demo.py               # Comprehensive demo script
├── best.pt                        # YOLO model file
└── README.md                      # This file
```

## 🔧 Configuration Presets

### Maximum Quality
- Process every frame at full resolution
- Strongest blur effects for maximum privacy
- Best for static images or when quality is priority
- **Speed**: ~5-10 FPS

### Balanced (Recommended)
- Good balance between quality and speed
- Suitable for most video processing tasks
- **Speed**: ~15-25 FPS

### Maximum Speed
- Optimized for real-time processing
- Some quality trade-offs for better performance
- **Speed**: ~25-35 FPS

### Real-Time Streaming
- Optimized for live streams and webcams
- Frame dropping when processing is slow
- **Speed**: ~30+ FPS

## 🚀 Quick Start

### 1. Basic Image Processing
```python
from test_pytorch_model import test_pytorch_model

# Process an image with enhanced blurring
test_pytorch_model()
```

### 2. Real-Time Webcam
```python
from realtime_video_processor import VideoStreamProcessor

processor = VideoStreamProcessor("best.pt")
processor.process_webcam_stream(display=True)
```

### 3. Video File Processing
```python
from realtime_video_processor import create_youtube_compatible_processor

processor = create_youtube_compatible_processor()
processor.process_video_file("input.mp4", "output_blurred.mp4")
```

### 4. Run Complete Demo
```python
python enhanced_demo.py
```

## ⚙️ Advanced Configuration

### Custom Hardware Optimization
```python
from config import get_optimized_config

# Define your hardware
hardware_info = {
    'cpu_cores': 8,
    'ram_gb': 16,
    'gpu_memory_gb': 6
}

# Get optimized configuration
config = get_optimized_config('balanced', hardware_info)
```

### Custom Blur Settings
```python
# Edit config.py to customize blur settings
BLUR_CONFIG = {
    'gaussian_kernel_size': 31,  # Larger = more blur
    'pixel_size': 8,             # Larger = more pixelation
    'use_multi_stage': True,     # Enable multi-stage blurring
    'edge_padding': 5,           # Smooth edge blending
}
```

## 📊 Performance Optimization Tips

### For Real-Time Processing (30+ FPS)
1. Use `real_time_streaming` preset
2. Lower confidence threshold (0.5+)
3. Reduce resize factor (0.6-0.7)
4. Enable frame skipping if needed
5. Use GPU acceleration

### For Maximum Quality
1. Use `maximum_quality` preset
2. Lower confidence threshold (0.3)
3. Full resolution processing (resize_factor = 1.0)
4. Enable multi-stage blurring
5. Process every frame

### For YouTube Videos
1. Use `balanced` preset
2. Enable hardware auto-optimization
3. Set appropriate target resolution
4. Use batch processing for multiple videos

## 🎯 Use Cases

### Live Streaming Platforms
- **Twitch/YouTube Live**: Real-time content filtering
- **Video Calls**: Webcam privacy protection
- **Social Media**: Live video content moderation

### Video Processing
- **Content Moderation**: Automated NSFW detection for platforms
- **Family-Safe Content**: Create safe versions of videos
- **Educational Use**: Filter content for educational environments

### Development Integration
- **APIs**: Integrate into existing video processing pipelines
- **Mobile Apps**: Embed in mobile applications
- **Web Services**: Deploy as a web service

## 🔧 Requirements

```bash
pip install ultralytics opencv-python numpy torch
```

### Optional for GPU Acceleration
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 📈 Performance Benchmarks

Tested on RTX 3070, Intel i7-10700K, 32GB RAM:

| Preset | Resolution | FPS | Quality | Use Case |
|--------|------------|-----|---------|----------|
| Maximum Speed | 720p | 35 FPS | Good | Live streaming |
| Balanced | 1080p | 22 FPS | High | Most videos |
| Maximum Quality | 1080p | 12 FPS | Excellent | Static images |
| Real-Time Streaming | 720p | 45 FPS | Good | Webcam/Live |

## 🛠️ Troubleshooting

### Low FPS Performance
1. Check GPU availability: `torch.cuda.is_available()`
2. Reduce resize factor in config
3. Lower confidence threshold
4. Enable frame skipping
5. Use `maximum_speed` preset

### High Memory Usage
1. Reduce queue sizes in config
2. Lower cache size
3. Process smaller batches
4. Reduce max_workers

### Quality Issues
1. Increase blur kernel size
2. Enable multi-stage blurring
3. Adjust confidence threshold
4. Increase edge padding

## 🔄 Integration Examples

### Web API Integration
```python
from flask import Flask, request, jsonify
from realtime_video_processor import VideoStreamProcessor

app = Flask(__name__)
processor = VideoStreamProcessor("best.pt")

@app.route('/process_video', methods=['POST'])
def process_video():
    # Your video processing logic here
    pass
```

### Batch Processing Script
```python
import os
from realtime_video_processor import create_youtube_compatible_processor

processor = create_youtube_compatible_processor()

# Process all videos in a directory
video_dir = "input_videos"
output_dir = "output_videos"

for filename in os.listdir(video_dir):
    if filename.endswith(('.mp4', '.avi', '.mov')):
        input_path = os.path.join(video_dir, filename)
        output_path = os.path.join(output_dir, f"filtered_{filename}")
        processor.process_video_file(input_path, output_path)
```

## 📝 License

This project is for educational and research purposes. Make sure to comply with relevant laws and platform policies when using for content moderation.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Run the performance benchmark
3. Try different configuration presets
4. Test with the enhanced demo script

---

**Note**: This system is designed for content moderation and privacy protection. Always ensure compliance with local laws and platform policies when deploying in production environments.
