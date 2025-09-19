"""
Advanced Optimizations for Nanosecond Latency Processing
GPU acceleration, model quantization, and performance tuning
"""

import torch
import torch.nn as nn
import numpy as np
import cv2
import asyncio
import uvloop
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from functools import lru_cache
import time

class GPUOptimizedProcessor:
    """GPU-optimized processor for maximum performance"""
    
    def __init__(self, model_path="best.pt"):
        self.model_path = model_path
        self.device = self._get_best_device()
        self.model = None
        self.stream = None
        
        # Ultra-performance settings
        self.batch_size = 4  # Process multiple frames at once
        self.use_tensorrt = torch.cuda.is_available()
        self.use_half_precision = True
        
        # Memory pool for GPU operations
        self.gpu_memory_pool = []
        self.cpu_memory_pool = []
        
        # Pre-allocated tensors
        self.input_tensor = None
        self.output_tensors = None
        
        print(f"GPU Optimizer initialized with device: {self.device}")
    
    def _get_best_device(self):
        """Select the best available device"""
        if torch.cuda.is_available():
            # Select GPU with most memory
            best_gpu = 0
            max_memory = 0
            
            for i in range(torch.cuda.device_count()):
                memory = torch.cuda.get_device_properties(i).total_memory
                if memory > max_memory:
                    max_memory = memory
                    best_gpu = i
            
            return f"cuda:{best_gpu}"
        return "cpu"
    
    def initialize_model(self):
        """Initialize model with all optimizations"""
        try:
            from ultralytics import YOLO
            
            # Load model
            self.model = YOLO(self.model_path)
            self.model.to(self.device)
            
            if self.device.startswith("cuda"):
                # Enable all CUDA optimizations
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                torch.backends.cudnn.allow_tf32 = True
                
                # Create CUDA stream for async operations
                self.stream = torch.cuda.Stream()
                
                # Convert to half precision if supported
                if self.use_half_precision:
                    self.model.model.half()
                
                # Optimize with TensorRT if available
                if self.use_tensorrt:
                    try:
                        self._optimize_with_tensorrt()
                    except Exception as e:
                        print(f"TensorRT optimization failed: {e}")
                
                # Pre-allocate GPU memory
                self._preallocate_memory()
            
            # Warm up the model with various input sizes
            self._warmup_model()
            
            print("Model initialized with all optimizations")
            return True
            
        except Exception as e:
            print(f"Failed to initialize optimized model: {e}")
            return False
    
    def _optimize_with_tensorrt(self):
        """Optimize model with TensorRT"""
        try:
            import torch_tensorrt
            
            # Convert model to TensorRT
            dummy_input = torch.randn(1, 3, 640, 640).to(self.device)
            if self.use_half_precision:
                dummy_input = dummy_input.half()
            
            # TensorRT compilation
            trt_model = torch_tensorrt.compile(
                self.model.model,
                inputs=[dummy_input],
                enabled_precisions={torch.float16} if self.use_half_precision else {torch.float32},
                workspace_size=1 << 30,  # 1GB workspace
                max_batch_size=self.batch_size,
                use_fast_math=True,
                allow_shape_inference=True
            )
            
            self.model.model = trt_model
            print("TensorRT optimization successful")
            
        except ImportError:
            print("TensorRT not available, skipping optimization")
        except Exception as e:
            print(f"TensorRT optimization failed: {e}")
    
    def _preallocate_memory(self):
        """Pre-allocate GPU memory for faster processing"""
        try:
            # Pre-allocate input tensors for common frame sizes
            common_sizes = [(640, 640), (1280, 720), (1920, 1080)]
            
            for size in common_sizes:
                tensor = torch.zeros(1, 3, size[1], size[0]).to(self.device)
                if self.use_half_precision:
                    tensor = tensor.half()
                self.gpu_memory_pool.append(tensor)
            
            print("GPU memory pre-allocated")
            
        except Exception as e:
            print(f"Memory pre-allocation failed: {e}")
    
    def _warmup_model(self):
        """Warm up model with various input sizes"""
        warmup_sizes = [(640, 640), (1280, 720), (320, 320)]
        
        for size in warmup_sizes:
            dummy_frame = np.zeros((size[1], size[0], 3), dtype=np.uint8)
            self.process_frame_gpu(dummy_frame)
        
        # Clear cache after warmup
        if self.device.startswith("cuda"):
            torch.cuda.empty_cache()
        
        print("Model warmup completed")
    
    def process_frame_gpu(self, frame):
        """Ultra-fast GPU frame processing"""
        if self.device.startswith("cuda"):
            with torch.cuda.stream(self.stream):
                return self._process_with_cuda_stream(frame)
        else:
            return self._process_cpu_optimized(frame)
    
    def _process_with_cuda_stream(self, frame):
        """Process frame using CUDA streams for maximum performance"""
        try:
            # Convert frame to tensor
            frame_tensor = self._frame_to_tensor_gpu(frame)
            
            # Run inference asynchronously
            with torch.no_grad():
                results = self.model(frame_tensor, verbose=False)
            
            # Process results and apply blur
            processed_frame = self._apply_gpu_blur(frame, results)
            
            # Synchronize stream
            torch.cuda.synchronize()
            
            return processed_frame
            
        except Exception as e:
            print(f"GPU processing error: {e}")
            return frame
    
    def _frame_to_tensor_gpu(self, frame):
        """Convert frame to GPU tensor with optimizations"""
        # Resize if needed
        height, width = frame.shape[:2]
        target_size = 640  # YOLO input size
        
        if height != target_size or width != target_size:
            frame = cv2.resize(frame, (target_size, target_size))
        
        # Convert to tensor format (CHW)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_normalized = frame_rgb.astype(np.float32) / 255.0
        frame_tensor = torch.from_numpy(frame_normalized).permute(2, 0, 1).unsqueeze(0)
        
        # Move to GPU
        frame_tensor = frame_tensor.to(self.device, non_blocking=True)
        
        if self.use_half_precision:
            frame_tensor = frame_tensor.half()
        
        return frame_tensor
    
    def _apply_gpu_blur(self, frame, results):
        """Apply blur using GPU acceleration where possible"""
        # Extract detections
        blur_regions = self._extract_detections_fast(results)
        
        if not blur_regions:
            return frame
        
        # Apply CPU blur (OpenCV is often faster for small regions)
        return self._apply_optimized_blur_cpu(frame, blur_regions)
    
    def _extract_detections_fast(self, results):
        """Fast detection extraction"""
        blur_regions = []
        nsfw_classes = {"BUTTOCKS_EXPOSED", "FEMALE_BREAST_EXPOSED", 
                       "FEMALE_GENITALIA_EXPOSED", "MALE_GENITALIA_EXPOSED", "ANUS_EXPOSED"}
        
        try:
            from test_pytorch_model import __labels
            
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    # Vectorized operations for speed
                    coords = boxes.xyxy.cpu().numpy()
                    confs = boxes.conf.cpu().numpy()
                    classes = boxes.cls.cpu().numpy().astype(int)
                    
                    for i, cls_idx in enumerate(classes):
                        if cls_idx < len(__labels):
                            class_name = __labels[cls_idx]
                            if class_name in nsfw_classes and confs[i] > 0.4:
                                x1, y1, x2, y2 = coords[i].astype(int)
                                blur_regions.append((x1, y1, x2, y2))
        
        except Exception as e:
            print(f"Detection extraction error: {e}")
        
        return blur_regions
    
    @lru_cache(maxsize=32)
    def _get_blur_kernel(self, size):
        """Cached blur kernel generation"""
        kernel_size = min(15, max(5, size // 4))
        if kernel_size % 2 == 0:
            kernel_size += 1
        return kernel_size
    
    def _apply_optimized_blur_cpu(self, frame, blur_regions):
        """Optimized CPU blur with caching"""
        for x1, y1, x2, y2 in blur_regions:
            if x2 > x1 and y2 > y1:
                # Ensure bounds
                height, width = frame.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)
                
                if x2 > x1 and y2 > y1:
                    roi = frame[y1:y2, x1:x2]
                    
                    # Get cached kernel size
                    region_size = min(x2 - x1, y2 - y1)
                    kernel_size = self._get_blur_kernel(region_size)
                    
                    # Apply fast blur
                    blurred = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)
                    frame[y1:y2, x1:x2] = blurred
        
        return frame
    
    def process_batch(self, frames):
        """Process multiple frames simultaneously"""
        if len(frames) == 1:
            return [self.process_frame_gpu(frames[0])]
        
        try:
            # Stack frames into batch tensor
            batch_tensor = self._frames_to_batch_tensor(frames)
            
            # Batch inference
            with torch.no_grad():
                batch_results = self.model(batch_tensor, verbose=False)
            
            # Process results
            processed_frames = []
            for i, (frame, results) in enumerate(zip(frames, batch_results)):
                processed_frame = self._apply_gpu_blur(frame, [results])
                processed_frames.append(processed_frame)
            
            return processed_frames
            
        except Exception as e:
            print(f"Batch processing error: {e}")
            # Fallback to individual processing
            return [self.process_frame_gpu(frame) for frame in frames]
    
    def _frames_to_batch_tensor(self, frames):
        """Convert multiple frames to batch tensor"""
        batch_size = len(frames)
        target_size = 640
        
        # Pre-allocate batch tensor
        batch_tensor = torch.zeros(batch_size, 3, target_size, target_size, 
                                 device=self.device, dtype=torch.float16 if self.use_half_precision else torch.float32)
        
        for i, frame in enumerate(frames):
            # Resize and normalize
            if frame.shape[:2] != (target_size, target_size):
                frame = cv2.resize(frame, (target_size, target_size))
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_normalized = frame_rgb.astype(np.float32) / 255.0
            
            # Convert to tensor and add to batch
            frame_tensor = torch.from_numpy(frame_normalized).permute(2, 0, 1)
            batch_tensor[i] = frame_tensor.to(self.device, non_blocking=True)
        
        return batch_tensor

class AsyncFrameProcessor:
    """Asynchronous frame processor for concurrent operations"""
    
    def __init__(self, gpu_processor):
        self.gpu_processor = gpu_processor
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.processing_queue = asyncio.Queue(maxsize=20)
        
        # Set uvloop for better async performance
        if hasattr(uvloop, 'install'):
            uvloop.install()
    
    async def process_frame_async(self, frame, frame_id=None):
        """Process frame asynchronously"""
        loop = asyncio.get_event_loop()
        
        # Run GPU processing in thread pool
        result = await loop.run_in_executor(
            self.executor,
            self.gpu_processor.process_frame_gpu,
            frame
        )
        
        return result
    
    async def process_batch_async(self, frames):
        """Process batch of frames asynchronously"""
        loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(
            self.executor,
            self.gpu_processor.process_batch,
            frames
        )
        
        return result

# Performance monitoring
class PerformanceMonitor:
    """Monitor and optimize performance in real-time"""
    
    def __init__(self):
        self.processing_times = []
        self.memory_usage = []
        self.gpu_utilization = []
        self.start_time = time.time()
    
    def log_processing_time(self, time_ms):
        """Log processing time"""
        self.processing_times.append(time_ms)
        if len(self.processing_times) > 1000:
            self.processing_times.pop(0)
    
    def get_performance_stats(self):
        """Get comprehensive performance statistics"""
        if not self.processing_times:
            return {}
        
        avg_time = sum(self.processing_times) / len(self.processing_times)
        
        stats = {
            'average_processing_time_ms': round(avg_time, 2),
            'max_processing_time_ms': round(max(self.processing_times), 2),
            'min_processing_time_ms': round(min(self.processing_times), 2),
            'estimated_fps': round(1000 / avg_time if avg_time > 0 else 0, 1),
            'total_frames': len(self.processing_times),
            'uptime_seconds': round(time.time() - self.start_time, 1)
        }
        
        # Add GPU stats if available
        if torch.cuda.is_available():
            stats.update({
                'gpu_memory_allocated_gb': round(torch.cuda.memory_allocated() / (1024**3), 2),
                'gpu_memory_reserved_gb': round(torch.cuda.memory_reserved() / (1024**3), 2),
                'gpu_utilization_percent': self._get_gpu_utilization()
            })
        
        return stats
    
    def _get_gpu_utilization(self):
        """Get GPU utilization percentage"""
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            return utilization.gpu
        except:
            return 0

# Factory function for creating optimized processor
def create_ultra_fast_processor(model_path="best.pt", enable_async=True):
    """Create the most optimized processor possible"""
    
    # Create GPU processor
    gpu_processor = GPUOptimizedProcessor(model_path)
    
    if not gpu_processor.initialize_model():
        raise RuntimeError("Failed to initialize optimized processor")
    
    # Add async layer if requested
    if enable_async:
        async_processor = AsyncFrameProcessor(gpu_processor)
        return async_processor, gpu_processor
    
    return gpu_processor, None
