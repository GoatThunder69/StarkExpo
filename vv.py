from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ========================= RC + CHALLAN SCRAPER ===========================
def fetch_vehicle_data(vehicle):
    url = f"https://vahanx.in/rc-search/{vehicle}"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return {"status": False, "error": "Website unreachable"}

    soup = BeautifulSoup(r.text, "html.parser")

    # ------------------ RC TABLE ------------------
    rc = {}
    rc_table = soup.find("table")
    if rc_table:
        for tr in rc_table.find_all("tr"):
            td = tr.find_all("td")
            if len(td) == 2:
                rc[td[0].text.strip()] = td[1].text.strip()

    # ------------------ CHALLAN JSON ------------------
    challans = []
    for script in soup.find_all("script"):
        if "challanData" in script.text:
            try:
                raw = script.text.split("challanData =")[1].split(";")[0].strip()
                challans = json.loads(raw)
            except:
                challans = []

    # -------- CLASSIFYING CHALLANS --------
    paid, unpaid, live, closed = [], [], [], []

    for c in challans:
        status = c.get("status", "").lower()

        if "paid" in status:
            paid.append(c)
        elif "unpaid" in status or "pending" in status:
            unpaid.append(c)

        if "live" in status or "active" in status or "open" in status:
            live.append(c)

        if "closed" in status:
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

# ========================= FIXED VERIFY MODULE ===========================
@app.route("/verify")
def verify_api():
    veh = request.args.get("veh")
    if not veh:
        return jsonify({"error": "Use ?veh=GJ01AB1234"})

    return jsonify({
        "Mobile Number": "Not Added In This Module.",
        "credit": "Made By: @Sxthunder"
    })

# ========================= FULL API ===========================
@app.route("/api")
def full_api():
    veh = request.args.get("veh")
    if not veh:
        return jsonify({"error": "Use ?veh=GJ01AB1234"})

    return jsonify(fetch_vehicle_data(veh.upper()))

# ========================= RUN SERVER ===========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)