from database import supabase

def upload_file(file, filename):
    try:
        # Read the uploaded file into bytes
        file_bytes = file.read()

        # Upload to Supabase Storage
        response = supabase.storage.from_("files").upload(
            path = filename,
            file = file_bytes,
            file_options = {"content-type": "application/pdf", "upsert": "true"}
        )
    except Exception as e:
        raise Exception(f"File upload failed: {str(e)}")
    
def get_signed_url(filename):
    try:
        response = supabase.storage.from_("files").create_signed_url(
            filename,
            3600
        )
        return response
    except Exception as e:
        raise Exception(f"File link generation failed: {str(e)}")