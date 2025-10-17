#!/bin/bash
# Example: Complete workflow - analyze a video, then generate a similar one

API_URL="https://your-username--video-analyzer-fastapi-app.modal.run"
VIDEO_URL="https://www.tiktok.com/@user/video/123"
IMAGE_URL="https://example.com/your-image.jpg"

echo "🎬 Step 1: Analyzing video..."
ANALYSIS=$(curl -s -X POST "$API_URL/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"video_url\": \"$VIDEO_URL\"}")

# Extract the prompt
PROMPT=$(echo "$ANALYSIS" | jq -r '.analysis')

echo "📝 Generated prompt:"
echo "$PROMPT"
echo ""

echo "🎨 Step 2: Generating new video with your image..."
RESULT=$(curl -s -X POST "$API_URL/generate" \
  -H "Content-Type: application/json" \
  -d "{
    \"image_urls\": [\"$IMAGE_URL\"],
    \"prompt\": $(echo "$PROMPT" | jq -Rs .),
    \"resolution\": \"720p\",
    \"duration\": \"8s\",
    \"generate_audio\": false
  }")

# Extract video URL
VIDEO_URL=$(echo "$RESULT" | jq -r '.video_url')

echo "✅ Done! Generated video:"
echo "$VIDEO_URL"
