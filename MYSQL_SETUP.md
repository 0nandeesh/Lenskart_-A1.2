# MySQL Database Setup Guide

The system has been migrated from PostgreSQL to **MySQL**.

## Quick Setup

### 1. Install MySQL

**Windows:**
- Download: https://dev.mysql.com/downloads/mysql/
- Or use XAMPP/WAMP (includes MySQL)
- During installation, set root password (remember it!)

**Linux:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### 2. Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

This installs:
- `aiomysql` - Async MySQL driver
- `pymysql` - MySQL connector

### 3. Create Database

```bash
python scripts/setup_mysql_database.py
```

Or manually:
```sql
CREATE DATABASE lenskart_search CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Configure Environment

Create `backend/.env`:

```env
# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=lenskart_search
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here

# Groq API (REQUIRED)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Vector DB
VECTOR_DB_PATH=./data/vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### 5. Start Backend

```bash
cd backend
uvicorn backend.app.main:app --reload
```

**Tables are created automatically on startup!**

## MySQL vs PostgreSQL Differences

The code has been updated to use MySQL syntax:
- Parameter placeholders: `%s` instead of `$1`
- Connection: `aiomysql` instead of `asyncpg`
- JSON columns: Native JSON type supported
- ON DUPLICATE KEY UPDATE instead of ON CONFLICT

## Testing Connection

```python
import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='lenskart_search'
)
print("Connected!")
conn.close()
```

## Troubleshooting

### MySQL Not Running

**Windows:**
- Services → MySQL → Start

**Linux:**
```bash
sudo systemctl status mysql
sudo systemctl start mysql
```

### Connection Refused

1. Check MySQL is running
2. Verify port 3306 is correct
3. Check firewall settings
4. Verify credentials in `.env`

### Access Denied

```sql
-- Connect as root
mysql -u root -p

-- Create user if needed
CREATE USER 'your_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON lenskart_search.* TO 'your_user'@'localhost';
FLUSH PRIVILEGES;
```

## Benefits of MySQL

1. **Widely Available**: Included in XAMPP/WAMP
2. **Easier Setup**: More common on Windows
3. **JSON Support**: Native JSON columns (MySQL 5.7+)
4. **Compatible**: Similar SQL syntax to PostgreSQL
5. **Performance**: Good for this use case

## Migration Complete

All code has been updated:
- ✅ Database connection (mysql_db.py)
- ✅ All services updated
- ✅ Analytics queries updated
- ✅ Behavior tracking updated
- ✅ Requirements updated

The system now uses MySQL instead of PostgreSQL!

