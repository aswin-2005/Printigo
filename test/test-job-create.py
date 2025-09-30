import requests

BASE_URL = "http://127.0.0.1:5500"  # Your Flask server

# Example user and printer IDs from your DB
USER_ID = "a3ae5994-0298-460b-acbb-2bdbed93d73b"     # normal user
PRINTER_ID = "9654b2d8-47a4-44e2-adf2-f6e3be9c3566"  # printer

# Step 1: Fetch slots for printers
slots_response = requests.get(f"{BASE_URL}/user/slots")
if slots_response.status_code != 200:
    print("Failed to fetch slots:", slots_response.text)
    exit(1)

slots_data = slots_response.json().get("slots", {})
printer_slots = slots_data.get(PRINTER_ID, [])

if not printer_slots:
    print("No slots found for this printer.")
    exit(1)

# Pick the first available slot
slot = printer_slots[0]
SLOT_ID = slot["id"]

# Step 2: Create a print job
print_job_payload = {
    "user_id": USER_ID,
    "printer_id": PRINTER_ID,
    "slot_id": SLOT_ID,
    "print_options": {
        "pages": [1, 2, 3],
        "color": "black_white",
        "copies": 1
    }
}

job_response = requests.post(f"{BASE_URL}/user/jobs", json=print_job_payload)

print("Job response:", job_response.status_code, job_response.json())
