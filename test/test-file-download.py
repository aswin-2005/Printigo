import os
from supabase import create_client
from dotenv import load_dotenv

# Load Supabase credentials
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Job ID for the PDF to download
job_id = "5d128108-77ed-457c-a8ac-b7efb8b5eff8"  # replace with actual job_id
remote_file_name = f"{job_id}.pdf"
local_download_path = f"./test/{remote_file_name}"

try:
    # Download file from Supabase
    file_bytes = supabase.storage.from_("files").download(remote_file_name)

    if file_bytes:
        # Ensure local downloads folder exists
        # os.makedirs(os.path.dirname(local_download_path), exist_ok=True)

        # Save bytes to local file
        with open(local_download_path, "wb") as f:
            f.write(file_bytes)

        print(f"Downloaded {remote_file_name} successfully to {local_download_path}")
    else:
        print(f"File {remote_file_name} not found in storage")

except Exception as e:
    print("Error downloading file:", e)
