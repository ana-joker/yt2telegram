---
title: YouTube → Telegram Bridge
emoji: 📹
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# YouTube → Telegram Bridge

Zero-local-usage YouTube downloader. Receives a YouTube link, downloads via yt-dlp,
and uploads the video directly to a Telegram chat.

## API

- `GET /health` — health check
- `POST /download` — `{"url": "youtube_link", "caption": "optional text"}`
- `POST /download-short` — optimized for Shorts/short content

## Environment Variables

- `TG_BOT_TOKEN` — Telegram bot token
- `TG_CHAT_ID` — Target chat ID
