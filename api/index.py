import requests
import re
from bs4 import BeautifulSoup

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
        data = {'vehicle_number': vehicle_number}

        cards = soup.find_all('div', class_=re.compile('card'))
        for card in cards:
            text = card.get_text(strip=True, separator=' | ')

            # Model
            if 'Modal Name' in text or 'Model Name' in text:
                parts = text.split(' | ')
                if parts:
                    data['model'] = parts[0]

            # Owner Name
            if 'Owner Name' in text and 'Ownership' not in text:
                parts = text.split(' | ')
                if parts and parts[0] != 'Owner Name':
                    data['owner_name'] = parts[0]

            # RTO Code
            rto_match = re.search(r'([A-Z]{2}-\d{1,2})', text)
            if rto_match and 'Code' in text:
                data['rto_code'] = rto_match.group(1)

            # City
            if 'City Name' in text:
                parts = text.split(' | ')
                if parts and parts[0] != 'City Name':
                    data['city'] = parts[0]

            # Ownership Details
            if 'Ownership Details' in text:
                fields = [
                    ("Father's Name", 'father_name'),
                    ('Owner Serial No', 'owner_sr'),
                    ('Registration Number', 'reg_no'),
                    ('Registered RTO', 'rto')
                ]
                for field, key in fields:
                    match = re.search(rf"{field} \| ([^|]+)", text)
                    if match:
                        data[key] = match.group(1).strip()

            # Vehicle Details
            if 'Vehicle Details' in text:
                fields = [
                    ('Model Name', 'maker'),
                    ('Maker Model', 'model'),
                    ('Vehicle Class', 'vehicle_class'),
                    ('Fuel Type', 'fuel_type'),
                    ('Chassis Number', 'chassis'),
                    ('Engine Number', 'engine')
                ]
                for field, key in fields:
                    match = re.search(rf"{field} \| ([^|]+)", text)
                    if match:
                        data[key] = match.group(1).strip()

            # Important Dates
            if 'Important Dates' in text:
                fields = [
                    ('Registration Date', 'reg_date'),
                    ('Vehicle Age', 'age'),
                    ('Fitness Upto', 'fitness_upto')
                ]
                for field, key in fields:
                    match = re.search(rf"{field} \| ([^|]+)", text)
                    if match:
                        data[key] = match.group(1).strip()

            # Other Info
            if 'Other Information' in text:
                fields = [
                    ('Financer Name', 'financer'),
                    ('Cubic Capacity', 'cc'),
                    ('Seating Capacity', 'seats')
                ]
                for field, key in fields:
                    match = re.search(rf"{field} \| ([^|]+)", text)
                    if match:
                        data[key] = match.group(1).strip()

        return data if len(data) > 1 else None

    except Exception:
        return None


# ================= CHALLAN INFO =================
def get_challan_info(vehicle_number: str) -> dict | None:
    try:
        url = f'https://vahanx.in/challan-search/{vehicle_number}'
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None

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
                ('Location', 'location'),
                ('Vehicle No', 'vehicle_no')
            ]

            for field, key in fields:
                match = re.search(rf"{field} \| ([^|]+)", text)
                if match:
                    challan[key] = match.group(1).strip()

            if challan:
                challans.append(challan)

        return {
            "total": len(challans),
            "challans": challans
        } if challans else {
            "total": 0,
            "challans": []
        }

    except Exception:
        return None


# ================= COMBINED RESULT =================
def get_vehicle_full(vehicle_number: str) -> dict:
    vehicle = get_vehicle_info(vehicle_number)
    challan = get_challan_info(vehicle_number)

    return {
        "status": True,
        "vehicle_number": vehicle_number,
        "vehicle_details": vehicle or "Not Available",
        "challan_details": challan or {
            "total": 0,
            "challans": []
        },
        "credit": "Made By: @Sxthunder"
    }
