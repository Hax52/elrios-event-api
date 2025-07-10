from playwright.async_api import async_playwright
from datetime import datetime

async def fetch_event_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto("https://www.elsrift.to/events", timeout=60000)
        await page.wait_for_selector("#calendar", timeout=10000)

        server_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        event = await page.eval_on_selector("td.fc-day-today .fc-event-title", "el => el?.innerText") or "Unknown Event"
        title = await page.eval_on_selector(".fc-toolbar-title", "el => el.innerText") or "Unknown Month"

        await browser.close()
        return server_time, event, title
