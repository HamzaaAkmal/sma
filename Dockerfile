# Ultra-Performance NSFW Detection API
# Optimized for Digital Ocean GPU Droplets

FROM nvidia/cuda:11.8-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    wget \
    curl \
    git \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libdc1394-22-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Upgrade pip and install wheel
RUN python -m pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements_production.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir -r requirements_production.txt

# Install additional performance packages
RUN pip install --no-cache-dir \
    uvloop \
    gunicorn[gevent] \
    psutil \
    numpy \
    opencv-python-headless \
    pillow-simd \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install TensorRT for maximum GPU performance (if available)
RUN pip install --no-cache-dir nvidia-tensorrt || echo "TensorRT not available, continuing without it"

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Set optimal environment variables for performance
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV CUDA_LAUNCH_BLOCKING=0
ENV TORCH_BACKENDS_CUDNN_BENCHMARK=true

# Start command with Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--worker-class", "gevent", "--worker-connections", "1000", "--max-requests", "10000", "--max-requests-jitter", "1000", "--preload", "--timeout", "120", "flask_api:app"]
