#!/usr/bin/env python3
"""
Local setup script for testing the Video Analyzer.

This script helps you set up the local environment for testing.
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages for local testing."""
    print("📦 Installing required packages...")
    
    packages = [
        "openai",
        "opencv-python",
        "pillow",
        "numpy",
        "requests",
        "python-dotenv"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def check_opencv():
    """Check if OpenCV is working properly."""
    print("🔍 Testing OpenCV...")
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        # Test basic functionality
        import numpy as np
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        success = cv2.imencode('.jpg', test_image)[0]
        if success:
            print("✅ OpenCV image encoding works")
        else:
            print("❌ OpenCV image encoding failed")
            return False
            
        return True
    except Exception as e:
        print(f"❌ OpenCV test failed: {e}")
        return False

def check_openai():
    """Check if OpenAI package is working."""
    print("🔍 Testing OpenAI package...")
    try:
        import openai
        print(f"✅ OpenAI package version: {openai.__version__}")
        return True
    except Exception as e:
        print(f"❌ OpenAI package test failed: {e}")
        return False

def create_test_video():
    """Create a simple test video if none exists."""
    print("🎬 Creating test video...")
    
    try:
        import cv2
        import numpy as np
        
        # Create a simple test video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('test_video.mp4', fourcc, 20.0, (640, 480))
        
        for i in range(60):  # 3 seconds at 20 FPS
            # Create a frame with moving text
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, f'Test Frame {i+1}', (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
            cv2.putText(frame, 'This is a test video', (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            out.write(frame)
        
        out.release()
        print("✅ Test video created: test_video.mp4")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test video: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Local Video Analyzer Setup")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return
    
    print()
    
    # Test packages
    if not check_opencv():
        print("❌ OpenCV setup failed")
        return
    
    if not check_openai():
        print("❌ OpenAI package setup failed")
        return
    
    print()
    
    # Create test video
    create_test_video()
    
    print()
    print("🎉 Local setup complete!")
    print()
    print("📚 Next steps:")
    print("1. Set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
    print("2. Run local test: python test_local.py test_video.mp4")
    print("3. Or test with your own video: python test_local.py /path/to/your/video.mp4")
    print()
    print("💡 The test will:")
    print("   - Extract frames from your video")
    print("   - Save them as images in 'extracted_frames/' folder")
    print("   - Ask if you want to proceed with OpenAI analysis")
    print("   - Save results to 'local_analysis_result.json'")

if __name__ == "__main__":
    main()
