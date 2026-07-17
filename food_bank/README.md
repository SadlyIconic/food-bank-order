# Food Bank Order App

A Flask app for coordinating food bank shopping under a weight limit. Households request items (capped per order), admins see total demand vs trip capacity, enter store surplus, plan what to pick up, and share fulfillment status. A public **Community Give** area lets donors see remaining shortages and pledge items after fulfillment is recorded.

## Features

- **Shop** — Browse ~54 items with category tabs, search, and package weights
- **Cart** — Running weight vs per-order limit (default 10 lb); stored in `localStorage`
- **Checkout** — Server-validated weight cap; optional household name
- **Status** — `/status?name=...` lookup for allocated vs requested items
- **Community Give** — `/community` public needs board and `/community/pledge` donor pledges
- **Admin** — Password-protected dashboard with demand weight vs trip limit
- **Store inventory** — Enter surplus qty and expiry per item
- **Plan pickup** — Interactive planner with weight bar and greedy “Suggest fill”
- **Community admin** — Preview shortages, publish board, moderate pledges
- **Archive** — Rounds include fulfillment shortfalls, pledges, and trip metadata
- **SQLite / Turso** — Orders, pledges, and planning data persist (local SQLite in dev, Turso on Render)

## Requirements

- Python 3.10+
- Flask, Gunicorn

## Setup and run

```powershell
cd "c:\Users\shrey\OneDrive\Desktop\Cursor stuffs\food_bank"
pip install -r requirements.txt
py -m flask --app app run
```

On Windows, use `py -m flask` instead of `flask` directly.

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) to shop. Admin: `/admin`. Community board: `/community`.

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | dev placeholder | Flask session signing |
| `ADMIN_PASSWORD` | `Iconic` | Admin login password |
| `TURSO_DATABASE_URL` | *(unset)* | Turso database URL (`libsql://...`) for production |
| `TURSO_AUTH_TOKEN` | *(unset)* | Turso auth token |
| `DATABASE_PATH` | `data/food_bank.db` | Local SQLite file when Turso is not configured |

For production on Render, set `TURSO_*` variables (see `docs/TURSO_SETUP.md`). For local dev, omit them to use SQLite.

## Usage

### Household shopping

1. **Shoppers** — Add items (watch the weight badge), review cart, place order. Check `/status` after planning.

### Admin trip workflow

1. Set trip weight limit and per-order cap on the admin dashboard.
2. View demand totals as orders come in.
3. Enter **Store inventory**, then **Plan pickup** (use Suggest fill or set pick quantities).
4. Click **Record fulfillment** on the plan page — this saves shortfalls to the database.
5. Open **Community** in admin — preview shortages, then **Publish to community**.
6. Share `/community` with donors (QR code, email, etc.).
7. Moderate pledges (mark **Received** or **Cancel** as items arrive).
8. **Archive** the round when done — pledges are closed and `community_published` resets for the next trip.

### Donor workflow

1. Visit `/community` after the board is published.
2. See items still needed (shortfall minus active pledges).
3. Submit a pledge at `/community/pledge` — name optional (anonymous supported).
4. Drop off pledged items; admin marks pledges received.

No household names or order details appear on community pages.

## Data

| Source | Purpose |
|--------|---------|
| `items.json` | Static catalog with `weight_lb` per package |
| `data/food_bank.db` | Local SQLite (dev only) |
| Turso cloud DB | Production persistence on Render free tier |
| `donor_pledges` table | Donor name, item, qty, status per trip round |
| `kv_store` trip key | Includes `community_published` toggle |
| Legacy `orders.json` / `archive.json` | Migrated into SQLite on first run |

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
