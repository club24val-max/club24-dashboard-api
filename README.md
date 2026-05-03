# Club 24 Dashboard API

FastAPI backend that securely reads Club 24 Google Sheets for the GM Dashboard.

## Endpoints

- `GET /health` — health check
- `GET /newtown/repair` — Equipment repair log
- `GET /newtown/supply` — Supply order inventory

## Deploy to Render

1. Push this folder to a new GitHub repo (e.g. `club24val-max/club24-dashboard-api`)
2. Go to render.com → New → Web Service → connect the repo
3. Settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Instance type: Free
4. Add Environment Variable:
   - Key: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - Value: paste the ENTIRE contents of your downloaded JSON key file

## Adding More Locations

Add sheet IDs to the `SHEET_IDS` dict in main.py and create new route functions following the same pattern.
