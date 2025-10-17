# Video Analyzer & Generator API

A serverless API for analyzing videos and generating new ones using AI.

## Features

- 🎬 **Analyze Videos** - Extract insights from TikTok, Instagram, YouTube, and other videos using Google Gemini
- 🎨 **Generate Videos** - Create new videos from images using fal.ai's Veo model
- ⚡ **Serverless** - Runs on Modal.dev with automatic scaling
- 🌐 **REST API** - Simple HTTP endpoints

## Quick Start

### 1. Prerequisites

- [Modal](https://modal.com) account
- [Google AI Studio](https://aistudio.google.com/app/apikey) API key (for Gemini)
- [fal.ai](https://fal.ai/dashboard/keys) API key (for video generation)

### 2. Setup Secrets

Add your API keys to Modal:

```bash
modal secret create intercom-hackathon \
  GOOGLE_API_KEY=your_google_api_key \
  FAL_KEY=your_fal_api_key \
  GEMINI_MODEL=gemini-2.5-flash
```

### 3. Deploy

```bash
pip install modal
modal setup
modal deploy video_analyzer.py
```

You'll get a URL like:
```
https://your-username--video-analyzer-fastapi-app.modal.run
```

## API Endpoints

### Analyze Video

Analyze any video and get a detailed video generation prompt:

```bash
curl -X POST https://your-url/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.tiktok.com/@user/video/123"
  }'
```

**Supported video sources:**
- TikTok, Instagram, Twitter/X (via yt-dlp)
- YouTube (native Gemini support)
- Direct video URLs

**Response:**
```json
{
  "success": true,
  "analysis": "VIDEO GENERATION PROMPT:\n\nCreate an 8-second video...",
  "model": "gemini-2.5-flash",
  "video_size_mb": 2.3
}
```

### Generate Video

Create a new video from reference images:

```bash
curl -X POST https://your-url/generate \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": ["https://example.com/image.jpg"],
    "prompt": "A graceful dancer twirling in a meadow",
    "resolution": "720p",
    "duration": "8s",
    "generate_audio": false
  }'
```

**Response:**
```json
{
  "success": true,
  "video_url": "https://storage.googleapis.com/...",
  "error": null
}
```

### Interactive Docs

Open in your browser for interactive API testing:
```
https://your-url/docs
```

## Configuration

### Environment Variables (.env)

```bash
# Google Gemini
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# fal.ai
FAL_KEY=your_fal_api_key_here
```

### Video Analysis Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `video_url` | string | URL to video (TikTok, Instagram, etc.) |
| `youtube_url` | string | YouTube video URL |
| `video_data` | string | Base64 encoded video data |
| `prompt` | string | Custom analysis prompt (optional) |
| `model` | string | Gemini model (default: gemini-2.5-flash) |

### Video Generation Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_urls` | array | Reference image URLs (required) |
| `prompt` | string | Animation description (required) |
| `resolution` | string | "720p" or "1080p" (default: 720p) |
| `duration` | string | "8s" (default) |
| `generate_audio` | boolean | Generate audio (default: true) |

## Examples

### Complete Workflow

1. **Analyze a TikTok video:**
```bash
curl -X POST https://your-url/analyze \
  -d '{"video_url": "https://tiktok.com/@user/video/123"}' \
  | jq -r '.analysis' > prompt.txt
```

2. **Generate a similar video with your own image:**
```bash
curl -X POST https://your-url/generate \
  -d "{
    \"image_urls\": [\"https://your-image.jpg\"],
    \"prompt\": \"$(cat prompt.txt)\",
    \"resolution\": \"720p\",
    \"generate_audio\": false
  }"
```

### Using with Python

```python
import requests

# Analyze
response = requests.post(
    "https://your-url/analyze",
    json={"video_url": "https://tiktok.com/@user/video/123"}
)
prompt = response.json()["analysis"]

# Generate
response = requests.post(
    "https://your-url/generate",
    json={
        "image_urls": ["https://your-image.jpg"],
        "prompt": prompt,
        "resolution": "720p"
    }
)
video_url = response.json()["video_url"]
print(f"Generated video: {video_url}")
```

## How It Works

### Video Analysis
- Uses **Google Gemini 2.5 Flash** for native video understanding
- Downloads videos from social media using **yt-dlp**
- Generates detailed prompts optimized for video AI tools

### Video Generation
- Uses **fal.ai's Veo 3.1** reference-to-video model
- Takes reference images + text prompt
- Generates 8-second videos at 720p or 1080p

## Cost Optimization

- Set `generate_audio: false` to save 33% on video generation credits
- Use 720p resolution instead of 1080p
- Gemini processes videos at ~300 tokens per second

## Limitations

- **TikTok**: May fail due to anti-bot measures
- **Video size**: Files > 20MB are uploaded to Gemini File API (slower)
- **Generation**: Requires at least one reference image
- **Duration**: Currently limited to 8-second videos

## License

MIT
