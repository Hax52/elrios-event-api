from playwright.async_api import async_playwright
from datetime import datetime
from PIL import Image, ImageColor
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "calendar.png")
CROPPED_IMAGE_PATH = os.path.join(BASE_DIR, "calendar_padded.png")
PADDING = 30

async def fetch_event_data():
    # Cleanup
    if os.path.exists(IMAGE_PATH):
        os.remove(IMAGE_PATH)
    if os.path.exists(CROPPED_IMAGE_PATH):
        os.remove(CROPPED_IMAGE_PATH)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(device_scale_factor=1.0, viewport={"width": 1920, "height": 1080})
        await page.goto("https://www.elsrift.to/events", timeout=60000)
        await page.wait_for_selector("#calendar", timeout=10000)

        calendar = await page.query_selector("#calendar")
        if calendar:
            await calendar.scroll_into_view_if_needed()
            box = await calendar.bounding_box()
            if box:
                expanded_box = {
                    "x": max(int(box["x"]) - 4, 0),
                    "y": max(int(box["y"]) - 4, 0),
                    "width": int(box["width"]) + 8,
                    "height": int(box["height"]) + 8
                }

                await page.screenshot(path=IMAGE_PATH, clip=expanded_box)

                with Image.open(IMAGE_PATH) as img:
                    bg = ImageColor.getrgb("#15151a")
                    padded = Image.new("RGB", (img.width + PADDING * 2, img.height + PADDING * 2), bg)
                    padded.paste(img, (PADDING, PADDING))
                    padded.save(CROPPED_IMAGE_PATH)

        server_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        event_title = await page.eval_on_selector("td.fc-day-today .fc-event-title", "el => el?.innerText") or "Unknown Event"
        calendar_title = await page.eval_on_selector(".fc-toolbar-title", "el => el.innerText") or "Unknown Month"

        await browser.close()
        return server_time, event_title, calendar_title
