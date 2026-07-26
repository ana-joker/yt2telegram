#!/bin/bash
# Trigger Video Downloader (explicit dev workflow, same as production now)
# Kept for backward compatibility — redirects to main trigger.
# Usage: ./trigger-dev.sh <url> [caption] [max_videos]

exec "$(dirname "$0")/trigger.sh" "$@"
