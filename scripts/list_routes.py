
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from backend.app.main import app

for route in app.routes:
    # Check if it has a 'path' attribute
    if hasattr(route, "path"):
        print(f"ROUTE: {route.path}")
