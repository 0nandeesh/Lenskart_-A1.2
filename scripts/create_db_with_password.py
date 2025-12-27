"""
Create database with password: Data@123
Run this script: python scripts/create_db_with_password.py
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configuration
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "Data@123"
DATABASE_NAME = "lenskart_search"

print("="*50)
print("Creating Database: lenskart_search")
print("="*50)
print(f"Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
print(f"User: {POSTGRES_USER}")
print(f"Database: {DATABASE_NAME}")
print()

try:
    # Connect to default postgres database
    print("Connecting to PostgreSQL server...")
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database='postgres'
    )
    
    # Set isolation level to allow CREATE DATABASE
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database already exists
    print(f"Checking if database '{DATABASE_NAME}' exists...")
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (DATABASE_NAME,)
    )
    exists = cursor.fetchone()
    
    if exists:
        print(f"[OK] Database '{DATABASE_NAME}' already exists!")
    else:
        # Create the database
        print(f"Creating database '{DATABASE_NAME}'...")
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DATABASE_NAME)
            )
        )
        print(f"[OK] Database '{DATABASE_NAME}' created successfully!")
    
    cursor.close()
    conn.close()
    
    # Verify connection to new database
    print(f"\nVerifying connection to '{DATABASE_NAME}'...")
    test_conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database=DATABASE_NAME
    )
    test_conn.close()
    print(f"[OK] Connection verified! Database is ready.")
    
    print("\n" + "="*50)
    print("SUCCESS! Database created.")
    print("="*50)
    print("\nNext steps:")
    print("1. Create backend/.env file with:")
    print("   POSTGRES_PASSWORD=Data@123")
    print("2. Start backend: uvicorn backend.app.main:app --reload")
    print("3. Tables will be created automatically")
    print("4. Ingest data: python scripts/ingest_products.py data/sample_products.json")
    print("="*50)
    
except psycopg2.OperationalError as e:
    print(f"\n[ERROR] Connection failed!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check PostgreSQL service is running")
    print("   - Open Services (Win+R -> services.msc)")
    print("   - Find 'PostgreSQL' service -> Start")
    print("2. Verify password is correct: Data@123")
    print("3. Check PostgreSQL is installed")
    import sys
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] {e}")
    import sys
    sys.exit(1)

