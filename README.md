# mamas-checker

One repo, two phases.

**Phase A (do now):** run the inspector — it opens the real reservation page
and hands back the HTML so the real availability-check logic can be written.
Only `inspector.py` + `requirements.txt` + `.github/workflows/inspect.yml`
are needed for this. No Telegram, no secrets, nothing else required yet.

**Phase B (later):** once you've sent back the inspector's output and gotten
a finished `checker.py` back, you'll add one more workflow file
(`.github/workflows/check.yml`) and two secrets, and it starts monitoring
for real, every 30 minutes, with Telegram alerts.

`notify.py`, `checker.py`, and `state.json` are already sitting in this repo
for Phase B — you don't need to touch them in Phase A. There's no
`check.yml` yet on purpose: adding the schedule before the real
availability-check code exists would just fire a warning message to
Telegram every 30 minutes for no reason.
