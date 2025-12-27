"""
Groq API client for LLaMA models
"""
from typing import Optional, List, Dict
from groq import Groq
from backend.app.config import settings
import json


class GroqClient:
    """Client for Groq API with LLaMA models"""
    
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment")
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
    
    def expand_query(self, query: str) -> str:
        """
        Expand search query using AI to improve semantic matching
        """
        prompt = f"""You are a search query expansion assistant. Given a user's search query, generate an expanded version that includes synonyms, related terms, and context that would help find relevant products.

Original query: {query}

Generate an expanded query that:
1. Includes synonyms and related terms
2. Adds context about what the user might be looking for
3. Keeps the core intent intact

Expanded query:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful search assistant that expands queries to improve product discovery."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            expanded = response.choices[0].message.content.strip()
            return expanded if expanded else query
        except Exception as e:
            print(f"Error expanding query: {e}")
            return query
    
    def rerank_results(
        self,
        query: str,
        products: List[Dict]
    ) -> List[Dict]:
        """
        AI-based re-ranking of top-K search results
        Products should have: id, title, description, category, price, rating
        """
        if not products:
            return products
        
        # Format products for AI
        products_text = "\n".join([
            f"{i+1}. ID: {p['id']}, Title: {p['title']}, "
            f"Description: {p['description'][:100]}..., "
            f"Category: {p['category']}, Price: ${p['price']}, Rating: {p['rating']}"
            for i, p in enumerate(products)
        ])
        
        prompt = f"""You are a product ranking assistant. Given a user query and a list of products, rank them by relevance to the query.

User Query: {query}

Products:
{products_text}

Return a JSON object with a "ranked_ids" array containing product IDs in order of relevance (most relevant first). Only include IDs that are relevant to the query.

Example format: {{"ranked_ids": ["id1", "id2", "id3"]}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product ranking assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            ranked_ids = result.get("ranked_ids", [])
            
            # Reorder products based on AI ranking
            id_to_product = {p['id']: p for p in products}
            ranked_products = []
            seen_ids = set()
            
            # Add ranked products
            for pid in ranked_ids:
                if pid in id_to_product:
                    ranked_products.append(id_to_product[pid])
                    seen_ids.add(pid)
            
            # Add remaining products
            for p in products:
                if p['id'] not in seen_ids:
                    ranked_products.append(p)
            
            return ranked_products
        except Exception as e:
            print(f"Error reranking: {e}")
            return products
    
    def generate_explanation(
        self,
        query: str,
        product: Dict
    ) -> str:
        """
        Generate AI explanation for why a product was shown for a query
        """
        prompt = f"""Explain why this product is relevant to the user's search query. Be concise (1-2 sentences).

User Query: {query}

Product:
- Title: {product['title']}
- Description: {product['description']}
- Category: {product['category']}
- Price: ${product['price']}
- Rating: {product['rating']}

Explanation:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that explains product relevance to search queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=150
            )
            explanation = response.choices[0].message.content.strip()
            return explanation
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return f"This product matches your search for '{query}' based on its title, description, and category."
    
    def extract_attributes(self, description: str) -> Dict[str, str]:
        """
        Extract structured attributes from product description
        """
        prompt = f"""Extract key attributes from this product description. Return a JSON object with attributes like brand, material, style, color, size if mentioned.

Description: {description}

Return JSON with extracted attributes:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an attribute extraction assistant. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            attributes = json.loads(response.choices[0].message.content)
            return attributes
        except Exception as e:
            print(f"Error extracting attributes: {e}")
            return {}


# Global instance (lazy initialization)
groq_client: Optional[GroqClient] = None

def get_groq_client() -> GroqClient:
    """Get or create Groq client instance"""
    global groq_client
    if groq_client is None:
        groq_client = GroqClient()
    return groq_client

