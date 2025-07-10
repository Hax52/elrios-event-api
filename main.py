from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fetch_event import fetch_event_data
import os
import subprocess

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "calendar.png")
CROPPED_IMAGE_PATH = os.path.join(BASE_DIR, "calendar_padded.png")

def ensure_chromium_installed():
    chromium_path = "/opt/render/.cache/ms-playwright/chromium_headless_shell-1179/chrome-linux/headless_shell"
    if not os.path.exists(chromium_path):
        try:
            print("▶ Installing Chromium via Playwright...")
            subprocess.run(["playwright", "install", "chromium"], check=True)
            print("✅ Chromium installed.")
        except Exception as e:
            print(f"❌ Failed to install Chromium: {e}")
    else:
        print("✅ Chromium already installed.")

# ─────────────────────────────
@app.on_event("startup")
async def startup_tasks():
    ensure_chromium_installed()
    try:
        print("▶ Generating calendar on startup...")
        await fetch_event_data()
        print("✅ Calendar image generated.")
    except Exception as e:
        print(f"❌ Failed to generate calendar image on startup: {e}")

@app.get("/healthz")
def health_check():
    return {"ok": True}

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
    if os.path.exists(CROPPED_IMAGE_PATH):
        return FileResponse(CROPPED_IMAGE_PATH)
    return JSONResponse(status_code=404, content={"error": "calendar_padded.png not found"})

# ─────────────────────────────
# Local dev only — ignored by Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
