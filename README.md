# Video Analyzer with Modal.dev and Google Gemini

A serverless function built with [Modal.dev](https://modal.com/docs/guide) that analyzes videos using Google Gemini's native video understanding capabilities. This function can process videos directly without frame extraction and provides comprehensive analysis.

## Features

- 🎥 **Native Video Processing**: Uses Gemini's built-in video understanding (no frame extraction needed)
- 🤖 **AI Analysis**: Powered by Google Gemini 2.5 Flash for fast, accurate video analysis
- 📊 **Comprehensive Reports**: Provides detailed analysis with timestamps
- 🌐 **YouTube Support**: Can analyze YouTube videos directly via URL
- 🎬 **Video Clipping**: Support for analyzing specific segments of videos
- ⚡ **Serverless**: Runs on Modal's cloud infrastructure with automatic scaling

## Why Gemini?

Gemini processes videos natively, which means:
- **No frame extraction** - more efficient and faster
- **Better context** - understands the full video, not just frames
- **Audio support** - can transcribe and analyze audio tracks
- **Timeline awareness** - provides accurate timestamps for events
- **Simpler code** - one API call instead of multiple frame analyses

## Setup

### Prerequisites

1. **Google API Key**: Get one from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **Modal Account**: Sign up at [modal.com](https://modal.com/)

### Local Testing

Test the functionality locally before deploying:

```bash
# 1. Install dependencies
pip install google-genai python-dotenv

# 2. Configure environment variables
# Edit .env and set your Google API key:
# GOOGLE_API_KEY=your_google_api_key_here

# 3. Test with a local video
python test_local.py test_video.mp4

# 4. Or test with a YouTube video
python test_local.py https://www.youtube.com/watch?v=VIDEO_ID
```

### Deploy to Modal

#### 1. Install Modal

```bash
pip install modal
```

#### 2. Authenticate with Modal

```bash
modal setup
```

#### 3. Set up Gemini Secret

Create a secret in Modal with your Google API key:

```bash
modal secret create gemini-secret GOOGLE_API_KEY=your_google_api_key_here
```

#### 4. Deploy the Function

```bash
modal deploy video_analyzer.py
```

## Usage

### Local Testing

#### Analyze a local video file:
```bash
python test_local.py /path/to/video.mp4
```

#### Analyze a YouTube video:
```bash
python test_local.py https://www.youtube.com/watch?v=VIDEO_ID
```

#### Interactive mode:
```bash
python test_local.py
# Follow the prompts to select video source and options
```

### Web Endpoint (After Deployment)

Once deployed, you can call the function via HTTP POST:

#### Analyze a video file by URL:
```bash
curl -X POST https://your-username--video-analyzer-analyze-video-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video.mp4"
  }'
```

#### Analyze with custom prompt:
```bash
curl -X POST https://your-username--video-analyzer-analyze-video-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/video.mp4",
    "prompt": "Describe the key events in this video with precise timestamps"
  }'
```

#### Analyze a YouTube video:
```bash
curl -X POST https://your-username--video-analyzer-analyze-video-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
  }'
```

#### Analyze a specific segment:
```bash
curl -X POST https://your-username--video-analyzer-analyze-video-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "start_offset": "1m30s",
    "end_offset": "3m45s"
  }'
```

#### With base64 encoded video data:
```bash
curl -X POST https://your-username--video-analyzer-analyze-video-endpoint.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "video_data": "base64_encoded_video_data_here"
  }'
```

### Modal Direct Invocation

Test directly via Modal:

```bash
modal run video_analyzer.py --video-path /path/to/video.mp4
```

### Python Integration

```python
import modal

# Connect to your deployed app
app = modal.App.lookup("video-analyzer", create_if_missing=False)

# Analyze a video file
result = app.analyze_video.remote(video_url="https://example.com/video.mp4")
print(result)

# Analyze a YouTube video
result = app.analyze_youtube_video.remote(
    youtube_url="https://www.youtube.com/watch?v=VIDEO_ID",
    start_offset="1m",
    end_offset="2m"
)
print(result)
```

## Response Format

The function returns a JSON response with the following structure:

```json
{
  "success": true,
  "analysis": "Detailed comprehensive analysis of the video...",
  "model": "gemini-2.5-flash",
  "video_size_mb": 6.1
}
```

For YouTube videos:
```json
{
  "success": true,
  "analysis": "Detailed comprehensive analysis of the video...",
  "model": "gemini-2.5-flash",
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

## Configuration

### Environment Variables (.env)

```bash
# Google Gemini Configuration
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Video Analysis Settings
ANALYSIS_TIMEOUT=600

# Modal Configuration
MODAL_APP_NAME=video-analyzer
MODAL_SECRET_NAME=gemini-secret

# Local Testing Settings
OUTPUT_RESULTS_FILE=local_analysis_result.json
```

### Available Models

- **gemini-2.5-flash** (default) - Fast and efficient, great for most use cases
- **gemini-2.0-flash** - Older version, still capable
- **gemini-2.5-pro** - More powerful, slower and more expensive

### Custom Prompts

You can customize the analysis by providing your own prompt:

```python
custom_prompt = """
Analyze this video and provide:
1. A list of all people visible in the video
2. What each person is doing
3. The setting and time of day
4. Any text or signs visible
"""

result = analyze_video.remote(
    video_url="https://example.com/video.mp4",
    prompt=custom_prompt
)
```

## Technical Details

### Video Processing
- **Small videos** (< 20MB): Processed inline for faster response
- **Large videos** (≥ 20MB): Uploaded to Gemini File API first
- **YouTube videos**: Processed directly via URL (no download needed)
- **Sampling rate**: Gemini samples at 1 FPS by default (customizable)
- **Token usage**: ~300 tokens per second of video at default resolution

### Supported Video Formats
- MP4 (recommended)
- MPEG
- MOV
- AVI
- WebM
- WMV
- FLV
- 3GPP

### YouTube Limitations
- **Free tier**: Up to 8 hours per day
- **Paid tier**: No limit
- Can upload up to 10 videos per request
- Only public videos supported

### Video Length Limits
- **2M context models**: Up to 2 hours at default resolution, 6 hours at low resolution
- **1M context models**: Up to 1 hour at default resolution, 3 hours at low resolution

## Error Handling

The function handles various error scenarios:
- Invalid video URLs or data
- Video format compatibility issues
- API rate limits and errors
- Network connectivity problems
- Large file handling

All errors return a structured response:
```json
{
  "success": false,
  "error": "Description of what went wrong"
}
```

## Cost Considerations

- **Modal**: Pay per second of execution time
- **Gemini**: Pay per token used (much cheaper than frame-by-frame analysis)
  - Input: Video tokens + text prompt tokens
  - Output: Response tokens
  - Approximately 300 tokens per second of video
- **Storage**: Videos < 20MB are not stored; larger videos are temporarily stored in File API

## Example Use Cases

1. **Content Moderation**: Analyze videos for inappropriate content
2. **Educational Content**: Generate summaries and timestamps for lectures
3. **Security Footage**: Extract key events with precise timestamps
4. **Social Media**: Analyze video content for metadata and tags
5. **Accessibility**: Generate detailed descriptions for visually impaired users
6. **Sports Analysis**: Track events, players, and actions
7. **Meeting Recordings**: Summarize discussions and action items

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   - Make sure you've run `modal setup`
   - Verify your Google API key is correct
   - Check that the secret name matches: `gemini-secret`

2. **Video Processing Error**:
   - Check that your video format is supported
   - For large videos, ensure you have a stable connection
   - Try using a lower resolution for very long videos

3. **Timeout Error**:
   - Very long videos may need more processing time
   - Consider clipping the video to analyze specific segments

4. **API Rate Limits**:
   - Gemini has rate limits that may cause temporary failures
   - For YouTube: check free tier limits (8 hours/day)

5. **YouTube URL Not Working**:
   - Ensure the video is public (not private or unlisted)
   - Check that the URL is correctly formatted
   - Try using the full URL, not shortened links

### Debug Mode

For more detailed error information, check the Modal logs:

```bash
modal app logs video-analyzer
```

## Comparison: Gemini vs OpenAI

| Feature | Gemini | OpenAI (Frame-based) |
|---------|--------|---------------------|
| Frame Extraction | Not needed | Required |
| API Calls | 1 per video | Multiple (1 per frame + summary) |
| Audio Support | Yes | No |
| Video Length | Up to 6 hours | Limited by frames |
| Timestamps | Native | Estimated |
| Cost | Lower | Higher |
| Speed | Faster | Slower |
| Setup | Simpler | More complex |

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see LICENSE file for details.

## Resources

- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Modal.dev Documentation](https://modal.com/docs/guide)
- [Video Understanding with Gemini](https://ai.google.dev/gemini-api/docs/video)
