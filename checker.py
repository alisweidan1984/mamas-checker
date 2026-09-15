"""
Mama's Fish House availability checker.

Runs headless (Playwright/"ghost browser"), checks all target dates for
PARTY_SIZE, and only messages Telegram when something actually changes:
  - a date newly opens up          -> instant alert
  - once per day, if nothing new   -> single "still nothing" heartbeat
This avoids pinging every 30 minutes with "no news" (that would be ~48
messages/day). If you'd rather get a message on every single check instead,
say so and this can be changed to unconditional per-run messages.
"""
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

from notify import send_telegram

RESTAURANT_URL = "https://www.mamasfishhouse.com/contact/"
PARTY_SIZE = 2
CHECK_DATES = [
    "2026-11-21", "2026-11-22", "2026-11-23", "2026-11-24", "2026-11-25",
    "2026-11-26", "2026-11-27", "2026-11-28", "2026-11-29",
]
STOP_AFTER = date(2026, 11, 29)
STATE_FILE = Path("state.json")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"available_dates": [], "last_heartbeat": None}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def check_date(page, target_date: str) -> bool:
    """
    Return True if a table for PARTY_SIZE is available on target_date.

    *** NOT YET WIRED UP ***
    This needs the real selectors from the SevenRooms widget, which come
    from running the inspector workflow (already built earlier) and sharing
    back page_full.html / frame_*.html. Everything else in this file --
    state diffing, dedup, the daily heartbeat, the Nov 29 cutoff, Telegram
    alerts -- is finished and doesn't depend on this function.
    """
    raise NotImplementedError("check_date needs real selectors from the inspector output")


def main() -> None:
    if date.today() > STOP_AFTER:
        print("Past the trip window -- nothing to check, exiting.")
        return

    state = load_state()
    newly_available = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(RESTAURANT_URL, wait_until="networkidle")

        for d in CHECK_DATES:
            try:
                is_open = check_date(page, d)
            except NotImplementedError:
                browser.close()
                send_telegram(
                    "⚠️ Mama's checker ran but check_date() isn't wired up yet -- "
                    "still waiting on real selectors from the inspector output."
                )
                sys.exit(1)

            was_open = d in state["available_dates"]
            if is_open and not was_open:
                newly_available.append(d)
            if not is_open and was_open:
                state["available_dates"].remove(d)

        browser.close()

    for d in newly_available:
        state["available_dates"].append(d)
        send_telegram(
            f"🎉 Table for {PARTY_SIZE} just opened at Mama's Fish House on {d}! "
            f"Book now: {RESTAURANT_URL}"
        )

    today_str = datetime.now(timezone.utc).date().isoformat()
    if not newly_available and state.get("last_heartbeat") != today_str:
        if state["available_dates"]:
            send_telegram(f"✅ Checked again -- still open: {', '.join(state['available_dates'])}")
        else:
            send_telegram("✅ Checked today -- nothing available yet for Nov 21-29.")
        state["last_heartbeat"] = today_str

    save_state(state)


if __name__ == "__main__":
    main()
