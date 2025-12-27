"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes import router
from backend.app.database.mysql_db import db
from backend.app.database.vector_db import vector_db
from backend.app.services.behavior_tracker import behavior_tracker
from backend.app.config import settings
import asyncio

app = FastAPI(
    title="Lenskart AI Search Platform",
    description="Production-ready AI-powered contextual search platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

# Configure global logging

# Configure global logging
# Use StreamHandler by default for container friendliness, or FileHandler if preferred
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

# Include routers
app.include_router(router, prefix="/api/v1", tags=["api"])

# Debug: List all registered routes
for route in app.routes:
    print(f"DEBUG_ROUTE: {route.path}")



@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    # Initialize MySQL
    await db.connect()
    
    # Initialize vector DB
    vector_db.initialize()
    
    # Initialize behavior tracker
    behavior_tracker.initialize()
    
    # Start background task for processing behavior events
    asyncio.create_task(process_behavior_events_background())


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await db.disconnect()
    vector_db.save()


async def process_behavior_events_background():
    """Background task to process behavior events"""
    while True:
        try:
            await behavior_tracker.process_events_batch()
            await asyncio.sleep(5)  # Process every 5 seconds
        except Exception as e:
            print(f"Error processing behavior events: {e}")
            await asyncio.sleep(10)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Lenskart AI Search Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

