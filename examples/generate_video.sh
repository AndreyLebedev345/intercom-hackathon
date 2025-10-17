#!/bin/bash
# Example: Generate a video from an image

API_URL="https://your-username--video-analyzer-fastapi-app.modal.run"

curl -X POST "$API_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": ["https://example.com/your-image.jpg"],
    "prompt": "A graceful dancer twirling in a meadow with flowers swaying",
    "resolution": "720p",
    "duration": "8s",
    "generate_audio": false
  }' | jq
