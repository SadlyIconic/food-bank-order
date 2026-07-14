# Food Bank Order App

A Flask app for coordinating food bank shopping under a weight limit. Households request items (capped per order), admins see total demand vs trip capacity, enter store surplus, plan what to pick up, and share fulfillment status.

## Features

- **Shop** — Browse ~54 items with category tabs, search, and package weights
- **Cart** — Running weight vs per-order limit (default 10 lb); stored in `localStorage`
- **Checkout** — Server-validated weight cap; optional household name
- **Status** — `/status?name=...` lookup for allocated vs requested items
- **Admin** — Password-protected dashboard with demand weight vs trip limit
- **Store inventory** — Enter surplus qty and expiry per item
- **Plan pickup** — Interactive planner with weight bar and greedy “Suggest fill”
- **Archive** — Rounds include fulfillment shortfalls and trip metadata
- **SQLite / Turso** — Orders and planning data persist (local SQLite in dev, Turso on Render)

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

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) to shop. Admin: `/admin`.

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

1. **Shoppers** — Add items (watch the weight badge), review cart, place order. Check `/status` after planning.
2. **Admin** — Set trip weight limit and per-order cap. View demand totals. Enter **Store inventory**, then **Plan pickup** (use Suggest fill or set pick quantities). Record fulfillment before archiving.
3. **Archive** — Reset round saves selection, inventory snapshot, and shortfalls to history.

## Data

| Source | Purpose |
|--------|---------|
| `items.json` | Static catalog with `weight_lb` per package |
| `data/food_bank.db` | Local SQLite (dev only) |
| Turso cloud DB | Production persistence on Render free tier |
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
