import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_A = "https://rc-info-ng.vercel.app/"
API_B = "https://anuj-rcc.vercel.app/rc"
OWNER_NAME = "@GoatThunder"

REMOVE_KEYS = {"owner", "Owner", "credit", "Credit", "by", "By", "username", "Username"}

def remove_external_owner(obj):
    if isinstance(obj, dict):
        return {
            k: remove_external_owner(v)
            for k, v in obj.items()
            if k not in REMOVE_KEYS
        }
    if isinstance(obj, list):
        return [remove_external_owner(i) for i in obj]
    return obj


@app.route("/api")
def proxy_api():
    veh = request.args.get("veh")
    if not veh:
        return jsonify({
            "status": False,
            "error": "Use ?veh=HR26CJ1818",
            "Owner": OWNER_NAME
        })

    try:
        # ---- API A ----
        r_a = requests.get(API_A, params={"rc": veh}, timeout=20)
        data_a = r_a.json() if r_a.status_code == 200 else {}

        # ---- API B ----
        r_b = requests.get(API_B, params={"query": veh}, timeout=20)
        data_b = r_b.json() if r_b.status_code == 200 else {}

        # remove only external owner/credit keys (RAW otherwise)
        data_a = remove_external_owner(data_a)
        data_b = remove_external_owner(data_b)

        return jsonify({
            "status": True,
            "vehicle": veh.upper(),

            "🚗 RC DETAILS (rc-info-ng) 🚗": "",
            **data_a,

            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━": "",

            "🚘 RC DETAILS (anuj-rcc) 🚘": "",
            **data_b,

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
        "message": "Dual Source RC API Running",
        "usage": "/api?veh=HR26CJ1818",
        "note": "Both APIs RAW data, nulls preserved, emoji sections, owner overridden",
        "Owner": OWNER_NAME
    })
