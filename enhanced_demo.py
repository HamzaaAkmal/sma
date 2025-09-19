"""
Comprehensive example script for NSFW content filtering
Shows how to use the enhanced system for different scenarios
"""

import cv2
import time
import os
from config import get_optimized_config, print_current_config
from realtime_video_processor import VideoStreamProcessor, create_youtube_compatible_processor

def demo_image_processing():
    """Demonstrate enhanced image processing"""
    
    print("=" * 60)
    print("ENHANCED IMAGE PROCESSING DEMO")
    print("=" * 60)
    
    # Import enhanced functions
    from test_pytorch_model import test_pytorch_model
    
    # Run the enhanced image processing
    test_pytorch_model()
    
    print("\nImage processing complete!")
    print("Check the output files:")
    print("- download_blurred.jpg (blurred version)")
    print("- download_debug_boxes.jpg (debug with boxes)")

def demo_video_file_processing():
    """Demonstrate video file processing"""
    
    print("=" * 60)
    print("VIDEO FILE PROCESSING DEMO")
    print("=" * 60)
    
    # Create processor optimized for video files
    processor = create_youtube_compatible_processor()
    
    # Example: Process a video file (you would replace with actual video path)
    print("Video processor ready for file processing")
    print("\nTo process a video file, use:")
    print("processor.process_video_file('input_video.mp4', 'output_blurred.mp4')")
    
    # Show configuration being used
    config = get_optimized_config('balanced')
    print("\nUsing configuration:")
    print(f"- Confidence threshold: {config['model']['confidence_threshold']}")
    print(f"- Resize factor: {config['performance']['resize_factor']}")
    print(f"- Blur kernel size: {config['blur']['gaussian_kernel_size']}")

def demo_realtime_webcam():
    """Demonstrate real-time webcam processing"""
    
    print("=" * 60)
    print("REAL-TIME WEBCAM DEMO")
    print("=" * 60)
    
    print("This will start real-time webcam processing with NSFW blurring")
    print("Press 'q' to quit, 's' to save frame")
    
    response = input("Start webcam demo? (y/n): ").lower().strip()
    
    if response == 'y':
        # Create processor optimized for real-time
        processor = VideoStreamProcessor("best.pt")
        
        # Use real-time streaming preset
        config = get_optimized_config('real_time_streaming')
        processor.resize_factor = config['performance']['resize_factor']
        processor.frame_skip = config['performance']['frame_skip']
        
        print("Starting webcam processing...")
        try:
            processor.process_webcam_stream(display=True, confidence_threshold=0.4)
        except KeyboardInterrupt:
            print("Webcam demo stopped by user")
    else:
        print("Webcam demo skipped")

def demo_performance_benchmark():
    """Demonstrate performance benchmarking"""
    
    print("=" * 60)
    print("PERFORMANCE BENCHMARK DEMO")
    print("=" * 60)
    
    # Test different presets
    presets = ['maximum_speed', 'balanced', 'maximum_quality']
    
    # Load test image
    test_image_path = "download.jpeg"
    if not os.path.exists(test_image_path):
        print(f"Test image {test_image_path} not found")
        return
    
    test_frame = cv2.imread(test_image_path)
    
    print(f"Testing performance with image: {test_image_path}")
    print(f"Image size: {test_frame.shape}")
    print()
    
    results = {}
    
    for preset in presets:
        print(f"Testing {preset} preset...")
        
        # Create processor with this preset
        processor = VideoStreamProcessor("best.pt")
        
        # Apply preset configuration
        config = get_optimized_config(preset)
        processor.resize_factor = config['performance']['resize_factor']
        
        if not processor.initialize_model():
            print(f"Failed to initialize model for {preset}")
            continue
        
        # Benchmark processing time
        num_frames = 20
        start_time = time.time()
        
        for i in range(num_frames):
            processed_frame = processor.process_single_frame(test_frame, 
                                                           config['model']['confidence_threshold'])
        
        total_time = time.time() - start_time
        avg_time_per_frame = total_time / num_frames
        estimated_fps = 1.0 / avg_time_per_frame
        
        results[preset] = {
            'avg_time_per_frame': avg_time_per_frame,
            'estimated_fps': estimated_fps,
            'total_time': total_time
        }
        
        print(f"  Average time per frame: {avg_time_per_frame:.3f}s")
        print(f"  Estimated FPS: {estimated_fps:.1f}")
        print()
    
    # Summary
    print("BENCHMARK RESULTS SUMMARY:")
    print("-" * 40)
    for preset, data in results.items():
        fps = data['estimated_fps']
        realtime_capable = "✓" if fps >= 20 else "✗"
        print(f"{preset:20}: {fps:5.1f} FPS {realtime_capable}")
    
    print("\n✓ = Real-time capable (20+ FPS)")
    print("✗ = Not real-time capable")

def demo_configuration_options():
    """Demonstrate configuration options"""
    
    print("=" * 60)
    print("CONFIGURATION OPTIONS DEMO")
    print("=" * 60)
    
    print("Available presets:")
    presets = ['maximum_quality', 'balanced', 'maximum_speed', 'real_time_streaming']
    
    for i, preset in enumerate(presets, 1):
        print(f"{i}. {preset}")
    
    print("\nShowing 'balanced' preset configuration:")
    config = get_optimized_config('balanced')
    print_current_config(config)
    
    print("\nYou can customize these settings in config.py")
    print("Or create your own presets for specific use cases")

def demo_hardware_optimization():
    """Demonstrate hardware-based optimization"""
    
    print("=" * 60)
    print("HARDWARE OPTIMIZATION DEMO")
    print("=" * 60)
    
    # Example hardware configurations
    hardware_examples = [
        {
            'name': 'Gaming PC',
            'cpu_cores': 8,
            'ram_gb': 32,
            'gpu_memory_gb': 8
        },
        {
            'name': 'Standard Laptop',
            'cpu_cores': 4,
            'ram_gb': 8,
            'gpu_memory_gb': 2
        },
        {
            'name': 'Budget System',
            'cpu_cores': 2,
            'ram_gb': 4,
            'gpu_memory_gb': 0
        }
    ]
    
    for hw in hardware_examples:
        print(f"\nOptimized config for {hw['name']}:")
        print(f"Hardware: {hw['cpu_cores']} cores, {hw['ram_gb']}GB RAM, {hw['gpu_memory_gb']}GB GPU")
        
        config = get_optimized_config('balanced', hw)
        
        print(f"  Max workers: {config['performance']['max_workers']}")
        print(f"  Queue size: {config['performance']['max_queue_size']}")
        print(f"  Use GPU: {config['performance']['use_gpu']}")
        print(f"  Resize factor: {config['performance']['resize_factor']}")

def main_menu():
    """Main demonstration menu"""
    
    print("🔞 NSFW Content Filter - Enhanced System Demo")
    print("=" * 60)
    print()
    print("This enhanced system provides:")
    print("✓ Pixel-perfect blurring with smooth edges")
    print("✓ Multi-stage blur (Gaussian + Pixelation + Motion)")
    print("✓ Real-time performance optimization")
    print("✓ Large-scale video processing support")
    print("✓ YouTube-compatible processing")
    print("✓ Hardware-specific optimizations")
    print()
    
    while True:
        print("\nSelect a demo:")
        print("1. Enhanced Image Processing")
        print("2. Video File Processing Setup")
        print("3. Real-time Webcam Demo")
        print("4. Performance Benchmark")
        print("5. Configuration Options")
        print("6. Hardware Optimization")
        print("7. Exit")
        
        try:
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == '1':
                demo_image_processing()
            elif choice == '2':
                demo_video_file_processing()
            elif choice == '3':
                demo_realtime_webcam()
            elif choice == '4':
                demo_performance_benchmark()
            elif choice == '5':
                demo_configuration_options()
            elif choice == '6':
                demo_hardware_optimization()
            elif choice == '7':
                print("Exiting demo. Thank you!")
                break
            else:
                print("Invalid choice. Please select 1-7.")
                
        except KeyboardInterrupt:
            print("\nDemo interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main_menu()
