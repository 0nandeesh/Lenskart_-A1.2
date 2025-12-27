"""
User behavior tracking models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """User behavior event types"""
    SEARCH = "search"
    CLICK = "click"
    ADD_TO_CART = "add_to_cart"
    PURCHASE = "purchase"
    BOUNCE = "bounce"  # Quick exit without interaction


class BehaviorEvent(BaseModel):
    """User behavior event"""
    event_id: str
    event_type: EventType
    user_id: Optional[str] = None
    session_id: str
    product_id: Optional[str] = None
    query: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    dwell_time: Optional[float] = None  # seconds
    metadata: Optional[dict] = None


class ProductBehaviorMetrics(BaseModel):
    """Aggregated behavior metrics for a product"""
    product_id: str
    total_clicks: int = 0
    total_searches: int = 0
    total_carts: int = 0
    total_purchases: int = 0
    total_bounces: int = 0
    total_dwell_time: float = 0.0
    avg_dwell_time: float = 0.0
    ctr: float = 0.0  # Click-through rate
    conversion_rate: float = 0.0
    bounce_rate: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.now)

