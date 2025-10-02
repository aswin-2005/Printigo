import uuid
import datetime
from flask import jsonify
from database import supabase, validate_user, create_slots

# ----------------------------
# Session Store
# ----------------------------
sessions = {}  # in-memory cache: token -> { user_id, created_at, expires_at }
SESSION_TTL_SECONDS = 3600  # 1 hour

def create_session_token(user_id):
    token = str(uuid.uuid4())
    now = datetime.datetime.utcnow()
    session_data = {
        "user_id": user_id,
        "created_at": now,
        "expires_at": now + datetime.timedelta(seconds=SESSION_TTL_SECONDS)
    }

    # Save in memory
    sessions[token] = session_data

    # Persist in DB
    try:
        supabase.table("sessions").insert({
            "id": token,
            "user_id": user_id,
            "created_at": session_data["created_at"].isoformat(),
            "expires_at": session_data["expires_at"].isoformat()
        }).execute()
    except Exception as e:
        print(f"Warning: failed to save session in DB: {str(e)}")

    return token

def validate_session(token):
    # First check in memory
    session = sessions.get(token)

    # If not found in memory, try DB
    if not session:
        try:
            result = supabase.table("sessions").select("*").eq("id", token).execute()
            if result.data:
                row = result.data[0]
                session = {
                    "user_id": row["user_id"],
                    "created_at": datetime.datetime.fromisoformat(row["created_at"]),
                    "expires_at": datetime.datetime.fromisoformat(row["expires_at"])
                }
                # restore in memory cache
                sessions[token] = session
        except Exception as e:
            print(f"Warning: failed to fetch session from DB: {str(e)}")
            return None

    if not session:
        return None

    # Check expiry
    if datetime.datetime.utcnow() > session["expires_at"]:
        del sessions[token]
        try:
            supabase.table("sessions").delete().eq("id", token).execute()
        except Exception as e:
            print(f"Warning: failed to delete expired session in DB: {str(e)}")
        return None

    # Fetch user role from DB
    try:
        result = supabase.table("users").select("role").eq("id", session["user_id"]).execute()
        if not result.data:
            return None
        session["role"] = result.data[0]["role"]
    except Exception as e:
        print(f"Warning: failed to fetch user role: {str(e)}")
        session["role"] = None

    return {"user_id": session["user_id"], "role": session.get("role")}



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
