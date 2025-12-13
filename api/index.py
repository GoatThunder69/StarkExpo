import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_1 = "https://anuj-rcc.vercel.app/rc"
API_2 = "https://rc-info-ng.vercel.app/"

OWNER_NAME = "@GoatThunder"

# --------- helpers ---------
def mask_start(val, keep):
    if not val or not isinstance(val, str):
        return None
    return val[:keep]

def safe_get(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k):
            return d.get(k)
    return None

def expand_address(*parts):
    clean = [p.strip() for p in parts if p and isinstance(p, str)]
    return ", ".join(clean) if clean else "Not Available"

def remove_other_owners(obj):
    REMOVE_KEYS = {"owner", "Owner", "credit", "Credit", "by", "By", "username", "Username"}
    if isinstance(obj, dict):
        return {
            k: remove_other_owners(v)
            for k, v in obj.items()
            if k not in REMOVE_KEYS
        }
    if isinstance(obj, list):
        return [remove_other_owners(i) for i in obj]
    return obj


@app.route("/api")
def combined_api():
    veh = request.args.get("veh")
    if not veh:
        return jsonify({
            "status": False,
            "error": "Use ?veh=HR26CJ1818",
            "Owner": OWNER_NAME
        })

    # ⏳ delay (safe for Vercel: 5 sec max)
    time.sleep(5)

    try:
        r1 = requests.get(API_1, params={"query": veh}, timeout=20)
        r2 = requests.get(API_2, params={"rc": veh}, timeout=20)

        data1 = r1.json() if r1.status_code == 200 else {}
        data2 = r2.json() if r2.status_code == 200 else {}

        # remove external owners/credits
        data1 = remove_other_owners(data1)
        data2 = remove_other_owners(data2)

        # -------- merge logic --------
        mobile = safe_get(data1, "mobile", "mobile_number") or safe_get(data2, "mobile", "mobile_number")
        if not mobile:
            mobile = "Not Found"

        address = expand_address(
            safe_get(data1, "address"),
            safe_get(data1, "city"),
            safe_get(data1, "district"),
            safe_get(data1, "state"),
            "INDIA"
        )

        chassis = mask_start(
            safe_get(data1, "chassis_number", "chassis"), 5
        )
        engine = mask_start(
            safe_get(data1, "engine_number", "engine"), 4
        )

        final_data = {
            "registration_number": veh.upper(),
            "owner_name": safe_get(data1, "owner_name") or safe_get(data2, "owner_name"),
            "father_name": safe_get(data1, "father_name"),

            "mobile_number": mobile,
            "address": address,
            "state": safe_get(data1, "state") or safe_get(data2, "state"),

            "vehicle_class": safe_get(data1, "vehicle_class"),
            "vehicle_type": safe_get(data2, "vehicle_type"),
            "vehicle_category": safe_get(data1, "vehicle_category"),
            "maker": safe_get(data1, "maker", "maker_name"),
            "model": safe_get(data1, "model", "model_name"),
            "fuel_type": safe_get(data1, "fuel_type"),

            "registration_date": safe_get(data1, "registration_date"),
            "registration_upto": safe_get(data1, "registration_upto"),
            "fitness_upto": safe_get(data1, "fitness_upto"),

            "rto_code": safe_get(data1, "rto_code"),
            "rto_name": safe_get(data1, "rto_name"),

            "insurance_company": safe_get(data1, "insurance_company"),
            "insurance_upto": safe_get(data1, "insurance_upto"),
            "pollution_upto": safe_get(data1, "pollution_upto"),

            "chassis_number": chassis,
            "engine_number": engine,

            "rc_status": safe_get(data1, "rc_status") or safe_get(data2, "status"),
            "blacklist_status": safe_get(data1, "blacklist_status"),
            "last_updated": safe_get(data1, "last_updated")
        }

        # remove None values
        final_data = {k: v for k, v in final_data.items() if v}

        return jsonify({
            "status": True,
            "vehicle": veh.upper(),
            "data": final_data,
            "Owner": OWNER_NAME
        })

    except Exception as e:
        return jsonify({
            "status": False,
            "error": str(e),
            "Owner": OWNER_NAME
        })


@app.route("/")
def home():
    return jsonify({
        "message": "Combined RC API Running",
        "usage": "/api?veh=HR26CJ1818",
        "note": "All data merged, mobile fallback, long address, masked chassis/engine",
        "Owner": OWNER_NAME
    })
