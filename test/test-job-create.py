import requests
import json

BASE_URL = "http://127.0.0.1:5500"

# -------------------------
# Global Auth
# -------------------------
USER_ID = "cd4d762e-5259-4dec-884f-1d23addf7b95"
TOKEN = "a86ed5d6-9795-4c42-8eb3-4c1937806c85"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

PRINTER_ID = "e1b6a38a-b5ee-407d-87d9-27c65073e8f2"
SLOT_ID = "2825e68e-4a3f-444f-8518-4eafa67f4bd1"

# Metadata payload (must be stringified for multipart/form-data)
payload = {
    "user_id": USER_ID,
    "printer_id": PRINTER_ID,
    "slot_id": SLOT_ID,
    "print_options": json.dumps({
        "pages": [1, 2, 3],
        "color": "black_white",
        "copies": 1
    })
}

# Attach file (open in binary mode)
files = {
    "file": open("./test/sample.pdf", "rb")   # replace with your PDF filename
}

response = requests.post(
    f"{BASE_URL}/user/jobs",
    headers=HEADERS,
    data=payload,   # use 'data' not 'json'
    files=files
)

print("Create Job:", response.status_code, response.json())
