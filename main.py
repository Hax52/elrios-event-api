from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fetch_event import fetch_event_data
import os

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

# Only for local testing — Render ignores this when using the Start Command
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render injects PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port)
