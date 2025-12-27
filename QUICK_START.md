# Quick Start Guide

## Step 1: Install Dependencies

```bash
# Install backend dependencies (includes psycopg2-binary)
pip install -r backend/requirements.txt

# Or install Streamlit UI dependencies (includes everything)
pip install -r requirements_streamlit.txt
```

## Step 2: Install PostgreSQL

**Windows:**
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer
3. Set password for `postgres` user (remember this!)
4. Complete installation

**After installation, start PostgreSQL service:**
- Open Services (Win+R → `services.msc`)
- Find "PostgreSQL" service
- Right-click → Start

## Step 3: Create Database (Using Python)

```bash
python scripts/setup_database.py
```

This script uses `psycopg2` (installed via pip) to create the database.

**If connection fails:**
- Check PostgreSQL service is running
- Verify password in `backend/.env`
- Default connection: `localhost:5432` as `postgres`

## Step 4: Configure Environment

Create `backend/.env`:

```env
# PostgreSQL (use password you set during installation)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=lenskart_search
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password_here

# Groq API (REQUIRED - get from https://console.groq.com/)
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

## Step 5: Start Backend

```bash
cd backend
uvicorn backend.app.main:app --reload
```

Backend will be available at `http://localhost:8000`

**Tables are created automatically on startup!**

## Step 6: Ingest Sample Data

```bash
# From project root
python scripts/ingest_products.py data/sample_products.json
```

## Step 7: Start Streamlit UI

```bash
streamlit run streamlit_app.py
```

UI will be available at `http://localhost:8501`

## Verify Everything Works

1. **Backend Health:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

2. **API Docs:**
   Open: http://localhost:8000/docs

3. **Streamlit UI:**
   Open: http://localhost:8501

4. **Test Search:**
   - Go to Streamlit UI
   - Search for "black sunglasses"
   - Check results appear

## Troubleshooting

### PostgreSQL Connection Issues

**Check if PostgreSQL is running:**
```bash
# Windows PowerShell
Get-Service | Where-Object {$_.Name -like "*postgres*"}
```

**Test connection manually:**
```python
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="your_password",
    database="postgres"
)
print("Connected!")
conn.close()
```

### Missing Dependencies

```bash
# Install all at once
pip install -r backend/requirements.txt
pip install streamlit requests pandas
```

### Groq API Key

1. Visit: https://console.groq.com/
2. Sign up / Log in
3. Create API key
4. Add to `backend/.env`

### Database Already Exists

If database already exists, the script will skip creation. This is fine!

## Next Steps

- Try different search queries
- Check Analytics Dashboard
- Review API documentation at `/docs`
- Customize ranking weights in `.env`

