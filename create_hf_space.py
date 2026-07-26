"""Create and deploy Hugging Face Space for yt2telegram.
Usage: set HF_TOKEN env var first, or pass as arg.
"""
import os, sys
from huggingface_hub import HfApi

HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    print("❌ Set HF_TOKEN environment variable")
    sys.exit(1)

api = HfApi(token=HF_TOKEN)

who = api.whoami()
username = who["name"]
space_id = f"{username}/yt2telegram"
print(f"Authenticated as: {username}")

# Check if space exists
try:
    info = api.repo_info(space_id, repo_type="space")
    print(f"Space exists: {space_id}")
except Exception as e:
    print(f"Creating space: {space_id}")
    api.create_repo(
        repo_id=space_id,
        repo_type="space",
        private=False,
        space_sdk="gradio",
    )
    print(f"Space created: {space_id}")

print(f"\n✅ Space: https://huggingface.co/spaces/{space_id}")
print("To set secrets, use HF dashboard Settings → Secrets")
print("Required: TG_BOT_TOKEN, TG_CHAT_ID")
