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
    "newtown":     {"supply":"1kcFFvHV-2cF2Yp4Mo0sa_aBc1NxG685ebN7-gQLASbQ","repair":"1oD5ADD1kzT95FyBCwgmjktFwJxqPNiJBtASZ6QnXjyg"},
    "ridgefield":  {"supply":"1h4M3mN6UnvY7QacAPSvQ_0xD-T-N3WdvAafB_9YugpA","repair":"1PNUFgo0_ncdW4JNGL7jqBOhQl97CXQrOk9KYijKgHBo"},
    "new-milford": {"supply":"1tG3iUCc9WpGg-WNVPmeZYxa5JpC2JkH48N2BkkPZflQ","repair":"110Myaf_x2Iw1HyDMlNu_M8xtwl9pevr3286Am87iFcY"},
    "wallingford": {"supply":"1iamDTbYwxlhR1K_T8Ktx3nkAUlF1CeYnh0jlB3zDt5c","repair":"1z8f1-xJMqF6Xmj7P-MJmBSEfMnbKo1kuD7y0-ZE3NAA"},
    "middletown":  {"supply":"1ePN4q2oLTlx9NGY4VDavFoXkqleYLrbQOIsoBHYbRdg","repair":"1EuPyZZTQ_Ve4p5li3OdoaS47a41YoLbsunUdwtz3k3o"},
    "torrington":  {"supply":"1MDarLC-iZ0ocilYgF2bBSVGOz8B1CtlmoKznomq15aQ"},
    "brookfield":  {"supply":"1KveTmbM6yQcULXyignOEagSfUqXxB0m-axAmI5kwjeE"},
}

def get_service():
    key_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key_json:
        raise HTTPException(status_code=500, detail="Service account credentials not configured")
    info = json.loads(key_json)
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)

def fetch_repair(loc: str):
    svc = get_service()
    result = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_IDS[loc]["repair"], range="A6:I100"
    ).execute()
    rows = result.get("values", [])
    if not rows: return {"repairs": []}
    headers = rows[0]
    repairs = []
    for row in rows[1:]:
        if not any(row): continue
        padded = row + [""] * (len(headers) - len(row))
        repairs.append({
            "date": padded[0] if len(padded)>0 else "",
            "brand": padded[1] if len(padded)>1 else "",
            "type": padded[2] if len(padded)>2 else "",
            "machine_num": padded[3] if len(padded)>3 else "",
            "machine_name": padded[4] if len(padded)>4 else "",
            "problem": padded[5] if len(padded)>5 else "",
            "serial": padded[6] if len(padded)>6 else "",
            "part_needed": padded[7] if len(padded)>7 else "",
        })
    return {"repairs": repairs}

def fetch_supply(loc: str):
    svc = get_service()
    result = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_IDS[loc]["supply"], range="A1:Z100"
    ).execute()
    rows = result.get("values", [])
    if not rows: return {"dates": [], "items": []}
    date_row = rows[0]
    dates = [d for d in date_row[2:] if d.strip()] if len(date_row)>2 else []
    items = []
    for row in rows[1:]:
        if not row or not row[0].strip(): continue
        quantities = [row[i].strip() if len(row)>i else "" for i in range(2, 2+len(dates))]
        items.append({"name": row[0].strip(), "quantities": quantities})
    return {"dates": dates, "items": items}

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/newtown/repair")
def newtown_repair():
    try: return fetch_repair("newtown")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/newtown/supply")
def newtown_supply():
    try: return fetch_supply("newtown")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/ridgefield/repair")
def ridgefield_repair():
    try: return fetch_repair("ridgefield")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/ridgefield/supply")
def ridgefield_supply():
    try: return fetch_supply("ridgefield")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/new-milford/repair")
def new_milford_repair():
    try: return fetch_repair("new-milford")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/new-milford/supply")
def new_milford_supply():
    try: return fetch_supply("new-milford")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/wallingford/repair")
def wallingford_repair():
    try: return fetch_repair("wallingford")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/wallingford/supply")
def wallingford_supply():
    try: return fetch_supply("wallingford")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/middletown/repair")
def middletown_repair():
    try: return fetch_repair("middletown")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/middletown/supply")
def middletown_supply():
    try: return fetch_supply("middletown")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/torrington/supply")
def torrington_supply():
    try: return fetch_supply("torrington")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/brookfield/supply")
def brookfield_supply():
    try: return fetch_supply("brookfield")
    except HTTPException: raise
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

