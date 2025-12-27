"""
Product ingestion service
"""
from typing import List
from backend.app.models.product import Product
from backend.app.database.mysql_db import db
from backend.app.database.vector_db import vector_db


class IngestionService:
    """Service for ingesting products into the system"""
    
    async def ingest_product(self, product: Product) -> str:
        """
        Ingest a single product:
        1. Store in PostgreSQL
        2. Generate embedding and store in vector DB
        """
        # Store in PostgreSQL
        await db.insert_product(product)
        
        # Generate embedding text (combine title, description, category, attributes)
        embedding_text = self._create_embedding_text(product)
        
        # Add to vector DB
        vector_db.add_product(product.id, embedding_text)
        
        # Save vector DB
        vector_db.save()
        
        return product.id
    
    async def ingest_products_batch(self, products: List[Product]) -> List[str]:
        """Ingest multiple products"""
        product_ids = []
        for product in products:
            product_id = await self.ingest_product(product)
            product_ids.append(product_id)
        return product_ids
    
    def _create_embedding_text(self, product: Product) -> str:
        """Create text for embedding generation"""
        parts = [
            product.title,
            product.description,
            product.category
        ]
        
        # Add attributes
        if product.attributes.brand:
            parts.append(f"brand: {product.attributes.brand}")
        if product.attributes.color:
            parts.append(f"color: {product.attributes.color}")
        if product.attributes.material:
            parts.append(f"material: {product.attributes.material}")
        if product.attributes.style:
            parts.append(f"style: {product.attributes.style}")
        
        return " ".join(parts)


# Global instance
ingestion_service = IngestionService()

