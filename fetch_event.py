from playwright.async_api import async_playwright
from datetime import datetime
from PIL import Image, ImageColor

IMAGE_PATH = "calendar.png"
CROPPED_IMAGE_PATH = "calendar_padded.png"
PADDING = 30

async def fetch_event_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto("https://www.elsrift.to/events", timeout=60000)
        await page.wait_for_selector("#calendar", timeout=10000)

        calendar = await page.query_selector("#calendar")
        if calendar:
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
