"""
Configuration settings for optimized NSFW detection and blurring
Adjust these settings based on your hardware and quality requirements
"""

# Model Configuration
MODEL_CONFIG = {
    'model_path': 'best.pt',
    'confidence_threshold': 0.4,  # Minimum confidence for detection
    'nms_threshold': 0.45,  # Non-maximum suppression threshold
    'max_detections': 100,  # Maximum detections per frame
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    # Frame processing
    'frame_skip': 1,  # Process every nth frame (1 = every frame)
    'resize_factor': 0.8,  # Resize frames for faster processing (0.5-1.0)
    'max_workers': 4,  # Number of worker threads
    
    # GPU settings (if available)
    'use_gpu': True,
    'gpu_device': 0,  # GPU device index
    
    # Memory management
    'max_queue_size': 10,
    'cache_size': 30,  # Detection cache size
}

# Blur Configuration
BLUR_CONFIG = {
    # Blur intensity settings
    'gaussian_kernel_size': 21,  # Must be odd number (15, 21, 31, etc.)
    'gaussian_sigma': 8,  # Blur strength
    
    # Pixelation settings
    'pixel_size': 6,  # Pixel block size for pixelation effect
    'adaptive_pixel_size': True,  # Adjust pixel size based on region size
    
    # Edge blending
    'use_smooth_edges': True,
    'edge_padding': 3,  # Pixels to extend blur region for smooth edges
    'blend_alpha': 0.8,  # Blending strength (0.0-1.0)
    
    # Multi-stage blurring
    'use_multi_stage': True,
    'stages': [
        {'type': 'gaussian', 'kernel': 15, 'sigma': 5},
        {'type': 'pixelate', 'size': 6},
        {'type': 'motion_blur', 'kernel': 7}
    ]
}

# Video Processing Configuration
VIDEO_CONFIG = {
    # Input/Output settings
    'input_resolution': (1920, 1080),  # Target input resolution
    'output_quality': 85,  # JPEG quality for output (1-100)
    'codec': 'mp4v',  # Video codec
    
    # Real-time processing
    'target_fps': 30,  # Target FPS for real-time processing
    'buffer_size': 5,  # Frame buffer size
    'drop_frames_if_slow': True,  # Drop frames if processing is too slow
    
    # YouTube optimization
    'youtube_optimized': True,
    'common_resolutions': [
        (1920, 1080),  # 1080p
        (1280, 720),   # 720p
        (854, 480),    # 480p
    ]
}

# Quality vs Performance Presets
PRESETS = {
    'maximum_quality': {
        'frame_skip': 1,
        'resize_factor': 1.0,
        'gaussian_kernel_size': 31,
        'pixel_size': 8,
        'use_multi_stage': True,
        'confidence_threshold': 0.3,
    },
    
    'balanced': {
        'frame_skip': 1,
        'resize_factor': 0.8,
        'gaussian_kernel_size': 21,
        'pixel_size': 6,
        'use_multi_stage': True,
        'confidence_threshold': 0.4,
    },
    
    'maximum_speed': {
        'frame_skip': 2,
        'resize_factor': 0.6,
        'gaussian_kernel_size': 15,
        'pixel_size': 4,
        'use_multi_stage': False,
        'confidence_threshold': 0.5,
    },
    
    'real_time_streaming': {
        'frame_skip': 1,
        'resize_factor': 0.7,
        'gaussian_kernel_size': 15,
        'pixel_size': 5,
        'use_multi_stage': False,
        'confidence_threshold': 0.45,
        'drop_frames_if_slow': True,
    }
}

# Hardware-specific optimizations
HARDWARE_OPTIMIZATIONS = {
    'cpu_cores': 8,  # Number of CPU cores available
    'ram_gb': 16,    # Available RAM in GB
    'gpu_memory_gb': 8,  # GPU memory in GB
    
    # Auto-adjust settings based on hardware
    'auto_optimize': True,
    'performance_target': 'real_time',  # 'quality', 'balanced', 'real_time'
}

def get_optimized_config(preset='balanced', hardware_info=None):
    """
    Get optimized configuration based on preset and hardware
    
    Args:
        preset: 'maximum_quality', 'balanced', 'maximum_speed', 'real_time_streaming'
        hardware_info: Dict with 'cpu_cores', 'ram_gb', 'gpu_memory_gb'
    
    Returns:
        Dict with optimized configuration
    """
    
    config = {
        'model': MODEL_CONFIG.copy(),
        'performance': PERFORMANCE_CONFIG.copy(),
        'blur': BLUR_CONFIG.copy(),
        'video': VIDEO_CONFIG.copy(),
    }
    
    # Apply preset
    if preset in PRESETS:
        preset_config = PRESETS[preset]
        
        # Update relevant sections
        config['performance']['frame_skip'] = preset_config.get('frame_skip', 1)
        config['performance']['resize_factor'] = preset_config.get('resize_factor', 0.8)
        config['blur']['gaussian_kernel_size'] = preset_config.get('gaussian_kernel_size', 21)
        config['blur']['pixel_size'] = preset_config.get('pixel_size', 6)
        config['blur']['use_multi_stage'] = preset_config.get('use_multi_stage', True)
        config['model']['confidence_threshold'] = preset_config.get('confidence_threshold', 0.4)
        
        if 'drop_frames_if_slow' in preset_config:
            config['video']['drop_frames_if_slow'] = preset_config['drop_frames_if_slow']
    
    # Auto-optimize based on hardware
    if hardware_info and HARDWARE_OPTIMIZATIONS['auto_optimize']:
        
        cpu_cores = hardware_info.get('cpu_cores', 4)
        ram_gb = hardware_info.get('ram_gb', 8)
        gpu_memory_gb = hardware_info.get('gpu_memory_gb', 0)
        
        # Adjust worker threads based on CPU cores
        config['performance']['max_workers'] = min(cpu_cores, 8)
        
        # Adjust queue sizes based on RAM
        if ram_gb >= 16:
            config['performance']['max_queue_size'] = 15
            config['performance']['cache_size'] = 50
        elif ram_gb >= 8:
            config['performance']['max_queue_size'] = 10
            config['performance']['cache_size'] = 30
        else:
            config['performance']['max_queue_size'] = 5
            config['performance']['cache_size'] = 15
        
        # GPU optimizations
        if gpu_memory_gb >= 4:
            config['performance']['use_gpu'] = True
            config['performance']['resize_factor'] = min(1.0, config['performance']['resize_factor'] + 0.1)
        else:
            config['performance']['use_gpu'] = False
            config['performance']['resize_factor'] = max(0.5, config['performance']['resize_factor'] - 0.1)
    
    return config

def print_current_config(config):
    """Print current configuration in a readable format"""
    
    print("Current Configuration:")
    print("=" * 50)
    
    print("\nModel Settings:")
    for key, value in config['model'].items():
        print(f"  {key}: {value}")
    
    print("\nPerformance Settings:")
    for key, value in config['performance'].items():
        print(f"  {key}: {value}")
    
    print("\nBlur Settings:")
    for key, value in config['blur'].items():
        if key != 'stages':
            print(f"  {key}: {value}")
    
    print("\nVideo Settings:")
    for key, value in config['video'].items():
        if key != 'common_resolutions':
            print(f"  {key}: {value}")

def save_config_to_file(config, filename='nsfw_filter_config.json'):
    """Save configuration to JSON file"""
    import json
    
    try:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {filename}")
    except Exception as e:
        print(f"Error saving configuration: {e}")

def load_config_from_file(filename='nsfw_filter_config.json'):
    """Load configuration from JSON file"""
    import json
    
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
        print(f"Configuration loaded from {filename}")
        return config
    except FileNotFoundError:
        print(f"Configuration file {filename} not found, using defaults")
        return get_optimized_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return get_optimized_config()

if __name__ == "__main__":
    # Example usage
    print("NSFW Filter Configuration Examples")
    print("=" * 50)
    
    # Show different presets
    presets_to_show = ['balanced', 'maximum_speed', 'real_time_streaming']
    
    for preset in presets_to_show:
        print(f"\n{preset.upper()} PRESET:")
        print("-" * 30)
        config = get_optimized_config(preset)
        
        # Show key settings
        print(f"Frame skip: {config['performance']['frame_skip']}")
        print(f"Resize factor: {config['performance']['resize_factor']}")
        print(f"Blur kernel: {config['blur']['gaussian_kernel_size']}")
        print(f"Confidence threshold: {config['model']['confidence_threshold']}")
    
    # Save example config
    example_config = get_optimized_config('balanced')
    save_config_to_file(example_config, 'example_config.json')
