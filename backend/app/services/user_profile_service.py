"""
User profile service for personalized search
"""
from typing import Optional, Dict, List
from datetime import datetime
import json
from backend.app.models.user_profile import (
    UserProfile, UserInteraction, UserPreferenceScore, UserProfileSummary
)
from backend.app.models.product import Product
from backend.app.database.mysql_db import db
from backend.app.config import settings
import logging

logger = logging.getLogger(__name__)


class UserProfileService:
    """Service for managing user profiles and calculating preference scores"""
    
    def __init__(self):
        self.category_weight = settings.CATEGORY_AFFINITY_WEIGHT
        self.brand_weight = settings.BRAND_AFFINITY_WEIGHT
        self.interaction_weight = settings.INTERACTION_HISTORY_WEIGHT
        self.min_interactions = settings.MIN_INTERACTIONS_FOR_PERSONALIZATION
        self.max_search_history = settings.MAX_SEARCH_HISTORY
        self.max_recent_products = settings.MAX_RECENT_PRODUCTS
    
    async def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get existing profile or create a new one"""
        try:
            profile_data = await db.get_user_profile(user_id)
            
            if profile_data:
                # Parse JSON fields
                return UserProfile(
                    user_id=profile_data['user_id'],
                    preferred_categories=json.loads(profile_data.get('preferred_categories', '{}')),
                    preferred_brands=json.loads(profile_data.get('preferred_brands', '{}')),
                    search_history=json.loads(profile_data.get('search_history', '[]')),
                    total_searches=profile_data.get('total_searches', 0),
                    total_clicks=profile_data.get('total_clicks', 0),
                    total_carts=profile_data.get('total_carts', 0),
                    total_purchases=profile_data.get('total_purchases', 0),
                    recent_product_ids=json.loads(profile_data.get('recent_product_ids', '[]')),
                    created_at=profile_data.get('created_at', datetime.now()),
                    last_updated=profile_data.get('last_updated', datetime.now())
                )
            else:
                # Create new profile
                await db.create_user_profile(user_id)
                return UserProfile(user_id=user_id)
        except Exception as e:
            logger.error(f"Error getting/creating profile for user {user_id}: {e}")
            # Return empty profile on error
            return UserProfile(user_id=user_id)
    
    async def update_profile_from_event(
        self,
        user_id: str,
        event_type: str,
        product: Optional[Product] = None,
        query: Optional[str] = None
    ):
        """Update user profile based on behavior event"""
        try:
            profile = await self.get_or_create_profile(user_id)
            
            # Update search history
            if query and event_type == 'search':
                if query not in profile.search_history:
                    profile.search_history.insert(0, query)
                    # Keep only recent searches
                    profile.search_history = profile.search_history[:self.max_search_history]
                profile.total_searches += 1
            
            # Update interaction counts and preferences
            if product:
                category = product.category
                brand = product.attributes.brand if hasattr(product.attributes, 'brand') else None
                
                # Update category preferences
                if category:
                    profile.preferred_categories[category] = profile.preferred_categories.get(category, 0) + 1
                
                # Update brand preferences
                if brand:
                    profile.preferred_brands[brand] = profile.preferred_brands.get(brand, 0) + 1
                
                # Update recent products
                if product.id not in profile.recent_product_ids:
                    profile.recent_product_ids.insert(0, product.id)
                    profile.recent_product_ids = profile.recent_product_ids[:self.max_recent_products]
                
                # Update interaction counts
                if event_type == 'click':
                    profile.total_clicks += 1
                elif event_type == 'add_to_cart':
                    profile.total_carts += 1
                elif event_type == 'purchase':
                    profile.total_purchases += 1
                
                # Store interaction in database
                await db.add_user_interaction(
                    user_id=user_id,
                    product_id=product.id,
                    interaction_type=event_type,
                    category=category,
                    brand=brand
                )
            
            # Save updated profile
            profile_data = {
                'preferred_categories': profile.preferred_categories,
                'preferred_brands': profile.preferred_brands,
                'search_history': profile.search_history,
                'total_searches': profile.total_searches,
                'total_clicks': profile.total_clicks,
                'total_carts': profile.total_carts,
                'total_purchases': profile.total_purchases,
                'recent_product_ids': profile.recent_product_ids
            }
            await db.update_user_profile(user_id, profile_data)
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
    
    async def calculate_user_preference_score(
        self,
        user_id: str,
        product: Product
    ) -> UserPreferenceScore:
        """Calculate preference score for a product based on user profile"""
        try:
            profile = await self.get_or_create_profile(user_id)
            
            # Check if user has sufficient history
            if not profile.has_sufficient_history(self.min_interactions):
                return UserPreferenceScore(
                    product_id=product.id,
                    category_score=0.0,
                    brand_score=0.0,
                    interaction_score=0.0,
                    final_preference_score=0.0
                )
            
            score = UserPreferenceScore(product_id=product.id)
            
            # Calculate category affinity score
            if product.category in profile.preferred_categories:
                # Normalize by max category count
                max_category_count = max(profile.preferred_categories.values()) if profile.preferred_categories else 1
                score.category_score = profile.preferred_categories[product.category] / max_category_count
            
            # Calculate brand affinity score
            brand = product.attributes.brand if hasattr(product.attributes, 'brand') else None
            if brand and brand in profile.preferred_brands:
                max_brand_count = max(profile.preferred_brands.values()) if profile.preferred_brands else 1
                score.brand_score = profile.preferred_brands[brand] / max_brand_count
            
            # Calculate interaction history score
            if product.id in profile.recent_product_ids:
                # Score based on recency (more recent = higher score)
                position = profile.recent_product_ids.index(product.id)
                # Exponential decay: score = e^(-position/20)
                import math
                score.interaction_score = math.exp(-position / 20.0)
            
            # Calculate final weighted score
            score.calculate_final_score(
                category_weight=self.category_weight,
                brand_weight=self.brand_weight,
                interaction_weight=self.interaction_weight
            )
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating preference score for user {user_id}, product {product.id}: {e}")
            return UserPreferenceScore(
                product_id=product.id,
                category_score=0.0,
                brand_score=0.0,
                interaction_score=0.0,
                final_preference_score=0.0
            )
    
    async def get_profile_summary(self, user_id: str) -> UserProfileSummary:
        """Get a summary of user profile for API responses"""
        try:
            profile = await self.get_or_create_profile(user_id)
            
            total_interactions = (
                profile.total_clicks +
                profile.total_carts +
                profile.total_purchases
            )
            
            return UserProfileSummary(
                user_id=user_id,
                top_categories=profile.get_top_categories(5),
                top_brands=profile.get_top_brands(5),
                total_interactions=total_interactions,
                total_searches=profile.total_searches,
                total_clicks=profile.total_clicks,
                total_carts=profile.total_carts,
                total_purchases=profile.total_purchases,
                has_personalization=profile.has_sufficient_history(self.min_interactions)
            )
        except Exception as e:
            logger.error(f"Error getting profile summary for user {user_id}: {e}")
            return UserProfileSummary(
                user_id=user_id,
                top_categories=[],
                top_brands=[],
                total_interactions=0,
                has_personalization=False
            )
    
    def detect_cold_start(self, profile: UserProfile) -> bool:
        """Detect if user is in cold-start state (insufficient history)"""
        return not profile.has_sufficient_history(self.min_interactions)


# Global instance
user_profile_service = UserProfileService()
