import requests

BASE_URL = "http://127.0.0.1:5500"  # Your Flask server

# Example user ID from your DB
USER_ID = "a3ae5994-0298-460b-acbb-2bdbed93d73b"

# Fetch all jobs for this user
response = requests.get(f"{BASE_URL}/user/jobs?user_id={USER_ID}")

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
