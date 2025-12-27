"""
Learning-based ranking service with personalization
"""
from typing import List, Dict, Optional
from backend.app.config import settings
from backend.app.database.mysql_db import db
from backend.app.models.product import Product, ProductWithScore
from backend.app.services.user_profile_service import user_profile_service
import logging

logger = logging.getLogger(__name__)


class RankingService:
    """
    Learning-based ranking service that combines:
    - Semantic similarity scores
    - User behavior metrics (CTR, conversions, bounce rate)
    - User personalization (category/brand affinity, interaction history)
    """
    
    def __init__(self):
        self.semantic_weight = settings.SEMANTIC_WEIGHT
        self.behavior_weight = settings.BEHAVIOR_WEIGHT
        self.user_preference_weight = settings.USER_PREFERENCE_WEIGHT
        self.ctr_weight = settings.CTR_WEIGHT
        self.conversion_weight = settings.CONVERSION_WEIGHT
        self.bounce_penalty = settings.BOUNCE_PENALTY
        self.enable_personalization = settings.ENABLE_PERSONALIZATION
    
    async def rank_products(
        self,
        products_with_semantic_scores: List[tuple],  # (product, semantic_score)
        user_id: Optional[str] = None  # Optional user ID for personalization
    ) -> List[ProductWithScore]:
        """
        Rank products using semantic + behavior + personalization scores
        
        Ranking Formula:
        final_score = (α * semantic_score) + 
                     (β * behavior_score) +
                     (γ * user_preference_score)
        
        behavior_score = (ctr_weight * normalized_ctr) +
                        (conversion_weight * normalized_conversion_rate) -
                        (bounce_penalty * normalized_bounce_rate)
        
        user_preference_score = calculated from user profile (category/brand affinity, interactions)
        If user has insufficient history (cold-start), γ = 0 (personalization disabled)
        """
        results = []
        
        # Check if personalization should be applied
        use_personalization = False
        user_preference_weight = 0.0
        
        if self.enable_personalization and user_id:
            try:
                profile = await user_profile_service.get_or_create_profile(user_id)
                # Check for cold-start
                if not user_profile_service.detect_cold_start(profile):
                    use_personalization = True
                    user_preference_weight = self.user_preference_weight
                    logger.info(f"Personalization enabled for user {user_id}")
                else:
                    logger.info(f"Cold-start detected for user {user_id}, using non-personalized ranking")
            except Exception as e:
                logger.warning(f"Error checking personalization for user {user_id}: {e}")
        
        for product, semantic_score in products_with_semantic_scores:
            # Get behavior metrics
            metrics = await db.get_behavior_metrics(product.id)
            
            if metrics:
                # Normalize metrics to [0, 1]
                ctr = float(metrics.get('ctr', 0.0))
                conversion_rate = float(metrics.get('conversion_rate', 0.0))
                bounce_rate = float(metrics.get('bounce_rate', 0.0))
                
                # Clamp to [0, 1]
                ctr = min(1.0, ctr)
                conversion_rate = min(1.0, conversion_rate)
                bounce_rate = min(1.0, bounce_rate)
                
                # Calculate behavior score
                behavior_score = (
                    self.ctr_weight * ctr +
                    self.conversion_weight * conversion_rate -
                    self.bounce_penalty * bounce_rate
                )
                # Clamp to [0, 1]
                behavior_score = max(0.0, min(1.0, behavior_score))
            else:
                # No behavior data yet, use neutral score
                behavior_score = 0.5
                ctr = 0.0
                conversion_rate = 0.0
                bounce_rate = 0.0
            
            # Calculate user preference score
            user_preference_score = 0.0
            if use_personalization:
                try:
                    pref_score = await user_profile_service.calculate_user_preference_score(
                        user_id, product
                    )
                    user_preference_score = pref_score.final_preference_score
                except Exception as e:
                    logger.warning(f"Error calculating preference score: {e}")
            
            # Calculate final score with personalization
            final_score = (
                self.semantic_weight * semantic_score +
                self.behavior_weight * behavior_score +
                user_preference_weight * user_preference_score
            )
            
            # Create score breakdown
            score_breakdown = {
                "semantic_score": semantic_score,
                "behavior_score": behavior_score,
                "user_preference_score": user_preference_score,
                "ctr": ctr,
                "conversion_rate": conversion_rate,
                "bounce_rate": bounce_rate,
                "semantic_weight": self.semantic_weight,
                "behavior_weight": self.behavior_weight,
                "user_preference_weight": user_preference_weight,
                "personalization_enabled": use_personalization
            }
            
            results.append(ProductWithScore(
                product=product,
                semantic_score=semantic_score,
                behavior_score=behavior_score,
                final_score=final_score,
                score_breakdown=score_breakdown
            ))
        
        # Sort by final score (descending)
        results.sort(key=lambda x: x.final_score, reverse=True)
        
        return results
    
    def get_ranking_explanation(self) -> str:
        """Get explanation of ranking formula"""
        return f"""
Ranking Formula:
================

Final Score = (Semantic Weight × Semantic Score) + (Behavior Weight × Behavior Score)

Where:
- Semantic Score: Vector similarity between query and product (0-1)
- Behavior Score = (CTR Weight × CTR) + (Conversion Weight × Conversion Rate) - (Bounce Penalty × Bounce Rate)

Current Weights:
- Semantic Weight: {self.semantic_weight}
- Behavior Weight: {self.behavior_weight}
- CTR Weight: {self.ctr_weight}
- Conversion Weight: {self.conversion_weight}
- Bounce Penalty: {self.bounce_penalty}

Learning Mechanism:
- Products with high CTR get boosted
- Products with high conversion rates get boosted
- Products with high bounce rates get penalized
- System learns from user interactions over time
"""


# Global instance
ranking_service = RankingService()

