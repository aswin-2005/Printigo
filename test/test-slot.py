# test-slot-job.py
import requests

BASE_URL = "http://127.0.0.1:5500"  # Flask server

# Replace these with actual IDs and tokens from your login response
USER_ID = "ba0b94fa-69ec-4758-a533-ac17ad5428e1"
TOKEN = "5b56fc2f-ac8f-42ee-a550-eb96f033a67b"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

# -------------------------
# Get Slots
# -------------------------
def get_slots():
    response = requests.get(f"{BASE_URL}/user/slots", headers=HEADERS)
    print(f"Slots response: {response.status_code}")
    print(response.json())

# -------------------------
# Get User Jobs
# -------------------------
def get_jobs():
    response = requests.get(f"{BASE_URL}/user/jobs", headers=HEADERS)
    print(f"Jobs response: {response.status_code}")
    print(response.json())

# -------------------------
# Run Tests
# -------------------------
if __name__ == "__main__":
    print("Fetching available slots...")
    get_slots()
    print("\nFetching user jobs...")
    get_jobs()
