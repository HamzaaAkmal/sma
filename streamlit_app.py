"""
Streamlit Web Application for Real-Time NSFW Video Filtering
Supports YouTube video processing with live preview and download
"""

import streamlit as st
import cv2
import numpy as np
import tempfile
import os
import time
import threading
import queue
from pathlib import Path
import subprocess
import sys
from io import BytesIO
import base64

# Try to import required packages
try:
    import yt_dlp
except ImportError:
    st.error("yt-dlp not installed. Please run: pip install yt-dlp")
    st.stop()

try:
    from ultralytics import YOLO
except ImportError:
    st.error("ultralytics not installed. Please run: pip install ultralytics")
    st.stop()

# Import our custom modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from realtime_video_processor import VideoStreamProcessor
from config import get_optimized_config, PRESETS

# Define labels directly to avoid import issues
LABELS = [
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

# Page configuration
st.set_page_config(
    page_title="NSFW Video Filter",
    page_icon="🔞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #FF6B6B;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 2rem;
}

.status-box {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.status-processing {
    background-color: #FFF3CD;
    border-left: 5px solid #FFC107;
}

.status-complete {
    background-color: #D4EDDA;
    border-left: 5px solid #28A745;
}

.status-error {
    background-color: #F8D7DA;
    border-left: 5px solid #DC3545;
}

.metrics-container {
    display: flex;
    justify-content: space-around;
    margin: 1rem 0;
}

.metric-box {
    text-align: center;
    padding: 1rem;
    background-color: #F8F9FA;
    border-radius: 0.5rem;
    border: 1px solid #DEE2E6;
}
</style>
""", unsafe_allow_html=True)

class YouTubeVideoProcessor:
    """Handle YouTube video download and processing"""
    
    def __init__(self):
        self.model_path = "best.pt"
        self.processor = None
        self.download_progress = 0
        self.processing_progress = 0
        self.current_status = "Ready"
        
    def download_youtube_video(self, url, quality='720p'):
        """Download YouTube video with specified quality"""
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': f'best[height<={quality[:-1]}]',  # Remove 'p' from quality
                'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
                'noplaylist': True,
            }
            
            # Progress hook
            def progress_hook(d):
                if d['status'] == 'downloading':
                    if 'total_bytes' in d:
                        self.download_progress = (d.get('downloaded_bytes', 0) / d['total_bytes']) * 100
                    elif '_percent_str' in d:
                        # Extract percentage from string
                        percent_str = d['_percent_str'].strip().replace('%', '')
                        try:
                            self.download_progress = float(percent_str)
                        except:
                            pass
                elif d['status'] == 'finished':
                    self.download_progress = 100
                    
            ydl_opts['progress_hooks'] = [progress_hook]
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'video')
                
                # Find downloaded file
                for file in os.listdir(temp_dir):
                    if file.endswith(('.mp4', '.webm', '.mkv')):
                        return os.path.join(temp_dir, file), video_title
                        
            return None, None
            
        except Exception as e:
            st.error(f"Error downloading video: {str(e)}")
            return None, None
    
    def initialize_processor(self, preset='balanced'):
        """Initialize the video processor"""
        
        if not os.path.exists(self.model_path):
            st.error(f"Model file {self.model_path} not found!")
            return False
            
        try:
            self.processor = VideoStreamProcessor(self.model_path)
            
            # Apply configuration preset
            config = get_optimized_config(preset)
            self.processor.resize_factor = config['performance']['resize_factor']
            self.processor.frame_skip = config['performance']['frame_skip']
            
            return self.processor.initialize_model()
            
        except Exception as e:
            st.error(f"Error initializing processor: {str(e)}")
            return False
    
    def process_video_with_progress(self, input_path, output_path, confidence_threshold=0.4):
        """Process video with progress tracking"""
        
        if not self.processor:
            return False
            
        try:
            # Open video to get properties
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                st.error("Could not open video file")
                return False
                
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            detections_count = 0
            blur_count = 0
            
            # Process frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                frame_count += 1
                
                # Process frame
                processed_frame, frame_detections, frame_blurs = self.process_frame_with_stats(
                    frame, confidence_threshold
                )
                
                detections_count += frame_detections
                blur_count += frame_blurs
                
                # Write frame
                writer.write(processed_frame)
                
                # Update progress
                self.processing_progress = (frame_count / total_frames) * 100
                
                # Yield progress periodically
                if frame_count % (fps // 2) == 0:  # Every 0.5 seconds
                    yield {
                        'progress': self.processing_progress,
                        'frame': frame_count,
                        'total_frames': total_frames,
                        'detections': detections_count,
                        'blurred_regions': blur_count,
                        'current_frame': processed_frame
                    }
            
            cap.release()
            writer.release()
            
            yield {
                'progress': 100,
                'frame': frame_count,
                'total_frames': total_frames,
                'detections': detections_count,
                'blurred_regions': blur_count,
                'completed': True
            }
            
            return True
            
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
            return False
    
    def process_frame_with_stats(self, frame, confidence_threshold):
        """Process frame and return statistics"""
        
        # Run inference
        results = self.processor.model(frame, verbose=False)
        
        # Count detections and blur regions
        detections = 0
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
                    detections += 1
                    
                    coords = box.xyxy[0].tolist()
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())
                    
                    if cls < len(LABELS):
                        class_name = LABELS[cls]
                        
                        if class_name in nudity_classes and conf > confidence_threshold:
                            x1, y1, x2, y2 = map(int, coords)
                            blur_regions.append((x1, y1, x2, y2, class_name, conf))
        
        # Apply blurring
        if blur_regions:
            frame = self.apply_fast_blur(frame, blur_regions)
        
        return frame, detections, len(blur_regions)
    
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

def create_download_link(file_path, filename):
    """Create a download link for processed video"""
    
    try:
        with open(file_path, "rb") as f:
            bytes_data = f.read()
        
        b64 = base64.b64encode(bytes_data).decode()
        href = f'<a href="data:video/mp4;base64,{b64}" download="{filename}">📥 Download Processed Video</a>'
        return href
    except Exception as e:
        return f"Error creating download link: {str(e)}"

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🔞 NSFW Video Filter</h1>', unsafe_allow_html=True)
    st.markdown("### Real-time NSFW content detection and blurring for YouTube videos")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Quality preset selection
    preset = st.sidebar.selectbox(
        "Performance Preset",
        options=list(PRESETS.keys()),
        index=1,  # Default to 'balanced'
        help="Choose between quality and speed"
    )
    
    # Video quality selection
    video_quality = st.sidebar.selectbox(
        "Video Quality",
        options=['480p', '720p', '1080p'],
        index=1,  # Default to 720p
        help="Higher quality = slower processing"
    )
    
    # Confidence threshold
    confidence_threshold = st.sidebar.slider(
        "Detection Confidence",
        min_value=0.1,
        max_value=0.9,
        value=0.4,
        step=0.05,
        help="Lower = more sensitive detection"
    )
    
    # Show configuration details
    with st.sidebar.expander("🔧 Advanced Settings"):
        config = get_optimized_config(preset)
        st.write(f"**Resize Factor:** {config['performance']['resize_factor']}")
        st.write(f"**Frame Skip:** {config['performance']['frame_skip']}")
        st.write(f"**Blur Kernel:** {config['blur']['gaussian_kernel_size']}")
        st.write(f"**Max Workers:** {config['performance']['max_workers']}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📹 Video Input")
        
        # YouTube URL input
        youtube_url = st.text_input(
            "YouTube Video URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste any YouTube video URL here"
        )
        
        # File upload as alternative
        st.write("**OR**")
        uploaded_file = st.file_uploader(
            "Upload Video File",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Upload a video file directly"
        )
    
    with col2:
        st.header("📊 Processing Stats")
        
        # Initialize session state
        if 'processor' not in st.session_state:
            st.session_state.processor = YouTubeVideoProcessor()
        
        # Status display
        status_placeholder = st.empty()
        metrics_placeholder = st.empty()
    
    # Processing section
    if st.button("🚀 Start Processing", type="primary"):
        
        if not youtube_url and not uploaded_file:
            st.error("Please provide a YouTube URL or upload a video file")
            return
        
        # Initialize processor
        with st.spinner("Initializing AI model..."):
            if not st.session_state.processor.initialize_processor(preset):
                st.error("Failed to initialize processor")
                return
        
        st.success("✅ AI model loaded successfully!")
        
        # Progress containers
        progress_container = st.container()
        video_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
        input_video_path = None
        video_title = "processed_video"
        
        try:
            # Handle YouTube URL
            if youtube_url:
                with st.spinner("📥 Downloading video from YouTube..."):
                    download_progress = st.progress(0)
                    
                    input_video_path, video_title = st.session_state.processor.download_youtube_video(
                        youtube_url, video_quality
                    )
                    
                    if not input_video_path:
                        st.error("Failed to download video")
                        return
                        
                    download_progress.progress(100)
                    st.success(f"✅ Downloaded: {video_title}")
            
            # Handle uploaded file
            elif uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    input_video_path = tmp_file.name
                    video_title = uploaded_file.name.split('.')[0]
            
            # Process video
            if input_video_path:
                output_path = f"processed_{video_title}.mp4"
                
                st.info("🎬 Processing video with NSFW filtering...")
                
                # Create processing generator
                processor_gen = st.session_state.processor.process_video_with_progress(
                    input_video_path, output_path, confidence_threshold
                )
                
                # Process with real-time updates
                preview_placeholder = st.empty()
                
                for update in processor_gen:
                    # Update progress
                    progress_bar.progress(update['progress'] / 100)
                    
                    # Update status
                    status_text.text(
                        f"Processing frame {update['frame']}/{update['total_frames']} "
                        f"({update['progress']:.1f}%)"
                    )
                    
                    # Update metrics
                    with metrics_placeholder.container():
                        met_col1, met_col2, met_col3 = st.columns(3)
                        
                        with met_col1:
                            st.metric("Detections", update['detections'])
                        
                        with met_col2:
                            st.metric("Blurred Regions", update['blurred_regions'])
                        
                        with met_col3:
                            if 'current_frame' in update:
                                fps_estimate = update['frame'] / (time.time() - processing_start_time) if 'processing_start_time' in locals() else 0
                                st.metric("Processing FPS", f"{fps_estimate:.1f}")
                    
                    # Show preview frame
                    if 'current_frame' in update and update['current_frame'] is not None:
                        # Convert frame for display
                        frame_rgb = cv2.cvtColor(update['current_frame'], cv2.COLOR_BGR2RGB)
                        preview_placeholder.image(frame_rgb, caption="Live Preview", use_column_width=True)
                    
                    # Check if completed
                    if update.get('completed', False):
                        break
                
                # Processing complete
                st.success("🎉 Video processing completed!")
                
                # Show download link
                if os.path.exists(output_path):
                    st.markdown("### 📥 Download Processed Video")
                    
                    # File info
                    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                    st.info(f"File size: {file_size:.1f} MB")
                    
                    # Create download button
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Processed Video",
                            data=file,
                            file_name=f"filtered_{video_title}.mp4",
                            mime="video/mp4"
                        )
                
                # Show final statistics
                with st.expander("📊 Processing Statistics"):
                    final_stats = st.session_state.processor.processor.get_performance_stats()
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Average Processing Time", f"{final_stats.get('average_processing_time', 0):.3f}s")
                    
                    with col2:
                        st.metric("Estimated FPS", f"{final_stats.get('estimated_fps', 0):.1f}")
                    
                    with col3:
                        st.metric("Total Frames", final_stats.get('total_frames_processed', 0))
        
        except Exception as e:
            st.error(f"Error during processing: {str(e)}")
        
        finally:
            # Cleanup temporary files
            if input_video_path and youtube_url:  # Only delete if downloaded from YouTube
                try:
                    os.unlink(input_video_path)
                except:
                    pass
    
    # Information section
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        **This application uses advanced AI to detect and blur NSFW content in videos:**
        
        1. **🤖 AI Detection**: Uses a trained YOLO model to identify inappropriate content
        2. **🎭 Smart Blurring**: Applies multi-stage blur (Gaussian + Pixelation) for privacy
        3. **⚡ Real-time Processing**: Optimized for speed while maintaining quality
        4. **🔧 Configurable**: Multiple presets for different speed/quality needs
        
        **Supported Platforms:**
        - YouTube videos (any public video)
        - Direct video file uploads
        - Multiple video formats (MP4, AVI, MOV, MKV)
        
        **Privacy Note:** All processing happens locally. Videos are not stored or shared.
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and YOLOv8 | For educational and content moderation purposes")

if __name__ == "__main__":
    main()
