# Food Bank Order App

A simple Flask app for coordinating food bank shopping. Family members and volunteers browse a fixed catalog, add items to a cart, and submit orders. An admin view aggregates all orders into a single shopping list sorted by quantity.

## Features

- **Shop** — Browse ~50 items with category tabs and name search
- **Cart** — Stored in browser `localStorage` until order is placed
- **Checkout** — Optional household/name field
- **Admin** — Password-protected aggregated totals (password: `Iconic`)
- **Archive** — Reset after shopping moves the round to history for analysis

## Requirements

- Python 3.10+
- Flask

## Setup and run

```powershell
cd "c:\Users\shrey\OneDrive\Desktop\Cursor stuffs\food_bank"
pip install -r requirements.txt
py -m flask --app app run
```

On Windows, use `py -m flask` instead of `flask` directly — the Flask executable is installed but its Scripts folder may not be on your PATH.

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) to shop. Go to `/admin` for the compiled shopping list.

## Usage

1. **Shoppers** — Add items on the shop page, review the cart, and place an order.
2. **Admin** — Log in at `/admin` with password `Iconic`. View **Current totals** (sorted highest to lowest). When shopping is done, click **Reset round** to archive totals and start a fresh round.
3. **Past rounds** — Use the **Past rounds** tab to review archived shopping lists.

## Data files

| File | Purpose |
|------|---------|
| `items.json` | Static catalog (edit to add/change items) |
| `orders.json` | Active submitted orders for the current round |
| `archive.json` | Past rounds after admin reset |

## Project structure

```
food_bank/
  app.py              # Flask routes
  store.py            # JSON load/save and aggregation
  items.json          # Catalog
  orders.json         # Current orders
  archive.json        # Archived rounds
  templates/          # HTML pages
  static/             # CSS and cart JavaScript
```

## Notes

- Suitable for local/trusted use on a single machine or LAN.
- No user accounts, payments, or inventory limits in v1.
- To change the catalog, edit `items.json` directly.

## Deploy on Render (free)

1. Push this repo to GitHub (the repo root should contain the `food_bank/` folder).
2. Sign up at [render.com](https://render.com) and click **New → Blueprint** (or **New → Web Service**).
3. Connect your GitHub repo.
4. If using **Blueprint**, Render reads `render.yaml` at the repo root and sets everything automatically.
5. If creating a **Web Service** manually, use these settings:

   | Setting | Value |
   |---------|--------|
   | Root Directory | `food_bank` |
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT` |
   | Plan | Free |

6. Deploy and share your `https://….onrender.com` URL.

**Note:** On Render’s free plan the app sleeps after ~15 minutes of inactivity (first visit may take 30–60 seconds). Order/archive JSON files persist while the service runs but may reset when you redeploy.
