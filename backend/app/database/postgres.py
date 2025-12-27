"""
PostgreSQL database connection and operations
"""
import asyncpg
from typing import List, Optional, Dict
from backend.app.config import settings
from backend.app.models.product import Product
import json


class PostgresDB:
    """PostgreSQL database manager"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create connection pool"""
        self.pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            min_size=5,
            max_size=20
        )
        await self._create_tables()
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def _create_tables(self):
        """Create necessary tables"""
        async with self.pool.acquire() as conn:
            # Products table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id VARCHAR PRIMARY KEY,
                    title VARCHAR NOT NULL,
                    description TEXT NOT NULL,
                    category VARCHAR NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    rating DECIMAL(3, 2) NOT NULL,
                    attributes JSONB,
                    image_url VARCHAR,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes for products
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON products(category)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_price ON products(price)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_rating ON products(rating)")
            
            # Behavior metrics table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS product_behavior_metrics (
                    product_id VARCHAR PRIMARY KEY,
                    total_clicks INTEGER DEFAULT 0,
                    total_searches INTEGER DEFAULT 0,
                    total_carts INTEGER DEFAULT 0,
                    total_purchases INTEGER DEFAULT 0,
                    total_bounces INTEGER DEFAULT 0,
                    total_dwell_time DECIMAL(10, 2) DEFAULT 0.0,
                    avg_dwell_time DECIMAL(10, 2) DEFAULT 0.0,
                    ctr DECIMAL(5, 4) DEFAULT 0.0,
                    conversion_rate DECIMAL(5, 4) DEFAULT 0.0,
                    bounce_rate DECIMAL(5, 4) DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Behavior events table (for analytics)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS behavior_events (
                    event_id VARCHAR PRIMARY KEY,
                    event_type VARCHAR NOT NULL,
                    user_id VARCHAR,
                    session_id VARCHAR NOT NULL,
                    product_id VARCHAR,
                    query TEXT,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    dwell_time DECIMAL(10, 2),
                    metadata JSONB
                )
            """)
            
            # Create indexes for behavior_events
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_product_id ON behavior_events(product_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON behavior_events(event_type)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON behavior_events(timestamp)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON behavior_events(user_id)")
            
            # User profiles table (for personalization)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id VARCHAR PRIMARY KEY,
                    preferred_categories JSONB DEFAULT '{}',
                    preferred_brands JSONB DEFAULT '{}',
                    search_history JSONB DEFAULT '[]',
                    total_searches INTEGER DEFAULT 0,
                    total_clicks INTEGER DEFAULT 0,
                    total_carts INTEGER DEFAULT 0,
                    total_purchases INTEGER DEFAULT 0,
                    recent_product_ids JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_updated TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes for user_profiles
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_last_updated ON user_profiles(last_updated)")
            
            # User interactions table (for detailed tracking)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR NOT NULL,
                    product_id VARCHAR NOT NULL,
                    interaction_type VARCHAR NOT NULL,
                    category VARCHAR,
                    brand VARCHAR,
                    timestamp TIMESTAMP DEFAULT NOW(),
                    metadata JSONB
                )
            """)
            
            # Create indexes for user_interactions
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_interactions_product_id ON user_interactions(product_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp ON user_interactions(timestamp)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_interactions(interaction_type)")
    
    async def insert_product(self, product: Product) -> bool:
        """Insert or update a product"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO products (id, title, description, category, price, rating, attributes, image_url, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    category = EXCLUDED.category,
                    price = EXCLUDED.price,
                    rating = EXCLUDED.rating,
                    attributes = EXCLUDED.attributes,
                    image_url = EXCLUDED.image_url
            """, product.id, product.title, product.description, product.category,
                product.price, product.rating, json.dumps(product.attributes.dict()),
                product.image_url, product.created_at)
            return True
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get a product by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM products WHERE id = $1", product_id
            )
            if row:
                attributes = json.loads(row['attributes']) if row['attributes'] else {}
                return Product(
                    id=row['id'],
                    title=row['title'],
                    description=row['description'],
                    category=row['category'],
                    price=float(row['price']),
                    rating=float(row['rating']),
                    attributes=attributes,
                    image_url=row['image_url'],
                    created_at=row['created_at']
                )
            return None
    
    async def get_products_by_ids(self, product_ids: List[str]) -> List[Product]:
        """Get multiple products by IDs"""
        if not product_ids:
            return []
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM products WHERE id = ANY($1)", product_ids
            )
            products = []
            for row in rows:
                attributes = json.loads(row['attributes']) if row['attributes'] else {}
                products.append(Product(
                    id=row['id'],
                    title=row['title'],
                    description=row['description'],
                    category=row['category'],
                    price=float(row['price']),
                    rating=float(row['rating']),
                    attributes=attributes,
                    image_url=row['image_url'],
                    created_at=row['created_at']
                ))
            return products
    
    async def filter_products(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None
    ) -> List[str]:
        """Filter products and return IDs"""
        conditions = []
        params = []
        param_idx = 1
        
        if category:
            conditions.append(f"category = ${param_idx}")
            params.append(category)
            param_idx += 1
        
        if min_price is not None:
            conditions.append(f"price >= ${param_idx}")
            params.append(min_price)
            param_idx += 1
        
        if max_price is not None:
            conditions.append(f"price <= ${param_idx}")
            params.append(max_price)
            param_idx += 1
        
        if min_rating is not None:
            conditions.append(f"rating >= ${param_idx}")
            params.append(min_rating)
            param_idx += 1
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                f"SELECT id FROM products WHERE {where_clause}",
                *params
            )
            return [row['id'] for row in rows]
    
    async def get_behavior_metrics(self, product_id: str) -> Optional[Dict]:
        """Get behavior metrics for a product"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM product_behavior_metrics WHERE product_id = $1",
                product_id
            )
            if row:
                return dict(row)
            return None
    
    async def update_behavior_metrics(self, product_id: str, metrics: Dict):
        """Update behavior metrics for a product"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO product_behavior_metrics (
                    product_id, total_clicks, total_searches, total_carts,
                    total_purchases, total_bounces, total_dwell_time,
                    avg_dwell_time, ctr, conversion_rate, bounce_rate, last_updated
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
                ON CONFLICT (product_id) DO UPDATE SET
                    total_clicks = EXCLUDED.total_clicks,
                    total_searches = EXCLUDED.total_searches,
                    total_carts = EXCLUDED.total_carts,
                    total_purchases = EXCLUDED.total_purchases,
                    total_bounces = EXCLUDED.total_bounces,
                    total_dwell_time = EXCLUDED.total_dwell_time,
                    avg_dwell_time = EXCLUDED.avg_dwell_time,
                    ctr = EXCLUDED.ctr,
                    conversion_rate = EXCLUDED.conversion_rate,
                    bounce_rate = EXCLUDED.bounce_rate,
                    last_updated = NOW()
            """, product_id, metrics.get('total_clicks', 0), metrics.get('total_searches', 0),
                metrics.get('total_carts', 0), metrics.get('total_purchases', 0),
                metrics.get('total_bounces', 0), metrics.get('total_dwell_time', 0.0),
                metrics.get('avg_dwell_time', 0.0), metrics.get('ctr', 0.0),
                metrics.get('conversion_rate', 0.0), metrics.get('bounce_rate', 0.0))
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by user_id"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM user_profiles WHERE user_id = $1",
                user_id
            )
            if row:
                return dict(row)
            return None
    
    async def create_user_profile(self, user_id: str) -> bool:
        """Create a new user profile"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO user_profiles (user_id)
                VALUES ($1)
                ON CONFLICT (user_id) DO NOTHING
            """, user_id)
            return True
    
    async def update_user_profile(self, user_id: str, profile_data: Dict) -> bool:
        """Update user profile"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO user_profiles (
                    user_id, preferred_categories, preferred_brands, search_history,
                    total_searches, total_clicks, total_carts, total_purchases,
                    recent_product_ids, last_updated
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW())
                ON CONFLICT (user_id) DO UPDATE SET
                    preferred_categories = EXCLUDED.preferred_categories,
                    preferred_brands = EXCLUDED.preferred_brands,
                    search_history = EXCLUDED.search_history,
                    total_searches = EXCLUDED.total_searches,
                    total_clicks = EXCLUDED.total_clicks,
                    total_carts = EXCLUDED.total_carts,
                    total_purchases = EXCLUDED.total_purchases,
                    recent_product_ids = EXCLUDED.recent_product_ids,
                    last_updated = NOW()
            """, user_id,
                json.dumps(profile_data.get('preferred_categories', {})),
                json.dumps(profile_data.get('preferred_brands', {})),
                json.dumps(profile_data.get('search_history', [])),
                profile_data.get('total_searches', 0),
                profile_data.get('total_clicks', 0),
                profile_data.get('total_carts', 0),
                profile_data.get('total_purchases', 0),
                json.dumps(profile_data.get('recent_product_ids', [])))
            return True
    
    async def add_user_interaction(
        self,
        user_id: str,
        product_id: str,
        interaction_type: str,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Add a user interaction record"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO user_interactions (
                    user_id, product_id, interaction_type, category, brand, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """, user_id, product_id, interaction_type, category, brand,
                json.dumps(metadata) if metadata else None)
            return True
    
    async def get_user_interactions(
        self,
        user_id: str,
        limit: int = 100,
        interaction_type: Optional[str] = None
    ) -> List[Dict]:
        """Get user interactions, optionally filtered by type"""
        async with self.pool.acquire() as conn:
            if interaction_type:
                rows = await conn.fetch("""
                    SELECT * FROM user_interactions
                    WHERE user_id = $1 AND interaction_type = $2
                    ORDER BY timestamp DESC
                    LIMIT $3
                """, user_id, interaction_type, limit)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM user_interactions
                    WHERE user_id = $1
                    ORDER BY timestamp DESC
                    LIMIT $2
                """, user_id, limit)
            return [dict(row) for row in rows]



# Global instance
db = PostgresDB()

