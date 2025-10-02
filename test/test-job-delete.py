# delete_job.py
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

# -------------------------
# Example job ID (replace with real one)
# -------------------------
JOB_ID = "replace-with-real-job-id"

response = requests.delete(f"{BASE_URL}/user/jobs",
                           headers=HEADERS,
                           params={"job_id": JOB_ID})

if response.status_code == 200:
    print(f"Job {JOB_ID} deleted successfully")
else:
    print(f"Failed to delete job: {response.status_code}, {response.json()}")
