from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ================= VEHICLE + CHALLAN =================
def fetch_vehicle(vehicle):
    url = f"https://vahanx.in/rc-search/{vehicle}"
    r = requests.get(url, headers=HEADERS, timeout=20)

    if r.status_code != 200:
        return {"status": False, "error": "Source not reachable"}

    soup = BeautifulSoup(r.text, "html.parser")

    # RC DETAILS
    rc = {}
    table = soup.find("table")
    if table:
        for tr in table.find_all("tr"):
            td = tr.find_all("td")
            if len(td) == 2:
                rc[td[0].text.strip()] = td[1].text.strip()

    # CHALLAN DATA
    challans = []
    for s in soup.find_all("script"):
        if "challanData" in s.text:
            try:
                raw = s.text.split("challanData =")[1].split(";")[0].strip()
                challans = json.loads(raw)
            except:
                challans = []

    paid, unpaid, live, closed = [], [], [], []

    for c in challans:
        st = c.get("status", "").lower()
        if "paid" in st:
            paid.append(c)
        elif "unpaid" in st or "pending" in st:
            unpaid.append(c)
        if "live" in st or "active" in st or "open" in st:
            live.append(c)
        if "closed" in st:
            closed.append(c)

    return {
        "status": True,
        "vehicle": vehicle,
        "rc_details": rc,
        "challans": {
            "total": len(challans),
            "paid": paid,
            "unpaid": unpaid,
            "live": live,
            "closed": closed,
            "all": challans
        },
        "credit": "Made By: @Sxthunder"
    }

# ================= ROUTES =================
@app.route("/")
def home():
    return jsonify({
        "message": "Vehicle API is running",
        "usage": {
            "/api": "/api?veh=GJ01AB1234",
            "/verify": "/verify?veh=GJ01AB1234"
        },
        "credit": "Made By: @Sxthunder"
    })

@app.route("/api")
def api():
    veh = request.args.get("veh")
    if not veh:
        return jsonify({"error": "Use ?veh=GJ01AB1234"})
    return jsonify(fetch_vehicle(veh.upper()))

@app.route("/verify")
def verify():
    return jsonify({
        "Mobile Number": "Not Added In This Module.",
        "credit": "Made By: @Sxthunder"
    })

# ================= VERCEL HANDLER =================
def handler(request, *args, **kwargs):
    return app(request, *args, **kwargs)
