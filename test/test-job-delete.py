import requests

BASE_URL = "http://127.0.0.1:5500"  # Your Flask server

# Example job ID to delete
JOB_ID = "7926da96-6c6f-4da5-b686-d3267c7389b9"  # replace with a real job ID

response = requests.delete(f"{BASE_URL}/user/jobs", params={"job_id": JOB_ID})

if response.status_code == 200:
    print(f"Job {JOB_ID} deleted successfully")
else:
    print(f"Failed to delete job: {response.status_code}, {response.json()}")
