"""
Telegram notification helper.

Uses the plain Telegram Bot HTTP API (no library needed beyond `requests`).
Requires two environment variables, set as GitHub Actions secrets:
  TELEGRAM_BOT_TOKEN  - the token BotFather gave you
  TELEGRAM_CHAT_ID    - your personal chat id (see SETUP.md for how to get it)
"""
import os
import requests


def send_telegram(message: str) -> dict:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=15)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    # Quick manual test: `python notify.py` sends a test ping.
    send_telegram("✅ Test message from mamas-checker — Telegram wiring works.")
    print("Sent. Check your Telegram app.")
