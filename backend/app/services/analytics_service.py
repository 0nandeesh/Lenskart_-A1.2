"""
Analytics service for query performance analysis
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from backend.app.database.mysql_db import db
from backend.app.models.analytics import QueryMetrics, AnalyticsSummary, ProductMetrics, TimeSeriesMetric
import aiomysql


class AnalyticsService:
    """Service for aggregating and analyzing query performance"""
    
    async def get_query_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_searches: int = 1
    ) -> List[QueryMetrics]:
        """
        Aggregate query metrics from behavior events
        
        Computes:
        - Total searches per query
        - Total clicks per query
        - CTR per query
        - Conversion rate per query
        - Zero-result queries
        - Average dwell time
        """
        async with db.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # Optimized query: Calculate all metrics in a single pass using session-based joins
                # We use a CTE or subquery to find all search sessions and then join other actions
                
                # Build date filter conditions for search events
                conditions = ["e1.event_type = 'search'", "e1.query IS NOT NULL", "e1.query != ''"]
                params = []
                
                if start_date:
                    conditions.append("e1.timestamp >= %s")
                    params.append(start_date)
                
                if end_date:
                    conditions.append("e1.timestamp <= %s")
                    params.append(end_date)
                
                where_clause = " AND ".join(conditions)
                params.append(min_searches)

                # This query aggregates metrics by query across sessions
                await cursor.execute(f"""
                    SELECT 
                        e1.query,
                        COUNT(DISTINCT e1.event_id) as search_count,
                        COUNT(DISTINCT CASE WHEN e2.event_type = 'click' THEN e2.event_id END) as click_count,
                        COUNT(DISTINCT CASE WHEN e2.event_type = 'add_to_cart' THEN e2.event_id END) as cart_count,
                        COUNT(DISTINCT CASE WHEN e2.event_type = 'purchase' THEN e2.event_id END) as purchase_count,
                        COUNT(DISTINCT e1.session_id) as total_sessions,
                        SUM(CASE WHEN e2.dwell_time IS NOT NULL THEN e2.dwell_time ELSE 0 END) as total_dwell,
                        COUNT(CASE WHEN e2.dwell_time IS NOT NULL THEN 1 END) as dwell_count,
                        MIN(e1.timestamp) as first_seen,
                        MAX(e1.timestamp) as last_seen
                    FROM behavior_events e1
                    LEFT JOIN behavior_events e2 ON e1.session_id = e2.session_id 
                    WHERE {where_clause}
                    GROUP BY e1.query
                    HAVING search_count >= %s
                    ORDER BY search_count DESC
                """, params)
                
                rows = await cursor.fetchall()
            
                query_metrics = []
                
                for row in rows:
                    search_count = row['search_count']
                    click_count = row['click_count'] or 0
                    cart_count = row['cart_count'] or 0
                    purchase_count = row['purchase_count'] or 0
                    dwell_count = row['dwell_count'] or 0
                    total_dwell = float(row['total_dwell']) if row['total_dwell'] else 0.0
                    
                    # Calculate average dwell time
                    avg_dwell = (total_dwell / dwell_count) if dwell_count > 0 else 0.0
                    
                    # Calculate CTR
                    ctr = (click_count / search_count) if search_count > 0 else 0.0
                    
                    # Calculate Conversion Rate (purchases per interaction session)
                    total_interactions = click_count + cart_count + purchase_count
                    conversion_rate = (purchase_count / total_interactions) if total_interactions > 0 else 0.0
                    
                    # Zero results estimation: Sessions with search but no clicks
                    # In this grouped context, we approximate it since a full subquery is expensive
                    # We can refine this if needed, but for large scale, statistical CTR is usually sufficient
                    zero_result_sessions = max(0, search_count - click_count)

                    query_metrics.append(QueryMetrics(
                        query=row['query'],
                        total_searches=search_count,
                        total_clicks=click_count,
                        total_carts=cart_count,
                        total_purchases=purchase_count,
                        zero_results_count=zero_result_sessions,
                        ctr=ctr,
                        conversion_rate=conversion_rate,
                        avg_dwell_time=avg_dwell,
                        first_seen=row['first_seen'],
                        last_seen=row['last_seen']
                    ))
            
            return query_metrics
            
    async def get_product_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 20
    ) -> List[ProductMetrics]:
        """Aggregate product metrics from behavior events"""
        async with db.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # We combine data from behavior_events (for raw interaction counts)
                # and product_behavior_metrics (for aggregated impressions/searches)
                await cursor.execute("""
                    SELECT 
                        p.id as product_id, 
                        p.title as product_title, 
                        COALESCE(m.total_searches, 0) as appearances,
                        SUM(CASE WHEN e.event_type = 'click' THEN 1 ELSE 0 END) as view_count,
                        SUM(CASE WHEN e.event_type = 'add_to_cart' THEN 1 ELSE 0 END) as cart_count,
                        SUM(CASE WHEN e.event_type = 'purchase' THEN 1 ELSE 0 END) as purchase_count
                    FROM products p
                    LEFT JOIN behavior_events e ON p.id = e.product_id
                    LEFT JOIN product_behavior_metrics m ON p.id = m.product_id
                    GROUP BY p.id, p.title, m.total_searches
                    HAVING appearances > 0 OR view_count > 0 OR cart_count > 0 OR purchase_count > 0
                    ORDER BY appearances DESC
                    LIMIT %s
                """, (limit * 2,))
                
                rows = await cursor.fetchall()
                
                results = []
                for row in rows:
                    total_actions = row['view_count'] + row['cart_count'] + row['purchase_count']
                    ctr = (row['view_count'] / row['appearances']) if row['appearances'] > 0 else 0.0
                    
                    results.append(ProductMetrics(
                        product_id=str(row['product_id']),
                        title=row['product_title'],
                        appearances=int(row['appearances']),
                        views=int(row['view_count']),
                        carts=int(row['cart_count']),
                        purchases=int(row['purchase_count']),
                        ctr=ctr
                    ))

                
                return results
                
    async def get_ctr_over_time(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        interval: str = 'hour' # 'hour' or 'day'
    ) -> List[TimeSeriesMetric]:
        """Aggregate CTR over time from behavior events"""
        async with db.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                py_date_format = '%Y-%m-%d %H:00:00' if interval == 'hour' else '%Y-%m-%d'
                sql_date_format = py_date_format.replace('%', '%%')
                
                # Build date filter conditions
                conditions = ["timestamp IS NOT NULL"]
                params = []
                
                if start_date:
                    conditions.append("timestamp >= %s")
                    params.append(start_date)
                
                if end_date:
                    conditions.append("timestamp <= %s")
                    params.append(end_date)
                
                where_clause = " AND ".join(conditions)
                
                # We need search counts and click counts grouped by time
                await cursor.execute(f"""
                    SELECT 
                        DATE_FORMAT(timestamp, '{sql_date_format}') as time_bucket,
                        SUM(CASE WHEN event_type = 'search' THEN 1 ELSE 0 END) as searches,
                        SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) as clicks
                    FROM behavior_events
                    WHERE {where_clause}
                    GROUP BY time_bucket
                    ORDER BY time_bucket ASC
                """, params)

                
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    timestamp = datetime.strptime(row['time_bucket'], py_date_format)
                    ctr = (row['clicks'] / row['searches']) if row['searches'] > 0 else 0.0
                    results.append(TimeSeriesMetric(timestamp=timestamp, value=ctr))
                
                return results


    
    async def get_analytics_summary(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> AnalyticsSummary:
        """
        Get overall analytics summary with top queries and poor performers
        """
        # Get all query metrics
        all_metrics = await self.get_query_metrics(
            start_date=start_date,
            end_date=end_date,
            min_searches=1
        )
        
        if not all_metrics:
            return AnalyticsSummary(
                total_queries=0,
                total_searches=0,
                total_clicks=0,
                total_conversions=0,
                overall_ctr=0.0,
                overall_conversion_rate=0.0,
                zero_result_queries=0,
                top_queries=[],
                poor_performing_queries=[]
            )
        
        # Calculate overall metrics
        total_queries = len(all_metrics)
        total_searches = sum(m.total_searches for m in all_metrics)
        total_clicks = sum(m.total_clicks for m in all_metrics)
        total_carts = sum(m.total_carts for m in all_metrics)
        total_conversions = sum(m.total_purchases for m in all_metrics)
        overall_ctr = (total_clicks / total_searches) if total_searches > 0 else 0.0
        total_interactions = total_clicks + total_carts + total_conversions

        overall_conversion_rate = (total_conversions / total_interactions) if total_interactions > 0 else 0.0
        zero_result_queries = len([m for m in all_metrics if m.zero_results_count > 0])
        
        # Top queries (by search volume)
        top_queries = sorted(
            all_metrics,
            key=lambda x: x.total_searches,
            reverse=True
        )[:limit]
        
        # Poor performing queries (low CTR, high zero results, or low conversion)
        poor_performing = [
            m for m in all_metrics
            if (
                m.ctr < 0.1 or  # CTR below 10%
                m.zero_results_count > 0 or  # Has zero result sessions
                (m.total_searches > 5 and m.conversion_rate < 0.05)  # Low conversion with enough searches
            )
        ]
        poor_performing = sorted(
            poor_performing,
            key=lambda x: (x.ctr, -x.conversion_rate),  # Sort by low CTR, then low conversion
        )[:limit]
        
        # Get product metrics
        product_metrics = await self.get_product_metrics(
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        top_viewed = sorted(product_metrics, key=lambda x: x.views, reverse=True)[:limit]
        top_converted = sorted(product_metrics, key=lambda x: x.purchases, reverse=True)[:limit]
        
        # Get CTR over time
        ctr_over_time = await self.get_ctr_over_time(
            start_date=start_date,
            end_date=end_date
        )
        
        return AnalyticsSummary(
            total_queries=total_queries,
            total_searches=total_searches,
            total_clicks=total_clicks,
            total_carts=total_carts,
            total_conversions=total_conversions,
            overall_ctr=overall_ctr,

            overall_conversion_rate=overall_conversion_rate,
            zero_result_queries=zero_result_queries,
            top_queries=top_queries,
            poor_performing_queries=poor_performing,
            top_viewed_products=top_viewed,
            top_converted_products=top_converted,
            ctr_over_time=ctr_over_time
        )


    
    async def get_zero_result_queries(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[QueryMetrics]:
        """Get queries that resulted in zero clicks"""
        all_metrics = await self.get_query_metrics(
            start_date=start_date,
            end_date=end_date,
            min_searches=1
        )
        return [m for m in all_metrics if m.zero_results_count > 0]


# Global instance
analytics_service = AnalyticsService()
