import sys
import os
import json

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Remove old test database if present
db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mindcare.db")
if os.path.exists(db_file):
    os.remove(db_file)

import src.database as db
from api import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_auth_flow():
    import time
    email = f"testuser_{int(time.time())}@example.com"
    password = "securepassword123"
    
    # Test Signup
    response = client.post("/auth/signup", json={"email": email, "password": password})
    print("Signup Status Code:", response.status_code)
    print("Signup Response:", response.json())
    assert response.status_code == 201
    user_data = response.json()
    user_id = user_data["id"]

    # Test duplicate Signup (should fail)
    dup_response = client.post("/auth/signup", json={"email": email, "password": password})
    print("Duplicate Signup Status Code:", dup_response.status_code)
    assert dup_response.status_code == 400

    print("\n--- 2. Testing Login ---")
    login_resp = client.post("/auth/login", json={"email": email, "password": password})
    print("Login Status Code:", login_resp.status_code)
    print("Login Response:", login_resp.json())
    assert login_resp.status_code == 200

    # Wrong password test
    wrong_login = client.post("/auth/login", json={"email": email, "password": "wrongpassword"})
    print("Wrong Login Status Code:", wrong_login.status_code)
    assert wrong_login.status_code == 401

    print("\n--- 3. Testing User Chat Persistence ---")
    chat_req = {
        "message": "I feel anxious about my upcoming exams",
        "user_id": user_id,
        "mood_info": {"mood": "Anxious", "stress_level": 8, "sleep_hours": 5.5}
    }
    chat_resp = client.post("/chat", json=chat_req)
    print("Chat Response Status:", chat_resp.status_code)
    print("Chat Intent:", chat_resp.json().get("intent"))

    history_resp = client.get(f"/chat/history/{user_id}")
    history = history_resp.json().get("history", [])
    print(f"Chat History count for User {user_id}:", len(history))
    assert len(history) == 2  # 1 user msg + 1 assistant msg

    print("\n--- 4. Testing Mood & Journal Persistence ---")
    mood_resp = client.post("/mood", json={"user_id": user_id, "mood": "Anxious", "stress_level": 8, "sleep_hours": 5.5, "notes": "Exam week"})
    print("Mood Log Response:", mood_resp.json())

    journal_resp = client.post("/journal", json={"user_id": user_id, "text": "Today was a tough day studying.", "mood_tag": "Stressed"})
    print("Journal Log Response:", journal_resp.json())

    user_moods = client.get(f"/mood/{user_id}").json().get("logs")
    print("Fetched User Mood Logs:", len(user_moods))

    print("\n[OK] All Auth & Persistence API tests passed successfully!")

if __name__ == "__main__":
    test_auth_flow()
