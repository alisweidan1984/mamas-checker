"""
One-off inspector. Does NOT check availability or send alerts.
It just opens the real page, clicks Reservations, and saves:
  - screenshots before/after the click
  - the full page HTML
  - the HTML of every iframe on the page (widgets are often inside one)

Run this once (via the GitHub Actions workflow_dispatch workflow),
download the artifact, and share the HTML/screenshots back so the
real checker script can be written with correct selectors instead
of guesses.
"""

from playwright.sync_api import sync_playwright

SITE_URL = "https://mamasfishhouse.com/contact/"


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 1000},
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = context.new_page()

        print(f"Loading {SITE_URL}")
        page.goto(SITE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        page.screenshot(path="01_initial_page.png", full_page=True)

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
            print("No obvious reservations trigger found. HTML dump below will show why.")

        page.wait_for_timeout(6000)
        page.screenshot(path="02_after_click.png", full_page=True)

        with open("page_full.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("Saved page_full.html")

        for i, frame in enumerate(page.frames):
            try:
                html = frame.content()
                safe_url = frame.url[:40].replace("/", "_").replace(":", "_") or "root"
                fname = f"frame_{i}_{safe_url}.html"
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"Saved {fname} (frame url: {frame.url})")
            except Exception as e:
                print(f"Could not read frame {i}: {e}")

        browser.close()
        print("Done.")


if __name__ == "__main__":
    run()
