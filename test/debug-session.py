import requests

DEBUG_URL = "http://127.0.0.1:5500/debug/sessions"

def show_sessions():
    try:
        response = requests.get(DEBUG_URL)
        if response.status_code == 200:
            data = response.json()
            sessions = data.get("sessions", {})
            if not sessions:
                print("No active sessions.")
                return
            print("Active Sessions:")
            print("-" * 40)
            for token, session in sessions.items():
                user_id = session.get("user_id")
                created_at = session.get("created_at")
                expires_at = session.get("expires_at")
                print(f"Token      : {token}")
                print(f"User ID    : {user_id}")
                print(f"Created At : {created_at}")
                print(f"Expires At : {expires_at}")
                print("-" * 40)
        else:
            print(f"Failed to fetch sessions. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error connecting to server: {str(e)}")

if __name__ == "__main__":
    show_sessions()
