"""
YouTube → Telegram Bridge - Hugging Face Space (Gradio)
Receives YouTube links, downloads via yt-dlp, uploads to Telegram.
Zero local device usage — all runs on HF cloud.
"""

import os
import subprocess
import tempfile
import threading
from pathlib import Path
import gradio as gr
import httpx
import json

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TG_CHAT_ID", "")

def download_and_send(url, status_box):
    """Download YouTube video and send to Telegram."""
    
    if not BOT_TOKEN or not CHAT_ID:
        yield status_box, "❌ Telegram not configured. Set TG_BOT_TOKEN and TG_CHAT_ID secrets."
        return
    
    if not url or not url.strip():
        yield status_box, "❌ Please provide a YouTube URL."
        return
    
    yield status_box, f"⏳ Starting download: {url}"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            # Step 1: Download with yt-dlp
            output_template = os.path.join(tmpdir, "video.%(ext)s")
            
            result = subprocess.run([
                "yt-dlp",
                "--restrict-filenames",
                "-f", "best[ext=mp4]/best",
                "-o", output_template,
                "--print", "filename",
                url.strip()
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                err = result.stderr[:500]
                yield status_box, f"❌ Download failed: {err}"
                return
            
            # Find the downloaded file
            output_files = list(Path(tmpdir).iterdir())
            if not output_files:
                yield status_box, "❌ No output file produced."
                return
            
            video_path = output_files[0]
            file_size_mb = video_path.stat().st_size / (1024 * 1024)
            yield status_box, f"📦 Downloaded: {video_path.name} ({file_size_mb:.1f} MB). Uploading to Telegram..."
            
            # Step 2: Upload to Telegram
            with open(video_path, "rb") as f:
                files = {"video": (video_path.name, f, "video/mp4")}
                data = {
                    "chat_id": CHAT_ID,
                    "caption": video_path.name,
                    "supports_streaming": "true"
                }
                
                with httpx.Client(timeout=300.0) as client:
                    resp = client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                        data=data,
                        files=files
                    )
                    
                    tg_result = resp.json()
                    
                    if tg_result.get("ok"):
                        yield status_box, f"✅ SUCCESS! Video sent to Telegram ({file_size_mb:.1f} MB)"
                    else:
                        # Try as document
                        with open(video_path, "rb") as f2:
                            files2 = {"document": (video_path.name, f2, "application/octet-stream")}
                            resp2 = client.post(
                                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                                data={"chat_id": CHAT_ID, "caption": video_path.name},
                                files=files2
                            )
                            tg2 = resp2.json()
                            if tg2.get("ok"):
                                yield status_box, f"✅ Sent as document ({file_size_mb:.1f} MB)"
                            else:
                                yield status_box, f"❌ Telegram error: {tg2}"
        
        except subprocess.TimeoutExpired:
            yield status_box, "❌ Download timed out (5 min limit for larger videos)"
        except Exception as e:
            yield status_box, f"❌ Error: {str(e)[:500]}"


def health_check():
    """Return service status."""
    info = []
    
    info.append(f"🤖 Bot configured: {'✅' if BOT_TOKEN else '❌'}")
    info.append(f"👤 Chat ID set: {'✅' if CHAT_ID else '❌'}")
    
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
        info.append(f"📦 yt-dlp: {result.stdout.strip()}")
    except:
        info.append("📦 yt-dlp: ❌ not found")
    
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        first_line = result.stdout.split("\n")[0] if result.stdout else "?"
        info.append(f"🎬 ffmpeg: {first_line[:60]}")
    except:
        info.append("🎬 ffmpeg: ❌ not found")
    
    return "\n".join(info)


# ─── Gradio UI ──────────────────────────────────

with gr.Blocks(title="YouTube → Telegram Bridge", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📹 YouTube → Telegram Bridge
    
    Paste any YouTube link (video, short, playlist) and it gets downloaded and sent to your Telegram.
    
    **All processing happens in the cloud — zero usage from your device.**
    """)
    
    with gr.Row():
        with gr.Column(scale=3):
            url_input = gr.Textbox(
                label="YouTube URL",
                placeholder="https://youtube.com/watch?v=... or https://youtu.be/... or https://youtube.com/shorts/...",
                lines=2
            )
            submit_btn = gr.Button("🚀 Download & Send to Telegram", variant="primary")
        
        with gr.Column(scale=2):
            status_box = gr.Textbox(label="Status", lines=6, interactive=False)
    
    gr.Markdown("---")
    
    with gr.Accordion("Health Check", open=False):
        health_btn = gr.Button("🩺 Check Service Status")
        health_output = gr.Textbox(label="Status", lines=5)
        health_btn.click(fn=health_check, outputs=health_output)
    
    submit_btn.click(
        fn=download_and_send,
        inputs=[url_input, gr.State()],
        outputs=[status_box]
    )
    
    gr.Markdown("""
    ### How it works
    1. You paste a YouTube URL
    2. The Space downloads it with yt-dlp + ffmpeg
    3. It uploads to Telegram via @CLI2ALBEDO_BOT
    4. Video appears in your ahmed1 chat
    
    ### Limits
    - Max 5 minutes download time (larger videos time out on free tier)
    - Telegram file limit: 2GB (most videos are fine)
    - Free tier may have cold starts (wake up delay)
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
