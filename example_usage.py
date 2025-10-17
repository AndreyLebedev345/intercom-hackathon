#!/usr/bin/env python3
"""
Example usage of the Video Analyzer Modal function.

This script demonstrates how to use the video analyzer both locally and via the web endpoint.
"""

import modal
import requests
import base64
import json
from pathlib import Path

# Example 1: Using Modal function directly
def analyze_with_modal_local(video_path: str):
    """Analyze a video using Modal function directly."""
    print("🔍 Analyzing video with Modal function...")
    
    # Connect to the deployed app
    app = modal.App.lookup("video-analyzer", create_if_missing=False)
    
    # Read video file
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    
    # Analyze video
    result = app.analyze_video.remote(video_bytes=video_bytes)
    
    print("✅ Analysis complete!")
    print(f"📊 Frames analyzed: {result.get('total_frames_analyzed', 0)}")
    print(f"📝 Summary: {result.get('overall_summary', 'No summary available')}")
    
    return result

# Example 2: Using web endpoint
def analyze_with_web_endpoint(video_path: str, endpoint_url: str):
    """Analyze a video using the web endpoint."""
    print("🌐 Analyzing video via web endpoint...")
    
    # Read and encode video
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    
    video_base64 = base64.b64encode(video_bytes).decode('utf-8')
    
    # Prepare request
    payload = {
        "video_data": video_base64
    }
    
    # Make request
    response = requests.post(
        endpoint_url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Analysis complete!")
        print(f"📊 Frames analyzed: {result.get('total_frames_analyzed', 0)}")
        print(f"📝 Summary: {result.get('overall_summary', 'No summary available')}")
        return result
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

# Example 3: Analyze video from URL
def analyze_video_url(video_url: str, endpoint_url: str):
    """Analyze a video from URL using the web endpoint."""
    print(f"🔗 Analyzing video from URL: {video_url}")
    
    payload = {
        "video_url": video_url
    }
    
    response = requests.post(
        endpoint_url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Analysis complete!")
        return result
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def save_analysis_result(result: dict, output_file: str = "analysis_result.json"):
    """Save analysis result to a JSON file."""
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"💾 Analysis result saved to {output_file}")

def main():
    """Main function demonstrating different usage patterns."""
    print("🎥 Video Analyzer Example Usage")
    print("=" * 50)
    
    # Configuration
    video_path = "sample_video.mp4"  # Replace with your video path
    endpoint_url = "https://your-username--video-analyzer-analyze-video-endpoint.modal.run"
    
    # Check if video file exists
    if not Path(video_path).exists():
        print(f"❌ Video file not found: {video_path}")
        print("Please provide a valid video file path.")
        return
    
    print(f"📁 Video file: {video_path}")
    print(f"🌐 Endpoint URL: {endpoint_url}")
    print()
    
    # Example 1: Direct Modal function call
    print("1️⃣ Direct Modal Function Call")
    print("-" * 30)
    try:
        result1 = analyze_with_modal_local(video_path)
        if result1:
            save_analysis_result(result1, "modal_analysis.json")
    except Exception as e:
        print(f"❌ Modal function error: {e}")
    
    print()
    
    # Example 2: Web endpoint call
    print("2️⃣ Web Endpoint Call")
    print("-" * 30)
    try:
        result2 = analyze_with_web_endpoint(video_path, endpoint_url)
        if result2:
            save_analysis_result(result2, "web_analysis.json")
    except Exception as e:
        print(f"❌ Web endpoint error: {e}")
    
    print()
    
    # Example 3: URL-based analysis
    print("3️⃣ URL-based Analysis")
    print("-" * 30)
    sample_video_url = "https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4"
    try:
        result3 = analyze_video_url(sample_video_url, endpoint_url)
        if result3:
            save_analysis_result(result3, "url_analysis.json")
    except Exception as e:
        print(f"❌ URL analysis error: {e}")
    
    print()
    print("🎉 Example usage complete!")

if __name__ == "__main__":
    main()
