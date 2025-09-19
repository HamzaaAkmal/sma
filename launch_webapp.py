"""
Launch script for NSFW Video Filter Streamlit App
Automatically installs dependencies and starts the web application
"""

import subprocess
import sys
import os
import pkg_resources

def install_package(package):
    """Install a package using pip"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_requirements():
    """Check if required packages are installed, install if missing"""
    
    required_packages = [
        'streamlit>=1.28.0',
        'ultralytics>=8.0.0',
        'yt-dlp>=2023.7.6',
        'opencv-python>=4.5.0',
        'numpy>=1.21.0',
        'torch>=1.9.0',
        'Pillow>=9.0.0'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        package_name = package.split('>=')[0].split('==')[0]
        try:
            pkg_resources.get_distribution(package_name)
            print(f"✅ {package_name} is already installed")
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package)
            print(f"❌ {package_name} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing {len(missing_packages)} missing packages...")
        for package in missing_packages:
            print(f"Installing {package}...")
            try:
                install_package(package)
                print(f"✅ Successfully installed {package}")
            except Exception as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
    
    return True

def check_model_file():
    """Check if the model file exists"""
    model_path = "best.pt"
    if not os.path.exists(model_path):
        print(f"❌ Model file '{model_path}' not found!")
        print("Please ensure the model file is in the current directory.")
        return False
    else:
        print(f"✅ Model file '{model_path}' found")
        return True

def launch_streamlit():
    """Launch the Streamlit application"""
    
    print("\n🚀 Launching NSFW Video Filter Web App...")
    print("=" * 50)
    
    try:
        # Change to the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error launching application: {e}")

def main():
    """Main launcher function"""
    
    print("🔞 NSFW Video Filter - Web App Launcher")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Check and install requirements
    print("\n📋 Checking requirements...")
    if not check_and_install_requirements():
        print("❌ Failed to install required packages")
        sys.exit(1)
    
    # Check model file
    print("\n🤖 Checking model file...")
    if not check_model_file():
        print("❌ Model file not found")
        sys.exit(1)
    
    print("\n✅ All requirements satisfied!")
    
    # Ask user to launch
    try:
        response = input("\n🚀 Launch the web application? (y/n): ").lower().strip()
        if response in ['y', 'yes', '']:
            launch_streamlit()
        else:
            print("👋 Launch cancelled by user")
    except KeyboardInterrupt:
        print("\n👋 Launch cancelled by user")

if __name__ == "__main__":
    main()
