"""
Reload vector DB from existing products
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database.mysql_db import db
from backend.app.database.vector_db import vector_db
from backend.app.services.ingestion_service import ingestion_service

async def reload_embeddings():
    """Reload all products and regenerate embeddings"""
    await db.connect()
    vector_db.initialize()
    
    # Get all products
    all_ids = await db.filter_products()
    print(f"Found {len(all_ids)} products in database")
    
    if not all_ids:
        print("No products found. Ingest products first.")
        await db.disconnect()
        return
    
    # Get all products
    products = await db.get_products_by_ids(all_ids)
    print(f"Regenerating embeddings for {len(products)} products...")
    
    # Re-ingest embeddings
    for product in products:
        embedding_text = ingestion_service._create_embedding_text(product)
        vector_db.add_product(product.id, embedding_text)
        print(f"  Added: {product.id} - {product.title[:50]}")
    
    # Save vector DB
    vector_db.save()
    print(f"\n[OK] Vector DB updated with {len(products)} products")
    
    # Test search
    print("\nTesting search...")
    results = vector_db.search("sunglasses", k=3)
    print(f"Found {len(results)} results for 'sunglasses'")
    for pid, score in results:
        print(f"  - {pid}: {score:.3f}")
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(reload_embeddings())

