"""
Enhanced Streamlit Configuration and Utilities
Additional features for the NSFW Video Filter Web App
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import json
import os

def setup_streamlit_config():
    """Setup Streamlit page configuration and styling"""
    
    st.set_page_config(
        page_title="NSFW Video Filter Pro",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo/nsfw-filter',
            'Report a bug': 'https://github.com/your-repo/nsfw-filter/issues',
            'About': """
            # NSFW Video Filter Pro
            
            Advanced AI-powered content filtering for videos and live streams.
            
            **Features:**
            - Real-time NSFW detection and blurring
            - YouTube video processing
            - Multiple quality presets
            - Live preview during processing
            - Batch processing support
            
            Built with YOLOv8 and Streamlit.
            """
        }
    )

def inject_custom_css():
    """Inject custom CSS for better styling"""
    
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #FF6B6B;
        --secondary-color: #4ECDC4;
        --success-color: #45B7D1;
        --warning-color: #FFA726;
        --error-color: #EF5350;
        --background-color: #F8F9FA;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    /* Status boxes */
    .status-box {
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid;
    }
    
    .status-processing {
        background: linear-gradient(135deg, #FFF3CD 0%, #FFF8E1 100%);
        border-left-color: #FFC107;
        animation: pulse 2s infinite;
    }
    
    .status-complete {
        background: linear-gradient(135deg, #D4EDDA 0%, #E8F5E8 100%);
        border-left-color: #28A745;
    }
    
    .status-error {
        background: linear-gradient(135deg, #F8D7DA 0%, #FFEBEE 100%);
        border-left-color: #DC3545;
    }
    
    .status-info {
        background: linear-gradient(135deg, #CCE5FF 0%, #E3F2FD 100%);
        border-left-color: #2196F3;
    }
    
    /* Metrics styling */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid var(--primary-color);
        transition: transform 0.2s ease;
    }
    
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary-color);
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #F8F9FA 0%, #E9ECEF 100%);
    }
    
    /* Animation for processing */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* File uploader styling */
    .uploadedFile {
        background: white;
        border-radius: 0.5rem;
        padding: 1rem;
        border: 2px dashed var(--primary-color);
    }
    
    /* Video preview styling */
    .video-preview {
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    
    /* Info cards */
    .info-card {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid var(--secondary-color);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2.5rem;
        }
        
        .metric-container {
            margin-bottom: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_performance_chart(processing_times):
    """Create a performance chart showing processing times"""
    
    if not processing_times:
        return None
        
    df = pd.DataFrame({
        'Frame': range(1, len(processing_times) + 1),
        'Processing Time (ms)': [t * 1000 for t in processing_times]
    })
    
    fig = px.line(
        df, 
        x='Frame', 
        y='Processing Time (ms)',
        title='Real-time Processing Performance',
        color_discrete_sequence=['#FF6B6B']
    )
    
    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

def create_detection_chart(detections_history):
    """Create a chart showing detection statistics"""
    
    if not detections_history:
        return None
        
    labels = list(detections_history.keys())
    values = list(detections_history.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color='rgba(255, 107, 107, 0.7)',
            marker_line_color='rgba(255, 107, 107, 1)',
            marker_line_width=2
        )
    ])
    
    fig.update_layout(
        title='Detection Statistics',
        xaxis_title='Content Type',
        yaxis_title='Count',
        height=300,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

def display_status_message(message, status_type="info"):
    """Display a styled status message"""
    
    status_classes = {
        "info": "status-info",
        "processing": "status-processing", 
        "complete": "status-complete",
        "error": "status-error"
    }
    
    icons = {
        "info": "ℹ️",
        "processing": "⚡",
        "complete": "✅",
        "error": "❌"
    }
    
    css_class = status_classes.get(status_type, "status-info")
    icon = icons.get(status_type, "ℹ️")
    
    st.markdown(f"""
    <div class="status-box {css_class}">
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)

def display_metric_card(value, label, icon="📊"):
    """Display a styled metric card"""
    
    st.markdown(f"""
    <div class="metric-container">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def save_processing_session(session_data):
    """Save processing session data for analytics"""
    
    sessions_file = "processing_sessions.json"
    
    # Load existing sessions
    sessions = []
    if os.path.exists(sessions_file):
        try:
            with open(sessions_file, 'r') as f:
                sessions = json.load(f)
        except:
            sessions = []
    
    # Add current session
    session_data['timestamp'] = datetime.now().isoformat()
    sessions.append(session_data)
    
    # Keep only last 100 sessions
    sessions = sessions[-100:]
    
    # Save back
    try:
        with open(sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
    except Exception as e:
        st.warning(f"Could not save session data: {e}")

def load_processing_history():
    """Load processing history for analytics"""
    
    sessions_file = "processing_sessions.json"
    
    if os.path.exists(sessions_file):
        try:
            with open(sessions_file, 'r') as f:
                return json.load(f)
        except:
            return []
    
    return []

def show_analytics_dashboard():
    """Show analytics dashboard with processing history"""
    
    st.header("📊 Analytics Dashboard")
    
    sessions = load_processing_history()
    
    if not sessions:
        st.info("No processing history available yet.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_metric_card(len(sessions), "Total Sessions", "🎬")
    
    with col2:
        total_detections = sum(s.get('total_detections', 0) for s in sessions)
        display_metric_card(total_detections, "Total Detections", "🔍")
    
    with col3:
        total_blurred = sum(s.get('total_blurred', 0) for s in sessions)
        display_metric_card(total_blurred, "Regions Blurred", "🔒")
    
    with col4:
        avg_fps = sum(s.get('avg_fps', 0) for s in sessions) / len(sessions)
        display_metric_card(f"{avg_fps:.1f}", "Avg FPS", "⚡")
    
    # Processing time trend
    if len(sessions) > 1:
        df = pd.DataFrame(sessions)
        df['date'] = pd.to_datetime(df['timestamp'])
        
        fig = px.line(
            df,
            x='date',
            y='avg_fps',
            title='Processing Speed Over Time',
            color_discrete_sequence=['#4ECDC4']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent sessions table
    st.subheader("Recent Processing Sessions")
    
    recent_sessions = sessions[-10:]  # Last 10 sessions
    
    if recent_sessions:
        df = pd.DataFrame(recent_sessions)
        
        # Format the data for display
        display_df = df[['timestamp', 'video_title', 'total_detections', 'total_blurred', 'avg_fps']].copy()
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['Date', 'Video', 'Detections', 'Blurred', 'FPS']
        
        st.dataframe(display_df, use_container_width=True)

def show_help_section():
    """Show help and FAQ section"""
    
    st.header("❓ Help & FAQ")
    
    with st.expander("🚀 Getting Started"):
        st.markdown("""
        **How to use the NSFW Video Filter:**
        
        1. **Choose your settings** in the sidebar (performance preset, video quality, etc.)
        2. **Input your video** either by:
           - Pasting a YouTube URL, or
           - Uploading a video file directly
        3. **Click "Start Processing"** to begin filtering
        4. **Monitor progress** with the real-time preview and metrics
        5. **Download** your filtered video when complete
        
        **Supported formats:** MP4, AVI, MOV, MKV
        """)
    
    with st.expander("⚙️ Performance Presets"):
        st.markdown("""
        **Choose the right preset for your needs:**
        
        - **Maximum Quality**: Best blur quality, slower processing (~5-10 FPS)
        - **Balanced**: Good quality and speed balance (~15-25 FPS) - *Recommended*
        - **Maximum Speed**: Fastest processing, some quality trade-offs (~25-35 FPS)
        - **Real-time Streaming**: Optimized for live content (~30+ FPS)
        
        **Hardware considerations:**
        - GPU acceleration automatically detected and used when available
        - More RAM = larger video processing capability
        - CPU cores automatically utilized for parallel processing
        """)
    
    with st.expander("🎯 Detection Confidence"):
        st.markdown("""
        **Confidence threshold controls detection sensitivity:**
        
        - **Lower values (0.1-0.3)**: More sensitive, may blur safe content
        - **Medium values (0.4-0.6)**: Balanced detection - *Recommended*
        - **Higher values (0.7-0.9)**: Less sensitive, may miss some content
        
        **Tip:** Start with 0.4 and adjust based on your content and needs.
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Common issues and solutions:**
        
        **Slow processing:**
        - Use "Maximum Speed" preset
        - Lower video quality (480p instead of 1080p)
        - Increase confidence threshold
        - Ensure GPU drivers are updated
        
        **High memory usage:**
        - Process shorter video segments
        - Lower video resolution
        - Close other applications
        
        **Download failed:**
        - Check YouTube URL is valid and public
        - Some videos may be region-restricted
        - Try a different video quality setting
        
        **Poor blur quality:**
        - Use "Maximum Quality" preset
        - Lower confidence threshold
        - Ensure good lighting in source video
        """)
    
    with st.expander("🛡️ Privacy & Security"):
        st.markdown("""
        **Your privacy is protected:**
        
        - **Local processing**: All video processing happens on your device
        - **No uploads**: Videos are not sent to external servers
        - **Temporary files**: Downloaded videos are automatically cleaned up
        - **No data collection**: No personal information is stored or transmitted
        
        **Model information:**
        - Uses YOLOv8 trained on content detection
        - Model runs entirely offline
        - No internet connection required after video download
        """)

# Utility functions for the main app
def format_file_size(size_bytes):
    """Format file size in human readable format"""
    
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def estimate_processing_time(video_duration_seconds, fps_estimate):
    """Estimate processing time based on video duration and FPS"""
    
    if fps_estimate <= 0:
        return "Unknown"
    
    estimated_seconds = video_duration_seconds / fps_estimate
    
    if estimated_seconds < 60:
        return f"{estimated_seconds:.0f} seconds"
    elif estimated_seconds < 3600:
        minutes = estimated_seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = estimated_seconds / 3600
        return f"{hours:.1f} hours"
