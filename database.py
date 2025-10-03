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
        return jsonify({"slots": slot_list}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch slots: {str(e)}"}), 500

def get_user_jobs(user_id):
    try:
        jobs = supabase.table("jobs").select("*").eq("user_id", user_id).execute()
        return jsonify({"jobs": jobs.data}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch jobs: {str(e)}"}), 500

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
        return jsonify({"job": job.data[0]}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create job: {str(e)}"}), 500

def delete_user_job(job_id):
    try:
        resp = supabase.table("jobs").select("slot_id").eq("id", job_id).execute()
        if not resp.data:
            return jsonify({"error": "Job not found"}), 404

        supabase.table("jobs").delete().eq("id", job_id).execute()
        slot_id = resp.data[0]["slot_id"]

        slot_resp = supabase.table("slots").select("current_jobs").eq("id", slot_id).execute()
        if slot_resp.data and slot_resp.data[0]["current_jobs"] > 0:
            supabase.table("slots").update({
                "current_jobs": slot_resp.data[0]["current_jobs"] - 1
            }).eq("id", slot_id).execute()

        return jsonify({"message": f"Job {job_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete job: {str(e)}"}), 500

def validate_user(email, password=None, mode="login"):
    try:
        query = supabase.table("users").select("*").eq("email", email)
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
        return jsonify({"error": f"User validation failed: {str(e)}"}), 500

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
        return jsonify({"message": "Slots created successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create slots: {str(e)}"}), 500

def get_printer_jobs(printer_id):
    try:
        jobs = supabase.table("jobs").select("*").eq("printer_id", printer_id).execute()
        return jsonify({"jobs": jobs.data}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch printer jobs: {str(e)}"}), 500
    
def update_job_status(job_id, new_status):
    try:
        job = supabase.table("jobs").select("*").eq("id", job_id).execute()
        if not job.data:
            return jsonify({"error": "Job not found"}), 404
        
        updated_job = supabase.table("jobs").update({
            "status": new_status
        }).eq("id", job_id).execute()

        return jsonify({"job": updated_job.data[0]}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update job status: {str(e)}"}), 500
