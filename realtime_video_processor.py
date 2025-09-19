"""
Real-time Video Processing for NSFW Content Blurring
Optimized for large-scale and YouTube video processing
"""

import cv2
import numpy as np
import threading
import queue
import time
from collections import deque
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class VideoStreamProcessor:
    """High-performance video stream processor for real-time NSFW blurring"""
    
    def __init__(self, model_path, max_workers=4):
        self.model_path = model_path
        self.model = None
        self.max_workers = max_workers
        
        # Performance optimization settings
        self.input_queue = queue.Queue(maxsize=10)
        self.output_queue = queue.Queue(maxsize=10)
        self.frame_skip = 1  # Process every nth frame for speed
        self.resize_factor = 1.0  # Resize frames for faster processing
        
        # Cache for detected regions to avoid reprocessing
        self.detection_cache = deque(maxlen=30)
        self.cache_threshold = 0.7  # Similarity threshold for using cache
        
        # Statistics tracking
        self.fps_counter = 0
        self.processing_times = deque(maxlen=100)
        self.last_fps_time = time.time()
        
        # Threading control
        self.processing_active = False
        self.worker_threads = []
        
        # NSFW classes to blur
        self.nudity_classes = [
            "BUTTOCKS_EXPOSED",
            "FEMALE_BREAST_EXPOSED", 
            "FEMALE_GENITALIA_EXPOSED",
            "MALE_GENITALIA_EXPOSED",
            "ANUS_EXPOSED"
        ]
        
    def initialize_model(self):
        """Initialize the YOLO model"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            self.model.overrides['verbose'] = False  # Reduce output
            print("Model initialized for video processing")
            return True
        except Exception as e:
            print(f"Failed to initialize model: {e}")
            return False
    
    def process_video_file(self, input_path, output_path=None, confidence_threshold=0.4):
        """Process a video file with NSFW blurring"""
        
        if not self.initialize_model():
            return False
            
        # Open video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error opening video: {input_path}")
            return False
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Processing video: {width}x{height} @ {fps}FPS, {total_frames} frames")
        
        # Setup video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Process frames
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Skip frames for performance if needed
                if frame_count % self.frame_skip != 0:
                    if writer:
                        writer.write(frame)
                    continue
                
                # Process frame
                processed_frame = self.process_single_frame(frame, confidence_threshold)
                
                # Write processed frame
                if writer:
                    writer.write(processed_frame)
                
                # Progress update
                if frame_count % (fps * 5) == 0:  # Every 5 seconds
                    elapsed = time.time() - start_time
                    progress = (frame_count / total_frames) * 100
                    estimated_total = (elapsed / frame_count) * total_frames
                    remaining = estimated_total - elapsed
                    
                    print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames}) "
                          f"- {remaining/60:.1f}min remaining")
        
        finally:
            cap.release()
            if writer:
                writer.release()
        
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time
        
        print(f"Video processing complete!")
        print(f"Processed {frame_count} frames in {total_time:.1f}s")
        print(f"Average FPS: {avg_fps:.1f}")
        
        return True
    
    def process_single_frame(self, frame, confidence_threshold=0.4):
        """Process a single frame with optimized blurring"""
        
        process_start = time.time()
        
        # Resize frame if needed for faster processing
        if self.resize_factor != 1.0:
            original_frame = frame.copy()
            height, width = frame.shape[:2]
            new_width = int(width * self.resize_factor)
            new_height = int(height * self.resize_factor)
            frame = cv2.resize(frame, (new_width, new_height))
        
        # Run inference
        results = self.model(frame, verbose=False)
        
        # Extract blur regions
        blur_regions = []
        
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    coords = box.xyxy[0].tolist()
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    
                    # Get class name from the labels
                    from test_pytorch_model import __labels
                    if cls < len(__labels):
                        class_name = __labels[cls]
                        
                        if class_name in self.nudity_classes and conf > confidence_threshold:
                            x1, y1, x2, y2 = map(int, coords)
                            
                            # Scale coordinates back if frame was resized
                            if self.resize_factor != 1.0:
                                scale = 1.0 / self.resize_factor
                                x1, y1, x2, y2 = [int(coord * scale) for coord in [x1, y1, x2, y2]]
                            
                            blur_regions.append((x1, y1, x2, y2, class_name, conf))
        
        # Use original frame for blurring if it was resized
        if self.resize_factor != 1.0:
            frame = original_frame
        
        # Apply optimized blurring
        if blur_regions:
            frame = self.apply_fast_blur(frame, blur_regions)
        
        # Track processing time
        processing_time = time.time() - process_start
        self.processing_times.append(processing_time)
        
        return frame
    
    def apply_fast_blur(self, frame, blur_regions):
        """Apply fast blur optimized for real-time processing"""
        
        for x1, y1, x2, y2, class_name, conf in blur_regions:
            
            # Ensure coordinates are within frame bounds
            height, width = frame.shape[:2]
            x1 = max(0, min(x1, width))
            y1 = max(0, min(y1, height))
            x2 = max(x1, min(x2, width))
            y2 = max(y1, min(y2, height))
            
            if x2 > x1 and y2 > y1:
                # Extract ROI
                roi = frame[y1:y2, x1:x2]
                
                if roi.size > 0:
                    # Multi-level blur for better privacy
                    
                    # Level 1: Gaussian blur
                    blurred = cv2.GaussianBlur(roi, (15, 15), 5)
                    
                    # Level 2: Pixelation
                    h, w = roi.shape[:2]
                    pixel_size = max(4, min(w//8, h//8))  # Adaptive pixel size
                    
                    if w > pixel_size and h > pixel_size:
                        # Downscale
                        small = cv2.resize(blurred, (w // pixel_size, h // pixel_size))
                        # Upscale with nearest neighbor
                        pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
                        
                        # Apply back to frame
                        frame[y1:y2, x1:x2] = pixelated
        
        return frame
    
    def process_webcam_stream(self, camera_index=0, display=True, confidence_threshold=0.4):
        """Process live webcam stream with real-time blurring"""
        
        if not self.initialize_model():
            return False
        
        # Open webcam
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Error opening camera {camera_index}")
            return False
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("Starting webcam stream processing (Press 'q' to quit)")
        print("Press 's' to save current frame")
        
        frame_count = 0
        fps_start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                processed_frame = self.process_single_frame(frame, confidence_threshold)
                
                # Calculate FPS
                frame_count += 1
                if frame_count % 30 == 0:  # Update every 30 frames
                    fps_end_time = time.time()
                    fps = 30 / (fps_end_time - fps_start_time)
                    fps_start_time = fps_end_time
                    
                    # Add FPS text to frame
                    cv2.putText(processed_frame, f"FPS: {fps:.1f}", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Display frame if requested
                if display:
                    cv2.imshow('NSFW Filter - Live Stream', processed_frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        # Save current frame
                        timestamp = int(time.time())
                        filename = f"webcam_capture_{timestamp}.jpg"
                        cv2.imwrite(filename, processed_frame)
                        print(f"Frame saved as: {filename}")
        
        finally:
            cap.release()
            if display:
                cv2.destroyAllWindows()
        
        return True
    
    def get_performance_stats(self):
        """Get performance statistics"""
        if not self.processing_times:
            return {}
        
        avg_time = sum(self.processing_times) / len(self.processing_times)
        max_time = max(self.processing_times)
        min_time = min(self.processing_times)
        
        return {
            'average_processing_time': avg_time,
            'max_processing_time': max_time,
            'min_processing_time': min_time,
            'estimated_fps': 1.0 / avg_time if avg_time > 0 else 0,
            'total_frames_processed': len(self.processing_times)
        }

def create_youtube_compatible_processor():
    """Create a processor optimized for YouTube-style videos"""
    
    processor = VideoStreamProcessor("best.pt", max_workers=6)
    
    # Optimize for YouTube common resolutions
    processor.frame_skip = 1  # Process every frame for quality
    processor.resize_factor = 0.75  # Slight downscale for speed
    
    return processor

def test_video_processing():
    """Test video processing capabilities"""
    
    print("Video Processing Test")
    print("=" * 40)
    
    # Test with different modes
    processor = create_youtube_compatible_processor()
    
    print("\nSelect test mode:")
    print("1. Process video file")
    print("2. Test webcam stream")
    print("3. Performance benchmark")
    
    try:
        choice = input("Enter choice (1/2/3): ").strip()
        
        if choice == '1':
            # For video file processing, you would specify the input file
            print("Video file processing ready")
            print("Usage: processor.process_video_file('input.mp4', 'output.mp4')")
            
        elif choice == '2':
            # Test webcam
            print("Starting webcam test...")
            processor.process_webcam_stream(display=True)
            
        elif choice == '3':
            # Performance benchmark
            print("Running performance benchmark...")
            
            # Load test image
            test_frame = cv2.imread("download.jpeg")
            if test_frame is None:
                print("Test image not found")
                return
            
            # Process multiple frames
            for i in range(50):
                processor.process_single_frame(test_frame)
                if i % 10 == 0:
                    print(f"Processed {i+1}/50 frames...")
            
            # Show stats
            stats = processor.get_performance_stats()
            print("\nPerformance Statistics:")
            print(f"Average processing time: {stats['average_processing_time']:.3f}s")
            print(f"Estimated FPS: {stats['estimated_fps']:.1f}")
            print(f"Min processing time: {stats['min_processing_time']:.3f}s")
            print(f"Max processing time: {stats['max_processing_time']:.3f}s")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_video_processing()
