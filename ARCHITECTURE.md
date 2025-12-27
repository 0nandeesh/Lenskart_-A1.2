# System Architecture

## Overview

The Lenskart AI Search Platform is a production-ready, modular system designed for contextual semantic search with learning-based ranking.

## Architecture Layers

### 1. Presentation Layer (Frontend)
- **Technology**: Next.js (React)
- **Purpose**: User interface for search and interaction
- **Components**:
  - Search bar with natural language input
  - Filter panel (category, price, rating)
  - Results grid with product cards
  - AI explanation display
  - User interaction tracking (clicks, carts, purchases)

### 2. API Layer (Backend)
- **Technology**: FastAPI
- **Purpose**: RESTful API endpoints
- **Endpoints**:
  - `/api/v1/search` - Main search endpoint
  - `/api/v1/products` - Product management
  - `/api/v1/events/*` - Behavior tracking
  - `/api/v1/health` - Health check

### 3. Service Layer
- **SearchService**: Orchestrates search flow
- **RankingService**: Implements learning-based ranking
- **BehaviorTracker**: Tracks and processes user events
- **IngestionService**: Handles product ingestion

### 4. AI Layer
- **Technology**: Groq API (LLaMA models)
- **Features**:
  - Query expansion
  - AI-based re-ranking
  - Explanation generation
  - Attribute extraction

### 5. Data Layer
- **PostgreSQL**: Structured product data and behavior metrics
- **FAISS**: Vector embeddings for semantic search
- **Redis**: Asynchronous event streaming (optional)

## Data Flow

### Search Flow
```
User Query
    ↓
Query Expansion (Groq AI)
    ↓
Semantic Search (FAISS)
    ↓
Structured Filtering (PostgreSQL)
    ↓
AI Re-ranking (Groq AI) [optional]
    ↓
Learning-based Ranking (Semantic + Behavior)
    ↓
AI Explanation Generation (Groq AI)
    ↓
Ranked Results with Explanations
```

### Behavior Tracking Flow
```
User Interaction (Click/Cart/Purchase)
    ↓
Event Published to Redis Stream (async)
    ↓
Event Stored in PostgreSQL (async)
    ↓
Background Processor Updates Metrics
    ↓
Metrics Update Product Behavior Scores
    ↓
Ranking Scores Updated (next search)
```

## Learning Mechanism

### Ranking Formula

```
final_score = (semantic_weight × semantic_score) + 
              (behavior_weight × behavior_score)

behavior_score = (ctr_weight × normalized_CTR) + 
                (conversion_weight × normalized_conversion_rate) - 
                (bounce_penalty × normalized_bounce_rate)
```

### Learning Components

1. **Semantic Score**: Vector similarity between query and product (0-1)
2. **Behavior Score**: Aggregated from user interactions
   - CTR (Click-Through Rate): clicks / searches
   - Conversion Rate: purchases / total interactions
   - Bounce Rate: bounces / total interactions

### Feedback Loop

- Products with high CTR → Boosted in rankings
- Products with high conversions → Boosted in rankings
- Products with high bounce rate → Penalized in rankings
- System continuously learns from user behavior

## Database Schema

### Products Table
- id (PK)
- title, description, category
- price, rating
- attributes (JSONB)
- image_url
- created_at

### Product Behavior Metrics Table
- product_id (PK, FK → products.id)
- total_clicks, total_searches, total_carts, total_purchases, total_bounces
- total_dwell_time, avg_dwell_time
- ctr, conversion_rate, bounce_rate
- last_updated

### Behavior Events Table
- event_id (PK)
- event_type, user_id, session_id
- product_id, query
- timestamp, dwell_time
- metadata (JSONB)

## Vector Database

- **Technology**: FAISS (Facebook AI Similarity Search)
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Dimension**: 384
- **Index Type**: L2 normalized (cosine similarity)
- **Storage**: On-disk index with in-memory mapping

## AI Integration (Groq)

### Query Expansion
- Input: User query
- Output: Expanded query with synonyms and context
- Model: LLaMA-3.1-70b-versatile

### AI Re-ranking
- Input: Top-K semantic results
- Output: Re-ranked by AI relevance
- Model: LLaMA-3.1-70b-versatile

### Explanation Generation
- Input: Query + Product
- Output: Natural language explanation
- Model: LLaMA-3.1-70b-versatile

## Scalability Considerations

### Horizontal Scaling
- Stateless API servers (FastAPI)
- Load balancer for distribution
- Shared PostgreSQL and Redis

### Vector DB Scaling
- FAISS: Single-node (suitable for <10M vectors)
- For larger scale: Consider Weaviate, Pinecone, or Qdrant

### Caching Strategy
- Redis for:
  - Query result caching
  - Behavior metrics caching
  - Session management

## Security

### Current State
- Basic CORS configuration
- Input validation via Pydantic
- SQL injection protection (parameterized queries)

### Production Recommendations
- Authentication/Authorization (JWT, OAuth)
- Rate limiting
- API key management
- Input sanitization
- HTTPS/TLS
- Secrets management

## Monitoring & Observability

### Metrics to Track
- Query latency (p50, p95, p99)
- Search result quality (CTR, conversion)
- AI API latency and costs
- Database query performance
- Event processing throughput

### Logging
- Structured logging (JSON)
- Request/response logging
- Error tracking
- Behavior event logging

## Deployment

### Development
- Local PostgreSQL
- Local FAISS index
- Local Redis (optional)
- Groq API (cloud)

### Production
- Managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Distributed vector DB (if needed)
- Managed Redis (AWS ElastiCache, Google Cloud Memorystore)
- Container orchestration (Kubernetes, Docker Compose)
- CI/CD pipeline

