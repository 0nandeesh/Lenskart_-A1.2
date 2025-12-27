"""
MySQL database connection and operations
"""
import aiomysql
from typing import List, Optional, Dict
from backend.app.config import settings
from backend.app.models.product import Product
import json
from datetime import datetime


class MySQLDB:
    """MySQL database manager"""
    
    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None
    
    async def connect(self):
        """Create connection pool"""
        self.pool = await aiomysql.create_pool(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DB,
            minsize=5,
            maxsize=20,
            charset='utf8mb4',
            autocommit=False
        )
        await self._create_tables()
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
    
    async def _create_tables(self):
        """Create necessary tables"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Products table
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id VARCHAR(255) PRIMARY KEY,
                        title VARCHAR(500) NOT NULL,
                        description TEXT NOT NULL,
                        category VARCHAR(255) NOT NULL,
                        price DECIMAL(10, 2) NOT NULL,
                        rating DECIMAL(3, 2) NOT NULL,
                        attributes JSON,
                        image_url VARCHAR(500),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_category (category),
                        INDEX idx_price (price),
                        INDEX idx_rating (rating)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # Behavior metrics table
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS product_behavior_metrics (
                        product_id VARCHAR(255) PRIMARY KEY,
                        total_clicks INT DEFAULT 0,
                        total_searches INT DEFAULT 0,
                        total_carts INT DEFAULT 0,
                        total_purchases INT DEFAULT 0,
                        total_bounces INT DEFAULT 0,
                        total_dwell_time DECIMAL(10, 2) DEFAULT 0.0,
                        avg_dwell_time DECIMAL(10, 2) DEFAULT 0.0,
                        ctr DECIMAL(5, 4) DEFAULT 0.0,
                        conversion_rate DECIMAL(5, 4) DEFAULT 0.0,
                        bounce_rate DECIMAL(5, 4) DEFAULT 0.0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # Behavior events table
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS behavior_events (
                        event_id VARCHAR(255) PRIMARY KEY,
                        event_type VARCHAR(50) NOT NULL,
                        user_id VARCHAR(255),
                        session_id VARCHAR(255) NOT NULL,
                        product_id VARCHAR(255),
                        query TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        dwell_time DECIMAL(10, 2),
                        metadata JSON,
                        INDEX idx_product_id (product_id),
                        INDEX idx_event_type (event_type),
                        INDEX idx_timestamp (timestamp),
                        INDEX idx_session_id (session_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # User profiles table (for personalization)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id VARCHAR(255) PRIMARY KEY,
                        preferred_categories JSON,
                        preferred_brands JSON,
                        search_history JSON,
                        total_searches INT DEFAULT 0,
                        total_clicks INT DEFAULT 0,
                        total_carts INT DEFAULT 0,
                        total_purchases INT DEFAULT 0,
                        recent_product_ids JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_user_id (user_id),
                        INDEX idx_last_updated (last_updated)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # User interactions table (for detailed tracking)
                await cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_interactions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        product_id VARCHAR(255) NOT NULL,
                        interaction_type VARCHAR(50) NOT NULL,
                        category VARCHAR(255),
                        brand VARCHAR(255),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSON,
                        INDEX idx_user_id (user_id),
                        INDEX idx_product_id (product_id),
                        INDEX idx_timestamp (timestamp),
                        INDEX idx_interaction_type (interaction_type)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                await conn.commit()
    
    async def insert_product(self, product: Product) -> bool:
        """Insert or update a product"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO products (id, title, description, category, price, rating, attributes, image_url, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) AS new
                    ON DUPLICATE KEY UPDATE
                        title = new.title,
                        description = new.description,
                        category = new.category,
                        price = new.price,
                        rating = new.rating,
                        attributes = new.attributes,
                        image_url = new.image_url
                """, (
                    product.id, product.title, product.description, product.category,
                    product.price, product.rating, json.dumps(product.attributes.dict()),
                    product.image_url, product.created_at
                ))
                await conn.commit()
                return True
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get a product by ID"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT * FROM products WHERE id = %s", (product_id,)
                )
                row = await cursor.fetchone()
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
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                placeholders = ','.join(['%s'] * len(product_ids))
                await cursor.execute(
                    f"SELECT * FROM products WHERE id IN ({placeholders})",
                    product_ids
                )
                rows = await cursor.fetchall()
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
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        if min_price is not None:
            conditions.append("price >= %s")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("price <= %s")
            params.append(max_price)
        
        if min_rating is not None:
            conditions.append("rating >= %s")
            params.append(min_rating)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    f"SELECT id FROM products WHERE {where_clause}",
                    params
                )
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    async def get_behavior_metrics(self, product_id: str) -> Optional[Dict]:
        """Get behavior metrics for a product"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT * FROM product_behavior_metrics WHERE product_id = %s",
                    (product_id,)
                )
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None
    
    async def update_behavior_metrics(self, product_id: str, metrics: Dict):
        """Update behavior metrics for a product"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO product_behavior_metrics (
                        product_id, total_clicks, total_searches, total_carts,
                        total_purchases, total_bounces, total_dwell_time,
                        avg_dwell_time, ctr, conversion_rate, bounce_rate
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) AS new
                    ON DUPLICATE KEY UPDATE
                        total_clicks = new.total_clicks,
                        total_searches = new.total_searches,
                        total_carts = new.total_carts,
                        total_purchases = new.total_purchases,
                        total_bounces = new.total_bounces,
                        total_dwell_time = new.total_dwell_time,
                        avg_dwell_time = new.avg_dwell_time,
                        ctr = new.ctr,
                        conversion_rate = new.conversion_rate,
                        bounce_rate = new.bounce_rate,
                        last_updated = CURRENT_TIMESTAMP
                """, (
                    product_id, metrics.get('total_clicks', 0), metrics.get('total_searches', 0),
                    metrics.get('total_carts', 0), metrics.get('total_purchases', 0),
                    metrics.get('total_bounces', 0), metrics.get('total_dwell_time', 0.0),
                    metrics.get('avg_dwell_time', 0.0), metrics.get('ctr', 0.0),
                    metrics.get('conversion_rate', 0.0), metrics.get('bounce_rate', 0.0)
                ))
                await conn.commit()
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile by user_id"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(
                    "SELECT * FROM user_profiles WHERE user_id = %s",
                    (user_id,)
                )
                row = await cursor.fetchone()
                return dict(row) if row else None
    
    async def create_user_profile(self, user_id: str):
        """Create a new user profile"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO user_profiles (
                        user_id, preferred_categories, preferred_brands,
                        search_history, recent_product_ids
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    user_id,
                    json.dumps({}),
                    json.dumps({}),
                    json.dumps([]),
                    json.dumps([])
                ))
                await conn.commit()
    
    async def update_user_profile(self, user_id: str, profile_data: Dict):
        """Update user profile"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    UPDATE user_profiles SET
                        preferred_categories = %s,
                        preferred_brands = %s,
                        search_history = %s,
                        total_searches = %s,
                        total_clicks = %s,
                        total_carts = %s,
                        total_purchases = %s,
                        recent_product_ids = %s,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (
                    json.dumps(profile_data.get('preferred_categories', {})),
                    json.dumps(profile_data.get('preferred_brands', {})),
                    json.dumps(profile_data.get('search_history', [])),
                    profile_data.get('total_searches', 0),
                    profile_data.get('total_clicks', 0),
                    profile_data.get('total_carts', 0),
                    profile_data.get('total_purchases', 0),
                    json.dumps(profile_data.get('recent_product_ids', [])),
                    user_id
                ))
                await conn.commit()
    
    async def add_user_interaction(
        self,
        user_id: str,
        product_id: str,
        interaction_type: str,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Add a user interaction record"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO user_interactions (
                        user_id, product_id, interaction_type,
                        category, brand, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    user_id, product_id, interaction_type,
                    category, brand,
                    json.dumps(metadata) if metadata else None
                ))
                await conn.commit()
    
    async def get_user_interactions(
        self,
        user_id: str,
        limit: int = 100,
        interaction_type: Optional[str] = None
    ) -> List[Dict]:
        """Get user interactions"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                if interaction_type:
                    await cursor.execute("""
                        SELECT ui.*, p.title as product_title 
                        FROM user_interactions ui
                        JOIN products p ON ui.product_id = p.id
                        WHERE ui.user_id = %s AND ui.interaction_type = %s
                        ORDER BY ui.timestamp DESC
                        LIMIT %s
                    """, (user_id, interaction_type, limit))
                else:
                    await cursor.execute("""
                        SELECT ui.*, p.title as product_title 
                        FROM user_interactions ui
                        JOIN products p ON ui.product_id = p.id
                        WHERE ui.user_id = %s
                        ORDER BY ui.timestamp DESC
                        LIMIT %s
                    """, (user_id, limit))
                rows = await cursor.fetchall()
                return rows

    async def get_recent_searches(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """Get recent searches with timestamps"""
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("""
                    SELECT query, timestamp 
                    FROM behavior_events
                    WHERE user_id = %s AND event_type = 'search'
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (user_id, limit))
                return await cursor.fetchall()
                return [dict(row) for row in rows]


# Global instance
db = MySQLDB()

