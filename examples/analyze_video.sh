#!/bin/bash
# Example: Analyze a video and get a generation prompt

API_URL="https://your-username--video-analyzer-fastapi-app.modal.run"

curl -X POST "$API_URL/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.tiktok.com/@user/video/123"
  }' | jq
