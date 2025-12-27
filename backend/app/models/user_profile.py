"""
User profile models for personalized search
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class UserInteraction(BaseModel):
    """Represents a user-product interaction"""
    user_id: str
    product_id: str
    interaction_type: str  # 'search', 'click', 'cart', 'purchase'
    category: Optional[str] = None
    brand: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict] = None


class UserProfile(BaseModel):
    """
    Lightweight user profile for personalized search
    Contains only behavioral data, no sensitive personal information
    """
    user_id: str
    
    # Category preferences (category -> interaction count)
    preferred_categories: Dict[str, int] = Field(default_factory=dict)
    
    # Brand preferences (brand -> interaction count)
    preferred_brands: Dict[str, int] = Field(default_factory=dict)
    
    # Recent search queries (limited to last 50)
    search_history: List[str] = Field(default_factory=list)
    
    # Interaction counts
    total_searches: int = 0
    total_clicks: int = 0
    total_carts: int = 0
    total_purchases: int = 0
    
    # Recently interacted product IDs (for similarity matching)
    recent_product_ids: List[str] = Field(default_factory=list)
    
    # Profile metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def has_sufficient_history(self, min_interactions: int = 3) -> bool:
        """Check if user has enough interaction history for personalization"""
        total_interactions = (
            self.total_clicks + 
            self.total_carts + 
            self.total_purchases
        )
        return total_interactions >= min_interactions
    
    def get_top_categories(self, limit: int = 5) -> List[str]:
        """Get user's top preferred categories"""
        sorted_categories = sorted(
            self.preferred_categories.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [cat for cat, _ in sorted_categories[:limit]]
    
    def get_top_brands(self, limit: int = 5) -> List[str]:
        """Get user's top preferred brands"""
        sorted_brands = sorted(
            self.preferred_brands.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [brand for brand, _ in sorted_brands[:limit]]


class UserPreferenceScore(BaseModel):
    """Calculated preference score for a product"""
    product_id: str
    category_score: float = 0.0  # Score based on category affinity
    brand_score: float = 0.0  # Score based on brand affinity
    interaction_score: float = 0.0  # Score based on past interactions
    final_preference_score: float = 0.0  # Weighted combination
    
    def calculate_final_score(
        self,
        category_weight: float = 0.4,
        brand_weight: float = 0.3,
        interaction_weight: float = 0.3
    ) -> float:
        """Calculate weighted final preference score"""
        self.final_preference_score = (
            category_weight * self.category_score +
            brand_weight * self.brand_score +
            interaction_weight * self.interaction_score
        )
        return self.final_preference_score


class UserProfileSummary(BaseModel):
    """Summary of user profile for API responses"""
    user_id: str
    top_categories: List[str]
    top_brands: List[str]
    total_interactions: int
    total_searches: int = 0
    total_clicks: int = 0
    total_carts: int = 0
    total_purchases: int = 0
    has_personalization: bool
    ai_interest_summary: Optional[str] = None  # AI-generated summary
