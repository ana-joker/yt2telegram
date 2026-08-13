#!/bin/bash
# Trigger Video Downloader pipeline (YouTube, Instagram, Facebook, Reddit, X/Twitter)
# Usage: ./trigger.sh <url> [caption] [max_videos] [mode]
#   mode: video (default) | audio (MP3 320kbps)

URL="$1"
CAPTION="${2:-From Albedo}"
MAX="${3:-3}"
MODE="${4:-video}"

if [ -z "$URL" ]; then
    echo "Usage: $0 <url> [caption] [max_videos] [mode]"
    echo ""
    echo "Examples:"
    echo "  $0 'https://youtube.com/watch?v=...'"
    echo "  $0 'https://www.instagram.com/reel/...' 'My caption'"
    echo "  $0 'https://www.reddit.com/r/.../comments/.../' 'Reddit vid' 5"
    echo "  $0 'https://youtube.com/watch?v=...' 'Song' 1 audio"
    echo ""
    echo "Supports: YouTube, Instagram, Facebook, Reddit, X/Twitter, TikTok"
    echo "Mode: video (default) or audio (MP3 320kbps)"
    exit 1
fi

echo "📥 Triggering download for: $URL"
echo "   Caption: $CAPTION"
echo "   Max videos: $MAX"
echo "   Mode: $MODE"

gh workflow run "Video Downloader" \
    --repo ana-joker/yt2telegram \
    --field url="$URL" \
    --field caption="$CAPTION" \
    --field max_videos="$MAX" \
    --field mode="$MODE"

if [ $? -eq 0 ]; then
    echo "✅ Pipeline triggered! Video arriving in your Telegram in ~1-2 min."
    echo "   View at: https://github.com/ana-joker/yt2telegram/actions"
else
    echo "❌ Failed. Check gh auth status."
fi
