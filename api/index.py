import requests, re
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://vahanx.in/"
}

# ---------------- VEHICLE INFO ----------------
def get_vehicle_info(vehicle_number: str):
    try:
        url = f"https://vahanx.in/rc-search/{vehicle_number}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        data = {}

        cards = soup.find_all("div", class_=re.compile("card"))
        for card in cards:
            text = card.get_text(strip=True, separator=" | ")

            def grab(field):
                m = re.search(rf"{field} \| ([^|]+)", text)
                return m.group(1).strip() if m else None

            if "Owner Name" in text and "Ownership" not in text:
                data["owner_name"] = grab("Owner Name")

            data["model"] = grab("Model Name") or grab("Modal Name")
            data["fuel_type"] = grab("Fuel Type")
            data["vehicle_class"] = grab("Vehicle Class")
            data["chassis"] = grab("Chassis Number")
            data["engine"] = grab("Engine Number")
            data["registration_date"] = grab("Registration Date")
            data["rto"] = grab("Registered RTO")

            rto_match = re.search(r"([A-Z]{2}-\d{1,2})", text)
            if rto_match:
                data["rto_code"] = rto_match.group(1)

        return data if data else None
    except:
        return None


# ---------------- CHALLAN INFO ----------------
def get_challan_info(vehicle_number: str):
    try:
        url = f"https://vahanx.in/challan-search/{vehicle_number}"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return {"total": 0, "challans": []}

        soup = BeautifulSoup(r.text, "html.parser")
        challans = []

        cards = soup.find_all("div", class_=re.compile("card"))
        for card in cards:
            text = card.get_text(strip=True, separator=" | ")
            c = {}

            for f, k in [
                ("Challan No", "challan_no"),
                ("Amount", "amount"),
                ("Status", "status"),
                ("Offence", "offence"),
                ("Location", "location")
            ]:
                m = re.search(rf"{f} \| ([^|]+)", text)
                if m:
                    c[k] = m.group(1).strip()

            if c:
                challans.append(c)

        return {"total": len(challans), "challans": challans}
    except:
        return {"total": 0, "challans": []}


# ---------------- API ROUTE ----------------
@app.route("/api")
def api():
    veh = request.args.get("veh")
    if not veh:
        return jsonify({"error": "use ?veh=RJ09UF0001"})

    return jsonify({
        "status": True,
        "vehicle": veh.upper(),
        "vehicle_details": get_vehicle_info(veh.upper()) or {},
        "challan_details": get_challan_info(veh.upper()),
        "credit": "Made By: @Sxthunder"
    })


# ---------------- HOME ----------------
@app.route("/")
def home():
    return jsonify({
        "message": "Vehicle JSON API Running",
        "usage": "/api?veh=RJ09UF0001",
        "credit": "Made By: @Sxthunder"
    })
