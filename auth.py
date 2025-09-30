import uuid
import datetime
from flask import jsonify
from database import supabase, validate_user, create_slots

# ----------------------------
# Session Store
# ----------------------------
sessions = {}  # token -> { user_id, created_at, expires_at }
SESSION_TTL_SECONDS = 3600  # 1 hour

def create_session_token(user_id):
    token = str(uuid.uuid4())
    now = datetime.datetime.utcnow()
    sessions[token] = {
        "user_id": user_id,
        "created_at": now,
        "expires_at": now + datetime.timedelta(seconds=SESSION_TTL_SECONDS)
    }

    return token

def validate_session(token):
    session = sessions.get(token)
    if not session:
        return None

    if datetime.datetime.utcnow() > session["expires_at"]:
        del sessions[token]
        return None
    

    return session["user_id"]

# ----------------------------
# Auth Functions
# ----------------------------
def register_user(email, password, name, role):
    try:
        user_id = str(uuid.uuid4())
        supabase.table("users").insert({
            "id": user_id,
            "email": email,
            "password": password,
            "name": name,
            "role": role
        }).execute()

        if role == "printer":
            create_slots(user_id)

        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"User registration failed: {str(e)}"}), 500


def login_user(email, password):
    try:
        user_info = validate_user(email, password, mode="login")
        if not user_info:
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_session_token(user_info["id"])
        return jsonify({
            "id": user_info["id"],
            "email": user_info["email"],
            "name": user_info["name"],
            "role": user_info["role"],
            "token": token
        }), 200
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500
