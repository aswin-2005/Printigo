# get_slots.py
import requests

BASE_URL = "http://127.0.0.1:5500"

# -------------------------
# Global Auth
# -------------------------
USER_ID = "ba0b94fa-69ec-4758-a533-ac17ad5428e1"  # replace as needed
TOKEN = "5b56fc2f-ac8f-42ee-a550-eb96f033a67b"   # replace as needed

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

PRINTER_ID = "9654b2d8-47a4-44e2-adf2-f6e3be9c3566"  # replace with your printer ID

# -------------------------
# Fetch slots
# -------------------------
response = requests.get(f"{BASE_URL}/user/slots", headers=HEADERS)
if response.status_code != 200:
    print("Failed to fetch slots:", response.text)
else:
    data = response.json().get("slots", {})
    printer_slots = data.get(PRINTER_ID, [])
    if not printer_slots:
        print("No slots found for this printer.")
    else:
        print(f"Slots for printer {PRINTER_ID}:")
        for slot in printer_slots:
            print(slot)
