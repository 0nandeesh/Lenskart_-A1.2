"""
AI-assisted personalization service using Groq LLaMA models
"""
from typing import Optional, Dict, List
from backend.app.models.user_profile import UserProfile
from backend.app.models.product import Product
from backend.app.ai.groq_client import get_groq_client
from backend.app.config import settings
import logging

logger = logging.getLogger(__name__)


class PersonalizationService:
    """Service for AI-assisted personalization (optional enhancement)"""
    
    def __init__(self):
        self.groq_available = settings.GROQ_API_KEY is not None
    
    async def summarize_user_interests(self, profile: UserProfile) -> Optional[str]:
        """
        Use Groq LLaMA to generate a natural language summary of user interests
        This is optional and gracefully degrades if Groq is unavailable
        """
        if not self.groq_available:
            return None
        
        try:
            groq = get_groq_client()
            
            # Prepare profile data for AI
            top_categories = profile.get_top_categories(5)
            top_brands = profile.get_top_brands(5)
            recent_searches = profile.search_history[:10]
            
            prompt = f"""Analyze this user's shopping behavior and generate a brief summary of their interests and preferences.

User Profile:
- Top Categories: {', '.join(top_categories) if top_categories else 'None yet'}
- Top Brands: {', '.join(top_brands) if top_brands else 'None yet'}
- Recent Searches: {', '.join(recent_searches) if recent_searches else 'None yet'}
- Total Interactions: {profile.total_clicks + profile.total_carts + profile.total_purchases}

Generate a 2-3 sentence summary of this user's shopping interests and preferences."""
            
            response = groq.client.chat.completions.create(
                model=groq.model,
                messages=[
                    {"role": "system", "content": "You are a user behavior analyst. Provide concise, insightful summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.warning(f"AI interest summarization failed: {e}")
            return None
    
    async def refine_preference_signals(
        self,
        profile: UserProfile,
        products: List[Product]
    ) -> Optional[Dict[str, float]]:
        """
        Use AI to refine preference scores for products
        Returns a dict of product_id -> refined_score
        """
        if not self.groq_available or not products:
            return None
        
        try:
            groq = get_groq_client()
            
            # Prepare data
            top_categories = profile.get_top_categories(3)
            top_brands = profile.get_top_brands(3)
            
            products_text = "\n".join([
                f"- ID: {p.id}, Title: {p.title}, Category: {p.category}, "
                f"Brand: {p.attributes.brand if hasattr(p.attributes, 'brand') else 'N/A'}"
                for p in products[:10]  # Limit to top 10 for API efficiency
            ])
            
            prompt = f"""Given a user's preferences and a list of products, rate how well each product matches the user's interests on a scale of 0.0 to 1.0.

User Preferences:
- Preferred Categories: {', '.join(top_categories)}
- Preferred Brands: {', '.join(top_brands)}

Products:
{products_text}

Return a JSON object with product IDs as keys and preference scores (0.0-1.0) as values.
Example: {{"product_1": 0.85, "product_2": 0.65}}"""
            
            response = groq.client.chat.completions.create(
                model=groq.model,
                messages=[
                    {"role": "system", "content": "You are a product recommendation expert. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=300,
                response_format={"type": "json_object"}
            )
            
            import json
            refined_scores = json.loads(response.choices[0].message.content)
            return refined_scores
            
        except Exception as e:
            logger.warning(f"AI preference refinement failed: {e}")
            return None
    
    async def predict_user_preferences(
        self,
        profile: UserProfile,
        product: Product
    ) -> Optional[float]:
        """
        Use AI to predict user preference for a specific product
        Returns a score between 0.0 and 1.0, or None if unavailable
        """
        if not self.groq_available:
            return None
        
        try:
            groq = get_groq_client()
            
            top_categories = profile.get_top_categories(3)
            top_brands = profile.get_top_brands(3)
            recent_searches = profile.search_history[:5]
            
            prompt = f"""Predict how interested this user would be in the following product, on a scale of 0.0 to 1.0.

User Profile:
- Preferred Categories: {', '.join(top_categories)}
- Preferred Brands: {', '.join(top_brands)}
- Recent Searches: {', '.join(recent_searches)}

Product:
- Title: {product.title}
- Category: {product.category}
- Description: {product.description[:200]}...
- Price: ${product.price}
- Rating: {product.rating}

Return only a single number between 0.0 and 1.0 representing the preference score."""
            
            response = groq.client.chat.completions.create(
                model=groq.model,
                messages=[
                    {"role": "system", "content": "You are a product recommendation expert. Respond with only a number."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            score = float(score_text)
            # Clamp to [0, 1]
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"AI preference prediction failed: {e}")
            return None


# Global instance
personalization_service = PersonalizationService()
