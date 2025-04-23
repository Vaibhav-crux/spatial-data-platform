from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout_seconds=10):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds  # Maximum allowed time per request (in seconds)

    async def dispatch(self, request: Request, call_next):
        try:
            # Attempt to process the request within the specified timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout_seconds
            )
            return response
        except asyncio.TimeoutError:
            # Raise a 504 error if the request exceeds the allowed time
            raise HTTPException(status_code=504, detail="Request timed out")

def add_timeout_middleware(app):
    # Register the timeout middleware with a 10-second request limit
    app.add_middleware(TimeoutMiddleware, timeout_seconds=10)
