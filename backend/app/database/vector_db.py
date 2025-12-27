"""
Vector database using FAISS for semantic search
"""
import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from backend.app.config import settings
import json


class VectorDB:
    """FAISS-based vector database for semantic search"""
    
    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.model: Optional[SentenceTransformer] = None
        self.id_to_index: dict = {}  # product_id -> faiss index
        self.index_to_id: dict = {}  # faiss index -> product_id
        self.dimension = settings.EMBEDDING_DIMENSION
        self.db_path = settings.VECTOR_DB_PATH
    
    def initialize(self):
        """Initialize the vector database"""
        # Load embedding model
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Create or load FAISS index
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        index_path = f"{self.db_path}.index"
        mapping_path = f"{self.db_path}.mapping"
        
        if os.path.exists(index_path) and os.path.exists(mapping_path):
            # Load existing index
            self.index = faiss.read_index(index_path)
            with open(mapping_path, 'rb') as f:
                mapping = pickle.load(f)
                self.id_to_index = mapping['id_to_index']
                self.index_to_id = mapping['index_to_id']
        else:
            # Create new index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.id_to_index = {}
            self.index_to_id = {}
    
    def save(self):
        """Save index and mappings to disk"""
        index_path = f"{self.db_path}.index"
        mapping_path = f"{self.db_path}.mapping"
        
        if self.index:
            faiss.write_index(self.index, index_path)
            with open(mapping_path, 'wb') as f:
                pickle.dump({
                    'id_to_index': self.id_to_index,
                    'index_to_id': self.index_to_id
                }, f)
    
    def add_product(self, product_id: str, text: str):
        """Add a product embedding to the index"""
        # Generate embedding
        embedding = self.model.encode([text], convert_to_numpy=True)
        embedding = embedding.astype('float32')
        
        # Normalize for cosine similarity (L2 normalization)
        faiss.normalize_L2(embedding)
        
        # Add to index
        idx = self.index.ntotal
        self.index.add(embedding)
        
        # Update mappings
        self.id_to_index[product_id] = idx
        self.index_to_id[idx] = product_id
    
    def search(
        self,
        query: str,
        k: int = 20,
        product_ids_filter: Optional[List[str]] = None
    ) -> List[Tuple[str, float]]:
        """
        Search for similar products
        Returns: List of (product_id, similarity_score) tuples
        """
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search
        k = min(k, self.index.ntotal)
        if k == 0:
            return []
        
        distances, indices = self.index.search(query_embedding, k)
        
        # Convert to product IDs and scores
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            
            product_id = self.index_to_id.get(idx)
            if product_id is None:
                continue
            
            # Apply filter if provided
            if product_ids_filter and product_id not in product_ids_filter:
                continue
            
            # Convert L2 distance to similarity (1 - normalized distance)
            # Since we normalized, distance is in [0, 2], similarity in [0, 1]
            similarity = 1 - (distance / 2.0)
            similarity = max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
            
            results.append((product_id, float(similarity)))
        
        return results
    
    def remove_product(self, product_id: str):
        """Remove a product from the index (not fully supported in FAISS, mark as removed)"""
        # FAISS doesn't support deletion, so we'll mark it
        # In production, consider rebuilding index periodically
        if product_id in self.id_to_index:
            del self.id_to_index[product_id]
            idx = self.id_to_index[product_id]
            if idx in self.index_to_id:
                del self.index_to_id[idx]
    
    def get_total_products(self) -> int:
        """Get total number of products in index"""
        return len(self.id_to_index)


# Global instance
vector_db = VectorDB()

