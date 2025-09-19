"""
Flask API Server for Real-Time NSFW Detection and Blurring
Optimized for ultra-low latency Chrome extension integration
"""

import os
import io
import time
import base64
import threading
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
import logging

import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import torch
from ultralytics import YOLO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UltraFastNSFWProcessor:
    """Ultra-optimized NSFW processor for nanosecond latency"""
    
    def __init__(self, model_path="best.pt"):
        self.model_path = model_path
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Ultra-fast processing settings
        self.resize_factor = 0.5  # Aggressive downscaling for speed
        self.confidence_threshold = 0.5  # Higher threshold for fewer false positives
        self.max_detections = 20  # Limit detections for speed
        
        # Frame cache for temporal consistency
        self.frame_cache = {}
        self.cache_ttl = 0.1  # 100ms cache lifetime
        
        # Processing statistics
        self.processing_times = []
        self.request_count = 0
        
        # NSFW classes to blur (optimized list)
        self.nsfw_classes = {
            "BUTTOCKS_EXPOSED": True,
            "FEMALE_BREAST_EXPOSED": True,
            "FEMALE_GENITALIA_EXPOSED": True,
            "MALE_GENITALIA_EXPOSED": True,
            "ANUS_EXPOSED": True,
        }
        
        # Thread pool for concurrent processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info(f"Processor initialized with device: {self.device}")
    
    def initialize_model(self):
        """Initialize YOLO model with optimizations"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            # Load model with optimizations
            self.model = YOLO(self.model_path)
            self.model.to(self.device)
            
            # Optimize model for inference
            if self.device == "cuda":
                # Enable GPU optimizations
                torch.backends.cudnn.benchmark = True
                self.model.model.half()  # Use FP16 for faster inference
            
            # Warm-up the model
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            self.process_frame(dummy_frame)
            
            logger.info("Model initialized and warmed up successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            return False
    
    def process_frame(self, frame, frame_id=None, *, confidence_threshold=None, fast_mode=None):
        """Process single frame with ultra-fast optimizations"""
        start_time = time.time()
        
        try:
            # Check cache first
            if frame_id and frame_id in self.frame_cache:
                cache_entry = self.frame_cache[frame_id]
                if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                    cached_frame = cache_entry['result']
                    cached_detections = cache_entry.get('detections', [])
                    return cached_frame, cached_detections
            
            original_shape = frame.shape[:2]
            
            # Use provided confidence threshold or default
            conf_threshold = confidence_threshold if confidence_threshold is not None else self.confidence_threshold
            
            # Handle fast mode
            resize_factor = 0.3 if fast_mode else self.resize_factor
            
            # Aggressive resize for speed
            if resize_factor != 1.0:
                height, width = frame.shape[:2]
                new_height = int(height * resize_factor)
                new_width = int(width * resize_factor)
                frame_resized = cv2.resize(frame, (new_width, new_height))
            else:
                frame_resized = frame
            
            # Run inference
            with torch.no_grad():
                results = self.model(
                    frame_resized,
                    verbose=False,
                    conf=conf_threshold,
                    max_det=self.max_detections
                )
            
            # Extract blur regions
            blur_regions = self._extract_blur_regions(results, original_shape, resize_factor)
            
            # Convert blur regions to detection format
            detections = []
            for region in blur_regions:
                x1, y1, x2, y2, class_name, conf = region
                detections.append({
                    'class': class_name,
                    'confidence': conf,
                    'bbox': [x1, y1, x2, y2]
                })
            
            # Apply ultra-fast blur
            if blur_regions:
                frame = self._apply_ultra_fast_blur(frame, blur_regions)
            
            # Cache result
            if frame_id:
                self.frame_cache[frame_id] = {
                    'result': frame,
                    'detections': detections,
                    'timestamp': time.time()
                }
                
                # Clean old cache entries
                self._clean_cache()
            
            # Track performance
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            self.processing_times.append(processing_time)
            if len(self.processing_times) > 100:
                self.processing_times.pop(0)
            
            self.request_count += 1
            
            return frame, detections
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return frame, []  # Return original frame and empty detections on error
    
    def _extract_blur_regions(self, results, original_shape, resize_factor=0.5):
        """Extract regions that need blurring"""
        blur_regions = []
        
        # It's better practice to define labels within the class or pass them in
        # rather than importing from a script that might not be available.
        # For this example, we assume `get_labels` is available.
        try:
            from test_pytorch_model import get_labels
            labels = get_labels()
        except ImportError:
            logger.warning("`test_pytorch_model.py` not found. Using placeholder labels.")
            # Define placeholder labels if the import fails
            labels = [
                "BUTTOCKS_EXPOSED", "FEMALE_BREAST_EXPOSED", 
                "FEMALE_GENITALIA_EXPOSED", "MALE_GENITALIA_EXPOSED", "ANUS_EXPOSED"
            ]

        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    coords = box.xyxy[0].tolist()
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    
                    if cls < len(labels):
                        class_name = labels[cls]
                        
                        if class_name in self.nsfw_classes:
                            x1, y1, x2, y2 = map(int, coords)
                            
                            # Scale coordinates back to original size
                            if resize_factor != 1.0:
                                scale = 1.0 / resize_factor
                                x1, y1, x2, y2 = [int(coord * scale) for coord in [x1, y1, x2, y2]]
                            
                            # Ensure coordinates are within bounds
                            height, width = original_shape
                            x1 = max(0, min(x1, width))
                            y1 = max(0, min(y1, height))
                            x2 = max(x1, min(x2, width))
                            y2 = max(y1, min(y2, height))
                            
                            blur_regions.append((x1, y1, x2, y2, class_name, conf))
        
        return blur_regions
    
    def _apply_ultra_fast_blur(self, frame, blur_regions):
        """Apply ultra-fast blur optimized for real-time processing"""
        
        for x1, y1, x2, y2, class_name, conf in blur_regions:
            if x2 > x1 and y2 > y1:
                # Extract ROI
                roi = frame[y1:y2, x1:x2]
                
                if roi.size > 0:
                    # Ultra-fast single-stage blur
                    h, w = roi.shape[:2]
                    
                    # Adaptive kernel size based on region size
                    kernel_size = min(15, max(5, min(w//4, h//4)))
                    if kernel_size % 2 == 0:
                        kernel_size += 1
                    
                    # Fast Gaussian blur
                    blurred = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)
                    
                    # Optional: Add light pixelation for extra privacy
                    pixel_size = max(2, min(w//12, h//12))
                    if pixel_size > 1:
                        small = cv2.resize(blurred, (w // pixel_size, h // pixel_size))
                        blurred = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
                    
                    # Apply back to frame
                    frame[y1:y2, x1:x2] = blurred
        
        return frame
    
    def _clean_cache(self):
        """Clean expired cache entries"""
        current_time = time.time()
        expired_keys = [
            k for k, v in self.frame_cache.items()
            if current_time - v['timestamp'] > self.cache_ttl
        ]
        for key in expired_keys:
            del self.frame_cache[key]
    
    def get_stats(self):
        """Get processing statistics"""
        if not self.processing_times:
            return {}
        
        avg_time = sum(self.processing_times) / len(self.processing_times)
        max_time = max(self.processing_times)
        min_time = min(self.processing_times)
        
        return {
            'average_processing_time_ms': round(avg_time, 2),
            'max_processing_time_ms': round(max_time, 2),
            'min_processing_time_ms': round(min_time, 2),
            'estimated_fps': round(1000 / avg_time if avg_time > 0 else 0, 1),
            'total_requests': self.request_count,
            'cache_size': len(self.frame_cache),
            'device': self.device
        }

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for Chrome extension

# Initialize processor
processor = UltraFastNSFWProcessor()

# Initialize the model immediately when the app starts
def initialize_app():
    """Initialize the model when app starts"""
    if not processor.initialize_model():
        logger.error("Failed to initialize model. Exiting...")
        exit(1)

# Call initialization immediately
initialize_app()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': processor.model is not None,
        'device': processor.device,
        'timestamp': time.time()
    })

@app.route('/process-image', methods=['POST'])
def process_image():
    """Endpoint for processing static images (thumbnails, profile pics, etc.)"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Get parameters
        image_data = data['image']
        image_id = data.get('image_id', f'img_{int(time.time())}')
        confidence_threshold = float(data.get('confidence', 0.5))
        fast_mode = data.get('fast_mode', True)
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # --- FIXED CODE ---
        # Process image for NSFW content using keyword arguments
        processed_image, detections = processor.process_frame(
            image, 
            frame_id=image_id, 
            confidence_threshold=confidence_threshold, 
            fast_mode=fast_mode
        )
        
        # Determine if image contains NSFW content
        nsfw_detected = len(detections) > 0
        max_confidence = max([det['confidence'] for det in detections]) if detections else 0.0
        
        processing_time = time.time() - start_time
        
        response = {
            'nsfw_detected': nsfw_detected,
            'confidence': max_confidence,
            'detections': len(detections),
            'image_id': image_id,
            'processing_time': processing_time,
            'status': 'success'
        }
        
        logger.info(f"Image processed: {image_id} - NSFW: {nsfw_detected} - Time: {processing_time:.3f}s")
        
        return jsonify(response)
        
    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"Image processing error: {str(e)} - Time: {error_time:.3f}s")
        return jsonify({
            'error': str(e),
            'processing_time': error_time,
            'status': 'error'
        }), 500

@app.route('/process-frame', methods=['POST'])
def process_frame():
    """Main endpoint for processing video frames"""
    start_time = time.time()
    
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'frame' not in data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        # Decode base64 frame
        try:
            frame_data = base64.b64decode(data['frame'])
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return jsonify({'error': 'Invalid frame data'}), 400
                
        except Exception as e:
            return jsonify({'error': f'Failed to decode frame: {str(e)}'}), 400
        
        # Get optional parameters
        frame_id = data.get('frame_id')
        confidence = data.get('confidence', processor.confidence_threshold)
        
        # Update confidence threshold if provided
        original_threshold = processor.confidence_threshold
        if confidence != original_threshold:
            processor.confidence_threshold = confidence
        
        # Process frame
        processed_frame, _ = processor.process_frame(frame, frame_id)
        
        # Restore original threshold
        processor.confidence_threshold = original_threshold
        
        # Encode processed frame
        _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        processed_frame_b64 = base64.b64encode(buffer).decode('utf-8')
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return jsonify({
            'processed_frame': processed_frame_b64,
            'processing_time_ms': round(total_time, 2),
            'frame_id': frame_id,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Error in process_frame: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/process-frame-stream', methods=['POST'])
def process_frame_stream():
    """Ultra-fast optimized endpoint for streaming frames"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        if not data or 'frame' not in data:
            return jsonify({'error': 'No frame data provided'}), 400
        
        # Decode frame
        frame_data = base64.b64decode(data['frame'])
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid frame data'}), 400
        
        frame_id = data.get('frame_id')
        fast_mode = data.get('fast_mode', False)
        confidence = data.get('confidence', 0.5)
        
        # Ultra-fast mode: resize frame for faster processing
        original_shape = frame.shape[:2]
        if fast_mode and max(frame.shape[:2]) > 320:
            scale_factor = 320 / max(frame.shape[:2])
            new_height = int(frame.shape[0] * scale_factor)
            new_width = int(frame.shape[1] * scale_factor)
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)
        
        # Process frame
        processed_frame, detections = processor.process_frame(frame, frame_id)
        
        # Check if any NSFW content was detected and blurred
        has_blur = len(detections) > 0
        
        if has_blur:
            # Resize back to original size if needed
            if fast_mode and processed_frame.shape[:2] != original_shape:
                processed_frame = cv2.resize(processed_frame, (original_shape[1], original_shape[0]), interpolation=cv2.INTER_LINEAR)
            
            # Encode with compression optimized for speed
            encode_param = [cv2.IMWRITE_JPEG_QUALITY, 50 if fast_mode else 70]
            _, buffer = cv2.imencode('.jpg', processed_frame, encode_param)
            processed_frame_b64 = base64.b64encode(buffer).decode('utf-8')
            
            total_time = (time.time() - start_time) * 1000
            
            return jsonify({
                'frame': processed_frame_b64,
                'time': round(total_time, 1),
                'detections': [{'detected': True}],  # Simplified detection info
                'processed': True
            })
        else:
            # No NSFW content detected, return minimal response
            total_time = (time.time() - start_time) * 1000
            return jsonify({
                'time': round(total_time, 1),
                'detections': [],
                'processed': False
            })
        
    except Exception as e:
        logger.error(f"Error in process_frame_stream: {e}")
        return jsonify({'error': 'Processing failed', 'processed': False}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get processing statistics"""
    return jsonify(processor.get_stats())

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Get or update processor configuration"""
    if request.method == 'GET':
        return jsonify({
            'resize_factor': processor.resize_factor,
            'confidence_threshold': processor.confidence_threshold,
            'max_detections': processor.max_detections,
            'cache_ttl': processor.cache_ttl,
            'device': processor.device
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        
        # Update configuration
        if 'resize_factor' in data:
            processor.resize_factor = max(0.1, min(1.0, data['resize_factor']))
        
        if 'confidence_threshold' in data:
            processor.confidence_threshold = max(0.1, min(0.9, data['confidence_threshold']))
        
        if 'max_detections' in data:
            processor.max_detections = max(1, min(100, data['max_detections']))
        
        if 'cache_ttl' in data:
            processor.cache_ttl = max(0.01, min(1.0, data['cache_ttl']))
        
        return jsonify({'status': 'Configuration updated'})

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle large request errors"""
    return jsonify({'error': 'Request too large. Please reduce frame size.'}), 413

@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Configuration for production
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )