# API Requirements & Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API uses session-based tracking via headers:
- **Header**: `X-Session-ID` (optional, auto-generated if not provided)
- **Purpose**: Track user sessions for behavior analytics

## API Endpoints

### 1. Search

**POST** `/search`

Perform contextual semantic search with learning-based ranking.

**Request Body:**
```json
{
  "query": "black sunglasses for men",
  "category": "Sunglasses",           // Optional
  "min_price": 50.0,                  // Optional
  "max_price": 200.0,                  // Optional
  "min_rating": 4.0,                  // Optional
  "limit": 20                         // Optional, default: 20
}
```

**Response:**
```json
{
  "query": "black sunglasses for men",
  "expanded_query": "black sunglasses for men, male eyewear, dark lenses",
  "results": [
    {
      "product": {
        "id": "prod_001",
        "title": "Classic Aviator Sunglasses",
        "description": "Timeless aviator style...",
        "category": "Sunglasses",
        "price": 129.99,
        "rating": 4.5,
        "attributes": {
          "brand": "Lenskart",
          "color": "Black",
          "material": "Metal"
        }
      },
      "semantic_score": 0.85,
      "behavior_score": 0.72,
      "final_score": 0.79,
      "ai_explanation": "This product matches your search...",
      "score_breakdown": {
        "semantic_score": 0.85,
        "behavior_score": 0.72,
        "ctr": 0.15,
        "conversion_rate": 0.08,
        "bounce_rate": 0.05
      }
    }
  ],
  "total_results": 12,
  "search_time_ms": 245.5,
  "filters_applied": {
    "category": "Sunglasses",
    "min_price": 50.0,
    "max_price": 200.0,
    "min_rating": 4.0
  }
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: your-session-id" \
  -d '{
    "query": "black sunglasses",
    "category": "Sunglasses",
    "min_price": 50,
    "max_price": 200,
    "limit": 20
  }'
```

---

### 2. Product Management

#### Create/Update Product

**POST** `/products`

Create or update a single product.

**Request Body:**
```json
{
  "id": "prod_001",
  "title": "Classic Aviator Sunglasses",
  "description": "Timeless aviator style with UV protection",
  "category": "Sunglasses",
  "price": 129.99,
  "rating": 4.5,
  "attributes": {
    "brand": "Lenskart",
    "size": "Medium",
    "color": "Black",
    "material": "Metal",
    "style": "Aviator"
  },
  "image_url": "https://example.com/image.jpg"  // Optional
}
```

**Response:**
```json
{
  "status": "success",
  "product_id": "prod_001"
}
```

#### Create/Update Multiple Products

**POST** `/products/batch`

Create or update multiple products at once.

**Request Body:**
```json
[
  {
    "id": "prod_001",
    "title": "Product 1",
    ...
  },
  {
    "id": "prod_002",
    "title": "Product 2",
    ...
  }
]
```

**Response:**
```json
{
  "status": "success",
  "count": 2,
  "product_ids": ["prod_001", "prod_002"]
}
```

#### Get Product

**GET** `/products/{product_id}`

Retrieve a product by ID.

**Response:**
```json
{
  "id": "prod_001",
  "title": "Classic Aviator Sunglasses",
  "description": "...",
  "category": "Sunglasses",
  "price": 129.99,
  "rating": 4.5,
  "attributes": {...},
  "image_url": "...",
  "created_at": "2024-01-01T00:00:00"
}
```

---

### 3. Behavior Tracking

All behavior tracking endpoints are **asynchronous** and return immediately.

#### Track Click

**POST** `/events/click`

Track when a user clicks on a product.

**Request Body:**
```json
{
  "product_id": "prod_001"
}
```

**Response:**
```json
{
  "status": "success"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/events/click" \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: your-session-id" \
  -d '{"product_id": "prod_001"}'
```

#### Track Add to Cart

**POST** `/events/add-to-cart`

Track when a user adds a product to cart.

**Request Body:**
```json
{
  "product_id": "prod_001"
}
```

#### Track Purchase

**POST** `/events/purchase`

Track when a user purchases a product.

**Request Body:**
```json
{
  "product_id": "prod_001"
}
```

---

### 4. Analytics

#### Get Analytics Summary

**POST** `/analytics/summary`

Get overall analytics with top queries and poor performers.

**Request Body:**
```json
{
  "start_date": "2024-01-01T00:00:00",  // Optional, ISO format
  "end_date": "2024-01-31T23:59:59",    // Optional, ISO format
  "limit": 50,                           // Optional, default: 50
  "min_searches": 1                      // Optional, default: 1
}
```

**Response:**
```json
{
  "total_queries": 150,
  "total_searches": 5000,
  "total_clicks": 1200,
  "total_conversions": 150,
  "overall_ctr": 0.24,
  "overall_conversion_rate": 0.125,
  "zero_result_queries": 12,
  "top_queries": [
    {
      "query": "black sunglasses",
      "total_searches": 500,
      "total_clicks": 120,
      "total_carts": 30,
      "total_purchases": 15,
      "zero_results_count": 0,
      "ctr": 0.24,
      "conversion_rate": 0.125,
      "avg_dwell_time": 45.5,
      "first_seen": "2024-01-01T00:00:00",
      "last_seen": "2024-01-31T23:59:59"
    }
  ],
  "poor_performing_queries": [...]
}
```

#### Get Query Metrics

**GET** `/analytics/queries`

Get detailed metrics for all queries.

**Query Parameters:**
- `start_date` (optional): ISO format datetime
- `end_date` (optional): ISO format datetime
- `min_searches` (optional): Minimum searches to include (default: 1)

**Example:**
```bash
curl "http://localhost:8000/api/v1/analytics/queries?start_date=2024-01-01T00:00:00&min_searches=5"
```

#### Get Zero Result Queries

**GET** `/analytics/zero-results`

Get queries that resulted in zero clicks.

**Query Parameters:**
- `start_date` (optional): ISO format datetime
- `end_date` (optional): ISO format datetime

---

### 5. Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Python Client Example

```python
import requests

API_URL = "http://localhost:8000/api/v1"
session_id = "your-session-id"

# Search
response = requests.post(
    f"{API_URL}/search",
    json={
        "query": "black sunglasses",
        "category": "Sunglasses",
        "limit": 20
    },
    headers={"X-Session-ID": session_id}
)
results = response.json()

# Track click
requests.post(
    f"{API_URL}/events/click",
    json={"product_id": "prod_001"},
    headers={"X-Session-ID": session_id}
)

# Get analytics
analytics = requests.post(
    f"{API_URL}/analytics/summary",
    json={
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-01-31T23:59:59",
        "limit": 50
    }
).json()
```

---

## Required Backend Dependencies

Install from `backend/requirements.txt`:

```bash
pip install -r backend/requirements.txt
```

**Key Dependencies:**
- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation
- `asyncpg==0.29.0` - PostgreSQL async driver
- `faiss-cpu==1.7.4` - Vector similarity search
- `sentence-transformers==2.2.2` - Embeddings
- `groq==0.4.1` - Groq API client
- `redis==5.0.1` - Redis client (optional)

---

## Environment Variables Required

Create `backend/.env`:

```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=lenskart_search
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Groq API (REQUIRED)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# Vector DB
VECTOR_DB_PATH=./data/vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

---

## Running the API

### Development Mode

```bash
cd backend
uvicorn backend.app.main:app --reload
```

### Production Mode

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.app.main:app
```

---

## API Documentation (Swagger UI)

Once the API is running, access interactive documentation at:

```
http://localhost:8000/docs
```

This provides:
- All available endpoints
- Request/response schemas
- Try-it-out functionality
- Example requests

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (product/endpoint not found)
- `500` - Internal Server Error

---

## Rate Limiting

Currently, no rate limiting is implemented. For production:
- Add rate limiting middleware
- Use Redis for distributed rate limiting
- Implement API key authentication

---

## CORS Configuration

Current CORS settings (in `backend/app/main.py`):
```python
allow_origins=["*"]  # Allows all origins
```

**For Production:**
```python
allow_origins=["https://yourdomain.com"]
```

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Search
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "sunglasses"}'

# Track event
curl -X POST http://localhost:8000/api/v1/events/click \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod_001"}'
```

### Using Python requests

```python
import requests

# Search
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={"query": "sunglasses", "limit": 10}
)
print(response.json())
```

### Using Swagger UI

1. Start the API server
2. Navigate to `http://localhost:8000/docs`
3. Click on any endpoint
4. Click "Try it out"
5. Fill in parameters and click "Execute"

---

## Notes

1. **Session ID**: Auto-generated if not provided. Used for behavior tracking.
2. **Asynchronous Events**: Behavior tracking events are processed asynchronously.
3. **Vector DB**: FAISS index must be initialized (run ingestion script first).
4. **Groq API**: Required for AI features (query expansion, explanations, re-ranking).
5. **PostgreSQL**: Required for structured data and behavior metrics.
6. **Redis**: Optional, used for async event streaming (falls back to PostgreSQL if unavailable).

