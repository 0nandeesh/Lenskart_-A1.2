"""
Test backend startup and diagnose issues
"""
import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_startup():
    """Test if backend can start"""
    try:
        print("Testing backend startup...")
        print("="*50)
        
        # Test imports
        print("1. Testing imports...")
        try:
            from backend.app.config import settings
            print("   [OK] Config imported")
        except Exception as e:
            print(f"   [ERROR] Config import failed: {e}")
            return
        
        # Test MySQL connection
        print("\n2. Testing MySQL connection...")
        try:
            from backend.app.database.mysql_db import db
            await db.connect()
            print("   [OK] MySQL connected")
            await db.disconnect()
        except Exception as e:
            print(f"   [ERROR] MySQL connection failed: {e}")
            print("   Please check:")
            print("   - MySQL is running")
            print("   - Credentials in backend/.env are correct")
            print("   - Database 'lenskart_search' exists")
            return
        
        # Test vector DB
        print("\n3. Testing vector DB initialization...")
        try:
            from backend.app.database.vector_db import vector_db
            vector_db.initialize()
            print("   [OK] Vector DB initialized")
        except Exception as e:
            print(f"   [ERROR] Vector DB failed: {e}")
            return
        
        # Test Groq client
        print("\n4. Testing Groq API...")
        try:
            from backend.app.ai.groq_client import get_groq_client
            client = get_groq_client()
            print("   [OK] Groq client initialized")
        except Exception as e:
            print(f"   [WARNING] Groq client failed: {e}")
            print("   (This is optional - backend will work without it)")
        
        print("\n" + "="*50)
        print("[SUCCESS] All tests passed!")
        print("Backend should start successfully.")
        print("="*50)
        
    except Exception as e:
        print(f"\n[ERROR] Startup test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_startup())

