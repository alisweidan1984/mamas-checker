"""
Follow-up inspector: also opens the Date and Guests pickers inside the
SevenRooms widget, pages the calendar forward toward November 2026, and
tries clicking Nov 21 - capturing HTML/screenshots at each stage.

Still diagnostic only - doesn't check availability or send alerts.
Every risky step is wrapped in try/except so a wrong guess about one
selector doesn't stop the rest of the run.
"""

from playwright.sync_api import sync_playwright

SITE_URL = "https://mamasfishhouse.com/contact/"


def dump_frame(frame, label):
    try:
        html = frame.content()
        with open(f"frame_{label}.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved frame_{label}.html")
    except Exception as e:
        print(f"Could not dump frame for {label}: {e}")


def find_sevenrooms_frame(page):
    for frame in page.frames:
        if "sevenrooms.com" in frame.url:
            return frame
    return None


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 1000},
        )
        page = context.new_page()

        print(f"Loading {SITE_URL}")
        page.goto(SITE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        candidates = [
            "a:has-text('Reservations')",
            "button:has-text('Reservations')",
            "a:has-text('Reserve')",
            "#sr-res-root",
            "[id*='sr-res']",
        ]
        clicked = False
        for sel in candidates:
            try:
                el = page.locator(sel).first
                if el.is_visible(timeout=2000):
                    print(f"Clicking: {sel}")
                    el.click()
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            print("No obvious reservations trigger found - iframe search will likely fail.")

        page.wait_for_timeout(6000)

        sr_frame = find_sevenrooms_frame(page)
        if sr_frame is None:
            print("Could not find the SevenRooms iframe - saving what we have and stopping.")
            page.screenshot(path="00_no_widget_found.png", full_page=True)
            with open("page_full.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            browser.close()
            return

        try:
            sr_frame.locator('button[aria-controls="search-pill-guest-popover"]').click()
            page.wait_for_timeout(1500)
            page.screenshot(path="03_guests_popover.png", full_page=True)
            dump_frame(sr_frame, "guests_popover")
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
        except Exception as e:
            print(f"Guests popover step failed: {e}")

        try:
            sr_frame.locator('button[aria-controls="search-pill-date-popover"]').click()
            page.wait_for_timeout(1500)
            page.screenshot(path="04_date_popover.png", full_page=True)
            dump_frame(sr_frame, "date_popover")
        except Exception as e:
            print(f"Date popover step failed: {e}")

        next_month_candidates = [
            'button[aria-label*="next month" i]',
            'button[aria-label*="Next Month" i]',
            'button[aria-label*="next" i]',
        ]
        advanced = False
        for sel in next_month_candidates:
            try:
                btn = sr_frame.locator(sel).first
                if btn.is_visible(timeout=1000):
                    for _ in range(3):
                        btn.click()
                        page.wait_for_timeout(600)
                    advanced = True
                    break
            except Exception:
                continue

        page.screenshot(path="05_calendar_after_nav.png", full_page=True)
        dump_frame(sr_frame, "calendar_after_nav")
        print(f"Advanced calendar months: {advanced}")

        day_candidates = [
            'button[aria-label*="November 21" i]',
            'button[aria-label*="Nov 21" i]',
        ]
        picked = False
        for sel in day_candidates:
            try:
                day_btn = sr_frame.locator(sel).first
                if day_btn.is_visible(timeout=1000):
                    day_btn.click()
                    picked = True
                    break
            except Exception:
                continue

        page.wait_for_timeout(2500)
        page.screenshot(path="06_after_date_pick.png", full_page=True)
        dump_frame(sr_frame, "after_date_pick")
        print(f"Picked a day cell: {picked}")

        browser.close()
        print("Done.")


if __name__ == "__main__":
    run()

