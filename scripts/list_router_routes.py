
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from backend.app.api.routes import router

for route in router.routes:
    if hasattr(route, "path"):
        print(f"ROUTE: {route.path}")
