import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SOURCE_API = "https://anuj-rcc.vercel.app/rc"
OWNER = "@GoatThunder"

# ---- RATE LIMIT CONFIG ----
RATE_LIMIT_SECONDS = 10
ip_last_request = {}

REMOVE_KEYS = {"owner", "Owner", "credit", "Credit", "by", "By", "username", "Username"}

def clean_owner(obj):
    if isinstance(obj, dict):
        return {
            k: clean_owner(v)
            for k, v in obj.items()
            if k not in REMOVE_KEYS
        }
    if isinstance(obj, list):
        return [clean_owner(i) for i in obj]
    return obj


def is_rate_limited(ip):
    now = time.time()
    last = ip_last_request.get(ip)
    if last and now - last < RATE_LIMIT_SECONDS:
        return True, RATE_LIMIT_SECONDS - int(now - last)
    ip_last_request[ip] = now
    return False, 0


@app.route("/api", methods=["GET"])
def rc_api():
    ip = request.headers.get("x-forwarded-for", request.remote_addr)

    limited, wait = is_rate_limited(ip)
    if limited:
        return jsonify({
            "status": False,
            "message": f"Rate limit exceeded. Try again after {wait} seconds",
            "Owner": OWNER
        }), 429

    veh = request.args.get("veh")
    if not veh:
        return jsonify({
            "status": False,
            "error": "Use ?veh=UP32JM0855",
            "Owner": OWNER
        })

    try:
        r = requests.get(SOURCE_API, params={"query": veh}, timeout=20)
        data = r.json() if r.status_code == 200 else {}

        data = clean_owner(data)

        return jsonify({
            "🔍 Query": veh,
            "📄 RC INFO": data,
            "Owner": OWNER
        })

    except Exception as e:
        return jsonify({
            "status": False,
            "error": str(e),
            "Owner": OWNER
        })


# ---- BLOCK ALL OTHER METHODS ----
@app.route("/api", methods=["POST", "PUT", "PATCH", "DELETE"])
def block_methods():
    return jsonify({
        "status": False,
        "error": "Read-only API. Modification not allowed.",
        "Owner": OWNER
    }), 403


@app.route("/")
def home():
    return jsonify({
        "message": "RC Emoji API Running (Read-Only + Rate Limited)",
        "rate_limit": "1 request / 10 seconds / IP",
        "usage": "/api?veh=UP32JM0855",
        "Owner": OWNER
    })
