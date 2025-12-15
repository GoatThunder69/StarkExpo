import requests
from flask import jsonify

OWNER = "@GoatThunder"

@app.route("/vehicle-merge/<reg_no>")
def vehicle_merge(reg_no):
    primary_data = None
    secondary_data = None

    # -------- PRIMARY API (anuj-rcc) --------
    try:
        primary_url = f"https://anuj-rcc.vercel.app/rc?query={reg_no}"
        p = requests.get(primary_url, timeout=20)
        if p.status_code == 200:
            primary_data = p.json()
        else:
            primary_data = {
                "error": "Primary API non-200 response",
                "status_code": p.status_code
            }
    except Exception as e:
        primary_data = {
            "error": "Primary API failed",
            "details": str(e)
        }

    # -------- SECONDARY API (flipcartstore) --------
    try:
        secondary_url = (
            "https://flipcartstore.serv00.net/vehicle/api.php"
            f"?reg={reg_no}&key=Tofficial"
        )
        s = requests.get(secondary_url, timeout=20)
        if s.status_code == 200:
            secondary_data = s.json()
        else:
            secondary_data = {
                "error": "Secondary API non-200 response",
                "status_code": s.status_code
            }
    except Exception as e:
        secondary_data = {
            "error": "Secondary API failed",
            "details": str(e)
        }

    # -------- FINAL PURE COPY-PASTE RESPONSE --------
    return jsonify({
        "success": True,
        "query": reg_no,

        "primary_api_response": primary_data,
        "secondary_api_response": secondary_data,

        "Owner": OWNER
    })
