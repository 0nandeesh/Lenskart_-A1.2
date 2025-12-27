# Lenskart AI Search Platform

<div align="center">

![Lenskart AI Search Platform](docs/images/hero-banner.png)

**A production-ready, modular AI-powered contextual search platform designed for Lenskart**

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![FAISS](https://img.shields.io/badge/FAISS-00ADD8?style=for-the-badge&logo=meta&logoColor=white)](https://github.com/facebookresearch/faiss)
[![Groq](https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=ai&logoColor=white)](https://groq.com/)

[Demo Video](#-demo-video) • [Features](#-features) • [Quick Start](#-quick-start) • [API Docs](#-api-reference)

</div>

---

## 🎥 Demo Video

<div align="center">

[![Watch Demo Video](./docs/images/watch-video-button-isolated-on-white-bakcground-design-vector.jpg)](./docs/images/demo-video.mp4)

*Click the button above to download and watch the demo video*

**What's in the demo:**
- 🔍 Natural language search with semantic understanding
- 🎯 AI-powered result ranking and explanations
- 📊 Real-time analytics and performance insights
- 🛒 Complete user journey from search to purchase

</div>

---

## ✨ Features Overview

### 🔐 User Authentication & Personalization

<div align="center">
<img src="docs/images/login-screen.png" alt="Login Screen" width="700"/>
<p><i>Secure authentication with personalized user experiences</i></p>
</div>

### 🔍 Intelligent Search Interface

<table>
<tr>
<td width="50%">

<img src="docs/images/search-interface.png" alt="Search Interface" width="100%"/>

</td>
<td width="50%">

### Natural Language Search
- **Semantic Understanding**: Comprehends context and intent
- **Query Expansion**: Automatically enriches queries with synonyms
- **Fast Results**: Sub-100ms response time
- **Dynamic Filters**: Category, price, and rating filters

</td>
</tr>
</table>

### 🎨 Advanced Filtering System

<div align="center">
<img src="docs/images/filters-expanded.png" alt="Dynamic Filters" width="700"/>
<p><i>Intuitive filters for category, price range, and minimum ratings</i></p>
</div>

### 🤖 AI-Powered Results

<table>
<tr>
<td width="50%">

### Intelligent Ranking
- **Semantic Relevance**: FAISS vector similarity search
- **Behavioral Learning**: CTR and conversion-based ranking
- **AI Explanations**: "Why this result?" transparency
- **Score Breakdown**: Detailed relevance metrics

</td>
<td width="50%">

<img src="docs/images/search-results.png" alt="Search Results" width="100%"/>

</td>
</tr>
</table>

---

## 📊 Analytics & Insights

### Personal Analytics Dashboard

<div align="center">
<img src="docs/images/user-analytics.png" alt="User Analytics" width="800"/>
<p><i>Track your search history, recently viewed products, and cart activity</i></p>
</div>

### Global Performance Metrics

<div align="center">
<img src="docs/images/global-analytics.png" alt="Global Performance Summary" width="800"/>
</div>

**Key Performance Indicators:**

| Metric | Description | Target |
|--------|-------------|--------|
| 🎯 **Overall CTR** | Click-through rate across all searches | > 15% |
| 💰 **Conversion Rate** | Percentage of searches leading to purchases | > 3% |
| ❌ **Zero Results** | Queries returning no products | < 5% |
| 📈 **Total Queries** | Unique search queries executed | Trending ↑ |

### Query Performance Analysis

<div align="center">
<img src="docs/images/top-queries.png" alt="Top Queries Analysis" width="800"/>
<p><i>Detailed breakdown of search performance by query with CTR and conversion metrics</i></p>
</div>

**Analytics Tabs:**
- **📊 Top Queries**: Most searched terms with engagement metrics
- **⚠️ Poor Performers**: Low CTR queries needing optimization
- **❌ Zero Results**: Failed searches requiring query expansion improvements

### Search Relevance Trends

<div align="center">
<img src="docs/images/ctr-trend.png" alt="CTR Over Time" width="800"/>
<p><i>Real-time CTR trends showing system learning and improvement</i></p>
</div>

### Performance Distribution

<div align="center">
<img src="docs/images/performance-distribution.png" alt="Performance Charts" width="800"/>
<p><i>Search success rate and engagement funnel visualization</i></p>
</div>

---

## 🏛️ Architecture

<div align="center">

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[Streamlit Frontend]
    end
    
    subgraph "API Layer"
        B[FastAPI Backend]
        C[REST Endpoints]
    end
    
    subgraph "AI Layer"
        D[Groq LLM]
        E[Query Expansion]
        F[AI Re-ranking]
        G[Explanations]
    end
    
    subgraph "Data Layer"
        H[(MySQL)]
        I[(FAISS Vector DB)]
        J[(Redis Cache)]
    end
    
    A -->|HTTP| B
    B --> C
    C -->|AI Calls| D
    D --> E
    D --> F
    D --> G
    C -->|Store| H
    C -->|Vector Search| I
    C -->|Cache| J
    
    style A fill:#FF4B4B
    style B fill:#009688
    style D fill:#F55036
    style H fill:#4479A1
    style I fill:#00ADD8
```

*Layered microservices architecture designed for scalability and maintainability*

</div>

### Architecture Components

#### 1. Presentation Layer (Frontend)
- **Technology**: Streamlit (Python-based)
- **Purpose**: Interactive search interface and analytics dashboard
- **Key Features**: 
  - Natural language input
  - Dynamic filters with real-time updates
  - AI-driven result explanations
  - Personal and global analytics

#### 2. API Layer (Backend)
- **Technology**: FastAPI
- **Purpose**: RESTful API endpoints for search, product management, and behavior tracking
- **Features**:
  - Async event processing
  - Request validation with Pydantic
  - Auto-generated OpenAPI docs
- **Docs**: Interactive Swagger UI at `http://localhost:8000/docs`

#### 3. AI Layer
- **Technology**: Groq API (LLaMA 3.1 70B Model)
- **Capabilities**:
  - **Query Expansion**: Enriches user queries with synonyms and context
  - **AI Re-ranking**: Dynamically re-ranks top results for maximum relevance
  - **Explanations**: Generates "Why this product?" insights
  - **Attribute Extraction**: Automatically parses material, color, and brand

#### 4. Data Layer
- **MySQL**: Relational storage for structured product data and persistent behavior metrics
- **FAISS**: High-performance vector database for semantic similarity search
- **Redis**: Asynchronous event streaming and low-latency metrics caching

---

## 🚀 Quick Start

### Prerequisites

```bash
# System Requirements
- Python 3.9+
- MySQL 8.0+
- 4GB RAM minimum
- Groq API Key (get from https://console.groq.com)
```

### 1. Clone & Install

```bash
# Clone the repository
git clone https://github.com/yourusername/lenskart-ai-search.git
cd lenskart-ai-search

# Install dependencies
pip install -r requirements_streamlit.txt
```

### 2. Database Setup (MySQL)

<details>
<summary>📖 Click to expand MySQL setup instructions</summary>

**Step 1**: Ensure MySQL is running on your system

**Step 2**: Create `.env` file in `backend/` directory:

```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=lenskart_search
MYSQL_USER=root
MYSQL_PASSWORD=your_password

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Ranking Weights (Optional - defaults provided)
SEMANTIC_WEIGHT=0.4
CTR_WEIGHT=0.3
CONVERSION_WEIGHT=0.3
```

**Step 3**: Initialize the database

```bash
python scripts/setup_mysql_database.py
```

Expected output:
```
✓ Database 'lenskart_search' created
✓ Tables initialized successfully
✓ Indexes created
```

</details>

### 3. Environment Configuration

Add your Groq API Key to `backend/.env`:

```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Run the Platform

**Terminal 1 - Start Backend:**
```bash
cd backend
uvicorn backend.app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run streamlit_app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

<div align="center">
<img src="docs/images/platform-running.png" alt="Platform Running" width="700"/>
<p><i>✅ Your platform is now accessible at http://localhost:8501</i></p>
</div>

### 5. Ingest Sample Data

```bash
python scripts/ingest_products.py data/sample_products.json
```

Expected output:
```
✓ Loaded 100 products from sample_products.json
✓ Generated embeddings for 100 products
✓ Stored in MySQL and FAISS
✓ Ingestion complete in 12.3s
```

---

## 📱 User Interface Walkthrough

### Login & Authentication

<div align="center">
<img src="docs/images/login-screen.png" alt="Login Screen" width="600"/>
</div>

**Features:**
- Secure user authentication
- Session management
- Personalized user profiles

### Search Experience

<div align="center">
<img src="docs/images/search-interface.png" alt="Search Interface" width="700"/>
</div>

**Natural Language Queries:**
- "blue light glasses for office work"
- "list glass which have rating 4.0 and above"
- "sunglasses under 150"
- "i need a Cat-Eye Sunglasses"

### Dynamic Filters

<div align="center">
<img src="docs/images/filters-expanded.png" alt="Filters" width="700"/>
</div>

**Filter Options:**
- 📁 **Category**: Sunglasses, Eyeglasses, Contact Lenses
- 💵 **Price Range**: Min/Max price sliders
- ⭐ **Minimum Rating**: 0.0 to 5.0 stars

### Search Results

<div align="center">
<img src="docs/images/search-results.png" alt="Results" width="700"/>
</div>

**Result Cards Include:**
- Product name and category
- Price and rating
- Product description
- "Why this result?" AI explanation
- Score breakdown (semantic + behavioral)
- Add to Cart / Purchase / View Details buttons

### My Analytics Dashboard

<div align="center">
<img src="docs/images/user-analytics.png" alt="User Analytics" width="700"/>
</div>

**Personal Insights:**
- 🔍 Recent searches with timestamps
- 👀 Recently viewed products
- 🛒 Items added to cart
- 📊 Your search behavior patterns

### Global Analytics

<div align="center">
<img src="docs/images/global-analytics.png" alt="Global Analytics" width="800"/>
</div>

**System-Wide Metrics:**
- Total queries, searches, and conversions
- Overall CTR and conversion rates
- Zero-result query tracking
- Performance trends over time

---

## 🎯 Technical Implementation

### Project Justification

<div align="center">
<img src="docs/images/project-justification.png" alt="Project Justification" width="800"/>
<p><i>Detailed breakdown of how requirements are met</i></p>
</div>

### How Functional Requirements Are Met

**3.1 Product Ingestion Pipeline**
- ✅ Modular pipeline in `ingestion_service.py`
- ✅ Text normalization and cleaning
- ✅ Dual storage: MySQL (structured) + FAISS (vector)
- ✅ Automatic embedding generation

**3.2 Contextual Search**
- ✅ Hybrid search: Semantic (FAISS) + SQL filtering
- ✅ Natural language query understanding
- ✅ Sub-100ms response time
- ✅ Faceted filtering support

**3.3 User Behavior Tracking**
- ✅ Asynchronous event system via Redis Streams
- ✅ Click tracking without latency impact
- ✅ Purchase conversion tracking
- ✅ Dwell time analysis

**3.4 Learning-Based Ranking**
- ✅ Feedback loop in `ranking_service.py`
- ✅ CTR-based product boosting
- ✅ Conversion signal integration
- ✅ Dynamic weight adjustment

**3.5 AI Integration**
- ✅ Query expansion via Groq LLM
- ✅ Result re-ranking with AI scores
- ✅ Transparent explanations
- ✅ Attribute extraction from descriptions

### Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant FastAPI
    participant Groq
    participant FAISS
    participant MySQL
    participant Redis

    User->>Streamlit: Enter search query
    Streamlit->>FastAPI: POST /search
    FastAPI->>Groq: Expand query
    Groq-->>FastAPI: Enhanced query
    FastAPI->>FAISS: Vector similarity search
    FAISS-->>FastAPI: Top 50 candidates
    FastAPI->>MySQL: Filter by price/category
    MySQL-->>FastAPI: Filtered products
    FastAPI->>Groq: Re-rank top 10
    Groq-->>FastAPI: Ranked results + explanations
    FastAPI-->>Streamlit: Final results
    Streamlit-->>User: Display products
    
    User->>Streamlit: Click product
    Streamlit->>FastAPI: POST /events/click
    FastAPI->>Redis: Publish click event
    Redis->>MySQL: Store for learning
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 🔍 Search Products

**POST** `/search`

Search products using natural language with AI-powered ranking.

```json
{
  "query": "blue light glasses for office work",
  "category": "Eyeglasses",
  "min_price": 50.0,
  "max_price": 200.0,
  "min_rating": 4.0,
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "product_id": "LKEG-5678",
      "name": "Blue Light Blocking Glasses",
      "description": "Specialized blue light filtering glasses...",
      "price": 69.99,
      "category": "Eyeglasses",
      "rating": 4.3,
      "brand": "Lenskart",
      "relevance_score": 0.94,
      "semantic_score": 0.89,
      "behavioral_score": 0.12,
      "ai_explanation": "Perfect match for office work with blue light protection..."
    }
  ],
  "total_results": 20,
  "query_time_ms": 87,
  "expanded_query": "blue light blocking eyeglasses computer work digital eye strain"
}
```

#### 📊 Click Tracking

**POST** `/events/click`

Track user clicks for learning-based ranking (async).

```json
{
  "user_id": "user_Virat",
  "product_id": "LKEG-5678",
  "query": "blue light glasses",
  "position": 1
}
```

#### 🛒 Purchase Tracking

**POST** `/events/purchase`

Track purchases for conversion analysis (async).

```json
{
  "user_id": "user_Virat",
  "product_id": "LKEG-5678",
  "query": "blue light glasses",
  "price": 69.99
}
```

#### 📈 Analytics Summary

**POST** `/analytics/summary`

Get search performance metrics.

```json
{
  "user_id": "user_Virat",  // Optional: for personal analytics
  "time_range": "24h"        // 1h, 24h, 7d, 30d
}
```

**Response:**
```json
{
  "total_queries": 29,
  "total_searches": 101,
  "total_clicks": 41,
  "total_carts": 30,
  "total_purchases": 16,
  "overall_ctr": 40.59,
  "conversion_rate": 15.48,
  "zero_results": 11,
  "top_queries": [...],
  "poor_performers": [...]
}
```

#### ❤️ Health Check

**GET** `/health`

System health status.

```json
{
  "status": "healthy",
  "mysql": "connected",
  "faiss": "loaded",
  "redis": "connected",
  "timestamp": "2025-12-27T10:30:00Z"
}
```

---

## 🎛️ Configuration & Tuning

### Environment Variables

```env
# Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=lenskart_search
MYSQL_USER=root
MYSQL_PASSWORD=your_password

# AI Services
GROQ_API_KEY=your_groq_api_key

# Ranking Weights (sum must equal 1.0)
SEMANTIC_WEIGHT=0.4      # Vector similarity importance
CTR_WEIGHT=0.3           # Click-through rate importance
CONVERSION_WEIGHT=0.3    # Purchase conversion importance

# Search Parameters
MAX_RESULTS=50           # Maximum candidates before re-ranking
DEFAULT_LIMIT=10         # Default results per page

# Performance
CACHE_TTL=300           # Redis cache time-to-live (seconds)
BATCH_SIZE=100          # Ingestion batch size
```

### Tuning for Better Results

Based on analytics insights:

**If CTR is low (<10%):**
- Increase `SEMANTIC_WEIGHT` to 0.5
- Improve query expansion prompts
- Add more synonyms to domain knowledge

**If conversion is low (<3%):**
- Increase `CONVERSION_WEIGHT` to 0.4
- Review product descriptions
- Optimize pricing filters

**If many zero results:**
- Enable more aggressive query expansion
- Add fuzzy matching
- Expand product catalog coverage

---

## 📸 Screenshots Gallery

<table>
<tr>
<td width="50%">
<img src="docs/images/login-screen.png" alt="Login"/>
<p align="center"><b>Secure Login</b></p>
</td>
<td width="50%">
<img src="docs/images/search-interface.png" alt="Search"/>
<p align="center"><b>Natural Language Search</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/images/filters-expanded.png" alt="Filters"/>
<p align="center"><b>Dynamic Filters</b></p>
</td>
<td width="50%">
<img src="docs/images/search-results.png" alt="Results"/>
<p align="center"><b>AI-Powered Results</b></p>
</td>
</tr>
<tr>
<td width="50%">
<img src="docs/images/user-analytics.png" alt="Personal Analytics"/>
<p align="center"><b>Personal Analytics</b></p>
</td>
<td width="50%">
<img src="docs/images/global-analytics.png" alt="Global Analytics"/>
<p align="center"><b>Global Performance</b></p>
</td>
</tr>
</table>

---

## 🧪 Testing

```bash
# Run unit tests
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v

# Run with coverage
pytest --cov=backend tests/ --cov-report=html
```

---

## 📦 Project Structure

```
lenskart-ai-search/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── routers/             # API endpoints
│   │   └── services/            # Business logic
│   │       ├── ingestion_service.py
│   │       ├── search_service.py
│   │       ├── ranking_service.py
│   │       └── analytics_service.py
│   └── .env                     # Environment configuration
├── streamlit_app.py             # Streamlit frontend
├── scripts/
│   ├── setup_mysql_database.py  # Database initialization
│   └── ingest_products.py       # Product ingestion
├── data/
│   └── sample_products.json     # Sample product data
├── docs/
│   └── images/                  # Screenshots and diagrams
├── requirements_streamlit.txt   # Python dependencies
└── README.md                    # This file
```

---

## 🚧 Roadmap

- [ ] Multi-language support
- [ ] Image search capabilities
- [ ] A/B testing framework
- [ ] Real-time personalization
- [ ] Mobile app development
- [ ] Voice search integration

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Groq** for lightning-fast LLM inference
- **FAISS** by Meta AI for vector similarity search
- **Streamlit** for the amazing frontend framework
- **FastAPI** for the blazing-fast backend

---

<div align="center">

**Developed for Lenskart Assessment A1.2**

![Lenskart](https://www.lenskart.com/lenskart-logo.svg)

Made with ❤️ by **Your Name**

[GitHub](https://github.com/yourusername) • [LinkedIn](https://linkedin.com/in/yourusername) • [Email](mailto:your.email@example.com)

</div>
