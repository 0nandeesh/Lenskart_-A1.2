# User Guide & Requirement Justification

This document provides a detailed justification of how this project achieves the requirements specified in the Lenskart Assessment.

## 3. Functional Requirements

### 3.1 Product Ingestion Pipeline
The project implements a modular and reusable ingestion pipeline.
- **Location**: `backend/app/services/ingestion_service.py`
- **Normalization**: The pipeline normalizes fields like title, description, category, and attributes in `_create_embedding_text` (L41-59).
- **Embeddings**: Generates vector embeddings using the `vector_db` service (L26).
- **Storage**:
    - **Structured**: Data is stored in a relational database via `db.insert_product` (L20).
    - **Vector**: Embeddings are stored in ChromaDB via `vector_db.add_product` (L26).
- **Reusable**: The `IngestionService` exposes `ingest_product` and `ingest_products_batch` for automated ingestion.

### 3.2 Contextual Search Engine
The search system goes beyond keyword matching to provide a semantic, AI-powered experience.
- **Location**: `backend/app/services/search_service.py`
- **Natural Language**: Accepts raw queries and expands them using an LLM in `search` (L52-59).
- **Semantic Search**: Uses vector embeddings to find relevant products regardless of exact keyword matches (L71-75).
- **Structured Filters**: Applies filters (price, category, rating) via PostgreSQL/MySQL queries in `db.filter_products` (L61-66).
- **Ranking**: Combines semantic scores with behavior-based metrics in `ranking_service.rank_products` (L133).

### 3.3 User Behavior Tracking & Analytics
All user interactions are tracked asynchronously to ensure zero impact on search latency.
- **Location**: `backend/app/services/behavior_tracker.py`
- **Events**: Tracks `SEARCH`, `CLICK`, `ADD_TO_CART`, `PURCHASE`, and `BOUNCE` events.
- **Asynchronous**: Uses `asyncio.create_task` (L82, L86) and Redis Streams (L60-78) for non-blocking event ingestion.
- **Persistence**: Events are stored in the database for analytical processing and dashboard visualization.

### 3.4 Learning from User Behavior
The system implements a feedback loop where user actions directly influence ranking.
- **Location**: `backend/app/services/ranking_service.py`
- **Mechanism**: The `rank_products` method (L31-138) calculates a `behavior_score` based on:
    - **Boost**: Products with frequent clicks (CTR) and conversions are boosted.
    - **Penalty**: Products with high bounce rates are penalized (L84, L157).
- **Formula**: `Final Score = (α * semantic) + (β * behavior) + (γ * personalization)` (L39-50).

### 3.5 AI Integration
Multiple AI features are integrated using the Groq API (LLaMA models).
- **Location**: `backend/app/ai/groq_client.py`
- **Implemented Features**:
    - **Query Expansion**: Expands queries to include synonyms and context (L19-48).
    - **AI Re-ranking**: Re-ranks the top-K search results for higher precision (L50-115).
    - **Attribute Extraction**: Automatically extracts brand, material, and size from descriptions (L154-179).
    - **AI Explanations**: Generates "Why was this product shown?" explanations for users (L117-152).

---

## 4. Non-Functional Requirements

### 4.1 Architecture
The project follows a strict **layered architecture**:
- **API Layer**: `backend/app/main.py` and `backend/app/api/`
- **Service Layer**: `backend/app/services/` (Business logic)
- **Data Layer**: `backend/app/database/` (DB interactions)
- **AI Layer**: `backend/app/ai/` (LLM integration)

### 4.2 Scalability
- **Asynchronous Processing**: All tracking and background tasks are handled using `asyncio` and `Redis`, ensuring the main request thread is never blocked.
- **Vector Search**: Uses `ChromaDB`, which is designed to handle millions of vector embeddings efficiently.

### 4.3 Observability
- **Logging**: Detailed logging implemented throughout the services (e.g., `ranking_service.py:L11`, `search_service.py:L20`).
- **Metrics**: The system tracks telemetry like `search_time_ms` (L185) and event counts, which are surfaced in the Global Analytics dashboard.
