"""
Simple user authentication for Streamlit
Stores user credentials in a JSON file (for demo purposes)
"""
import json
import hashlib
from pathlib import Path

USERS_FILE = Path("users.json")

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def register_user(username: str, password: str) -> bool:
    """Register a new user"""
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password_hash": hash_password(password),
        "user_id": f"user_{username}"
    }
    save_users(users)
    return True

def authenticate_user(username: str, password: str) -> tuple[bool, str]:
    """Authenticate user and return (success, user_id)"""
    users = load_users()
    if username not in users:
        return False, None
    if users[username]["password_hash"] == hash_password(password):
        return True, users[username]["user_id"]
    return False, None

def get_user_id(username: str) -> str:
    """Get user_id for a username"""
    users = load_users()
    if username in users:
        return users[username]["user_id"]
    return None
