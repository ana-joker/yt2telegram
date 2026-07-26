#!/bin/bash
# Trigger YouTube → Telegram pipeline
# Usage: ./trigger.sh <youtube_url> [caption]

URL="$1"
CAPTION="${2:-From @CLI2ALBEDO_BOT}"

if [ -z "$URL" ]; then
    echo "Usage: $0 <youtube_url> [caption]"
    exit 1
fi

echo "📥 Triggering download for: $URL"

# Use workflow_dispatch (reliable) instead of repository_dispatch API
gh workflow run "YouTube Downloader" \
    --repo ana-joker/yt2telegram \
    --field url="$URL" \
    --field caption="$CAPTION"

if [ $? -eq 0 ]; then
    echo "✅ Pipeline triggered! Video arriving in your Telegram in ~1 min."
    echo "   View at: https://github.com/ana-joker/yt2telegram/actions"
else
    echo "❌ Failed. Check gh auth status."
fi
