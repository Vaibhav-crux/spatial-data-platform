from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests=10, window_seconds=60):
        super().__init__(app)
        self.max_requests = max_requests  # Maximum allowed requests per client
        self.window_seconds = window_seconds  # Time window in seconds
        self.request_counts = defaultdict(list)  # Stores request timestamps per client IP

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host  # Identify client by IP address
        current_time = time.time()  # Current timestamp

        # Remove expired request timestamps outside the current time window
        self.request_counts[client_ip] = [
            t for t in self.request_counts[client_ip]
            if current_time - t < self.window_seconds
        ]

        # Check if client exceeded allowed request limit
        if len(self.request_counts[client_ip]) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Too Many Requests")

        # Record the current request timestamp
        self.request_counts[client_ip].append(current_time)

        # Continue processing the request
        response = await call_next(request)
        return response

def add_rate_limit_middleware(app):
    # Register the rate limiting middleware with default limits (10 requests per 60 seconds)
    app.add_middleware(RateLimitMiddleware, max_requests=10, window_seconds=60)
