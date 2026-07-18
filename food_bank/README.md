# Food Bank Demand Intelligence

> Predict next week's supply from anonymous client category requests — staff adjust their Food Lifeline order manually. Zero integrations, zero LLM, pure SQL on SQLite or Turso.

Clients tap planning categories (Produce, Protein, Gluten-Free Staples, Diapers, etc.). The app aggregates weekly trends so staff can export a CSV before Monday ordering. No Food Lifeline APIs, no inventory sync, no NLP.

## Features

- **Category board** — Clients tap what they expect to need this week (one anonymous submission per session/week)
- **Weekly SQL aggregation** — `COUNT(DISTINCT client_id)` by category with ISO week keys
- **Trend dashboard** — `/admin/trends` with headline insights, comparison table, week selector
- **CSV export** — Download trends for your Monday Food Lifeline workflow (second screen)
- **Rolling averages** — Configurable N-week comparison from saved snapshots
- **SQLite / Turso** — Same deploy model as before; no Firebase or Supabase

## Requirements

- Python 3.10+
- Flask, Gunicorn

## Setup and run

```powershell
cd food_bank
pip install -r requirements.txt
py -m flask --app app run
```

On Windows, use `py -m flask` instead of `flask` directly.

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) for the client board. Admin: `/admin` → trends dashboard.

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | dev placeholder | Flask session signing (also assigns anonymous `client_id`) |
| `ADMIN_PASSWORD` | `Iconic` | Admin login password |
| `TURSO_DATABASE_URL` | *(unset)* | Turso database URL (`libsql://...`) for production |
| `TURSO_AUTH_TOKEN` | *(unset)* | Turso auth token |
| `DATABASE_PATH` | `data/food_bank.db` | Local SQLite file when Turso is not configured |

For production on Render, set `TURSO_*` variables (see `docs/TURSO_SETUP.md`). For local dev, omit them to use SQLite.

## Usage

### Staff workflow (Monday Food Lifeline prep)

1. **Share the client board** — Send `/` to clients during the week (QR code, kiosk, SMS).
2. **Review trends** — Open `/admin/trends` (password required). Default view is the current ISO week.
3. **Compare history** — Table shows % of clients per category, delta vs last week, and vs rolling average.
4. **Save snapshot** — Click **Save snapshot** (optional Sunday routine) to persist metrics for future comparisons.
5. **Export CSV** — Download `demand-trends-YYYY-Www.csv` and use it while placing your Food Lifeline order manually.
6. **Adjust settings** — `/admin/settings` for agency name, `food_bank_id`, and rolling window (1–12 weeks).

Legacy shop, cart, donor board, and shortage-broadcast URLs redirect to the new flow.

### Client workflow

1. Visit `/` — no login, no names.
2. Tap every category you expect to need this week.
3. Submit once — a session UUID tracks anonymous demand; one submission per week.

## Data model

| Table / file | Purpose |
|--------------|---------|
| `categories.json` | Seed planning buckets (Produce, Protein, Diapers, …) |
| `categories` table | Active planning categories per `food_bank_id` |
| `client_requests` | One row per category tap; `visit_week` = ISO week key |
| `trend_snapshots` | Saved weekly metrics for WoW / rolling-average comparisons |
| `kv_store` `app_settings` | Agency name, `food_bank_id`, rolling window |
| `items.json` | Legacy SKU catalog (optional reference; client UX no longer uses it) |
| Turso / `data/food_bank.db` | Persistence |

## Multi-agency roadmap

**Today:** Single agency per deployment (`food_bank_id = default`).

**Future:** Multiple agencies scoped by `food_bank_id` column already present on core tables.

## Donors (phase 2 — not built)

Public read-only view of top rising categories from the latest snapshot, using `donor_friendly_translation`. No pledges or inventory in v1 of this pivot.

## Deploy on Render (free)

1. Push this repo to GitHub.
2. Create a **Turso** database (free) — step-by-step: [`docs/TURSO_SETUP.md`](docs/TURSO_SETUP.md).
3. Create a **Web Service** or sync the Blueprint from `render.yaml` (free plan, **no disk**).
4. In Render, set environment variables:
   - `TURSO_DATABASE_URL`
   - `TURSO_AUTH_TOKEN`
   - `ADMIN_PASSWORD` (choose a strong password)
   - `SECRET_KEY` (auto-generated is fine)

Data persists in Turso across redeploys. Without `TURSO_*` vars, the app falls back to ephemeral local SQLite and loses data on redeploy.
