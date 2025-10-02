import os
from supabase import create_client
from dotenv import load_dotenv

# Load Supabase credentials
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Local PDF file
local_file_path = "./test/sample.pdf"
remote_file_name = "sample.pdf"

try:
    with open(local_file_path, "rb") as f:
        response = supabase.storage.from_("files").upload(
            file=f,
            path=remote_file_name,
            file_options={"content_type": "application/pdf", "upsert": "true"}
        )
        print("Upload Response:", response)
except Exception as e:
    print("Error uploading file:", e)
