# Query Analytics Dashboard

## Overview

The Query Analytics Dashboard is a bonus feature that provides comprehensive insights into search performance, helping identify improvement opportunities and validate the learning-based ranking system.

## Purpose & Alignment with Objectives

### Core Objectives

1. **Improve Search Relevance**
   - Identify low-quality search results through CTR and conversion metrics
   - Detect zero-result queries that need better query expansion
   - Validate ranking improvements over time

2. **Tune Ranking Weights**
   - Analytics show which queries have low CTR → adjust semantic vs behavior weights
   - Poor conversion rates indicate ranking issues → fine-tune conversion weight
   - Zero-result queries suggest query expansion problems

3. **Enhance Query Expansion**
   - Zero-result queries are flagged for AI query expansion improvement
   - Low CTR queries may need better semantic matching
   - Analytics guide which queries to prioritize for expansion tuning

4. **Validate Learning Logic**
   - CTR trends validate that behavior-based ranking is working
   - Conversion rate improvements confirm learning effectiveness
   - Dwell time metrics indicate result quality

## Features

### Metrics Displayed

1. **Top Search Queries**
   - Ranked by search volume
   - Shows total searches, clicks, CTR, conversions
   - Helps identify popular queries

2. **Zero-Result Queries**
   - Queries that resulted in searches with no clicks
   - Critical for identifying query expansion gaps
   - Highlights need for better semantic matching

3. **Click-Through Rate (CTR)**
   - Percentage of searches that resulted in clicks
   - Low CTR (<10%) indicates poor result relevance
   - High CTR (>20%) indicates good matching

4. **Conversion Rate**
   - Percentage of interactions that led to purchases
   - Validates that shown products are actually desired
   - Low conversion suggests ranking issues

5. **Average Dwell Time**
   - Time users spend viewing clicked products
   - Longer dwell = more relevant results
   - Short dwell = potential bounce

### Dashboard Components

1. **Summary Cards**
   - Total queries, searches, clicks, conversions
   - Overall CTR and conversion rate
   - Zero-result query count

2. **Query Table**
   - Detailed metrics for each query
   - Sortable columns
   - Color-coded performance indicators

3. **Time-Range Filtering**
   - Filter analytics by date range
   - Track performance over time
   - Identify trends and improvements

4. **Poor-Performing Query Highlighting**
   - Automatically identifies queries with:
     - CTR < 10%
     - Zero-result sessions
     - Low conversion rate (<5%) with sufficient searches
   - Highlighted in red for easy identification

## Data Source

All analytics are computed from **asynchronous user behavior events** stored in PostgreSQL:

- Search events (queries)
- Click events (product interactions)
- Add-to-cart events
- Purchase events
- Dwell time data

No synchronous logging - all data comes from the async event processing system.

## API Endpoints

### GET `/api/v1/analytics/summary`
Returns overall analytics summary with top queries and poor performers.

**Request:**
```json
{
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-31T23:59:59",
  "limit": 50,
  "min_searches": 1
}
```

**Response:**
```json
{
  "total_queries": 150,
  "total_searches": 5000,
  "total_clicks": 1200,
  "total_conversions": 150,
  "overall_ctr": 0.24,
  "overall_conversion_rate": 0.125,
  "zero_result_queries": 12,
  "top_queries": [...],
  "poor_performing_queries": [...]
}
```

### GET `/api/v1/analytics/queries`
Returns detailed metrics for all queries.

**Query Parameters:**
- `start_date`: ISO format datetime
- `end_date`: ISO format datetime
- `min_searches`: Minimum searches to include (default: 1)

### GET `/api/v1/analytics/zero-results`
Returns queries that resulted in zero clicks.

## How Analytics Improve the System

### 1. Ranking Weight Tuning

**Example Scenario:**
- Analytics show overall CTR of 15% (good)
- But conversion rate is only 3% (low)
- **Action**: Increase `CONVERSION_WEIGHT` in ranking formula
- **Result**: Products with higher conversion history rank higher

**Configuration:**
```env
# Adjust in .env based on analytics
SEMANTIC_WEIGHT=0.4
BEHAVIOR_WEIGHT=0.6
CTR_WEIGHT=0.3
CONVERSION_WEIGHT=0.5  # Increase if conversions are low
BOUNCE_PENALTY=0.2
```

### 2. Query Expansion Improvement

**Example Scenario:**
- Analytics show "sunglasses for men" has zero results
- **Action**: Improve Groq query expansion prompt
- **Result**: Better semantic matching for similar queries

**Implementation:**
- Zero-result queries are flagged in dashboard
- Review and improve query expansion logic
- Add synonyms and context for common zero-result patterns

### 3. Learning Logic Validation

**Example Scenario:**
- Week 1: CTR = 12%, Conversion = 4%
- Week 2: CTR = 18%, Conversion = 6%
- **Validation**: Learning is working! Behavior scores improving rankings
- **Action**: Continue monitoring, system is self-improving

**Metrics to Track:**
- CTR trend over time (should increase)
- Conversion rate trend (should increase)
- Zero-result queries (should decrease)

## Usage Workflow

1. **Access Dashboard**
   - Navigate to `/analytics` in the frontend
   - Or click "Analytics Dashboard" button from main search page

2. **Set Time Range**
   - Select start and end dates
   - Click "Refresh Analytics"
   - View metrics for selected period

3. **Analyze Performance**
   - Review summary cards for overall health
   - Check "Top Queries" tab for popular searches
   - Review "Poor Performers" for improvement opportunities
   - Check "Zero Results" for query expansion gaps

4. **Take Action**
   - Adjust ranking weights based on CTR/conversion trends
   - Improve query expansion for zero-result queries
   - Add products for queries with no matches
   - Monitor improvements over time

## Periodic Aggregation

Analytics are computed on-demand from behavior events. For production:

- **Current**: Real-time computation (suitable for <100K events)
- **Recommended for Scale**: Pre-compute aggregations periodically
  - Run aggregation job every hour/day
  - Store in `query_analytics` table
  - Dashboard reads from pre-computed data

**Future Enhancement:**
```python
# Background task to pre-compute analytics
async def aggregate_analytics_periodically():
    while True:
        # Compute and store analytics
        await analytics_service.aggregate_and_store()
        await asyncio.sleep(3600)  # Every hour
```

## Performance Considerations

- Analytics queries can be slow for large datasets
- Consider adding indexes on `behavior_events` table:
  ```sql
  CREATE INDEX idx_query_timestamp ON behavior_events(query, timestamp);
  CREATE INDEX idx_event_type_session ON behavior_events(event_type, session_id);
  ```
- For production, implement caching (Redis) for frequently accessed analytics
- Consider materialized views for complex aggregations

## Integration with Learning System

The analytics dashboard directly supports the learning-based ranking:

1. **CTR Metrics** → Used in `behavior_score` calculation
2. **Conversion Metrics** → Used in `behavior_score` calculation
3. **Zero Results** → Identifies queries needing better expansion
4. **Dwell Time** → Can be added to behavior scoring

**Feedback Loop:**
```
User Searches → Behavior Events → Analytics Dashboard
                                    ↓
                            Identify Issues
                                    ↓
                        Adjust Ranking Weights
                                    ↓
                            Better Rankings
                                    ↓
                        Improved Metrics (validated in dashboard)
```

## Conclusion

The Query Analytics Dashboard is essential for:
- **Monitoring** search quality
- **Identifying** improvement opportunities
- **Validating** that learning is working
- **Tuning** ranking parameters
- **Improving** query expansion

All analytics are derived from asynchronous behavior events, ensuring no impact on search performance while providing actionable insights.

