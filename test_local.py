#!/usr/bin/env python3
"""
Local testing script for the Video Analyzer using Google Gemini.

This script allows you to test video analysis functionality locally
without deploying to Modal first.
"""

import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv('.env')


def download_video_with_ytdlp(url: str) -> bytes:
    """
    Download video from social media platforms using yt-dlp.
    Supports TikTok, Instagram, Twitter, and many other platforms.

    Args:
        url: URL to the video (TikTok, Instagram, etc.)

    Returns:
        Video bytes
    """
    import yt_dlp
    import tempfile
    import os
    import shutil

    # Create temp directory for download
    temp_dir = tempfile.mkdtemp()
    output_template = os.path.join(temp_dir, 'video.%(ext)s')

    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Prefer mp4
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        # TikTok requires browser impersonation
        'extractor_args': {
            'tiktok': {
                'webpage_download_timeout': 30,
            }
        },
        # Add headers to mimic a browser
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    try:
        print("📥 Downloading video with yt-dlp...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download video
            info = ydl.extract_info(url, download=True)

            # Find the downloaded file
            downloaded_file = ydl.prepare_filename(info)

            # Read video bytes
            with open(downloaded_file, 'rb') as f:
                video_bytes = f.read()

            print(f"✅ Downloaded video ({len(video_bytes) / (1024*1024):.2f} MB)")
            return video_bytes
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def is_social_media_url(url: str) -> bool:
    """Check if URL is from a social media platform that needs yt-dlp."""
    social_platforms = [
        'tiktok.com',
        'instagram.com',
        'twitter.com',
        'x.com',
        'facebook.com',
        'reddit.com',
        'snapchat.com',
        'vimeo.com'
    ]
    return any(platform in url.lower() for platform in social_platforms)


def analyze_video_local(
    video_path: str = None,
    youtube_url: str = None,
    video_url: str = None,
    google_api_key: str = None,
    prompt: str = None,
    model: str = None,
    start_offset: str = None,
    end_offset: str = None
) -> Dict[str, Any]:
    """
    Analyze a video locally using Google Gemini's native video understanding.

    Args:
        video_path: Path to local video file (optional)
        youtube_url: YouTube video URL (optional)
        video_url: Any video URL (TikTok, Instagram, direct URLs, etc.) (optional)
        google_api_key: Google API key
        prompt: Custom analysis prompt (optional)
        model: Gemini model to use (default: gemini-2.5-flash)
        start_offset: Start time for clipping (e.g., "10s", "1m30s")
        end_offset: End time for clipping (e.g., "2m", "3m45s")

    Returns:
        Dictionary containing analysis results
    """
    import os
    from google import genai
    from google.genai import types

    # Initialize Gemini client
    client = genai.Client(api_key=google_api_key)

    # Use default model if not specified
    if not model:
        model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

    # Default prompt if none provided
    if not prompt:
        prompt = """Analyze this video comprehensively. Please provide:
1. Overall description of the video content
2. Key themes, topics, or narrative
3. Notable objects, people, actions, or events
4. Setting, context, and atmosphere
5. Any interesting, unusual, or significant elements
6. Timeline of major events with timestamps (use MM:SS format)

Be specific and detailed in your analysis."""

    try:
        # Handle YouTube URL
        if youtube_url:
            print(f"🎥 Analyzing YouTube video: {youtube_url}")

            # Build parts
            parts = []

            # Add video with optional metadata
            if start_offset or end_offset:
                video_metadata = types.VideoMetadata()
                if start_offset:
                    video_metadata.start_offset = start_offset
                    print(f"⏩ Start offset: {start_offset}")
                if end_offset:
                    video_metadata.end_offset = end_offset
                    print(f"⏸  End offset: {end_offset}")

                parts.append(
                    types.Part(
                        file_data=types.FileData(file_uri=youtube_url),
                        video_metadata=video_metadata
                    )
                )
            else:
                parts.append(
                    types.Part(file_data=types.FileData(file_uri=youtube_url))
                )

            # Add prompt
            parts.append(types.Part(text=prompt))

            # Generate content
            print(f"🤖 Using model: {model}")
            print("⏳ Analyzing... (this may take a minute)")
            response = client.models.generate_content(
                model=f'models/{model}',
                contents=types.Content(parts=parts)
            )

            return {
                "success": True,
                "analysis": response.text,
                "model": model,
                "youtube_url": youtube_url
            }

        # Handle other video URLs (TikTok, Instagram, direct URLs, etc.)
        elif video_url:
            print(f"🎥 Analyzing video URL: {video_url}")

            # Check if it's a social media URL that needs yt-dlp
            if is_social_media_url(video_url):
                video_bytes = download_video_with_ytdlp(video_url)
            else:
                # Direct URL download
                print("📥 Downloading video from URL...")
                import requests
                response = requests.get(video_url)
                video_bytes = response.content
                print(f"✅ Downloaded video ({len(video_bytes) / (1024*1024):.2f} MB)")

            # Check video size
            video_size_mb = len(video_bytes) / (1024 * 1024)
            print(f"📦 Video size: {video_size_mb:.2f} MB")

            # For videos < 20MB, use inline data
            if video_size_mb < 20:
                print("📤 Processing video inline")
                response = client.models.generate_content(
                    model=f'models/{model}',
                    contents=types.Content(
                        parts=[
                            types.Part(
                                inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
                            ),
                            types.Part(text=prompt)
                        ]
                    )
                )
            else:
                # For larger videos, use File API
                print("☁️  Uploading video to Gemini File API")
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                    temp_file.write(video_bytes)
                    temp_path = temp_file.name

                try:
                    myfile = client.files.upload(file=temp_path)
                    print("✅ Upload complete")

                    # Generate content
                    print(f"🤖 Using model: {model}")
                    print("⏳ Analyzing... (this may take a minute)")
                    response = client.models.generate_content(
                        model=model,
                        contents=[myfile, prompt]
                    )
                finally:
                    import os
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

            return {
                "success": True,
                "analysis": response.text,
                "model": model,
                "video_size_mb": video_size_mb
            }

        # Handle local video file
        elif video_path:
            if not os.path.exists(video_path):
                return {"error": f"Video file not found: {video_path}"}

            print(f"🎥 Analyzing video file: {video_path}")

            # Read video bytes
            with open(video_path, 'rb') as f:
                video_bytes = f.read()

            # Check video size
            video_size_mb = len(video_bytes) / (1024 * 1024)
            print(f"📦 Video size: {video_size_mb:.2f} MB")

            # For videos < 20MB, use inline data
            if video_size_mb < 20:
                print("📤 Processing video inline")
                response = client.models.generate_content(
                    model=f'models/{model}',
                    contents=types.Content(
                        parts=[
                            types.Part(
                                inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
                            ),
                            types.Part(text=prompt)
                        ]
                    )
                )
            else:
                # For larger videos, use File API
                print("☁️  Uploading video to Gemini File API")
                myfile = client.files.upload(file=video_path)
                print("✅ Upload complete")

                # Generate content
                print(f"🤖 Using model: {model}")
                print("⏳ Analyzing... (this may take a minute)")
                response = client.models.generate_content(
                    model=model,
                    contents=[myfile, prompt]
                )

            return {
                "success": True,
                "analysis": response.text,
                "model": model,
                "video_size_mb": video_size_mb
            }

        else:
            return {"error": "Either video_path, youtube_url, or video_url must be provided"}

    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }


def main():
    """Main function for local testing."""
    print("🧪 Local Video Analyzer Test (Google Gemini)")
    print("=" * 50)

    # Parse arguments
    video_path = None
    youtube_url = None
    video_url = None
    custom_prompt = None
    start_offset = None
    end_offset = None

    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg.startswith("http"):
            # Determine if it's YouTube or other URL
            if 'youtube.com' in arg or 'youtu.be' in arg:
                youtube_url = arg
            else:
                video_url = arg
        else:
            video_path = arg

    # If no args, ask user
    if not video_path and not youtube_url and not video_url:
        choice = input("Analyze (1) local video, (2) YouTube video, or (3) other URL (TikTok, Instagram, etc.)? Enter 1, 2, or 3: ").strip()
        if choice == "2":
            youtube_url = input("Enter YouTube URL: ").strip()
            if youtube_url:
                clip = input("Clip video? (y/n): ").strip().lower()
                if clip == 'y':
                    start_offset = input("Start offset (e.g., 10s, 1m30s): ").strip() or None
                    end_offset = input("End offset (e.g., 2m, 3m45s): ").strip() or None
        elif choice == "3":
            video_url = input("Enter video URL (TikTok, Instagram, direct link, etc.): ").strip()
        else:
            video_path = input("Enter path to video file: ").strip()

    # Validate input
    if video_path and not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return

    if not video_path and not youtube_url and not video_url:
        print("❌ No video provided")
        return

    # Get Google API key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("❌ Google API key not found in environment variables")
        print("Please set GOOGLE_API_KEY in .env or run:")
        print("export GOOGLE_API_KEY=your_google_api_key_here")
        google_api_key = input("Enter your Google API key: ").strip()
        if not google_api_key:
            print("❌ Google API key is required")
            return

    print(f"🔑 Google API key: {'*' * 20}{google_api_key[-4:]}")
    print()

    # Optional: custom prompt
    use_custom = input("Use custom prompt? (y/n, default=n): ").strip().lower()
    if use_custom == 'y':
        print("Enter your custom prompt (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "" and (not lines or lines[-1] == ""):
                break
            lines.append(line)
        custom_prompt = "\n".join(lines).strip() or None

    try:
        # Analyze video
        result = analyze_video_local(
            video_path=video_path,
            youtube_url=youtube_url,
            video_url=video_url,
            google_api_key=google_api_key,
            prompt=custom_prompt,
            start_offset=start_offset,
            end_offset=end_offset
        )

        if result.get("success"):
            print("\n" + "=" * 50)
            print("🎉 Analysis complete!")
            print("=" * 50)
            print("\n📝 Analysis:\n")
            print(result.get('analysis', 'No analysis available'))
            print("\n" + "=" * 50)
            print(f"🤖 Model: {result.get('model', 'N/A')}")
            if 'video_size_mb' in result:
                print(f"📦 Video size: {result['video_size_mb']:.2f} MB")
            print("=" * 50)

            # Save results
            import json
            output_file = os.getenv('OUTPUT_RESULTS_FILE', 'local_analysis_result.json')
            with open(output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to {output_file}")

        else:
            print(f"\n❌ Analysis failed: {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
