# 🚀 Complete Deployment Guide: Real-Time NSFW Detection System

## 🎯 System Overview

This system provides **sub-10ms latency** NSFW content detection and blurring for video streams through:

1. **Flask API Server**: Ultra-optimized YOLO-based detection API
2. **Chrome Extension**: Real-time frame capture and processing
3. **Digital Ocean VPS**: GPU-accelerated cloud infrastructure

---

## 📋 Prerequisites

### System Requirements:
- Python 3.10+
- CUDA-compatible GPU (recommended)
- Docker & Docker Compose
- Node.js (for Chrome extension development)

### Required Files:
- `best.pt` - Your trained YOLO model
- `test_pytorch_model.py` - Contains `__labels` list
- All generated files from this project

---

## 🏗️ Part 1: VPS Setup & Deployment

### Step 1: Create Digital Ocean GPU Droplet

```bash
# Recommended configuration:
# - GPU-Optimized Droplet: g-8vcpu-32gb-nvidia-v100
# - Ubuntu 22.04 LTS
# - Location: Closest to your users
# - Add SSH key for security
```

### Step 2: Initial Server Setup

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Create non-root user
adduser nsfw-api
usermod -aG sudo nsfw-api
su - nsfw-api

# Clone your project
git clone https://github.com/your-username/nsfw-detection-api.git
cd nsfw-detection-api

# Make deployment script executable
chmod +x deploy_to_vps.sh

# Run deployment script
./deploy_to_vps.sh
```

### Step 3: Upload Model and Configure

```bash
# Upload your YOLO model (from local machine)
scp best.pt nsfw-api@your-vps-ip:~/nsfw-detection-api/

# Update configuration
nano .env

# Edit the following variables:
FLASK_ENV=production
API_PORT=5000
DOMAIN=your-domain.com
EMAIL=your-email@domain.com
```

### Step 4: Deploy Application

```bash
# Deploy the application
./deploy.sh

# Check status
docker-compose ps
docker-compose logs -f nsfw-api

# Test API
curl http://localhost:5000/health
```

### Step 5: Configure SSL and Domain

```bash
# Point your domain to VPS IP address (A record)
# The deployment script automatically sets up SSL with Let's Encrypt

# Verify SSL
curl https://your-domain.com/health
```

---

## 🌐 Part 2: Chrome Extension Development

### Step 1: Prepare Extension Files

```bash
# Create extension directory
mkdir chrome-extension
cd chrome-extension

# Copy all extension files:
# - manifest.json
# - content_script.js
# - background.js
# - popup.html
# - popup.js
# - icons/ (create icon files)
```

### Step 2: Create Extension Icons

Create icons in `icons/` directory:
- `icon16.png` (16x16)
- `icon32.png` (32x32)
- `icon48.png` (48x48)
- `icon128.png` (128x128)

### Step 3: Update API Endpoint

Edit `manifest.json` and update host permissions:

```json
"host_permissions": [
    "https://your-domain.com/*"
]
```

Edit extension files to use your API endpoint:

```javascript
// In content_script.js and background.js
const API_ENDPOINT = 'https://your-domain.com/process-frame-stream';
```

### Step 4: Test Extension Locally

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select your extension directory
6. Test on YouTube, TikTok, etc.

---

## 🔧 Part 3: Performance Optimization

### Server-Side Optimizations

```bash
# Monitor GPU usage
nvidia-smi -l 1

# Monitor API performance
./monitor.sh

# Check logs
docker-compose logs -f nsfw-api

# Performance tuning
nano ultra_fast_processor.py

# Adjust these parameters for your hardware:
RESIZE_FACTOR = 0.4        # Lower = faster but less accurate
CONFIDENCE_THRESHOLD = 0.6  # Higher = fewer false positives
MAX_DETECTIONS = 10        # Lower = faster processing
CACHE_TTL = 0.2           # 200ms cache for repeated frames
```

### Client-Side Optimizations

```javascript
// In content_script.js, adjust these parameters:
frameRate: 15,              // Frames per second to process
compressionQuality: 0.7,    // Image compression (0.3-1.0)
maxQueueSize: 3,           // Limit pending requests
```

---

## 📊 Part 4: Testing & Validation

### API Testing

```bash
# Health check
curl https://your-domain.com/health

# Performance stats
curl https://your-domain.com/stats

# Test frame processing (with base64 image)
curl -X POST https://your-domain.com/process-frame-stream \
  -H "Content-Type: application/json" \
  -d '{"frame":"base64-encoded-image-data"}'
```

### Load Testing

```bash
# Install testing tools
pip install locust

# Create load test script
cat > load_test.py << 'EOF'
import base64
from locust import HttpUser, task, between

class NSFWAPIUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        # Load test image
        with open("test_image.jpg", "rb") as f:
            self.test_frame = base64.b64encode(f.read()).decode()
    
    @task
    def process_frame(self):
        self.client.post("/process-frame-stream", json={
            "frame": self.test_frame,
            "frame_id": f"test_{self.user_id}"
        })
EOF

# Run load test
locust -f load_test.py --host=https://your-domain.com
```

### Extension Testing

1. **YouTube Testing**:
   - Open any video
   - Check browser console for processing logs
   - Monitor extension popup for stats

2. **TikTok Testing**:
   - Scroll through feed
   - Verify frame capture on autoplay videos

3. **Performance Testing**:
   - Monitor CPU/GPU usage
   - Check network usage in DevTools
   - Verify latency in extension popup

---

## 🔍 Part 5: Monitoring & Maintenance

### Performance Monitoring

```bash
# Set up monitoring dashboard
docker-compose up prometheus grafana -d

# Access Grafana at http://your-domain.com:3000
# Default login: admin/admin123

# Key metrics to monitor:
# - API response time
# - GPU utilization
# - Memory usage
# - Error rates
# - Request volume
```

### Log Analysis

```bash
# API logs
docker-compose logs -f nsfw-api

# System logs
tail -f /var/log/syslog

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Backup & Recovery

```bash
# Create backup
./backup.sh

# Restore from backup (if needed)
tar -xzf backups/nsfw-detection-api_DATE.tar.gz
./deploy.sh
```

---

## ⚡ Part 6: Performance Benchmarks

### Expected Performance Metrics

#### GPU-Optimized VPS (NVIDIA V100):
- **Processing Time**: 2-8ms per frame
- **API Response**: <15ms total
- **Throughput**: 100-500 FPS
- **Concurrent Users**: 200-1000

#### CPU-Optimized VPS:
- **Processing Time**: 15-30ms per frame  
- **API Response**: <50ms total
- **Throughput**: 30-100 FPS
- **Concurrent Users**: 50-200

### Optimization Checklist

- [ ] GPU drivers installed and working
- [ ] Model loaded with FP16 precision
- [ ] Frame caching enabled
- [ ] Nginx rate limiting configured
- [ ] SSL/TLS optimized
- [ ] CDN enabled (optional)
- [ ] Monitoring active

---

## 🚨 Part 7: Troubleshooting

### Common Issues & Solutions

#### API Not Responding
```bash
# Check container status
docker-compose ps

# Restart services
docker-compose restart

# Check logs
docker-compose logs nsfw-api
```

#### High Latency
```bash
# Check GPU usage
nvidia-smi

# Adjust resize factor
# Edit ultra_fast_processor.py
RESIZE_FACTOR = 0.3  # Make it smaller for speed

# Restart API
docker-compose restart nsfw-api
```

#### Extension Not Working
1. Check browser console for errors
2. Verify API endpoint in manifest.json
3. Test API directly with curl
4. Check CORS headers

#### Memory Issues
```bash
# Check memory usage
free -h

# Restart containers to clear memory
docker-compose restart

# Reduce batch size in processor
```

---

## 🎯 Part 8: Production Readiness

### Security Checklist

- [ ] SSL certificate configured
- [ ] Firewall rules active
- [ ] Rate limiting enabled
- [ ] API authentication (if needed)
- [ ] Regular security updates
- [ ] Backup strategy in place

### Scaling Considerations

1. **Horizontal Scaling**: Deploy multiple VPS instances with load balancer
2. **Geographic Distribution**: Deploy in multiple regions
3. **Auto-scaling**: Set up based on CPU/GPU usage
4. **CDN Integration**: Cache static resources

### Maintenance Schedule

- **Daily**: Check API health and performance stats
- **Weekly**: Review logs and update dependencies
- **Monthly**: Security patches and backups
- **Quarterly**: Performance optimization review

---

## 📝 Part 9: API Documentation

### Endpoints

#### Health Check
```http
GET /health
Response: {"status": "healthy", "device": "cuda:0"}
```

#### Process Frame
```http
POST /process-frame-stream
Content-Type: application/json

{
  "frame": "base64-encoded-image",
  "frame_id": "unique-identifier",
  "confidence": 0.5
}

Response: {
  "frame": "base64-processed-image",
  "time": 5.2
}
```

#### Statistics
```http
GET /stats
Response: {
  "average_processing_time_ms": 6.5,
  "estimated_fps": 153.8,
  "total_requests": 1024,
  "device": "cuda:0"
}
```

---

## 🎉 Success Metrics

Your deployment is successful when:

- [ ] API responds to health checks
- [ ] Processing time < 10ms for GPU, < 30ms for CPU
- [ ] Chrome extension captures and processes frames
- [ ] No visible delay in video playback
- [ ] Error rate < 1%
- [ ] 99% uptime

---

## 🆘 Support & Resources

### Documentation Links
- [Digital Ocean GPU Droplets](https://docs.digitalocean.com/products/droplets/resources/gpu/)
- [Chrome Extension Development](https://developer.chrome.com/docs/extensions/)
- [YOLO Documentation](https://docs.ultralytics.com/)

### Performance Tuning Resources
- GPU optimization guides
- Docker performance best practices
- Nginx configuration for APIs

Remember: This system is designed for **educational and content moderation purposes**. Ensure compliance with applicable laws and platform terms of service.
