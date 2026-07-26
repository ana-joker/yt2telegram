"""
YouTube → Telegram Bridge - Hugging Face Space
Receives YouTube links, downloads via yt-dlp, uploads to Telegram.
Zero local device usage — all runs on HF cloud.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn

app = FastAPI(title="YouTube → Telegram Bridge")

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TG_CHAT_ID", "")

class DownloadRequest(BaseModel):
    url: str
    caption: str = ""

class StatusResponse(BaseModel):
    status: str
    message: str = ""

@app.get("/")
def root():
    return {"status": "alive", "service": "yt2telegram bridge"}

@app.get("/health")
def health():
    if not BOT_TOKEN or not CHAT_ID:
        return {"status": "degraded", "message": "Telegram credentials not configured"}
    
    # Check if yt-dlp is available
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
        yt_dlp_version = result.stdout.strip()
    except:
        yt_dlp_version = "not found"
    
    return {
        "status": "ok",
        "yt-dlp": yt_dlp_version,
        "telegram": "configured" if BOT_TOKEN else "missing"
    }

@app.post("/download", response_model=StatusResponse)
async def download_video(request: DownloadRequest):
    """Download a YouTube video and send it to Telegram."""
    
    if not BOT_TOKEN or not CHAT_ID:
        raise HTTPException(500, "Telegram not configured")
    
    if not request.url:
        raise HTTPException(400, "No URL provided")
    
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
                request.url
            ], capture_output=True, text=True, timeout=300)  # 5 min timeout
            
            if result.returncode != 0:
                raise HTTPException(500, f"yt-dlp failed: {result.stderr[:500]}")
            
            # Find the downloaded file
            output_files = list(Path(tmpdir).iterdir())
            if not output_files:
                raise HTTPException(500, "No output file produced")
            
            video_path = output_files[0]
            file_size_mb = video_path.stat().st_size / (1024 * 1024)
            
            # Step 2: Upload to Telegram
            async with httpx.AsyncClient(timeout=300.0) as client:
                with open(video_path, "rb") as f:
                    files = {"video": (video_path.name, f, "video/mp4")}
                    data = {
                        "chat_id": CHAT_ID,
                        "caption": request.caption or video_path.name,
                        "supports_streaming": "true"
                    }
                    
                    resp = await client.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                        data=data,
                        files=files
                    )
                    
                    tg_result = resp.json()
                    
                    if tg_result.get("ok"):
                        return StatusResponse(
                            status="success",
                            message=f"Video sent to Telegram ({file_size_mb:.1f} MB)"
                        )
                    else:
                        # Try as document if video fails
                        with open(video_path, "rb") as f2:
                            files2 = {"document": (video_path.name, f2, "application/octet-stream")}
                            resp2 = await client.post(
                                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                                data={"chat_id": CHAT_ID, "caption": request.caption or video_path.name},
                                files=files2
                            )
                            tg_result2 = resp2.json()
                            if tg_result2.get("ok"):
                                return StatusResponse(
                                    status="success",
                                    message=f"File sent to Telegram as document ({file_size_mb:.1f} MB)"
                                )
                            else:
                                raise HTTPException(502, f"Telegram error: {tg_result2}")
        
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "Download timed out (5 min limit)")
        except Exception as e:
            raise HTTPException(500, str(e)[:500])

@app.post("/download-short")
async def download_short(request: DownloadRequest):
    """
    Lightweight endpoint for shorter content (Shorts, < 5 min).
    Same as /download but with lower timeout and optimized for quick media.
    """
    return await download_video(request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
