# Food Bank Shortage Broadcast

> A zero-integration, anonymous tool that allows partner agencies to broadcast their daily shortages directly to local neighborhood donors, reducing logistical delivery burden for high-demand items.

A Flask app with two sides: **anonymous client ordering** (aggregated demand, no names) and a **public neighborhood donor board** (shareable URL, no login). No Link2Feed hooks, no per-item inventory sync, no warehouse integrations — just a browser and SQLite or Turso.

## Features

- **Shop** — Browse ~54 items with category tabs, search, and package weights
- **Cart** — Running weight vs per-order limit (default 10 lb); stored in `localStorage`
- **Checkout** — Server-validated weight cap; fully anonymous (no names collected)
- **Neighborhood Give** — `/community` public shortage board and `/community/pledge` donor pledges
- **Admin** — Password-protected dashboard with aggregated demand vs trip weight limit
- **Daily shortage broadcast** — Agency sets category + storage levels once daily; high-demand items surface first
- **Broadcast controls** — Preview shortages, publish to neighborhood donors, moderate pledges
- **Archive** — Rounds snapshot demand totals, shortage settings, and pledges
- **SQLite / Turso** — Zero external integrations; data persists locally or on Render

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

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) to shop. Admin: `/admin`. Neighborhood board: `/community`.

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

### Agency workflow

1. **Collect anonymous demand** — Clients shop and place orders (no names required).
2. **Review totals** — Admin dashboard shows aggregated demand by item and weight.
3. **Set today's shortages** — Open **Daily shortage broadcast** (`/admin/capacity`): mark categories critically low → full, and storage limits (dry / refrigerated / frozen). No integrations required.
4. **Preview and broadcast** — Open **Broadcast** in admin, review the shortage list, then **Broadcast to neighborhood donors**.
5. **Share the board** — Send `/community` to local donors (QR code, email, social).
6. **Moderate pledges** — Mark **Received** or **Cancel** as items arrive.
7. **Archive** — Reset the round when done; shortage settings and publish flag clear for the next cycle.

Legacy **Store inventory** and **Plan pickup** URLs redirect to Daily shortage broadcast.

### Neighborhood donor workflow

1. Visit `/community` after the agency broadcasts today's shortages.
2. See high-demand items still open (client demand minus active pledges, filtered by agency shortage settings).
3. Submit a pledge at `/community/pledge` — name optional (anonymous supported).
4. Drop off pledged items; agency staff mark pledges **Received** (status only).

No client names or order details appear on the public board.

## Data

| Source | Purpose |
|--------|---------|
| `items.json` | Static catalog with `weight_lb` and `storage_type` per item |
| `data/food_bank.db` | Local SQLite (dev only) |
| Turso cloud DB | Production persistence on Render free tier |
| `donor_pledges` table | Donor name, item, qty, status per trip round |
| `kv_store` `staff_thresholds` | Daily category + storage shortage levels |
| `kv_store` trip key | Includes `community_published` broadcast toggle |
| Legacy `orders.json` / `archive.json` | Migrated into SQLite on first run |

## Multi-agency roadmap

**Today:** One partner agency per deployment — one admin login, one trip context, one public board URL.

**Future (not built):** Multi-agency would add an `agency_id` or URL slug scoped to trip settings, `staff_thresholds`, pledges, and archive rows. Each agency gets its own broadcast URL without changing the zero-integration model — still no parent-network API hooks.

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
