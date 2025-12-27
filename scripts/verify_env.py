"""
Verify .env file is being loaded correctly
"""
import os
import sys

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
os.chdir(backend_dir)

print("Current directory:", os.getcwd())
print("Checking for .env file...")

if os.path.exists('.env'):
    print("[OK] .env file exists")
    print("\nFirst few lines of .env:")
    with open('.env', 'r') as f:
        lines = f.readlines()[:10]
        for line in lines:
            if 'PASSWORD' in line:
                print(line.replace('PASSWORD', 'PASSWORD')[:50] + "...")
            else:
                print(line.strip())
else:
    print("[ERROR] .env file not found in", backend_dir)

print("\nTesting config loading...")
try:
    from backend.app.config import settings
    print(f"MYSQL_HOST: {settings.MYSQL_HOST}")
    print(f"MYSQL_PORT: {settings.MYSQL_PORT}")
    print(f"MYSQL_USER: {settings.MYSQL_USER}")
    print(f"MYSQL_PASSWORD: {'*' * len(settings.MYSQL_PASSWORD) if settings.MYSQL_PASSWORD else '(empty)'}")
    print(f"MYSQL_DB: {settings.MYSQL_DB}")
    print(f"GROQ_API_KEY: {'Set' if settings.GROQ_API_KEY else 'Not set'}")
except Exception as e:
    print(f"[ERROR] Failed to load config: {e}")

