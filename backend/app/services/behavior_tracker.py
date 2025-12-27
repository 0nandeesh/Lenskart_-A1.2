"""
User behavior tracking service with async event processing and user profile updates
"""
import redis
import json
import uuid
from datetime import datetime
from typing import Optional
from backend.app.config import settings
from backend.app.models.behavior import BehaviorEvent, EventType
from backend.app.database.mysql_db import db
import asyncio


class BehaviorTracker:
    """Tracks user behavior events asynchronously"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.stream_name = "behavior_events"
    
    def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            print(f"Warning: Redis not available, using in-memory queue: {e}")
            self.redis_client = None
    
    async def track_event(
        self,
        event_type: EventType,
        session_id: str,
        product_id: Optional[str] = None,
        query: Optional[str] = None,
        user_id: Optional[str] = None,
        dwell_time: Optional[float] = None,
        metadata: Optional[dict] = None
    ):
        """Track a behavior event asynchronously"""
        event = BehaviorEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            product_id=product_id,
            query=query,
            timestamp=datetime.now(),
            dwell_time=dwell_time,
            metadata=metadata
        )
        
        # Publish to Redis Stream (non-blocking)
        if self.redis_client:
            try:
                self.redis_client.xadd(
                    self.stream_name,
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                        "user_id": event.user_id or "",
                        "session_id": event.session_id,
                        "product_id": event.product_id or "",
                        "query": event.query or "",
                        "timestamp": event.timestamp.isoformat(),
                        "dwell_time": str(event.dwell_time) if event.dwell_time else "",
                        "metadata": json.dumps(event.metadata) if event.metadata else ""
                    }
                )
            except Exception as e:
                print(f"Error publishing to Redis: {e}")
        
        # Also store directly in MySQL for reliability
        # This is async but we don't wait for it
        asyncio.create_task(self._store_event_in_db(event))
        
        # Update user profile asynchronously (if user_id is present)
        if event.user_id:
            asyncio.create_task(self._update_user_profile_from_event(event))
    
    async def _store_event_in_db(self, event: BehaviorEvent):
        """Store event in MySQL"""
        try:
            async with db.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("""
                        INSERT INTO behavior_events (
                            event_id, event_type, user_id, session_id,
                            product_id, query, timestamp, dwell_time, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        event.event_id, event.event_type.value, event.user_id,
                        event.session_id, event.product_id, event.query,
                        event.timestamp, event.dwell_time,
                        json.dumps(event.metadata) if event.metadata else None
                    ))
                    await conn.commit()
        except Exception as e:
            print(f"Error storing event in DB: {e}")
    
    async def _update_user_profile_from_event(self, event: BehaviorEvent):
        """Update user profile based on behavior event"""
        try:
            from backend.app.services.user_profile_service import user_profile_service
            
            # Get product if available
            product = None
            if event.product_id:
                product = await db.get_product(event.product_id)
            
            # Update profile
            await user_profile_service.update_profile_from_event(
                user_id=event.user_id,
                event_type=event.event_type.value,
                product=product,
                query=event.query
            )
        except Exception as e:
            print(f"Error updating user profile from event: {e}")
    
    async def process_events_batch(self):
        """Process events from Redis Stream and update metrics"""
        if not self.redis_client:
            return
        
        try:
            # Read events from stream
            messages = self.redis_client.xread({self.stream_name: "0"}, count=100, block=0)
            
            for stream, events in messages:
                for event_id, data in events:
                    await self._update_metrics_from_event(data)
                    # Acknowledge processing (in production, use consumer groups)
        except Exception as e:
            print(f"Error processing events: {e}")
    
    async def _update_metrics_from_event(self, event_data: dict):
        """Update product metrics based on event"""
        event_type = event_data.get('event_type')
        product_id = event_data.get('product_id')
        
        if not product_id or not event_type:
            return
        
        # Get current metrics
        metrics = await db.get_behavior_metrics(product_id)
        if not metrics:
            metrics = {
                'total_clicks': 0,
                'total_searches': 0,
                'total_carts': 0,
                'total_purchases': 0,
                'total_bounces': 0,
                'total_dwell_time': 0.0
            }
        
        # Update metrics
        if event_type == EventType.CLICK.value:
            metrics['total_clicks'] = metrics.get('total_clicks', 0) + 1
        elif event_type == EventType.SEARCH.value:
            metrics['total_searches'] = metrics.get('total_searches', 0) + 1
        elif event_type == EventType.ADD_TO_CART.value:
            metrics['total_carts'] = metrics.get('total_carts', 0) + 1
        elif event_type == EventType.PURCHASE.value:
            metrics['total_purchases'] = metrics.get('total_purchases', 0) + 1
        elif event_type == EventType.BOUNCE.value:
            metrics['total_bounces'] = metrics.get('total_bounces', 0) + 1
        
        # Update dwell time
        dwell_time = event_data.get('dwell_time')
        if dwell_time:
            try:
                dt = float(dwell_time)
                metrics['total_dwell_time'] = metrics.get('total_dwell_time', 0.0) + dt
            except:
                pass
        
        # Calculate derived metrics
        total_interactions = (
            metrics.get('total_clicks', 0) +
            metrics.get('total_carts', 0) +
            metrics.get('total_purchases', 0)
        )
        
        if metrics.get('total_searches', 0) > 0:
            metrics['ctr'] = metrics.get('total_clicks', 0) / metrics.get('total_searches', 1)
        else:
            metrics['ctr'] = 0.0
        
        if total_interactions > 0:
            metrics['conversion_rate'] = metrics.get('total_purchases', 0) / total_interactions
        else:
            metrics['conversion_rate'] = 0.0
        
        if total_interactions > 0:
            metrics['bounce_rate'] = metrics.get('total_bounces', 0) / total_interactions
        else:
            metrics['bounce_rate'] = 0.0
        
        total_clicks = metrics.get('total_clicks', 0)
        if total_clicks > 0:
            metrics['avg_dwell_time'] = metrics.get('total_dwell_time', 0.0) / total_clicks
        else:
            metrics['avg_dwell_time'] = 0.0
        
        # Save updated metrics
        await db.update_behavior_metrics(product_id, metrics)


# Global instance
behavior_tracker = BehaviorTracker()
