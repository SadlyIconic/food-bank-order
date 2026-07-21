# Food Bank Demand Intelligence

> Predict next week's supply from anonymous client category requests — staff adjust their Food Lifeline order manually. Zero integrations, zero LLM, pure SQL on SQLite or Turso.

Clients tap planning categories (Produce, Protein, Gluten-Free Staples, Diapers, etc.). Staff set supply levels, review an FLL pallet worksheet, and broadcast remaining category gaps to neighborhood donors.

## Features

- **Category board** — Clients tap what they expect to need this week (one anonymous submission per session/week)
- **Weekly SQL aggregation** — `COUNT(DISTINCT client_id)` by category with ISO week keys
- **Trend dashboard** — `/admin/trends` with headline insights, comparison table, week selector
- **Supply levels** — `/admin/supply` five-level assessment per planning category + storage limits
- **Monday order worksheet** — `/admin/order` FLL pallet recommendations (6–8 cap) from demand + supply gap engine, plus recommended mix summary, also-consider list, and bundle hints
- **Next-week forecast** — Rolling average + optional seasonal bumps (`seasonal_bumps.json`) on trends and order pages
- **Category donor board** — `/community` with category pledges (no PII, no SKU math)
- **CSV export** — Trends and FLL worksheet downloads for manual Food Lifeline ordering
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
2. **Review trends** — Open `/admin/trends`. Compare % of clients per category vs last week, rolling average, and next-week forecast estimate.
3. **Set supply levels** — `/admin/supply`: rate each planning category (critically low → full) and storage areas.
4. **Monday order worksheet** — `/admin/order`: review recommended mix, FLL pallet checklist (max 6–8), also-consider pallets, bundle suggestions, category gap table, donor queue preview. Export CSV.
5. **Place FLL order manually** — Use the worksheet alongside your Food Lifeline portal (no API integration).
6. **Broadcast donor gaps** — `/admin/community` or one-click **Publish donor needs** from the order page. Share `/community` with neighborhood donors.
7. **Adjust settings** — `/admin/settings` for agency name, rolling window, FLL pallet cap, high-demand threshold, seasonal bumps toggle, and donor/About content.

Legacy shop and cart URLs redirect to the client request board.

### Client workflow

1. Visit `/` — no login, no names.
2. Tap every category you expect to need this week.
3. Submit once — a session UUID tracks anonymous demand; one submission per week.

### Donor workflow

1. Visit `/community` when staff have published the board.
2. See low/critically low categories with example items (no client names or counts).
3. Pledge a category at `/community/pledge` with optional note.

## Data model

| Table / file | Purpose |
|--------------|---------|
| `categories.json` | Seed planning buckets (Produce, Protein, Diapers, …) |
| `fll_pallets.json` | Food Lifeline pallet names mapped to planning categories |
| `seasonal_bumps.json` | Month → category extra percentage points for forecast/priority |
| `bundle_rules.json` | Cooler/shelf bundle hints when multiple categories are low |
| `client_week_meta` | Anonymous “expecting visit this week?” flag per client/week |
| `categories` table | Active planning categories per `food_bank_id` |
| `client_requests` | One row per category tap; `visit_week` = ISO week key |
| `trend_snapshots` | Saved weekly metrics for WoW / rolling-average comparisons |
| `kv_store` `staff_thresholds` | Supply levels per planning category + storage |
| `kv_store` `app_settings` | Agency name, rolling window, FLL pallet cap, seasonal bumps toggle |
| `category_pledges` | Donor pledges by planning category |
| `items.json` | Legacy SKU catalog (example items enrichment) |
| Turso / `data/food_bank.db` | Persistence |

## Multi-agency roadmap

**Today:** Single agency per deployment (`food_bank_id = default`).

**Future:** Multiple agencies scoped by `food_bank_id` column already present on core tables.

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
