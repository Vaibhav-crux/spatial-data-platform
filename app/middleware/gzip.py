from fastapi.middleware.gzip import GZipMiddleware

def add_gzip_middleware(app):
    """Add GZip compression middleware."""
    app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB