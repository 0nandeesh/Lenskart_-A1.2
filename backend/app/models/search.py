"""
Search request/response models
"""
from pydantic import BaseModel
from typing import Optional, List
from backend.app.models.product import ProductWithScore


class SearchRequest(BaseModel):
    """Search request"""
    query: str
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    limit: int = 20


class SearchResponse(BaseModel):
    """Search response"""
    query: str
    expanded_query: Optional[str] = None
    results: List[ProductWithScore]
    total_results: int
    search_time_ms: float
    filters_applied: dict

