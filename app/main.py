from fastapi import FastAPI
from app.api.v1.routes.points import router as points_router
from app.api.v1.routes.polygons import router as polygons_router
from app.api.v1.routes.health import router as health_router
from app.middleware.cors import add_cors_middleware
from app.middleware.error_handler import add_error_handler_middleware
from app.middleware.gzip import add_gzip_middleware
from app.middleware.rate_limit import add_rate_limit_middleware
from app.middleware.timeout import add_timeout_middleware
from app.database.db import init_db

# Create the FastAPI application instance
app = FastAPI(title="Spatial Data Platform API")

# Apply middleware for CORS support
add_cors_middleware(app)

# Apply centralized error handling
add_error_handler_middleware(app)

# Enable GZIP compression for responses
add_gzip_middleware(app)

# Apply rate limiting to control request frequency
add_rate_limit_middleware(app)

# Enforce request timeout to avoid long-running operations
add_timeout_middleware(app)

# Register API routes with appropriate prefixes and tags
app.include_router(points_router, prefix="/api/v1/points", tags=["points"])
app.include_router(polygons_router, prefix="/api/v1/polygons", tags=["polygons"])
app.include_router(health_router, prefix="/api/v1/health", tags=["health"])

# Initialize the database on application startup
@app.on_event("startup")
async def startup_event():
    await init_db()
