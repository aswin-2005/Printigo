# list_jobs.py
import requests

BASE_URL = "http://127.0.0.1:5500"

# -------------------------
# Global Auth
# -------------------------
USER_ID = "ba0b94fa-69ec-4758-a533-ac17ad5428e1"
TOKEN = "5b56fc2f-ac8f-42ee-a550-eb96f033a67b"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

response = requests.get(f"{BASE_URL}/user/jobs", headers=HEADERS, params={"user_id": USER_ID})

if response.status_code != 200:
    print("Failed to fetch jobs:", response.text)
else:
    jobs = response.json().get("jobs", [])
    if not jobs:
        print("No jobs found for this user.")
    else:
        print(f"Jobs for user {USER_ID}:")
        for job in jobs:
            print(job)
