# Streamlit UI Guide

## Overview

The Lenskart AI Search Platform uses **Streamlit** for all UI components. This provides a clean, Python-based interface without requiring JavaScript or frontend frameworks.

## Features

### Search Interface

1. **Natural Language Search**
   - Simple text input for queries
   - Real-time search execution
   - Expanded query display (if AI expansion was used)

2. **Filters Panel** (Expandable)
   - Category filter
   - Price range (min/max)
   - Minimum rating filter

3. **Search Results**
   - Product cards with full details
   - Expandable AI explanations ("Why this result?")
   - Expandable score breakdown (semantic, behavior, CTR, conversion)
   - Action buttons:
     - **Add to Cart**: Tracks add-to-cart event
     - **Purchase**: Tracks purchase event
     - **View Details**: Tracks click event

### Analytics Dashboard

Access via sidebar navigation or direct URL.

1. **Summary Metrics**
   - Total queries, searches, clicks
   - Overall CTR and conversion rate
   - Zero-result query count

2. **Query Analysis Tabs**
   - **Top Queries**: Ranked by search volume
   - **Poor Performers**: Queries with low CTR, zero results, or low conversion
   - **Zero Results**: Queries with no clicks

3. **Time-Range Filtering**
   - Date pickers for start/end dates
   - Refresh button to reload analytics

4. **Query Metrics Table**
   - Detailed metrics per query
   - Color-coded performance indicators
   - Actionable insights and recommendations

## Running the Streamlit App

### Basic Usage

```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

### Configuration

#### API URL Configuration

1. **Via Streamlit Secrets** (Recommended):
   Create `.streamlit/secrets.toml`:
   ```toml
   API_URL = "http://localhost:8000"
   ```

2. **Via Environment Variable**:
   ```bash
   export API_URL="http://localhost:8000"
   streamlit run streamlit_app.py
   ```

3. **Default**:
   If not configured, defaults to `http://localhost:8000`

### Customization

Edit `streamlit_app.py` to customize:
- UI layout and styling
- Additional metrics or visualizations
- Custom filters or features

## Architecture

```
┌─────────────────────┐
│  Streamlit App      │
│  (streamlit_app.py) │
└──────────┬──────────┘
           │ HTTP/REST
           ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  (localhost:8000)   │
└─────────────────────┘
```

The Streamlit app is a **thin client** that:
- Sends HTTP requests to the FastAPI backend
- Displays results in a user-friendly format
- Tracks user interactions asynchronously
- Provides analytics visualization

## Dependencies

Install Streamlit dependencies:

```bash
pip install -r requirements_streamlit.txt
```

Or install individually:
```bash
pip install streamlit requests pandas
```

## Deployment

### Local Development
```bash
streamlit run streamlit_app.py
```

### Production Deployment

1. **Streamlit Cloud** (Recommended):
   - Push code to GitHub
   - Connect to Streamlit Cloud
   - Set secrets via Streamlit Cloud dashboard
   - Deploy

2. **Docker**:
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY requirements_streamlit.txt .
   RUN pip install -r requirements_streamlit.txt
   COPY streamlit_app.py .
   CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

3. **Custom Server**:
   - Use `streamlit run` with proper configuration
   - Set up reverse proxy (nginx)
   - Configure SSL/TLS

## Troubleshooting

### App Won't Start
- Check Python version (3.9+)
- Verify dependencies: `pip list | grep streamlit`
- Check for port conflicts (default: 8501)

### Can't Connect to Backend
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check API_URL configuration
- Verify CORS settings in backend

### Analytics Not Loading
- Ensure backend has behavior event data
- Check date range (may be too narrow)
- Verify database connection in backend

### Search Not Working
- Check backend logs for errors
- Verify products are ingested
- Check Groq API key is set in backend

## Advantages of Streamlit

1. **Pure Python**: No JavaScript/TypeScript required
2. **Rapid Development**: Fast iteration and prototyping
3. **Built-in Components**: Pre-built UI components
4. **Easy Deployment**: Streamlit Cloud integration
5. **Interactive**: Automatic reactivity
6. **Data Science Friendly**: Native pandas/plotting support

## Limitations

1. **Less Customization**: Compared to React/Vue
2. **Performance**: May be slower for very large datasets
3. **Styling**: Limited CSS customization
4. **Mobile**: Not optimized for mobile (though responsive)

For this use case, Streamlit is ideal as it provides:
- Clean, functional UI
- Fast development
- Easy maintenance
- No frontend complexity

