"""
Script to ingest sample products into the system
"""
import asyncio
import json
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.models.product import Product
from backend.app.services.ingestion_service import ingestion_service


async def ingest_products_from_file(file_path: str):
    """Ingest products from JSON file"""
    with open(file_path, 'r') as f:
        products_data = json.load(f)
    
    products = []
    for data in products_data:
        # Handle attributes
        attributes_data = data.get('attributes', {})
        from backend.app.models.product import ProductAttributes
        attributes = ProductAttributes(**attributes_data)
        
        product = Product(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            category=data['category'],
            price=data['price'],
            rating=data['rating'],
            attributes=attributes,
            image_url=data.get('image_url')
        )
        products.append(product)
    
    # Ingest all products
    print(f"Ingesting {len(products)} products...")
    product_ids = await ingestion_service.ingest_products_batch(products)
    print(f"Successfully ingested {len(product_ids)} products:")
    for pid in product_ids:
        print(f"  - {pid}")


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "../data/sample_products.json"
    
    # Initialize database connections
    from backend.app.database.mysql_db import db
    from backend.app.database.vector_db import vector_db
    
    async def main():
        await db.connect()
        vector_db.initialize()
        
        try:
            await ingest_products_from_file(file_path)
        finally:
            await db.disconnect()
            vector_db.save()
    
    asyncio.run(main())

