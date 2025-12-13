import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SOURCE_API = "https://anuj-rcc.vercel.app/rc"

def mask_start(value, keep):
    if not value or not isinstance(value, str):
        return value
    return value[:keep]

@app.route("/api")
def proxy_api():
    vehicle = request.args.get("veh")
    if not vehicle:
        return jsonify({
            "status": False,
            "error": "Use ?veh=MH43CR0111",
            "credit": "@GoatThunder"
        })

    # ⏳ 5 second delay
    time.sleep(5)

    try:
        r = requests.get(
            SOURCE_API,
            params={"query": vehicle},
            timeout=25
        )

        if r.status_code != 200:
            return jsonify({
                "status": False,
                "message": "Source API error",
                "credit": "@GoatThunder"
            })

        # 🔥 FULL BIG RESPONSE (unchanged)
        data = r.json()

        # 🔐 MODIFY ONLY THESE TWO FIELDS
        if isinstance(data, dict):
            if "chassis_number" in data:
                data["chassis_number"] = mask_start(data["chassis_number"], 5)

            if "engine_number" in data:
                data["engine_number"] = mask_start(data["engine_number"], 4)

        return jsonify({
            "status": True,
            "vehicle": vehicle.upper(),
            "data": data,
            "credit": "@GoatThunder"
        })

    except Exception as e:
        return jsonify({
            "status": False,
            "error": str(e),
            "credit": "@GoatThunder"
        })


@app.route("/")
def home():
    return jsonify({
        "message": "Vehicle Proxy API Running",
        "usage": "/api?veh=MH43CR0111",
        "note": "Full response returned, only chassis & engine partially shown",
        "credit": "@GoatThunder"
    })
