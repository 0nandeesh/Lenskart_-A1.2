"""
Setup MySQL database using Python (pip install method)
This script creates the lenskart_search database using pymysql
"""
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.app.config import settings
except ImportError:
    # Fallback to environment variables or defaults
    settings = type('obj', (object,), {
        'MYSQL_HOST': os.getenv('MYSQL_HOST', 'localhost'),
        'MYSQL_PORT': int(os.getenv('MYSQL_PORT', '3306')),
        'MYSQL_USER': os.getenv('MYSQL_USER', 'root'),
        'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD', ''),
        'MYSQL_DB': os.getenv('MYSQL_DB', 'lenskart_search')
    })()

def create_database():
    """Create the database using pymysql"""
    try:
        import pymysql
    except ImportError:
        print("ERROR: pymysql not installed!")
        print("\nPlease install it using:")
        print("  pip install pymysql")
        print("\nOr install all backend requirements:")
        print("  pip install -r backend/requirements.txt")
        sys.exit(1)
    
    # Connect to MySQL server (without database)
    print(f"Connecting to MySQL server...")
    print(f"  Host: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}")
    print(f"  User: {settings.MYSQL_USER}")
    print(f"  Password: {'*' * len(settings.MYSQL_PASSWORD) if settings.MYSQL_PASSWORD else '(empty)'}")
    
    try:
        # Connect to MySQL server
        conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
            (settings.MYSQL_DB,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"\n[OK] Database '{settings.MYSQL_DB}' already exists.")
            print("  No action needed.")
        else:
            # Create the database
            print(f"\nCreating database '{settings.MYSQL_DB}'...")
            cursor.execute(f"CREATE DATABASE {settings.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
            print(f"[OK] Database '{settings.MYSQL_DB}' created successfully!")
        
        cursor.close()
        conn.close()
        
        # Verify connection to new database
        print(f"\nVerifying connection to '{settings.MYSQL_DB}'...")
        test_conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DB,
            charset='utf8mb4'
        )
        test_conn.close()
        print(f"[OK] Connection verified! Database is ready.")
        
        print("\n" + "="*50)
        print("Next steps:")
        print("1. Start the backend: uvicorn backend.app.main:app --reload")
        print("2. Tables will be created automatically on startup")
        print("3. Ingest sample data: python scripts/ingest_products.py data/sample_products.json")
        print("="*50)
        
    except pymysql.Error as e:
        print(f"\n[ERROR] Connection failed!")
        print(f"  Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check MySQL is installed and running")
        print("2. Verify credentials in backend/.env")
        print("3. Check MySQL service is started")
        print("4. Verify host/port are correct")
        print("\nTo install MySQL:")
        print("  Windows: Download from https://dev.mysql.com/downloads/mysql/")
        print("  Or use XAMPP/WAMP which includes MySQL")
        print("  After installation, start MySQL service and run this script again")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("="*50)
    print("Lenskart Search - MySQL Database Setup")
    print("="*50)
    create_database()

