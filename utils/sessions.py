import json
import os

USER_SESSION = "session.json"


def save_session(user_id, name_user, email, role):
    try:
        session_data = {"user_id": user_id, "name_user": name_user, "email": email, "role": role}
        with open(USER_SESSION, "w") as session_file:
            json.dump(session_data, session_file, indent=4)
            print("Session saved successfully.")
    except Exception as e:
        print(f"Error saving session: {e}")


def load_session():
    try:
        if os.path.exists(USER_SESSION):
            with open(USER_SESSION, "r") as file:
                return json.load(file)
    except Exception as e:
        print(f"Error loading session: {e}")
        return None


def clear_session():
    try:
        if os.path.exists(USER_SESSION):
            os.remove(USER_SESSION)
            print("Session cleared successfully.")
        else:
            print("No active session to clear.")
    except Exception as e:
        print(f"Error clearing session: {e}")
