# Setup Guide

## Quick Start

### 1. Prerequisites

Install the following:
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis (optional, for async event processing)

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL database
createdb lenskart_search
# Or using psql:
psql -U postgres -c "CREATE DATABASE lenskart_search;"

# Copy environment file
cp .env.example .env

# Edit .env and set:
# - POSTGRES_* credentials
# - GROQ_API_KEY (REQUIRED - get from https://console.groq.com/)
# - REDIS_* (optional)
```

### 3. Streamlit UI Setup

```bash
# Install Streamlit and dependencies
pip install -r requirements_streamlit.txt

# Or install just Streamlit if backend dependencies already installed
pip install streamlit requests pandas
```

### 4. Get Groq API Key

1. Visit https://console.groq.com/
2. Sign up / Log in
3. Create an API key
4. Add it to `backend/.env`:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn backend.app.main:app --reload
```

Backend will be available at `http://localhost:8000`

**Terminal 2 - Streamlit UI:**
```bash
streamlit run streamlit_app.py
```

Streamlit UI will be available at `http://localhost:8501`

### 6. Ingest Sample Data

```bash
# From project root
python scripts/ingest_products.py data/sample_products.json
```

### 7. Test the System

1. Open `http://localhost:3000` in your browser
2. Try searching for:
   - "black sunglasses"
   - "eyeglasses for reading"
   - "sport sunglasses"
   - "cheap glasses under 100"
3. Click products, add to cart, make purchases
4. Observe how rankings change based on behavior

## Troubleshooting

### PostgreSQL Connection Error
- Ensure PostgreSQL is running
- Check credentials in `.env`
- Verify database exists: `psql -U postgres -l`

### Groq API Error
- Verify API key is set in `.env`
- Check API key is valid at https://console.groq.com/
- Ensure you have API credits/quota

### Vector DB Not Found
- Run the ingestion script to create the index
- Check `VECTOR_DB_PATH` in `.env`

### Redis Connection Error
- Redis is optional
- If not using Redis, events will be stored directly in PostgreSQL
- Set `REDIS_HOST=localhost` and ensure Redis is running if you want async processing

### Streamlit Can't Connect to Backend
- Ensure backend is running on port 8000
- Check `API_URL` in `streamlit_app.py` (defaults to `http://localhost:8000`)
- You can set it via Streamlit secrets: create `.streamlit/secrets.toml` with `API_URL = "http://localhost:8000"`
- Check CORS settings in `backend/app/main.py`

## Production Deployment

### Backend
- Use production ASGI server: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app.main:app`
- Set `DEBUG=False` in `.env`
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Use managed Redis (AWS ElastiCache, Google Cloud Memorystore)
- Set up proper CORS origins

### Frontend
- Build: `npm run build`
- Run: `npm start`
- Or deploy to Vercel/Netlify

### Environment Variables
- Use secrets management (AWS Secrets Manager, Google Secret Manager)
- Never commit `.env` files
- Use different API keys for production

