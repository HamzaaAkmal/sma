"""
Local Flask Server for NSFW Detection Testing
Run this script to test the Chrome extension locally
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to Python path to import the Flask app
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import the Flask app from vps_deployment
try:
    from vps_deployment.flask_api import app, processor
    print("✅ Successfully imported Flask app from vps_deployment")
except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    print("Make sure you're running this from the LimitX NSFW Model directory")
    sys.exit(1)

# Configure logging for local testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_model_file():
    """Check if the model file exists"""
    model_path = parent_dir / "best.pt"
    if model_path.exists():
        print(f"✅ Model file found: {model_path}")
        return True
    else:
        print(f"❌ Model file not found: {model_path}")
        print("Please ensure 'best.pt' is in the root directory")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/health')
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
        
        # Test CORS headers
        response = client.options('/process-frame-stream')
        if 'Access-Control-Allow-Origin' in response.headers:
            print("✅ CORS headers configured")
        else:
            print("❌ CORS headers missing")

if __name__ == "__main__":
    print("🚀 Starting Local NSFW Detection Server for Chrome Extension Testing")
    print("=" * 70)
    
    # Check prerequisites
    if not check_model_file():
        sys.exit(1)
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n📋 Server Configuration:")
    print(f"   • Host: localhost")
    print(f"   • Port: 5000")
    print(f"   • API Endpoint: http://localhost:5000/process-frame-stream")
    print(f"   • Health Check: http://localhost:5000/health")
    print(f"   • Model: {parent_dir}/best.pt")
    print(f"   • CORS: Enabled for all origins")
    
    print("\n🔧 Chrome Extension Setup:")
    print("   1. Load chrome_extension_universal in Chrome (Developer mode)")
    print("   2. Extension will connect to http://localhost:5000")
    print("   3. Test on any website with video content")
    print("   4. Check browser console for processing logs")
    
    print("\n🎬 Starting Flask Server...")
    print("   Press Ctrl+C to stop the server")
    print("=" * 70)
    
    try:
        # Run Flask app
        app.run(
            host='localhost',
            port=5000,
            debug=True,
            threaded=True,
            use_reloader=False  # Disable reloader for cleaner output
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)
