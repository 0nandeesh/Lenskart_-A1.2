"""
Start backend server from project root
"""
import os
import sys
import subprocess

# Ensure we're in the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)

print("Starting backend server...")
print(f"Project root: {project_root}")
print(f"Working directory: {os.getcwd()}")
print("\n" + "="*50)

# Start uvicorn
try:
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.app.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ], cwd=project_root)
except KeyboardInterrupt:
    print("\nServer stopped.")

