"""
Product data models
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime


class ProductAttributes(BaseModel):
    """Product attributes"""
    brand: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    style: Optional[str] = None
    # Allow additional attributes
    extra: Optional[Dict[str, str]] = None


class Product(BaseModel):
    """Product model"""
    id: str
    title: str
    description: str
    category: str
    price: float = Field(gt=0)
    rating: float = Field(ge=0, le=5)
    attributes: ProductAttributes
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "prod_001",
                "title": "Classic Aviator Sunglasses",
                "description": "Timeless aviator style with UV protection and lightweight frame",
                "category": "Sunglasses",
                "price": 129.99,
                "rating": 4.5,
                "attributes": {
                    "brand": "Lenskart",
                    "size": "Medium",
                    "color": "Black",
                    "material": "Metal"
                }
            }
        }


class ProductWithScore(BaseModel):
    """Product with ranking score"""
    product: Product
    semantic_score: float
    behavior_score: float
    final_score: float
    ai_explanation: Optional[str] = None
    score_breakdown: Dict[str, float] = Field(default_factory=dict)

