# Connect Pantry — Food Bank Demand Intelligence

> Predict next week's supply from anonymous client category requests — staff adjust their Food Lifeline order manually. Zero integrations, zero LLM, pure SQL on SQLite or Turso.

Clients tap planning categories (Produce, Protein, Gluten-Free Staples, Diapers, etc.), optionally flag whether they expect a visit this week, and staff review trends, set supply levels, prepare Monday FLL orders, and broadcast remaining gaps to neighborhood donors.

## Features

### Client & donor (public)
- **Category board** — `/` — tap categories with detail modal; one anonymous submission per session/week
- **Visit question** — “Expecting a visit this week?” normalizes demand % for staff trends
- **Six-language UI** — English, Español, 中文, Tiếng Việt, Tagalog, Soomaali (`static/i18n.js`)
- **About page** — `/about` — mission, hours, location, map link, how to help
- **Donor board** — `/community` — category needs with donor tips, supply badges, pledge board
- **Donor pledge flow** — `/community/pledge` → thank-you with drop-off instructions and Maps link

### Staff (admin)
- **Trend dashboard** — `/admin/trends` — WoW + rolling average + next-week forecast estimate
- **Supply levels** — `/admin/supply` — five-level assessment per category + storage limits
- **Monday order worksheet** — `/admin/order` — FLL pallet checklist, recommended mix, also-consider, bundle hints
- **Settings** — `/admin/settings` — agency identity, distribution info, planning limits, seasonal bumps toggle
- **Weekly reset** — snapshot trends, clear client taps, reset supply, unpublish donor board
- **CSV export** — trends and order worksheet downloads

### Planning engine (local rules, no ML)
- **Priority scores** — integer-ranked categories and pallets from demand + supply + trend delta + optional seasonal bump
- **Recommended mix** — headline summary by storage type (cooler vs shelf)
- **Also consider** — next pallets below cap that still score above zero
- **Forecast** — rolling average + `seasonal_bumps.json` for next ISO week
- **Bundle rules** — `bundle_rules.json` hints (e.g. produce + dairy both low → both cooler pallets)

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

### Smoke tests

```bash
cd food_bank
python -m unittest tests.test_planning_smoke
```

Covers visit normalization, forecast, bundle rules, recommended mix, map URL validation, and donor guidance.

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
2. **Review trends** — `/admin/trends`: compare demand %, WoW delta, rolling average, and next-week forecast (estimate only).
3. **Set supply levels** — `/admin/supply`: rate each planning category (critically low → full) and storage areas.
4. **Monday order worksheet** — `/admin/order`: recommended mix, FLL checklist (max 6–8), also-consider, bundle suggestions, donor queue preview. Export CSV.
5. **Place FLL order manually** — Use the worksheet alongside your Food Lifeline portal (no API integration).
6. **Broadcast donor gaps** — `/admin/community` or **Publish donor needs** from the order page. Share `/community`.
7. **Adjust settings** — `/admin/settings` (see table below). Use **Reset planning week** when starting a fresh cycle.

Legacy shop and cart URLs redirect to the client request board.

### Client workflow

1. Visit `/` — no login, no names.
2. Answer whether you expect to visit for food this week (yes/no).
3. Tap categories you expect to need; submit once per week.

When clients answer “yes” to the visit question, their category taps count toward normalized demand % on the trends dashboard. Clients who answer “no” still submit needs but are excluded from the percentage denominator.

### Donor workflow

1. Visit `/community` when staff have published the board.
2. See low/critically low categories with donor tips and example items.
3. Pledge at `/community/pledge`; thank-you page shows drop-off instructions and optional Google Maps link.

### Settings reference (`/admin/settings`)

| Field | Purpose |
|-------|---------|
| Agency display name | Shown in nav and page titles |
| Food bank ID | Single agency today (`default`); reserved for multi-site |
| Distribution name / date / location label | Shown on donor board and pledge thank-you |
| Donor drop-off instructions | Text on donor board, About, pledge thank-you |
| Drop-off Google Maps URL | `https://` only; “Open in Maps” button for donors |
| Agency hours | About page |
| Extra About paragraph | Optional second mission block on `/about` |
| Rolling average window | Weeks used for trend comparison and forecast base |
| Max FLL pallets | 6–8 cap for Monday worksheet |
| High demand threshold | Categories above this % stay in FLL plan even when supply is high |
| Apply seasonal bumps | Toggle `seasonal_bumps.json` for forecast and priority scores |

## Config files

| File | Purpose |
|------|---------|
| `categories.json` | Planning categories + descriptions + optional `donor_guidance` per category |
| `fll_pallets.json` | FLL pallet names mapped to planning categories |
| `seasonal_bumps.json` | Month (1–12) → category_id → extra percentage points |
| `bundle_rules.json` | Rules like “produce + dairy both low → suggest cooler pallets” |

Edit JSON locally; no redeploy needed for content-only changes beyond what is baked into releases.

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
| `kv_store` `app_settings` | Agency name, rolling window, FLL cap, seasonal toggle, About/donor fields |
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
