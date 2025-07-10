from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fetch_event import fetch_event_data
import os
import subprocess

app = FastAPI()

IMAGE_PATH = "calendar.png"
CROPPED_IMAGE_PATH = "calendar_padded.png"

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

# Local dev only — ignored by Render
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
