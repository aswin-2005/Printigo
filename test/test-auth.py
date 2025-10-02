import requests

BASE_URL = "http://127.0.0.1:5500"  # Flask server

# -------------------------
# Test Registration
# -------------------------
def test_register():
    users = [
        {
            "email": "testprinter1@example.com",
            "password": "printer123",
            "name": "Test Printer 1",
            "role": "printer"
        },
        {
            "email": "testuser1@example.com",
            "password": "user123",
            "name": "Test User 1",
            "role": "user"
        }
    ]

    for user in users:
        response = requests.post(f"{BASE_URL}/auth/register", json=user)
        print(f"Register {user['email']}: {response.status_code} {response.json()}")

# -------------------------
# Test Login
# -------------------------
def test_login():
    accounts = [
        {"email": "testprinter1@example.com", "password": "printer123"},
        {"email": "testuser1@example.com", "password": "user123"}
    ]

    for acc in accounts:
        response = requests.post(f"{BASE_URL}/auth/login", json=acc)
        print(f"Login {acc['email']}: {response.status_code} {response.json()}")
        if response.status_code == 200:
            token = response.json().get("token")
            print(f"Session token for {acc['email']}: {token}")

# -------------------------
# Run Tests
# -------------------------
if __name__ == "__main__":
    test_register()
    test_login()
