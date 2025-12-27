"""
Script to create PostgreSQL database
Alternative to psql command
"""
import sys
import os

# Try different methods to connect to PostgreSQL
try:
    import psycopg2
    from psycopg2 import sql
    
    # Get connection parameters from environment or defaults
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    dbname = 'postgres'  # Connect to default postgres database first
    
    print(f"Connecting to PostgreSQL at {host}:{port} as {user}...")
    
    # Connect to default postgres database
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=dbname
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'lenskart_search'")
    exists = cursor.fetchone()
    
    if exists:
        print("Database 'lenskart_search' already exists.")
    else:
        # Create database
        cursor.execute(sql.SQL("CREATE DATABASE lenskart_search"))
        print("Database 'lenskart_search' created successfully!")
    
    cursor.close()
    conn.close()
    
except ImportError:
    print("Error: psycopg2 not installed.")
    print("Install it with: pip install psycopg2-binary")
    sys.exit(1)
    
except Exception as e:
    print(f"Error creating database: {e}")
    print("\nAlternative methods:")
    print("1. Use pgAdmin (GUI tool)")
    print("2. Use psql command line (if PostgreSQL is in PATH)")
    print("3. Check PostgreSQL is installed and running")
    print("4. Verify connection parameters in backend/.env")
    sys.exit(1)

