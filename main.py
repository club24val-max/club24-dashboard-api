from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SHEET_IDS = {
    "newtown": {
        "supply":  "1hHY6CJNrvCTEdMtTvgWb2V13UgLiZjGOgVVoME-poHI",
        "repair":  "1oD5ADD1kzT95FyBCwgmjktFwJxqPNiJBtASZ6QnXjyg",
    }
}

def get_service():
    key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key_json:
        raise HTTPException(status_code=500, detail="Service account credentials not configured")
    info = json.loads(key_json)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/newtown/repair")
def newtown_repair():
    try:
        svc = get_service()
        result = svc.spreadsheets().values().get(
            spreadsheetId=SHEET_IDS["newtown"]["repair"],
            range="A6:I100"
        ).execute()
        rows = result.get("values", [])
        if not rows:
            return {"repairs": []}
        headers = rows[0]
        repairs = []
        for row in rows[1:]:
            if not any(row):
                continue
            padded = row + [""] * (len(headers) - len(row))
            repairs.append({
                "date":          padded[0] if len(padded) > 0 else "",
                "brand":         padded[1] if len(padded) > 1 else "",
                "type":          padded[2] if len(padded) > 2 else "",
                "machine_num":   padded[3] if len(padded) > 3 else "",
                "machine_name":  padded[4] if len(padded) > 4 else "",
                "problem":       padded[5] if len(padded) > 5 else "",
                "serial":        padded[6] if len(padded) > 6 else "",
                "part_needed":   padded[7] if len(padded) > 7 else "",
            })
        return {"repairs": repairs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/newtown/supply")
def newtown_supply():
    try:
        svc = get_service()
        result = svc.spreadsheets().values().get(
            spreadsheetId=SHEET_IDS["newtown"]["supply"],
            range="A1:Z100"
        ).execute()
        rows = result.get("values", [])
        if not rows:
            return {"dates": [], "items": []}

        # Row 1 = dates (cols C onward), Row 2+ = item rows
        date_row = rows[0] if rows else []
        dates = [d for d in date_row[2:] if d.strip()] if len(date_row) > 2 else []

        items = []
        for row in rows[1:]:
            if not row or not row[0].strip():
                continue
            name = row[0].strip()
            quantities = []
            for i in range(2, 2 + len(dates)):
                val = row[i].strip() if len(row) > i else ""
                quantities.append(val)
            items.append({"name": name, "quantities": quantities})

        return {"dates": dates, "items": items}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
