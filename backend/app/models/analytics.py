"""
Analytics data models
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class QueryMetrics(BaseModel):
    """Metrics for a specific query"""
    query: str
    total_searches: int = 0
    total_clicks: int = 0
    total_carts: int = 0
    total_purchases: int = 0
    zero_results_count: int = 0
    ctr: float = 0.0
    conversion_rate: float = 0.0
    avg_dwell_time: float = 0.0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


class ProductMetrics(BaseModel):
    """Metrics for a specific product"""
    product_id: str
    title: Optional[str] = None
    appearances: int = 0
    views: int = 0

    carts: int = 0
    purchases: int = 0
    ctr: float = 0.0


class TimeSeriesMetric(BaseModel):
    """Metric value at a specific point in time"""
    timestamp: datetime
    value: float




class AnalyticsSummary(BaseModel):
    """Overall analytics summary"""
    total_queries: int
    total_searches: int
    total_clicks: int
    total_carts: int = 0
    total_conversions: int

    overall_ctr: float
    overall_conversion_rate: float
    zero_result_queries: int
    top_queries: List[QueryMetrics]
    poor_performing_queries: List[QueryMetrics]
    top_viewed_products: List[ProductMetrics] = []
    top_converted_products: List[ProductMetrics] = []
    ctr_over_time: List[TimeSeriesMetric] = []




class AnalyticsRequest(BaseModel):
    """Request for analytics data"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 50
    min_searches: int = 1  # Minimum searches to include in results

