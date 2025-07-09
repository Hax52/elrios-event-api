from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fetch_event import fetch_event_data

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
