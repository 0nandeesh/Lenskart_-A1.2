# Database Setup Guide

## Creating the Database

### Method 1: Using psql Command Line (if PostgreSQL is in PATH)

```bash
psql -U postgres -c "CREATE DATABASE lenskart_search;"
```

If `psql` is not in PATH, use full path:
```bash
# Windows (typical installation)
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE lenskart_search;"

# Or add PostgreSQL bin to PATH
```

### Method 2: Using Python Script

```bash
python scripts/create_database.py
```

This script:
- Uses psycopg2 to connect
- Reads connection parameters from environment or defaults
- Creates the database if it doesn't exist

### Method 3: Using pgAdmin (GUI)

1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click on "Databases"
4. Select "Create" → "Database"
5. Name: `lenskart_search`
6. Click "Save"

### Method 4: Manual SQL Connection

Connect to PostgreSQL using any client and run:
```sql
CREATE DATABASE lenskart_search;
```

## Verifying Database Creation

### Using psql:
```bash
psql -U postgres -l | grep lenskart_search
```

### Using Python:
```python
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="postgres",
    database="lenskart_search"
)
print("Database connection successful!")
conn.close()
```

## Troubleshooting

### PostgreSQL Not Installed

**Windows:**
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer
3. Remember the password you set for `postgres` user
4. Add PostgreSQL bin directory to PATH

**Linux:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### Connection Errors

1. **Check PostgreSQL is running:**
   - Windows: Services → PostgreSQL
   - Linux: `sudo systemctl status postgresql`
   - macOS: `brew services list`

2. **Verify credentials in `backend/.env`:**
   ```env
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password_here
   POSTGRES_DB=lenskart_search
   ```

3. **Test connection:**
   ```python
   import psycopg2
   try:
       conn = psycopg2.connect(
           host="localhost",
           user="postgres",
           password="your_password",
           database="postgres"
       )
       print("Connection successful!")
       conn.close()
   except Exception as e:
       print(f"Connection failed: {e}")
   ```

### Permission Errors

If you get permission errors:
```sql
-- Connect as postgres superuser
psql -U postgres

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE lenskart_search TO your_user;
```

## Next Steps

After creating the database:

1. **Configure backend/.env** with correct credentials
2. **Run the backend** - tables will be created automatically on startup
3. **Ingest sample data:**
   ```bash
   python scripts/ingest_products.py data/sample_products.json
   ```

## Database Schema

The backend automatically creates these tables on startup:

1. **products** - Product catalog
2. **product_behavior_metrics** - Aggregated behavior metrics
3. **behavior_events** - Individual user behavior events

No manual schema setup required!

