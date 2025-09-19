import os
import cv2
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor
import time

# Labels from best.pt model
__labels = [
    "FEMALE_GENITALIA_COVERED",
    "FACE_FEMALE",
    "BUTTOCKS_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_BREAST_EXPOSED",
    "ANUS_EXPOSED",
    "FEET_EXPOSED",
    "BELLY_COVERED",
    "FEET_COVERED",
    "ARMPITS_COVERED",
    "ARMPITS_EXPOSED",
    "FACE_MALE",
    "BELLY_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_COVERED",
    "FEMALE_BREAST_COVERED",
    "BUTTOCKS_COVERED",
]

def get_labels():
    """Get the NSFW detection labels"""
    return __labels

def test_pytorch_model():
    """Test using PyTorch/Ultralytics YOLO model"""
    
    # Check if files exist
    model_path = "best.pt"
    image_path = "images.jpeg"
    
    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found")
        return
    
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        return
    
    try:
        # Try to import ultralytics
        from ultralytics import YOLO
        print("Successfully imported ultralytics YOLO")
        
        # Load the model
        print(f"Loading model from {model_path}...")
        model = YOLO(model_path)
        
        # Run inference
        print(f"Running inference on {image_path}...")
        results = model(image_path)
        
        # Process results
        print(f"\nAnalysis Results:")
        print("-" * 50)
        
        nudity_detected = False
        
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                print(f"Found {len(boxes)} detections:")
                
                for i, box in enumerate(boxes):
                    # Get box coordinates
                    coords = box.xyxy[0].tolist()  # x1, y1, x2, y2
                    conf = box.conf[0].item()  # confidence
                    cls = int(box.cls[0].item())  # class index
                    
                    # Convert to width/height format
                    x1, y1, x2, y2 = coords
                    w = x2 - x1
                    h = y2 - y1
                    
                    # Get class name
                    class_name = __labels[cls] if cls < len(__labels) else f"CLASS_{cls}"
                    
                    # Check if this is a nudity class
                    nudity_classes = [
                        "BUTTOCKS_EXPOSED",
                        "FEMALE_BREAST_EXPOSED", 
                        "FEMALE_GENITALIA_EXPOSED",
                        "MALE_GENITALIA_EXPOSED",
                        "ANUS_EXPOSED"
                    ]
                    
                    is_nudity = class_name in nudity_classes
                    if is_nudity and conf > 0.3:
                        nudity_detected = True
                    
                    status = "🔞 NUDITY" if is_nudity else "✓ Safe"
                    
                    print(f"Detection {i+1}: {status}")
                    print(f"  Class: {class_name}")
                    print(f"  Confidence: {conf:.4f}")
                    print(f"  Box: [{int(x1)}, {int(y1)}, {int(w)}, {int(h)}]")
                    print()
                
                print(f"\n{'='*50}")
                if nudity_detected:
                    print("🔞 NUDITY DETECTED - Creating blurred version...")
                else:
                    print("✓ No significant nudity detected")
                print(f"{'='*50}")
                
                # Create blurred version (main output)
                create_blurred_image(image_path, results, "download_blurred.jpg")
                
                # Create debug visualization with boxes
                create_visualization_with_boxes(image_path, results, "download_debug_boxes.jpg")
            else:
                print("No detections found")
        
    except ImportError:
        print("Ultralytics not available. Trying torch directly...")
        try_torch_direct(model_path, image_path)
    except Exception as e:
        print(f"Error with ultralytics: {e}")
        import traceback
        traceback.print_exc()

def try_torch_direct(model_path, image_path):
    """Try loading with torch directly"""
    try:
        import torch
        print("Trying to load with PyTorch directly...")
        
        # Load the model
        model = torch.load(model_path, map_location='cpu')
        print("Model loaded successfully!")
        print(f"Model type: {type(model)}")
        
        if hasattr(model, 'names'):
            print(f"Model classes: {model.names}")
        
        # For now, just show that we can load the model
        print("PyTorch model loaded successfully!")
        print("You may need to implement inference manually or install ultralytics.")
        
    except ImportError:
        print("PyTorch not available. Please install torch or ultralytics.")
    except Exception as e:
        print(f"Error loading model with torch: {e}")

def create_blurred_image(image_path, results, output_path):
    """Create image with nudity areas blurred using optimized techniques"""
    try:
        # Load the image
        img = cv2.imread(image_path)
        
        # Define nudity classes that should be blurred
        nudity_classes = [
            "BUTTOCKS_EXPOSED",
            "FEMALE_BREAST_EXPOSED", 
            "FEMALE_GENITALIA_EXPOSED",
            "MALE_GENITALIA_EXPOSED",
            "ANUS_EXPOSED"
        ]
        
        blur_count = 0
        
        # Pre-create blur masks for better performance
        blur_regions = []
        
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    coords = box.xyxy[0].tolist()
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    
                    x1, y1, x2, y2 = map(int, coords)
                    
                    # Get class name
                    class_name = __labels[cls] if cls < len(__labels) else f"CLASS_{cls}"
                    
                    # Only blur if it's a nudity class and confidence is high enough
                    if class_name in nudity_classes and conf > 0.3:
                        print(f"Preparing blur for {class_name} area (confidence: {conf:.3f})")
                        blur_regions.append((x1, y1, x2, y2, class_name, conf))
                    else:
                        print(f"Detected {class_name} (confidence: {conf:.3f}) - not blurring")
        
        # Apply optimized blurring
        if blur_regions:
            img = apply_optimized_blur(img, blur_regions)
            blur_count = len(blur_regions)
        
        # Save result
        cv2.imwrite(output_path, img)
        print(f"Blurred image saved as: {output_path}")
        print(f"Total areas blurred: {blur_count}")
        
    except Exception as e:
        print(f"Error creating blurred image: {e}")

def apply_optimized_blur(img, blur_regions):
    """Apply pixel-perfect optimized blurring for real-time performance"""
    
    # Create a copy to work with
    result_img = img.copy()
    
    # Create a combined mask for all blur regions
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    # Mark all blur regions in the mask
    for x1, y1, x2, y2, class_name, conf in blur_regions:
        # Add padding for better edge blending
        padding = 5
        x1_pad = max(0, x1 - padding)
        y1_pad = max(0, y1 - padding)
        x2_pad = min(img.shape[1], x2 + padding)
        y2_pad = min(img.shape[0], y2 + padding)
        
        # Create smooth transition mask
        roi_mask = create_smooth_mask(x2_pad - x1_pad, y2_pad - y1_pad, padding)
        mask[y1_pad:y2_pad, x1_pad:x2_pad] = np.maximum(
            mask[y1_pad:y2_pad, x1_pad:x2_pad], 
            roi_mask
        )
    
    # Apply different blur techniques based on content
    blurred_img = apply_multi_stage_blur(img)
    
    # Use the mask to blend original and blurred images
    mask_3d = np.stack([mask] * 3, axis=2).astype(np.float32) / 255.0
    result_img = (result_img.astype(np.float32) * (1 - mask_3d) + 
                  blurred_img.astype(np.float32) * mask_3d).astype(np.uint8)
    
    return result_img

def create_smooth_mask(width, height, padding):
    """Create a smooth transition mask for better blending"""
    mask = np.ones((height, width), dtype=np.uint8) * 255
    
    if padding > 0:
        # Create gradient edges for smooth blending
        for i in range(padding):
            alpha = (i + 1) / padding
            intensity = int(255 * alpha)
            
            # Top edge
            if i < height:
                mask[i, :] = intensity
            # Bottom edge
            if height - 1 - i >= 0:
                mask[height - 1 - i, :] = intensity
            # Left edge
            if i < width:
                mask[:, i] = np.minimum(mask[:, i], intensity)
            # Right edge
            if width - 1 - i >= 0:
                mask[:, width - 1 - i] = np.minimum(mask[:, width - 1 - i], intensity)
    
    return mask

def apply_multi_stage_blur(img):
    """Apply multi-stage blur for better privacy and performance"""
    
    # Stage 1: Heavy Gaussian blur for primary obscuring
    blur_heavy = cv2.GaussianBlur(img, (45, 45), 15)
    
    # Stage 2: Motion blur for additional obscuring
    kernel_size = 15
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1) / 2), :] = np.ones(kernel_size)
    kernel = kernel / kernel_size
    blur_motion = cv2.filter2D(blur_heavy, -1, kernel)
    
    # Stage 3: Pixelation effect for extra privacy
    height, width = img.shape[:2]
    pixel_size = 8
    
    # Downscale
    small = cv2.resize(blur_motion, (width // pixel_size, height // pixel_size), 
                      interpolation=cv2.INTER_LINEAR)
    
    # Upscale back with nearest neighbor for pixelated effect
    pixelated = cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)
    
    return pixelated

def create_realtime_blur_processor():
    """Create a real-time blur processor optimized for video streams"""
    
    class RealtimeBlurProcessor:
        def __init__(self):
            self.model = None
            self.blur_cache = {}
            self.frame_buffer = []
            self.max_buffer_size = 3
            self.processing_time_history = []
            
        def load_model(self, model_path):
            """Load the YOLO model for processing"""
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_path)
                print("Model loaded for real-time processing")
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        
        def process_frame(self, frame, confidence_threshold=0.3):
            """Process a single frame with optimized blurring"""
            start_time = time.time()
            
            # Run inference
            results = self.model(frame, verbose=False)
            
            # Get blur regions
            blur_regions = []
            nudity_classes = [
                "BUTTOCKS_EXPOSED",
                "FEMALE_BREAST_EXPOSED", 
                "FEMALE_GENITALIA_EXPOSED",
                "MALE_GENITALIA_EXPOSED",
                "ANUS_EXPOSED"
            ]
            
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        coords = box.xyxy[0].tolist()
                        conf = box.conf[0].item()
                        cls = int(box.cls[0].item())
                        
                        if cls < len(__labels):
                            class_name = __labels[cls]
                            
                            if class_name in nudity_classes and conf > confidence_threshold:
                                x1, y1, x2, y2 = map(int, coords)
                                blur_regions.append((x1, y1, x2, y2, class_name, conf))
            
            # Apply fast blur if regions detected
            if blur_regions:
                frame = apply_fast_realtime_blur(frame, blur_regions)
            
            # Track processing time
            processing_time = time.time() - start_time
            self.processing_time_history.append(processing_time)
            if len(self.processing_time_history) > 30:
                self.processing_time_history.pop(0)
            
            return frame
        
        def get_average_processing_time(self):
            """Get average processing time for performance monitoring"""
            if self.processing_time_history:
                return sum(self.processing_time_history) / len(self.processing_time_history)
            return 0
        
        def get_fps_estimate(self):
            """Get estimated FPS based on processing time"""
            avg_time = self.get_average_processing_time()
            return 1.0 / avg_time if avg_time > 0 else 0
    
    return RealtimeBlurProcessor()

def apply_fast_realtime_blur(frame, blur_regions):
    """Apply fast blur optimized for real-time video processing"""
    
    # Use smaller kernel sizes for speed
    for x1, y1, x2, y2, class_name, conf in blur_regions:
        
        # Add small padding
        padding = 3
        x1_pad = max(0, x1 - padding)
        y1_pad = max(0, y1 - padding)
        x2_pad = min(frame.shape[1], x2 + padding)
        y2_pad = min(frame.shape[0], y2 + padding)
        
        # Extract ROI
        roi = frame[y1_pad:y2_pad, x1_pad:x2_pad]
        
        if roi.size > 0:
            # Fast blur using smaller kernel
            blurred_roi = cv2.GaussianBlur(roi, (21, 21), 8)
            
            # Additional pixelation for privacy
            h, w = roi.shape[:2]
            pixel_size = 6
            
            if w > pixel_size and h > pixel_size:
                # Quick pixelation
                small = cv2.resize(blurred_roi, (w // pixel_size, h // pixel_size))
                pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
                
                # Apply back to frame
                frame[y1_pad:y2_pad, x1_pad:x2_pad] = pixelated
    
    return frame

def test_realtime_performance():
    """Test the real-time performance of the blur processor"""
    
    # Create processor
    processor = create_realtime_blur_processor()
    
    # Load model
    if not processor.load_model("best.pt"):
        print("Failed to load model for performance test")
        return
    
    # Load test image
    test_frame = cv2.imread("download.jpeg")
    if test_frame is None:
        print("Failed to load test image")
        return
    
    print("Testing real-time performance...")
    print("-" * 40)
    
    # Process multiple frames to get average performance
    num_test_frames = 10
    
    for i in range(num_test_frames):
        processed_frame = processor.process_frame(test_frame)
        
        if i % 3 == 0:  # Print every 3rd frame
            avg_time = processor.get_average_processing_time()
            fps_estimate = processor.get_fps_estimate()
            print(f"Frame {i+1}: {avg_time:.3f}s per frame, ~{fps_estimate:.1f} FPS")
    
    # Final statistics
    final_avg_time = processor.get_average_processing_time()
    final_fps = processor.get_fps_estimate()
    
    print("-" * 40)
    print(f"Final Performance:")
    print(f"Average processing time: {final_avg_time:.3f} seconds")
    print(f"Estimated FPS: {final_fps:.1f}")
    print(f"Suitable for real-time: {'Yes' if final_fps >= 20 else 'No'}")
    
    # Save a sample processed frame
    processed_frame = processor.process_frame(test_frame)
    cv2.imwrite("realtime_test_output.jpg", processed_frame)
    print("Sample processed frame saved as: realtime_test_output.jpg")

def create_visualization_with_boxes(image_path, results, output_path):
    """Create visualization with bounding boxes for debugging"""
    try:
        # Load the image
        img = cv2.imread(image_path)
        
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    # Get box coordinates
                    coords = box.xyxy[0].tolist()
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    
                    x1, y1, x2, y2 = map(int, coords)
                    
                    # Get class name
                    class_name = __labels[cls] if cls < len(__labels) else f"CLASS_{cls}"
                    
                    # Draw rectangle (green for non-nudity, red for nudity)
                    nudity_classes = [
                        "BUTTOCKS_EXPOSED",
                        "FEMALE_BREAST_EXPOSED", 
                        "FEMALE_GENITALIA_EXPOSED",
                        "MALE_GENITALIA_EXPOSED",
                        "ANUS_EXPOSED"
                    ]
                    
                    color = (0, 0, 255) if class_name in nudity_classes else (0, 255, 0)
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                    
                    # Prepare label
                    label = f"{class_name}: {conf:.2f}"
                    
                    # Draw label background
                    (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                    cv2.rectangle(img, (x1, y1 - text_height - 5), (x1 + text_width, y1), color, -1)
                    
                    # Draw text
                    cv2.putText(img, label, (x1, y1 - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Save result
        cv2.imwrite(output_path, img)
        print(f"Debug visualization saved as: {output_path}")
        
    except Exception as e:
        print(f"Error creating visualization: {e}")

if __name__ == "__main__":
    print("PyTorch Model Test - Enhanced Real-time Version")
    print("=" * 50)
    
    # Add menu for different test modes
    print("\nSelect test mode:")
    print("1. Standard image processing test")
    print("2. Real-time performance test")
    print("3. Both tests")
    
    try:
        choice = input("Enter choice (1/2/3): ").strip()
        
        if choice in ['1', '3']:
            print("\n" + "="*30)
            print("STANDARD IMAGE TEST")
            print("="*30)
            test_pytorch_model()
        
        if choice in ['2', '3']:
            print("\n" + "="*30)
            print("REAL-TIME PERFORMANCE TEST")
            print("="*30)
            test_realtime_performance()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")
        # Fallback to standard test
        test_pytorch_model()
