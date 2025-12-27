
import sys
import os

# Add project root to path
# scripts/ is usually where this script is, so project root is one level up
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app.database.vector_db import vector_db
from backend.app.config import settings
import logging

logging.basicConfig(level=logging.INFO)

print(f"Project Root: {project_root}")
print(f"Vector DB Path: {settings.VECTOR_DB_PATH}")
print(f"Embedding Model: {settings.EMBEDDING_MODEL}")

print("\nInitializing VectorDB...")
try:
    vector_db.initialize()
    print("VectorDB Initialized.")
except Exception as e:
    print(f"\n[ERROR] VectorDB Initialization FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting Search...")
try:
    results = vector_db.search("sunglasses")
    print(f"Search Results: {results}")
except Exception as e:
    print(f"\n[ERROR] Search FAILED: {e}")
    import traceback
    traceback.print_exc()
