#!/usr/bin/env python3
"""
Deployment script for the Video Analyzer Modal function (Google Gemini version).

This script helps you deploy and manage your video analyzer function.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command: str, description: str):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_modal_installed():
    """Check if Modal is installed."""
    try:
        import modal
        print("✅ Modal is installed")
        return True
    except ImportError:
        print("❌ Modal is not installed")
        print("Please install Modal: pip install modal")
        return False

def check_modal_auth():
    """Check if Modal is authenticated."""
    result = run_command("modal token current", "Checking Modal authentication")
    return result

def create_gemini_secret():
    """Create Gemini secret in Modal."""
    print("🔐 Setting up Gemini secret...")
    print("You'll need your Google API key from https://aistudio.google.com/app/apikey")

    api_key = input("Enter your Google API key: ").strip()

    if not api_key:
        print("❌ No API key provided")
        return False

    command = f'modal secret create gemini-secret GOOGLE_API_KEY="{api_key}"'
    return run_command(command, "Creating Gemini secret")

def deploy_function():
    """Deploy the video analyzer function."""
    return run_command("modal deploy video_analyzer.py", "Deploying video analyzer function")

def test_deployment():
    """Test the deployed function."""
    print("🧪 Testing deployment...")

    # Check if we have a test video
    test_videos = ["sample_video.mp4", "test_video.mp4", "example.mp4"]
    test_video = None

    for video in test_videos:
        if Path(video).exists():
            test_video = video
            break

    if not test_video:
        print("⚠️  No test video found. Skipping test.")
        print("To test manually, run:")
        print("modal run video_analyzer.py --video-path /path/to/your/video.mp4")
        return True

    command = f"modal run video_analyzer.py --video-path {test_video}"
    return run_command(command, f"Testing with {test_video}")

def get_endpoint_url():
    """Get the endpoint URL for the deployed function."""
    print("🌐 Getting endpoint URL...")
    try:
        result = subprocess.run(
            "modal app list",
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print("📋 Available apps:")
        print(result.stdout)

        print("\n🔗 Your endpoint URL will be:")
        print("https://your-username--video-analyzer-analyze-video-endpoint.modal.run")
        print("\nReplace 'your-username' with your actual Modal username.")
        print("\n📚 Usage examples:")
        print("\n1. Analyze a video file:")
        print('curl -X POST https://[YOUR-URL] -H "Content-Type: application/json" -d \'{"video_url": "https://example.com/video.mp4"}\'')
        print("\n2. Analyze a YouTube video:")
        print('curl -X POST https://[YOUR-URL] -H "Content-Type: application/json" -d \'{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}\'')

    except subprocess.CalledProcessError as e:
        print(f"❌ Could not get app list: {e}")

def main():
    """Main deployment function."""
    print("🚀 Video Analyzer Deployment Script (Google Gemini)")
    print("=" * 50)

    # Check prerequisites
    if not check_modal_installed():
        sys.exit(1)

    if not check_modal_auth():
        print("🔐 Please run 'modal setup' first to authenticate")
        sys.exit(1)

    # Create Gemini secret
    create_secret = input("Create/update Gemini secret? (y/n): ").strip().lower()
    if create_secret == 'y':
        if not create_gemini_secret():
            print("❌ Failed to create Gemini secret")
            sys.exit(1)
    else:
        print("⏭️  Skipping secret creation (assuming it already exists)")

    # Deploy function
    if not deploy_function():
        print("❌ Failed to deploy function")
        sys.exit(1)

    # Test deployment
    test = input("Test deployment with local video? (y/n): ").strip().lower()
    if test == 'y':
        test_deployment()

    # Show endpoint URL
    get_endpoint_url()

    print("\n🎉 Deployment complete!")
    print("\n📚 Next steps:")
    print("1. Test your function with: python test_local.py test_video.mp4")
    print("2. Use the web endpoint for integration (see URL above)")
    print("3. Check the README.md for more usage examples")
    print("4. Try YouTube analysis: python test_local.py https://www.youtube.com/watch?v=VIDEO_ID")

if __name__ == "__main__":
    main()
