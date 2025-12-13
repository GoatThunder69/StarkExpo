import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SOURCE_API = "https://rc-info-ng.vercel.app/"
OWNER_NAME = "@GoatThunder"

REMOVE_KEYS = {"owner", "Owner", "credit", "Credit", "by", "By", "username", "Username"}

def remove_external_owner(data):
    if isinstance(data, dict):
        return {
            k: remove_external_owner(v)
            for k, v in data.items()
            if k not in REMOVE_KEYS
        }
    if isinstance(data, list):
        return [remove_external_owner(i) for i in data]
    return data


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
        r = requests.get(
            SOURCE_API,
            params={"rc": veh},
            timeout=20
        )

        if r.status_code != 200:
            return jsonify({
                "status": False,
                "message": "Source API error",
                "Owner": OWNER_NAME
            })

        raw_data = r.json()

        # remove only external owner/credit keys
        raw_data = remove_external_owner(raw_data)

        return jsonify({
            "status": True,
            "vehicle": veh.upper(),

            "🚗 RC DETAILS 🚗": "",
            **raw_data,

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
        "message": "Single Source RC API Running",
        "usage": "/api?veh=HR26CJ1818",
        "note": "Raw data from source, nothing removed except external owner/credit",
        "Owner": OWNER_NAME
    })
