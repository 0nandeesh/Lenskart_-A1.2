# Database Migration: PostgreSQL → MySQL

## ✅ Migration Complete!

The system has been successfully migrated from PostgreSQL to **MySQL**.

## Changes Made

### 1. Database Driver
- **Before**: `asyncpg` (PostgreSQL async driver)
- **After**: `aiomysql` (MySQL async driver)

### 2. Configuration
- Updated `backend/app/config.py` with MySQL settings:
  - `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DB`, `MYSQL_USER`, `MYSQL_PASSWORD`

### 3. Database Module
- **New**: `backend/app/database/mysql_db.py`
- Replaced: `backend/app/database/postgres.py` (still exists for reference)

### 4. SQL Syntax Changes
- Parameter placeholders: `$1, $2` → `%s`
- ON CONFLICT → ON DUPLICATE KEY UPDATE
- JSONB → JSON (native MySQL JSON type)
- All queries updated to MySQL syntax

### 5. Files Updated
- ✅ `backend/app/main.py`
- ✅ `backend/app/services/search_service.py`
- ✅ `backend/app/services/ranking_service.py`
- ✅ `backend/app/services/behavior_tracker.py`
- ✅ `backend/app/services/analytics_service.py`
- ✅ `backend/app/services/ingestion_service.py`
- ✅ `backend/app/api/routes.py`
- ✅ `scripts/ingest_products.py`

### 6. Dependencies
- ✅ Updated `backend/requirements.txt`:
  - Removed: `asyncpg`, `psycopg2-binary`
  - Added: `aiomysql`, `pymysql`

## Setup Instructions

### 1. Install MySQL
```bash
# Windows: Download from https://dev.mysql.com/downloads/mysql/
# Or use XAMPP/WAMP
```

### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Create Database
```bash
python scripts/setup_mysql_database.py
```

### 4. Configure `.env`
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=lenskart_search
MYSQL_USER=root
MYSQL_PASSWORD=your_password
```

### 5. Start Backend
```bash
uvicorn backend.app.main:app --reload
```

Tables are created automatically on startup!

## Benefits

1. **Easier Setup**: MySQL often comes with XAMPP/WAMP
2. **Widely Used**: More common on Windows development
3. **JSON Support**: Native JSON columns (MySQL 5.7+)
4. **Compatible**: Similar SQL to PostgreSQL
5. **No psql Needed**: Uses Python directly

## Testing

Test the connection:
```bash
python scripts/setup_mysql_database.py
```

If successful, you'll see:
```
[OK] Database 'lenskart_search' created successfully!
[OK] Connection verified! Database is ready.
```

## Notes

- PostgreSQL code (`postgres.py`) is kept for reference but not used
- All functionality remains the same
- No data migration needed (fresh setup)
- Vector DB (FAISS) unchanged - independent of SQL database

See `MYSQL_SETUP.md` for detailed setup instructions.

