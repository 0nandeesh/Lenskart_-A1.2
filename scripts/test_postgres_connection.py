"""
Test PostgreSQL connection with password
"""
import psycopg2
import sys

# Configuration
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "Data@123"

print("="*50)
print("Testing PostgreSQL Connection")
print("="*50)
print(f"Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
print(f"User: {POSTGRES_USER}")
print(f"Password: {'*' * len(POSTGRES_PASSWORD)}")
print()

try:
    print("Attempting connection...")
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        database='postgres'
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    
    print("[SUCCESS] Connected to PostgreSQL!")
    print(f"Version: {version[0]}")
    
    # Check if lenskart_search exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'lenskart_search'")
    exists = cursor.fetchone()
    
    if exists:
        print("\n[INFO] Database 'lenskart_search' already exists.")
    else:
        print("\n[INFO] Database 'lenskart_search' does not exist yet.")
        print("       You can create it using: python scripts/setup_database.py")
    
    cursor.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print("[ERROR] Connection failed!")
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("1. PostgreSQL service is not running")
    print("2. Wrong password")
    print("3. PostgreSQL not installed")
    print("\nTo start PostgreSQL service (Windows):")
    print("  1. Open Services (Win+R -> services.msc)")
    print("  2. Find 'PostgreSQL' service")
    print("  3. Right-click -> Start")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

