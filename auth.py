import secrets
import datetime
from flask import jsonify
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# In-memory sessions
sessions = {}

# -------------------------------
# Register User
# -------------------------------
def register_user(email, password, name, role):
    try:
        result = supabase.table("users").insert({
            "email": email,
            "password": password,   # unchanged
            "name": name,
            "role": role
        }).execute()

        if not result.data:
            return jsonify({"error": "User registration failed"}), 500

        return jsonify({
            "id": result.data[0]["id"],
            "email": email,
            "name": name,
            "role": role
        }), 201
    except Exception as e:
        return jsonify({"error": f"Registration error: {str(e)}"}), 500

# -------------------------------
# Login User
# -------------------------------
def login_user(email, password):
    try:
        result = supabase.table("users").select("*").eq("email", email).execute()

        if not result.data:
            return jsonify({"error": "User not found"}), 404

        user = result.data[0]

        if user["password"] != password:
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate token
        token = secrets.token_hex(32)
        expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        sessions[token] = {
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "expiry": expiry.isoformat()
        }

        # Store in DB
        supabase.table("sessions").insert({
            "token": token,
            "user_id": user["id"],
            "expiry": expiry.isoformat()
        }).execute()

        return jsonify({
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "token": token
        }), 200
    except Exception as e:
        return jsonify({"error": f"Login error: {str(e)}"}), 500

# -------------------------------
# Validate Session
# -------------------------------
def validate_session(token):
    try:
        session = sessions.get(token)
        if session:
            expiry = datetime.datetime.fromisoformat(session["expiry"])
            if datetime.datetime.utcnow() > expiry:
                sessions.pop(token, None)
                return None
            return session

        # fallback to DB
        result = supabase.table("sessions").select("*").eq("token", token).execute()
        if not result.data:
            return None

        db_session = result.data[0]
        expiry = datetime.datetime.fromisoformat(db_session["expiry"])
        if datetime.datetime.utcnow() > expiry:
            supabase.table("sessions").delete().eq("token", token).execute()
            return None

        user_result = supabase.table("users").select("*").eq("id", db_session["user_id"]).execute()
        if not user_result.data:
            return None

        user = user_result.data[0]
        session_data = {
            "user_id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "expiry": db_session["expiry"]
        }
        sessions[token] = session_data
        return session_data
    except Exception:
        return None
