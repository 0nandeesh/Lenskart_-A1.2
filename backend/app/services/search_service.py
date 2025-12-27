"""
Contextual search service
"""
import time
from typing import List, Optional
from backend.app.models.search import SearchRequest, SearchResponse
from backend.app.models.product import ProductWithScore
from backend.app.database.vector_db import vector_db
from backend.app.database.mysql_db import db
from backend.app.services.ranking_service import ranking_service
from backend.app.services.behavior_tracker import behavior_tracker
from backend.app.ai.groq_client import get_groq_client
from backend.app.config import settings
import uuid



import logging

logger = logging.getLogger(__name__)

class SearchService:
    """Main search service orchestrating all components"""
    
    async def search(
        self,
        request: SearchRequest,
        session_id: str,
        user_id: Optional[str] = None  # Optional user ID for personalization
    ) -> SearchResponse:
        """
        Perform contextual search with:
        1. Query expansion (AI)
        2. Semantic search (vector DB)
        3. Structured filtering (PostgreSQL)
        4. Learning-based ranking
        5. AI re-ranking (optional, for top-K)
        6. AI explanations
        """
        try:
            start_time = time.time()
            
            # Track search event with user_id
            from backend.app.models.behavior import EventType
            await behavior_tracker.track_event(
                event_type=EventType.SEARCH,
                session_id=session_id,
                query=request.query,
                user_id=user_id
            )
            
            # Step 1: Query expansion using Groq
            expanded_query = request.query
            try:
                groq = get_groq_client()
                expanded_query = groq.expand_query(request.query)
            except Exception as e:
                logger.warning(f"Query expansion failed: {e}")
            
            # Step 2: Apply structured filters to get candidate product IDs
            filtered_ids = await db.filter_products(
                category=request.category,
                min_price=request.min_price,
                max_price=request.max_price,
                min_rating=request.min_rating
            )
            
            # Step 3: Semantic search in vector DB (with filter)
            # If filtered_ids is empty list, search all products (pass None)
            product_ids_filter = filtered_ids if filtered_ids else None
            semantic_results = vector_db.search(
                query=expanded_query,
                k=settings.TOP_K_FOR_AI_RERANK,
                product_ids_filter=product_ids_filter
            )
            
            if not semantic_results:
                return SearchResponse(
                    query=request.query,
                    expanded_query=expanded_query,
                    results=[],
                    total_results=0,
                    search_time_ms=(time.time() - start_time) * 1000,
                    filters_applied={
                        "category": request.category,
                        "min_price": request.min_price,
                        "max_price": request.max_price,
                        "min_rating": request.min_rating
                    }
                )
            
            # Step 4: Get full product objects
            product_ids = [pid for pid, _ in semantic_results]
            products = await db.get_products_by_ids(product_ids)
            
            # Create mapping: product_id -> (product, semantic_score)
            id_to_product = {p.id: p for p in products}
            products_with_scores = [
                (id_to_product[pid], score)
                for pid, score in semantic_results
                if pid in id_to_product
            ]
            
            # Step 5: AI-based re-ranking (optional, for top results)
            if len(products_with_scores) > 10:
                try:
                    groq = get_groq_client()
                    # Prepare products for AI
                    products_for_ai = [
                        {
                            "id": p.id,
                            "title": p.title,
                            "description": p.description,
                            "category": p.category,
                            "price": p.price,
                            "rating": p.rating
                        }
                        for p, _ in products_with_scores[:settings.TOP_K_FOR_AI_RERANK]
                    ]
                    
                    # AI re-rank
                    reranked = groq.rerank_results(expanded_query, products_for_ai)
                    
                    # Update order based on AI ranking
                    reranked_ids = {p['id']: i for i, p in enumerate(reranked)}
                    products_with_scores.sort(
                        key=lambda x: reranked_ids.get(x[0].id, 999)
                    )
                except Exception as e:
                    logger.warning(f"AI re-ranking failed: {e}")
            
            # Step 6: Learning-based ranking (with personalization)
            ranked_results = await ranking_service.rank_products(products_with_scores, user_id=user_id)
            
            # Step 7: Limit results
            ranked_results = ranked_results[:request.limit]
            
            # Step 7.5: Track product impressions (total_searches) in background
            async def track_impressions(results: List[ProductWithScore]):
                for res in results:
                    try:
                        # Get current metrics or initialize
                        metrics = await db.get_behavior_metrics(res.product.id)
                        if not metrics:
                            metrics = {
                                'total_clicks': 0,
                                'total_searches': 0,
                                'total_carts': 0,
                                'total_purchases': 0,
                                'total_bounces': 0,
                                'total_dwell_time': 0.0,
                                'avg_dwell_time': 0.0,
                                'ctr': 0.0,
                                'conversion_rate': 0.0,
                                'bounce_rate': 0.0
                            }
                        metrics['total_searches'] += 1
                        await db.update_behavior_metrics(res.product.id, metrics)
                    except Exception as e:
                        logger.warning(f"Failed to track impression for {res.product.id}: {e}")

            import asyncio
            asyncio.create_task(track_impressions(ranked_results))

            
            # Step 8: Generate AI explanations for top results
            try:
                groq = get_groq_client()
                for result in ranked_results[:5]:  # Explain top 5
                    explanation = groq.generate_explanation(
                        request.query,
                        {
                            "id": result.product.id,
                            "title": result.product.title,
                            "description": result.product.description,
                            "category": result.product.category,
                            "price": result.product.price,
                            "rating": result.product.rating
                        }
                    )
                    result.ai_explanation = explanation
            except Exception as e:
                logger.warning(f"Explanation generation failed: {e}")
            
            search_time = (time.time() - start_time) * 1000
            
            return SearchResponse(
                query=request.query,
                expanded_query=expanded_query,
                results=ranked_results,
                total_results=len(ranked_results),
                search_time_ms=search_time,
                filters_applied={
                    "category": request.category,
                    "min_price": request.min_price,
                    "max_price": request.max_price,
                    "min_rating": request.min_rating
                }
            )
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            raise e


# Global instance
search_service = SearchService()

