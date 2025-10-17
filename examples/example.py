"""
Example: Using the Video Analyzer & Generator API with Python
"""

import requests

API_URL = "https://your-username--video-analyzer-fastapi-app.modal.run"


def analyze_video(video_url: str) -> str:
    """Analyze a video and get a generation prompt."""
    response = requests.post(
        f"{API_URL}/analyze",
        json={"video_url": video_url}
    )
    response.raise_for_status()
    return response.json()["analysis"]


def generate_video(image_urls: list[str], prompt: str, resolution: str = "720p") -> str:
    """Generate a video from images and prompt."""
    response = requests.post(
        f"{API_URL}/generate",
        json={
            "image_urls": image_urls,
            "prompt": prompt,
            "resolution": resolution,
            "duration": "8s",
            "generate_audio": False
        }
    )
    response.raise_for_status()
    return response.json()["video_url"]


def main():
    # Example 1: Analyze a TikTok video
    print("🎬 Analyzing video...")
    prompt = analyze_video("https://www.tiktok.com/@user/video/123")
    print(f"📝 Generated prompt:\n{prompt}\n")

    # Example 2: Generate a video
    print("🎨 Generating video...")
    video_url = generate_video(
        image_urls=["https://example.com/your-image.jpg"],
        prompt=prompt
    )
    print(f"✅ Generated video: {video_url}")


if __name__ == "__main__":
    main()
