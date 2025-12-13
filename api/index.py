import requests
import re
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://vahanx.in/",
    "Connection": "keep-alive"
}

# ================= VEHICLE INFO =================
def get_vehicle_info(vehicle_number: str) -> dict | None:
    try:
        url = f'https://vahanx.in/rc-search/{vehicle_number}'
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        data = {"vehicle_number": vehicle_number}

        cards = soup.find_all('div', class_=re.compile('card'))
        for card in cards:
            text = card.get_text(strip=True, separator=' | ')

            if 'Owner Name' in text and 'Ownership' not in text:
                m = re.search(r'Owner Name \| ([^|]+)', text)
                if m:
                    data['owner_name'] = m.group(1).strip()

            if 'Modal Name' in text or 'Model Name' in text:
                m = re.search(r'(?:Modal Name|Model Name) \| ([^|]+)', text)
                if m:
                    data['model'] = m.group(1).strip()

            if 'Fuel Type' in text:
                m = re.search(r'Fuel Type \| ([^|]+)', text)
                if m:
                    data['fuel_type'] = m.group(1).strip()

            if 'Vehicle Class' in text:
                m = re.search(r'Vehicle Class \| ([^|]+)', text)
                if m:
                    data['vehicle_class'] = m.group(1).strip()

            if 'Chassis Number' in text:
                m = re.search(r'Chassis Number \| ([^|]+)', text)
                if m:
                    data['chassis'] = m.group(1).strip()

            if 'Engine Number' in text:
                m = re.search(r'Engine Number \| ([^|]+)', text)
                if m:
                    data['engine'] = m.group(1).strip()

            if 'Registration Date' in text:
                m = re.search(r'Registration Date \| ([^|]+)', text)
                if m:
                    data['registration_date'] = m.group(1).strip()

            if 'Registered RTO' in text:
                m = re.search(r'Registered RTO \| ([^|]+)', text)
                if m:
                    data['rto'] = m.group(1).strip()

            rto_match = re.search(r'([A-Z]{2}-\d{1,2})', text)
            if rto_match:
                data['rto_code'] = rto_match.group(1)

        return data if len(data) > 1 else None

    except Exception:
        return None


# ================= CHALLAN INFO =================
def get_challan_info(vehicle_number: str) -> dict:
    try:
        url = f'https://vahanx.in/challan-search/{vehicle_number}'
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return {"total": 0, "challans": []}

        soup = BeautifulSoup(response.text, 'html.parser')
        challans = []

        cards = soup.find_all('div', class_=re.compile('card'))
        for card in cards:
            text = card.get_text(strip=True, separator=' | ')
            challan = {}

            fields = [
                ('Challan No', 'challan_no'),
                ('Challan Date', 'date'),
                ('Amount', 'amount'),
                ('Status', 'status'),
                ('Offence', 'offence'),
                ('Location', 'location')
            ]

            for field, key in fields:
                m = re.search(rf"{field} \| ([^|]+)", text)
                if m:
                    challan[key] = m.group(1).strip()

            if challan:
                challans.append(challan)

        return {
            "total": len(challans),
            "challans": challans
        }

    except Exception:
        return {"total": 0, "challans": []}


# ================= API ROUTE =================
@app.route("/api")
def api():
    vehicle_number = request.args.get("veh")
    if not vehicle_number:
        return jsonify({"error": "Use ?veh=RJ09UF0001"})

    vehicle = get_vehicle_info(vehicle_number.upper())
    challan = get_challan_info(vehicle_number.upper())

    return jsonify({
        "status": True,
        "vehicle_number": vehicle_number.upper(),
        "vehicle_details": vehicle or "Not Available",
        "challan_details": challan,
        "credit": "Made By: @Sxthunder"
    })


# ================= VERIFY MODULE =================
@app.route("/verify")
def verify():
    return jsonify({
        "Mobile Number": "Not Added In This Module.",
        "credit": "Made By: @Sxthunder"
    })


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
