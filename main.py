from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fetch_event import fetch_event_data
import os
import subprocess

# Install Chromium on Render free tier (if not already installed)
def ensure_chromium_installed():
    chromium_path = "/opt/render/.cache/ms-playwright/chromium_headless_shell-1179/chrome-linux/headless_shell"
    if not os.path.exists(chromium_path):
        try:
            print("▶ Installing Chromium for Playwright...")
            subprocess.run(["playwright", "install", "chromium"], check=True)
        except Exception as e:
            print("❌ Failed to install Chromium:", e)

# Call before FastAPI starts
ensure_chromium_installed()

# ────────────────────────────
app = FastAPI()

@app.get("/api/event")
async def get_event():
    try:
        server_time, event_name, calendar_title = await fetch_event_data()
        return JSONResponse({
            "server_time": server_time,
            "event_name": event_name,
            "calendar_title": calendar_title
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/event/image")
def get_event_image():
    return FileResponse("calendar_padded.png")

# Local dev only — Render ignores this section
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
