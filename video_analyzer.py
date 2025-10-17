import modal
from typing import Dict, Any
import os

# Create Modal app
app = modal.App("video-analyzer")

# Define the image with all necessary dependencies
image = modal.Image.debian_slim(python_version="3.11").pip_install([
    "google-genai",
    "requests",
    "yt-dlp",
    "fastapi",
    "fal-client"
])


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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download video
            info = ydl.extract_info(url, download=True)

            # Find the downloaded file
            downloaded_file = ydl.prepare_filename(info)

            # Read video bytes
            with open(downloaded_file, 'rb') as f:
                video_bytes = f.read()

            return video_bytes
    finally:
        # Clean up temp directory
        import shutil
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


# Set up Gemini client
@app.function(
    image=image,
    secrets=[modal.Secret.from_name("intercom-hackathon")],
    timeout=600  # 10 minutes timeout for video processing
)
def analyze_video(
    video_url: str = None,
    video_bytes: bytes = None,
    prompt: str = None,
    model: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Analyze a video using Google Gemini's native video understanding.

    Args:
        video_url: URL to the video file (optional)
        video_bytes: Raw video bytes (optional)
        prompt: Custom analysis prompt (optional)
        model: Gemini model to use (default: gemini-2.5-flash)

    Returns:
        Dictionary containing analysis results
    """
    from google import genai
    from google.genai import types

    # Initialize Gemini client
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    # Download video if URL provided
    if video_url:
        # Check if it's a social media URL that needs yt-dlp
        if is_social_media_url(video_url):
            print(f"Detected social media URL, using yt-dlp to download")
            video_bytes = download_video_with_ytdlp(video_url)
        else:
            # Direct URL download
            import requests
            response = requests.get(video_url)
            video_bytes = response.content

    if not video_bytes:
        return {"error": "No video data provided"}

    # Check video size
    video_size_mb = len(video_bytes) / (1024 * 1024)

    # Default prompt if none provided
    if not prompt:
        prompt = """Analyze this TikTok video and write a video generation prompt that captures its visual essence. This prompt should be detailed enough that feeding it to a video generation AI would recreate a similar video.

DO NOT include any text overlays or on-screen text in your prompt, as video generation models cannot reliably create text.

Focus on:
- The core visual concept and format
- Visual progression (what happens and when)
- Camera movements and shot types
- Subject actions and transformations
- Pacing and timing
- Mood and emotional tone
- Audio/music cues
- How the story is told through visuals alone

Write the output as a single, detailed video generation prompt that someone could use as-is with a video AI tool.

Format your output as:

VIDEO GENERATION PROMPT:
[Your detailed prompt here - write it as if you're instructing a video generation AI]"""

    try:
        # For videos < 20MB, use inline data
        if video_size_mb < 20:
            print(f"Processing video inline ({video_size_mb:.2f} MB)")
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
            print(f"Uploading video to File API ({video_size_mb:.2f} MB)")
            import tempfile

            # Save to temporary file for upload
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
                temp_file.write(video_bytes)
                temp_video_path = temp_file.name

            try:
                # Upload file
                myfile = client.files.upload(file=temp_video_path)

                # Generate content
                response = client.models.generate_content(
                    model=model,
                    contents=[myfile, prompt]
                )
            finally:
                # Clean up temp file
                if os.path.exists(temp_video_path):
                    os.unlink(temp_video_path)

        return {
            "success": True,
            "analysis": response.text,
            "model": model,
            "video_size_mb": video_size_mb
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}",
            "video_size_mb": video_size_mb
        }


# Analyze YouTube video
@app.function(
    image=image,
    secrets=[modal.Secret.from_name("intercom-hackathon")],
    timeout=600
)
def analyze_youtube_video(
    youtube_url: str,
    prompt: str = None,
    model: str = "gemini-2.5-flash",
    start_offset: str = None,
    end_offset: str = None
) -> Dict[str, Any]:
    """
    Analyze a YouTube video using Google Gemini.

    Args:
        youtube_url: YouTube video URL
        prompt: Custom analysis prompt (optional)
        model: Gemini model to use (default: gemini-2.5-flash)
        start_offset: Start time for clipping (e.g., "10s", "1m30s")
        end_offset: End time for clipping (e.g., "2m", "3m45s")

    Returns:
        Dictionary containing analysis results
    """
    from google import genai
    from google.genai import types

    # Initialize Gemini client
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    # Default prompt if none provided
    if not prompt:
        prompt = """Analyze this TikTok video and write a video generation prompt that captures its visual essence. This prompt should be detailed enough that feeding it to a video generation AI would recreate a similar video.

DO NOT include any text overlays or on-screen text in your prompt, as video generation models cannot reliably create text.

Focus on:
- The core visual concept and format
- Visual progression (what happens and when)
- Camera movements and shot types
- Subject actions and transformations
- Pacing and timing
- Mood and emotional tone
- Audio/music cues
- How the story is told through visuals alone

Write the output as a single, detailed video generation prompt that someone could use as-is with a video AI tool.

Format your output as:

VIDEO GENERATION PROMPT:
[Your detailed prompt here - write it as if you're instructing a video generation AI]"""

    try:
        # Build parts
        parts = []

        # Add video with optional metadata
        if start_offset or end_offset:
            video_metadata = types.VideoMetadata()
            if start_offset:
                video_metadata.start_offset = start_offset
            if end_offset:
                video_metadata.end_offset = end_offset

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

    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}",
            "youtube_url": youtube_url
        }


# Generate video from images
@app.function(
    image=image,
    secrets=[modal.Secret.from_name("intercom-hackathon")],
    timeout=600
)
def generate_video(
    image_urls: list,
    prompt: str,
    duration: str = "8s",
    resolution: str = "720p",
    generate_audio: bool = True
) -> Dict[str, Any]:
    """
    Generate a video from reference images using fal.ai's Veo model.

    Args:
        image_urls: List of reference image URLs
        prompt: Text prompt describing the animation
        duration: Video duration ("8s")
        resolution: Video resolution ("720p" or "1080p")
        generate_audio: Whether to generate audio

    Returns:
        Dictionary containing video URL and metadata
    """
    import fal_client
    import os

    # Set FAL_KEY from environment (Modal secret)
    fal_client.api_key = os.environ.get("FAL_KEY")

    try:
        result = fal_client.subscribe(
            "fal-ai/veo3.1/reference-to-video",
            arguments={
                "image_urls": image_urls,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "generate_audio": generate_audio
            },
            with_logs=True
        )

        return {
            "success": True,
            "video_url": result.get("video", {}).get("url"),
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Video generation failed: {str(e)}"
        }


# Web endpoint for video file analysis
@app.function(
    image=image,
    secrets=[modal.Secret.from_name("intercom-hackathon")],
    timeout=600
)
@modal.asgi_app()
def fastapi_app():
    """
    FastAPI web endpoint for video analysis.
    """
    from fastapi import FastAPI
    from pydantic import BaseModel, Field
    from typing import Optional

    web_app = FastAPI(title="Video Analyzer API", version="1.0.0")

    # Request model
    class VideoAnalysisRequest(BaseModel):
        video_url: Optional[str] = Field(None, description="URL to video file (TikTok, Instagram, direct URL, etc.)")
        video_data: Optional[str] = Field(None, description="Base64 encoded video data")
        youtube_url: Optional[str] = Field(None, description="YouTube video URL")
        prompt: Optional[str] = Field(None, description="Custom analysis prompt")
        model: Optional[str] = Field("gemini-2.5-flash", description="Gemini model to use")
        start_offset: Optional[str] = Field(None, description="Start time for clipping (e.g., '10s', '1m30s') - YouTube only")
        end_offset: Optional[str] = Field(None, description="End time for clipping (e.g., '2m', '3m45s') - YouTube only")

    # Response model for analysis
    class VideoAnalysisResponse(BaseModel):
        success: bool = Field(..., description="Whether the analysis succeeded")
        analysis: Optional[str] = Field(None, description="The video analysis text from Gemini")
        model: Optional[str] = Field(None, description="The Gemini model used")
        video_size_mb: Optional[float] = Field(None, description="Size of the video in MB")
        youtube_url: Optional[str] = Field(None, description="YouTube URL if applicable")
        error: Optional[str] = Field(None, description="Error message if analysis failed")

    # Request model for video generation
    class VideoGenerationRequest(BaseModel):
        image_urls: list[str] = Field(..., description="URLs of reference images", min_length=1)
        prompt: str = Field(..., description="Text prompt describing the animation")
        duration: Optional[str] = Field("8s", description="Video duration")
        resolution: Optional[str] = Field("720p", description="Video resolution (720p or 1080p)")
        generate_audio: Optional[bool] = Field(True, description="Whether to generate audio")

    # Response model for video generation
    class VideoGenerationResponse(BaseModel):
        success: bool = Field(..., description="Whether the generation succeeded")
        video_url: Optional[str] = Field(None, description="URL of the generated video")
        error: Optional[str] = Field(None, description="Error message if generation failed")

    @web_app.post("/analyze", response_model=VideoAnalysisResponse)
    async def analyze_endpoint(request: VideoAnalysisRequest):
        """
        Analyze a video using Google Gemini.

        Supports:
        - TikTok, Instagram, Twitter/X videos via video_url
        - YouTube videos via youtube_url (with optional clipping)
        - Direct video file URLs via video_url
        - Base64 encoded video data via video_data
        """
        # Check for YouTube URL
        if request.youtube_url:
            result = analyze_youtube_video.remote(
                youtube_url=request.youtube_url,
                prompt=request.prompt,
                model=request.model,
                start_offset=request.start_offset,
                end_offset=request.end_offset
            )
            return result

        # Handle video file
        if request.video_data:
            # Decode base64 video data
            import base64
            video_bytes = base64.b64decode(request.video_data)
            result = analyze_video.remote(
                video_bytes=video_bytes,
                prompt=request.prompt,
                model=request.model
            )
            return result
        elif request.video_url:
            result = analyze_video.remote(
                video_url=request.video_url,
                prompt=request.prompt,
                model=request.model
            )
            return result
        else:
            return VideoAnalysisResponse(
                success=False,
                error="Either video_url, video_data, or youtube_url must be provided"
            )

    @web_app.post("/generate", response_model=VideoGenerationResponse)
    async def generate_endpoint(request: VideoGenerationRequest):
        """
        Generate a video from reference images using fal.ai's Veo model.

        Provide 1-3 reference images and a prompt describing how to animate them.
        The prompt should include:
        - Action: How the images should be animated
        - Style: Desired animation style
        - Camera motion (optional)
        - Ambiance (optional)
        """
        result = generate_video.remote(
            image_urls=request.image_urls,
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.resolution,
            generate_audio=request.generate_audio
        )
        return result

    return web_app


# Local function for testing
@app.local_entrypoint()
def test_video_analysis(video_path: str, prompt: str = None):
    """
    Test the video analysis function locally.

    Usage: modal run video_analyzer.py --video-path /path/to/video.mp4
    """
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    result = analyze_video.remote(video_bytes=video_bytes, prompt=prompt)
    print("Analysis Result:")
    print(result)
