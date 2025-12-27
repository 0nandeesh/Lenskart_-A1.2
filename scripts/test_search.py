"""
Test search functionality
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database.mysql_db import db
from backend.app.database.vector_db import vector_db

async def test():
    await db.connect()
    vector_db.initialize()
    
    # Check products in DB
    print("1. Checking products in MySQL...")
    all_ids = await db.filter_products()
    print(f"   Found {len(all_ids)} products in database")
    if all_ids:
        print(f"   Sample IDs: {all_ids[:3]}")
    
    # Check vector DB
    print(f"\n2. Checking vector DB...")
    print(f"   Total products in vector DB: {vector_db.get_total_products()}")
    
    # Test search
    print(f"\n3. Testing vector search...")
    results = vector_db.search("sunglasses", k=5)
    print(f"   Found {len(results)} results")
    if results:
        for pid, score in results[:3]:
            print(f"     - {pid}: {score:.3f}")
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(test())

