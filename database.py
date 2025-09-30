from supabase import Client, create_client
from dotenv import load_dotenv
import os
import uuid
from flask import jsonify

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_slots():
    try:
        slots = supabase.table("slots").select("*").execute()
        slot_list = {}
        for i in slots.data:
            if i["printer_id"] not in slot_list:
                slot_list[i["printer_id"]] = []
            slot_list[i["printer_id"]].append(i)
        return slot_list
    except Exception as e:
        raise Exception(f"Failed to fetch slots: {str(e)}")

def get_user_jobs(user_id):
    try:
        jobs = supabase.table("jobs").select("*").eq("user_id", user_id).execute()
        return jobs.data
    except Exception as e:
        raise Exception(f"Failed to fetch jobs: {str(e)}")

def create_user_job(user_id, slot_id, printer_id, print_options):
    try:
        response = supabase.table("slots").select("current_jobs,max_jobs").eq("id", slot_id).execute()
        if not response.data:
            return jsonify({"error": "Slot not found"}), 404
        slot = response.data[0]
        if slot["current_jobs"] >= slot["max_jobs"]:
            return jsonify({"error": "Slot is full"}), 400
        
        supabase.table("slots").update({
            "current_jobs": slot["current_jobs"] + 1
        }).eq("id", slot_id).execute()
        
        job_id = str(uuid.uuid4())
        job = supabase.table("jobs").insert({
            "id": job_id,
            "user_id": user_id,
            "slot_id": slot_id,
            "printer_id": printer_id,
            "print_options": print_options,
            "status": "pending"
        }).execute()
        return job.data[0]
    except Exception as e:
        raise Exception(f"Failed to create job: {str(e)}")

def delete_user_job(job_id):
    try:
        job = supabase.table("jobs").select("*").eq("id", job_id).execute()
        if not job.data:
            return None
        supabase.table("jobs").delete().eq("id", job_id).execute()
        return job.data[0]
    except Exception as e:
        raise Exception(f"Failed to delete job: {str(e)}")

def validate_user(email, password=None, mode="login"):
    try:
        query = supabase.table("users").select("*")
        query = query.eq("email", email)
        
        if mode == "login":
            if not password:
                return None
            query = query.eq("password", password)
        
        result = query.execute()
        
        if mode == "login":
            return result.data[0] if result.data else None
        else:
            return len(result.data) == 0
    except Exception as e:
        raise Exception(f"User validation failed: {str(e)}")

def create_slots(printer_id):
    try:
        for i in range(4):
            slot_id = str(uuid.uuid4())
            supabase.table("slots").insert({
                "id": slot_id,
                "slot_type": f"slot{i+1}",
                "printer_id": printer_id,
                "max_jobs": 10,
                "current_jobs": 0
            }).execute()
    except Exception as e:
        raise Exception(f"Failed to create slots: {str(e)}")


def get_printer_jobs(printer_id):
    try:
        jobs = supabase.table("jobs").select("*").eq("printer_id", printer_id).execute()
        return jobs.data
    except Exception as e:
        raise Exception(f"Failed to fetch printer jobs: {str(e)}")
    
def update_job_status(job_id, new_status):
    try:
        job = supabase.table("jobs").select("*").eq("id", job_id).execute()
        if not job.data:
            return None
        updated_job = supabase.table("jobs").update({
            "status": new_status
        }).eq("id", job_id).execute()
        return updated_job.data[0]
    except Exception as e:
        raise Exception(f"Failed to update job status: {str(e)}")