#!/bin/bash

# Digital Ocean VPS Deployment Script for Ultra-Fast NSFW Detection API
# Optimized for GPU droplets with CUDA support

set -e

echo "🚀 Starting Digital Ocean VPS Deployment..."

# Configuration
APP_NAME="nsfw-detection-api"
DOMAIN="server.superioruniversity.app"  # Replace with your domain
EMAIL="your-email@domain.com"  # Replace with your email
GPU_ENABLED=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    htop \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban

# Install Docker
print_status "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    print_warning "Please log out and back in to use Docker without sudo"
else
    print_status "Docker already installed"
fi

# Install Docker Compose
print_status "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    print_status "Docker Compose already installed"
fi

# Install NVIDIA Docker (for GPU support)
if [[ "$GPU_ENABLED" == true ]]; then
    print_status "Installing NVIDIA Docker for GPU support..."
    
    # Install NVIDIA drivers if not present
    if ! command -v nvidia-smi &> /dev/null; then
        print_status "Installing NVIDIA drivers..."
        sudo apt install -y nvidia-driver-470 nvidia-dkms-470
        print_warning "NVIDIA drivers installed. Please reboot the system and run this script again."
        exit 0
    fi
    
    # Install NVIDIA Docker
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
        && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
        && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    sudo apt update
    sudo apt install -y nvidia-docker2
    
    # Restart Docker to apply changes
    sudo systemctl restart docker
    
    # Test GPU access
    print_status "Testing GPU access..."
    sudo docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi
fi

# Setup firewall
print_status "Configuring firewall..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp  # API port
sudo ufw --force enable

# Setup fail2ban
print_status "Configuring fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create application directory
print_status "Setting up application directory..."
APP_DIR="/home/$USER/$APP_NAME"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or copy application files (assuming they're already on the server)
print_status "Application files should be in: $APP_DIR"
print_warning "Please ensure the following files are present:"
echo "  - Dockerfile"
echo "  - docker-compose.yml"
echo "  - flask_api.py"
echo "  - ultra_fast_processor.py"
echo "  - requirements_production.txt"
echo "  - best.pt (YOLO model file)"

# Create logs directory
mkdir -p logs

# Create environment file
print_status "Creating environment configuration..."
cat > .env << EOF
# Production Configuration
FLASK_ENV=production
FLASK_APP=flask_api.py

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
NVIDIA_VISIBLE_DEVICES=all

# Performance Tuning
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
TORCH_BACKENDS_CUDNN_BENCHMARK=true

# API Configuration
API_PORT=5000
MAX_WORKERS=4
WORKER_CONNECTIONS=1000

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/api.log

# Security
SECRET_KEY=$(openssl rand -hex 32)
EOF

# Install Nginx for reverse proxy
print_status "Installing and configuring Nginx..."
sudo apt install -y nginx

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts for real-time processing
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Large file upload support
        client_max_body_size 50M;
    }

    location /health {
        proxy_pass http://localhost:5000/health;
        access_log off;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# Install and configure SSL with Let's Encrypt
print_status "Installing SSL certificate..."
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive --redirect

# Setup automatic SSL renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

# Create monitoring script
print_status "Creating monitoring script..."
cat > monitor.sh << 'EOF'
#!/bin/bash

# System monitoring script
echo "=== System Status ==="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo "Memory: $(free -h | grep Mem)"
echo "Disk: $(df -h / | tail -1)"

if command -v nvidia-smi &> /dev/null; then
    echo "=== GPU Status ==="
    nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits
fi

echo "=== Docker Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "=== API Health ==="
curl -s http://localhost:5000/health | jq . || echo "API not responding"

echo "=== Recent Logs ==="
docker logs nsfw-detection-api --tail 10
EOF

chmod +x monitor.sh

# Create deployment script
print_status "Creating deployment script..."
cat > deploy.sh << 'EOF'
#!/bin/bash

set -e

echo "🚀 Deploying NSFW Detection API..."

# Stop existing containers
docker-compose down || true

# Pull latest images and rebuild
docker-compose build --no-cache

# Start services
docker-compose up -d

# Wait for services to start
sleep 30

# Check health
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
    echo "API is running at: http://localhost:5000"
    echo "Health check: http://localhost:5000/health"
    echo "Stats: http://localhost:5000/stats"
else
    echo "❌ Deployment failed - API not responding"
    echo "Checking logs..."
    docker-compose logs
    exit 1
fi
EOF

chmod +x deploy.sh

# Create backup script
print_status "Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/$USER/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_NAME="nsfw-detection-api"

mkdir -p $BACKUP_DIR

# Backup application files
tar -czf "$BACKUP_DIR/${APP_NAME}_${DATE}.tar.gz" \
    --exclude='logs/*' \
    --exclude='__pycache__' \
    --exclude='.git' \
    .

# Keep only last 7 backups
ls -t $BACKUP_DIR/${APP_NAME}_*.tar.gz | tail -n +8 | xargs -r rm

echo "Backup created: ${APP_NAME}_${DATE}.tar.gz"
EOF

chmod +x backup.sh

# Setup log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/$APP_NAME << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        docker-compose restart nsfw-api > /dev/null 2>&1 || true
    endscript
}
EOF

# Create systemd service for auto-start
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=NSFW Detection API
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable $APP_NAME.service

# Setup cron jobs
print_status "Setting up cron jobs..."
(crontab -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/monitor.sh >> $APP_DIR/logs/monitor.log 2>&1") | crontab -

# Performance tuning
print_status "Applying performance optimizations..."

# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize network settings
sudo tee -a /etc/sysctl.conf << EOF
# Network optimizations for high-performance API
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 120
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 3
EOF

sudo sysctl -p

print_status "Deployment setup completed!"
print_warning "Next steps:"
echo "1. Ensure your model file (best.pt) is in the application directory"
echo "2. Review and update the .env file with your configuration"
echo "3. Run './deploy.sh' to start the application"
echo "4. Test the API: curl http://$DOMAIN/health"
echo "5. Monitor logs: docker-compose logs -f"

print_status "Useful commands:"
echo "  Start:   docker-compose up -d"
echo "  Stop:    docker-compose down"
echo "  Logs:    docker-compose logs -f"
echo "  Stats:   ./monitor.sh"
echo "  Backup:  ./backup.sh"
