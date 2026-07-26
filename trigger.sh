#!/bin/bash
# Trigger YouTube → Telegram pipeline
# Usage: ./trigger.sh <youtube_url> [caption]

URL="$1"
CAPTION="${2:-From @CLI2ALBEDO_BOT}"

if [ -z "$URL" ]; then
    echo "Usage: $0 <youtube_url> [caption]"
    exit 1
fi

echo "📥 Dispatching: $URL"
gh api repos/ana-joker/yt2telegram/dispatches \
    --method POST \
    --field event_type="download-youtube" \
    --field client_payload="{\"url\": \"$URL\", \"caption\": \"$CAPTION\"}" \
    --silent

if [ $? -eq 0 ]; then
    echo "✅ GitHub Action dispatched! Video arriving in your Telegram in ~1 min."
else
    echo "❌ Failed to dispatch. Check gh auth status."
fi
