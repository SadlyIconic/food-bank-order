# AGENTS.md

This repository is a collection of small, independent apps. Each lives in its own
top-level directory and can be run on its own.

| App | Dir | Type | Deps |
|-----|-----|------|------|
| Food Bank Demand Intelligence | `food_bank/` | Flask web app (deployed product, see `render.yaml`) | `flask`, `gunicorn`, `Pillow` |
| Tennis Journal | `tennis_journal/` | Flask web app | `flask` |
| Quiz App | `quiz_app/` | Tkinter desktop GUI | stdlib + `python3-tk` (system) |
| Chess Openings | `chess_openings/` | Static site (ES modules + CDN libs) | none (needs a static server) |
| Tic Tac Toe | `tic-tac-toe/` | Static HTML/JS | none |

## Cursor Cloud specific instructions

Dependencies (Python packages) are refreshed automatically by the startup update
script. System package `python3-tk` (needed only by `quiz_app`) is not in the
update script; it is a one-off system dependency installed via
`sudo apt-get install -y python3-tk`.

Running the apps (all commands are non-obvious caveats only; see each app's README
for the documented commands):

- `food_bank` and `tennis_journal` both default to port `5000` (`app.run` /
  `flask run`). Run them on different ports if running simultaneously, e.g.
  `flask --app app run --port 5001` for `tennis_journal`.
- `food_bank`: `cd food_bank && python3 app.py`. Locally it uses ephemeral SQLite
  under `food_bank/data/` (gitignored, auto-created); `TURSO_*` env vars are only
  for production. Admin login password defaults to `Iconic` (`ADMIN_PASSWORD`).
- `tennis_journal`: persists to `tennis_journal/entries.json`.
- `chess_openings`: must be served over HTTP (ES modules + `fetch`), e.g.
  `cd chess_openings && python3 -m http.server 8080`. Board/engine libraries load
  from CDNs, so the interactive board needs network egress.
- `quiz_app`: GUI app; needs a display (`DISPLAY=:1` in the cloud desktop):
  `cd quiz_app && DISPLAY=:1 python3 quiz_app.py`.
- `tic-tac-toe`: open `tic-tac-toe/index.html` or serve the folder statically.

The `pip install` commands need `--break-system-packages` on this Ubuntu image
(PEP 668 externally-managed environment). Console scripts (`flask`, `gunicorn`)
install to `~/.local/bin`; add it to `PATH` or invoke via `python3 -m`.

There are no test suites or lint configs in this repo.
