#!/bin/bash
# Trigger DEV YouTube/Media pipeline (multi-platform + playlists)
# Usage: ./trigger-dev.sh <url> [caption] [max_videos]

URL="$1"
CAPTION="${2:-From @CLI2ALBEDO_BOT}"
MAX="${3:-3}"

if [ -z "$URL" ]; then
    echo "Usage: $0 <url> [caption] [max_videos]"
    echo ""
    echo "Examples:"
    echo "  ./trigger-dev.sh \"https://youtube.com/watch?v=...\""
    echo "  ./trigger-dev.sh \"https://youtube.com/playlist?list=...\" \"My playlist\" 5"
    echo "  ./trigger-dev.sh \"https://instagram.com/reel/...\""
    echo "  ./trigger-dev.sh \"https://x.com/user/status/...\""
    echo "  ./trigger-dev.sh \"https://facebook.com/watch/?v=...\""
    echo "  ./trigger-dev.sh \"https://reddit.com/r/.../comments/.../\""
    exit 1
fi

echo "Triggering DEV pipeline for: $URL"
echo "Caption: $CAPTION"
echo "Max videos: $MAX"
echo "Branch: develop"
echo ""

gh workflow run "YouTube Downloader Dev" \
    --repo ana-joker/yt2telegram \
    --ref develop \
    --field url="$URL" \
    --field caption="$CAPTION" \
    --field max_videos="$MAX"

if [ $? -eq 0 ]; then
    echo ""
    echo "DEV pipeline triggered! View at:"
    echo "  https://github.com/ana-joker/yt2telegram/actions"
    echo "Make sure branch is set to 'develop' in the UI."
else
    echo "Failed. Check gh auth status."
    exit 1
fi
