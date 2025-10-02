from flask import Flask, request, jsonify, send_file
import io
from auth import register_user, login_user, validate_session, sessions
from database import get_slots, get_user_jobs, validate_user, create_user_job, delete_user_job, get_printer_jobs, update_job_status
from file import upload_file, get_signed_url

app = Flask(__name__)

# -------------------------------
# Authentication Routes
# -------------------------------

@app.route("/auth/register", methods=["POST"])
def register():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        role = data.get("role")

        if not email or not password or not name or not role:
            return jsonify({"error": "Email, password, role or name missing"}), 400
        
        if role not in ["printer", "user"]:
            return jsonify({"error": "Invalid role"}), 400
            
        if not validate_user(email, mode="register"):
            return jsonify({"error": "User already exists"}), 400
        
        return register_user(email, password, name, role)
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@app.route("/auth/login", methods=["POST"])
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email or password missing"}), 400
        
        return login_user(email, password)
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

# -------------------------------
# Session Validation Helper
# -------------------------------
def get_user_id_from_token():
    token = request.headers.get("Authorization")
    if not token:
        return None, {"error": "Missing token"}, 401
    # print(f"Token: {token}")
    token = token.replace("Bearer ", "")
    user_info = validate_session(token)
    if not user_info:
        return None, {"error": "Invalid or expired session"}, 401
    return user_info, None, None

# -------------------------------
# User Routes
# -------------------------------

@app.route("/user/slots", methods=["GET"])
def slots():
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    try:
        slots = get_slots()
        return {"slots": slots}, 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch slots: {str(e)}"}), 500

@app.route("/user/jobs", methods=["GET"])
def get_jobs(): 
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    try:
        jobs = get_user_jobs(user_id)
        return {"jobs": jobs}, 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch jobs: {str(e)}"}), 500

@app.route("/user/jobs", methods=["POST"])
def create_job():
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    try:
        # Read form fields instead of request.json
        slot_id = request.form.get("slot_id")
        printer_id = request.form.get("printer_id")
        print_options = request.form.get("print_options")

        import json
        print_options = json.loads(print_options) if print_options else {}

        if not slot_id or not printer_id or not print_options:
            return {"error": "slot_id, printer_id or print_options missing"}, 400

        if "file" not in request.files:
            return jsonify({"error": "File is required"}), 400

        file = request.files["file"]
        if not file:
            return jsonify({"error": "No file provided"}), 400

        # Create job in DB
        job = create_user_job(user_id, slot_id, printer_id, print_options)

        # Save file (example: uploads/jobid.pdf)
        filepath = f"{job['id']}.pdf"
        upload_file(file, filepath)

        return {
            "message": "Print job created successfully",
            "job": job
        }, 201
    except Exception as e:
        return jsonify({"error": f"Failed to create job: {str(e)}"}), 500


@app.route("/user/jobs", methods=["DELETE"])
def delete_job():
    user_id, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code

    try:
        job_id = request.args.get("job_id")
        if not job_id:
            return {"error": "job_id is required"}, 400
        job = delete_user_job(job_id)
        if not job:
            return {"error": "Job not found"}, 404
        return {"message": f"Job {job_id} deleted successfully"}, 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete job: {str(e)}"}), 500

# -------------------------------
# Printer Routes
# -------------------------------

@app.route("/print/jobs", methods=["GET"])
def printer_jobs():
    user_info, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code
    
    user_id = user_info["user_id"]
    role = user_info.get("role")

    if role != "printer":
        return {"error": "Unauthorized, not a printer"}, 403

    try:
        jobs = get_printer_jobs(user_id)
        return {"jobs": jobs}, 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch printer jobs: {str(e)}"}), 500

@app.route("/print/jobs", methods=["PATCH"])
def patch_job_status():
    user_info, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code
    
    user_id = user_info["user_id"]
    role = user_info.get("role")

    if role != "printer":
        return {"error": "Unauthorized, not a printer"}, 403

    try:
        data = request.json
        job_id = data.get("job_id")
        status = data.get("status")

        if not job_id or not status:
            return {"error": "job_id or status missing"}, 400
        
        if status not in ["pending", "in_progress", "completed", "failed"]:
            return {"error": "Invalid status"}, 400
        
        job = update_job_status(job_id, status)
        if not job:
            return {"error": "Job not found"}, 404
        
        return {"message": f"Job {job_id} status updated to {status}"}, 200
    except Exception as e:
        return jsonify({"error": f"Failed to update job status: {str(e)}"}), 500
    
@app.route("/print/file", methods=["GET"])
def give_file():
    user_info, error_response, status_code = get_user_id_from_token()
    if error_response:
        return error_response, status_code
    
    user_id = user_info["user_id"]
    role = user_info.get("role")

    if role != "printer":
        return {"error": "Unauthorized, not a printer"}, 403

    job_id = request.args.get("job_id")
    if not job_id:
        return {"error": "job_id is required"}, 400

    try:
        filepath = f"{job_id}.pdf"
        file_url = get_signed_url(filepath)
        if not file_url:
            return {"error": "File url not found"}, 404

        # Wrap bytes in BytesIO for Flask
        return jsonify({"file_url": file_url}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch file: {str(e)}"}), 500

# ----------------------------
# Debug Routes
# ----------------------------

@app.route("/debug/sessions", methods=["GET"])
def debug_sessions():
    return {"sessions": sessions}



if __name__ == "__main__":
    app.run(debug=True, port=5500)
