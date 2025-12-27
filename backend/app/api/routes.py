"""
API routes for the search platform
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from backend.app.models.search import SearchRequest, SearchResponse
from backend.app.models.product import Product
from backend.app.models.analytics import AnalyticsRequest, AnalyticsSummary, QueryMetrics
from backend.app.services.search_service import search_service
from backend.app.services.behavior_tracker import behavior_tracker
from backend.app.services.analytics_service import analytics_service
from backend.app.models.behavior import EventType
from datetime import datetime
import uuid

router = APIRouter()


def get_or_create_session_id(session_id: Optional[str] = None) -> str:
    """Get or create session ID"""
    if not session_id:
        return str(uuid.uuid4())
    return session_id


@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """
    Perform contextual search
    
    - **query**: Natural language search query
    - **category**: Optional category filter
    - **min_price**: Optional minimum price filter
    - **max_price**: Optional maximum price filter
    - **min_rating**: Optional minimum rating filter
    - **limit**: Maximum number of results (default: 20)
    """
    try:
        print(f"DEBUG: Search request received: {request}")
        session_id = get_or_create_session_id(x_session_id)
        return await search_service.search(request, session_id, user_id=x_user_id)
    except Exception as e:
        import traceback
        print(f"DEBUG: Error in search route: {e}")
        print(traceback.format_exc())
        raise e


@router.post("/products", response_model=dict)
async def create_product(product: Product):
    """Create or update a product"""
    from backend.app.services.ingestion_service import ingestion_service
    result = await ingestion_service.ingest_product(product)
    return {"status": "success", "product_id": result}


@router.post("/products/batch", response_model=dict)
async def create_products_batch(products: list[Product]):
    """Create or update multiple products"""
    from backend.app.services.ingestion_service import ingestion_service
    results = await ingestion_service.ingest_products_batch(products)
    return {"status": "success", "count": len(results), "product_ids": results}


@router.post("/events/click")
async def track_click(
    request: dict,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """Track product click event"""
    product_id = request.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    session_id = get_or_create_session_id(x_session_id)
    await behavior_tracker.track_event(
        event_type=EventType.CLICK,
        session_id=session_id,
        product_id=product_id,
        user_id=x_user_id
    )
    return {"status": "success"}


@router.post("/events/add-to-cart")
async def track_add_to_cart(
    request: dict,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """Track add to cart event"""
    product_id = request.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    session_id = get_or_create_session_id(x_session_id)
    await behavior_tracker.track_event(
        event_type=EventType.ADD_TO_CART,
        session_id=session_id,
        product_id=product_id,
        user_id=x_user_id
    )
    return {"status": "success"}


@router.post("/events/purchase")
async def track_purchase(
    request: dict,
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """Track purchase event"""
    product_id = request.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    session_id = get_or_create_session_id(x_session_id)
    await behavior_tracker.track_event(
        event_type=EventType.PURCHASE,
        session_id=session_id,
        product_id=product_id,
        user_id=x_user_id
    )
    return {"status": "success"}


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a product by ID"""
    from backend.app.database.mysql_db import db
    product = await db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@router.get("/ping")
async def ping():
    return {"status": "pong"}


# User profile endpoints
@router.get("/users/{user_id}/myprofile")
async def get_user_profile(user_id: str):
    """Get user profile summary"""

    from backend.app.services.user_profile_service import user_profile_service
    summary = await user_profile_service.get_profile_summary(user_id)
    return summary


@router.get("/users/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """Get user preference details"""
    from backend.app.services.user_profile_service import user_profile_service
    from backend.app.services.personalization_service import personalization_service
    
    profile = await user_profile_service.get_or_create_profile(user_id)
    summary = await user_profile_service.get_profile_summary(user_id)
    
    # Try to get AI interest summary
    ai_summary = None
    if profile.has_sufficient_history():
        ai_summary = await personalization_service.summarize_user_interests(profile)
    
    return {
        "user_id": user_id,
        "top_categories": summary.top_categories,
        "top_brands": summary.top_brands,
        "total_interactions": summary.total_interactions,
        "has_personalization": summary.has_personalization,
        "ai_interest_summary": ai_summary,
        "recent_searches": profile.search_history[:10]
    }


@router.get("/users/{user_id}/recent-activity")
async def get_recent_activity(user_id: str):
    """Get summarized recent activity for the dashboard"""
    from backend.app.database.mysql_db import db
    
    recent_searches = await db.get_recent_searches(user_id, limit=5)
    viewed = await db.get_user_interactions(user_id, interaction_type='click', limit=10)
    carts = await db.get_user_interactions(user_id, interaction_type='add_to_cart', limit=10)
    
    return {
        "recent_searches": recent_searches,
        "recently_viewed": viewed,
        "added_to_cart": carts
    }


@router.get("/users/{user_id}/interactions")
async def get_user_interactions(user_id: str, limit: int = 50):
    """Get recent interactions for a user"""
    from backend.app.database.mysql_db import db
    interactions = await db.get_user_interactions(user_id, limit=limit)
    return interactions



# Analytics endpoints
@router.post("/analytics/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(request: AnalyticsRequest):
    """
    Get analytics summary with top queries and poor performers
    
    - **start_date**: Optional start date filter (ISO format)
    - **end_date**: Optional end date filter (ISO format)
    - **limit**: Maximum number of queries to return (default: 50)
    - **min_searches**: Minimum searches to include a query (default: 1)
    """
    return await analytics_service.get_analytics_summary(
        start_date=request.start_date,
        end_date=request.end_date,
        limit=request.limit
    )


@router.get("/analytics/queries", response_model=list[QueryMetrics])
async def get_query_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_searches: int = 1
):
    """
    Get query metrics for all queries
    
    - **start_date**: Optional start date filter (ISO format: YYYY-MM-DDTHH:MM:SS)
    - **end_date**: Optional end date filter (ISO format: YYYY-MM-DDTHH:MM:SS)
    - **min_searches**: Minimum searches to include a query (default: 1)
    """
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    return await analytics_service.get_query_metrics(
        start_date=start,
        end_date=end,
        min_searches=min_searches
    )


@router.get("/analytics/zero-results", response_model=list[QueryMetrics])
async def get_zero_result_queries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get queries that resulted in zero clicks (no results)
    
    - **start_date**: Optional start date filter (ISO format)
    - **end_date**: Optional end date filter (ISO format)
    """
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    return await analytics_service.get_zero_result_queries(
        start_date=start,
        end_date=end
    )

