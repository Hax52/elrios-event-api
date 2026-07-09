import asyncio
import json
import math
import os
import sys
from datetime import datetime, timezone

from playwright.async_api import async_playwright
from PIL import Image, ImageColor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "calendar.png")
CROPPED_IMAGE_PATH = os.path.join(BASE_DIR, "calendar_padded.png")
DATA_PATH = os.path.join(BASE_DIR, "event_data.json")
PADDING = 30
MAX_ATTEMPTS = 3
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class ScrapeFailure(Exception):
    """Raised when the scrape ran but produced data we don't trust."""


async def fetch_event_data_once():
    if os.path.exists(IMAGE_PATH):
        os.remove(IMAGE_PATH)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            device_scale_factor=1.0,
            viewport={"width": 1920, "height": 1600},
            user_agent=USER_AGENT,
        )
        await page.goto("https://www.elsrift.to/events", timeout=60000)
        await page.wait_for_selector("#calendar", timeout=15000)
        calendar = await page.query_selector("#calendar")

        if not calendar:
            await browser.close()
            raise ScrapeFailure("Could not find #calendar element on the page")

        await calendar.scroll_into_view_if_needed()
        box = await calendar.bounding_box()
        if not box:
            await browser.close()
            raise ScrapeFailure("Calendar element had no bounding box")

        expanded_box = {
            # Floor the origin (expanding up/left), ceil the dimensions
            # (expanding down/right): int() truncation of fractional pixel
            # values was shaving off the calendar's bottom/right border line.
            "x": max(math.floor(box["x"]) - 4, 0),
            "y": max(math.floor(box["y"]) - 4, 0),
            "width": math.ceil(box["width"]) + 8,
            "height": math.ceil(box["height"]) + 8,
        }
        await page.screenshot(path=IMAGE_PATH, clip=expanded_box)

        server_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        event_title = await page.eval_on_selector(
            "td.fc-day-today .fc-event-title", "el => el?.innerText"
        )
        calendar_title = await page.eval_on_selector(
            ".fc-toolbar-title", "el => el?.innerText"
        )

        await browser.close()

        # Trust nothing: if either selector came back empty, the page structure
        # likely changed or didn't finish loading. Don't silently ship a fake
        # "Unknown Event" — treat it as a failed attempt so we retry, and if all
        # retries fail, the workflow errors out loudly instead of committing junk.
        if not event_title or not calendar_title:
            raise ScrapeFailure(
                f"Selectors returned empty data (event_title={event_title!r}, "
                f"calendar_title={calendar_title!r}) — page structure may have changed"
            )

        with Image.open(IMAGE_PATH) as img:
            bg = ImageColor.getrgb("#15151a")
            padded = Image.new("RGB", (img.width + PADDING * 2, img.height + PADDING * 2), bg)
            padded.paste(img, (PADDING, PADDING))
            padded.save(CROPPED_IMAGE_PATH)

        return server_time, event_title, calendar_title


async def fetch_event_data_with_retries():
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}...")
            return await fetch_event_data_once()
        except Exception as e:
            last_error = e
            print(f"Attempt {attempt} failed: {e}")
            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(5 * attempt)  # 5s, then 10s backoff
    raise last_error


async def main():
    try:
        server_time, event_title, calendar_title = await fetch_event_data_with_retries()
    except Exception as e:
        # Fail the whole job loudly. This is deliberate: we do NOT write a
        # partial/placeholder event_data.json here, so the last known-good
        # file already committed in the repo stays in place until a future
        # run succeeds, instead of getting overwritten with garbage.
        print(f"::error::All {MAX_ATTEMPTS} scrape attempts failed: {e}")
        sys.exit(1)

    data = {
        "server_time": server_time,
        "event_name": event_title,
        "calendar_title": calendar_title,
    }
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {DATA_PATH}: {data}")


if __name__ == "__main__":
    asyncio.run(main())
