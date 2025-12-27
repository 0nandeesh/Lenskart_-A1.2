"""
Setup MySQL database with password: Data@123
"""
import pymysql
import sys

# Configuration
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "Nandeesh@123"  # Your MySQL password
DATABASE_NAME = "lenskart_search"

print("="*50)
print("Lenskart Search - MySQL Database Setup")
print("="*50)
print(f"Host: {MYSQL_HOST}:{MYSQL_PORT}")
print(f"User: {MYSQL_USER}")
print(f"Database: {DATABASE_NAME}")
print()

try:
    # Connect to MySQL server
    print("Connecting to MySQL server...")
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # Check if database already exists
    print(f"Checking if database '{DATABASE_NAME}' exists...")
    cursor.execute(
        "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
        (DATABASE_NAME,)
    )
    exists = cursor.fetchone()
    
    if exists:
        print(f"[OK] Database '{DATABASE_NAME}' already exists!")
        print("  No action needed.")
    else:
        # Create the database
        print(f"Creating database '{DATABASE_NAME}'...")
        cursor.execute(f"CREATE DATABASE {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        print(f"[OK] Database '{DATABASE_NAME}' created successfully!")
    
    cursor.close()
    conn.close()
    
    # Verify connection to new database
    print(f"\nVerifying connection to '{DATABASE_NAME}'...")
    test_conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DATABASE_NAME,
        charset='utf8mb4'
    )
    test_conn.close()
    print(f"[OK] Connection verified! Database is ready.")
    
    print("\n" + "="*50)
    print("SUCCESS! Database created.")
    print("="*50)
    print("\nNext steps:")
    print("1. Create backend/.env file with:")
    print("   MYSQL_PASSWORD=Data@123")
    print("2. Start backend: uvicorn backend.app.main:app --reload")
    print("3. Tables will be created automatically on startup")
    print("4. Ingest data: python scripts/ingest_products.py data/sample_products.json")
    print("="*50)
    
except pymysql.Error as e:
    print(f"\n[ERROR] Connection failed!")
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check MySQL is installed and running")
    print("2. Verify password is correct: Data@123")
    print("3. Check MySQL service is started")
    print("   - Windows: Services -> MySQL -> Start")
    print("   - Or use XAMPP/WAMP MySQL")
    print("4. Try connecting manually:")
    print("   mysql -u root -p")
    print("   (enter password: Data@123)")
    sys.exit(1)
except Exception as e:
    print(f"\n[ERROR] {e}")
    sys.exit(1)

