import requests
import json

BASE_URL = "http://127.0.0.1:5500"

# -------------------------
# Global Auth
# -------------------------
PRINTER_ID = "e1b6a38a-b5ee-407d-87d9-27c65073e8f2"
TOKEN = "a86ed5d6-9795-4c42-8eb3-4c1937806c85"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

JOB_ID = "34979528-7a3b-4e59-b57d-391e1bbcbc51"

response = requests.get(
    f"{BASE_URL}/print/file",
    headers=HEADERS,
    params={"job_id": JOB_ID}
)

print("Get Job:", response.status_code, response.json())
