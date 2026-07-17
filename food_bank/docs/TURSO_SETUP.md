# Turso setup (free tier)

Use Turso for **persistent storage** on Render’s free web plan (no paid disk required).

## 1. Create a Turso account and database

Sign up at [turso.tech](https://turso.tech), then either use the dashboard or the CLI:

```bash
# Install CLI: https://docs.turso.tech/cli/install
turso auth login
turso db create food-bank-order
turso db show food-bank-order --url
turso db tokens create food-bank-order
```

Save the **database URL** (`libsql://...`) and **auth token**.

## 2. Configure Render

In your Render web service (or Blueprint sync), set:

| Variable | Value |
|----------|--------|
| `TURSO_DATABASE_URL` | `libsql://...` from step 1 |
| `TURSO_AUTH_TOKEN` | token from step 1 |
| `ADMIN_PASSWORD` | your admin password |
| `SECRET_KEY` | auto-generated is fine |

Do **not** attach a persistent disk on the free tier.

## 3. Deploy

Push to GitHub and deploy. On first request the app creates tables automatically (`orders`, `archive_rounds`, `kv_store`).

The app uses **Turso SQL over HTTP** (stdlib only — no native `libsql` package). This avoids gunicorn worker crashes on Render’s free tier.

Optional: set `TURSO_HTTP_URL` instead of `TURSO_DATABASE_URL` if you have the HTTP URL from `turso db show <name> --http-url` (the app appends `/v2/pipeline` automatically).

## 4. Verify persistence

1. Place a test order on the live site.
2. Trigger a **manual redeploy** on Render.
3. Confirm the order still appears in admin.

## Local development

Without Turso env vars, the app uses **local SQLite** at `data/food_bank.db` (see `.env.example`).

To test against Turso locally:

```powershell
cd food_bank
$env:TURSO_DATABASE_URL = "libsql://..."
$env:TURSO_AUTH_TOKEN = "..."
py -m flask --app app run
```

## Free tier notes

- Turso free tier limits apply (storage / rows / locations) — enough for a small food bank.
- Render free tier may sleep when idle; Turso data stays in the cloud.
