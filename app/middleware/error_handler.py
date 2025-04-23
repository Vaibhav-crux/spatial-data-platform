from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
import httpx
import asyncio
import uuid
from app.middleware.logger import logger
from app.services.v1.point_service import NotFoundError as PointNotFoundError
from app.services.v1.polygon_service import NotFoundError as PolygonNotFoundError

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate a unique error ID for tracing
        error_id = str(uuid.uuid4())
        
        # Extract request context
        request_context = {
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "error_id": error_id
        }

        try:
            # Process the incoming request
            response = await call_next(request)
            return response

        # Handle NotFoundError for points
        except PointNotFoundError as e:
            logger.error(
                "Point not found",
                exc_info=True,
                error_message=str(e),
                **request_context
            )
            return JSONResponse(
                status_code=404,
                content={
                    "error_code": "NOT_FOUND_ERROR",
                    "message": str(e),
                    "error_id": error_id
                }
            )

        # Handle NotFoundError for polygons
        except PolygonNotFoundError as e:
            logger.error(
                "Polygon not found",
                exc_info=True,
                error_message=str(e),
                **request_context
            )
            return JSONResponse(
                status_code=404,
                content={
                    "error_code": "NOT_FOUND_ERROR",
                    "message": str(e),
                    "error_id": error_id
                }
            )

        # Handle FastAPI HTTP exceptions
        except HTTPException as e:
            logger.error(
                "HTTP exception occurred",
                exc_info=True,
                status_code=e.status_code,
                detail=e.detail,
                **request_context
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error_code": "HTTP_EXCEPTION",
                    "message": e.detail,
                    "error_id": error_id
                }
            )

        # Handle SQLAlchemy database errors
        except SQLAlchemyError as e:
            logger.error(
                "Database error occurred",
                exc_info=True,
                error_type=str(type(e).__name__),
                **request_context
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error_code": "DATABASE_ERROR",
                    "message": "A database error occurred",
                    "error_id": error_id
                }
            )

        # Handle HTTP errors from external services
        except httpx.HTTPError as e:
            logger.error(
                "External service error",
                exc_info=True,
                error_type=str(type(e).__name__),
                **request_context
            )
            return JSONResponse(
                status_code=502,
                content={
                    "error_code": "EXTERNAL_SERVICE_ERROR",
                    "message": f"External service error: {str(e)}",
                    "error_id": error_id
                }
            )

        # Handle request timeout errors
        except asyncio.TimeoutError:
            logger.error(
                "Request timed out",
                exc_info=True,
                **request_context
            )
            return JSONResponse(
                status_code=504,
                content={
                    "error_code": "TIMEOUT_ERROR",
                    "message": "Request timed out",
                    "error_id": error_id
                }
            )

        # Handle validation errors
        except ValueError as e:
            logger.error(
                "Validation error",
                exc_info=True,
                error_message=str(e),
                **request_context
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error_code": "VALIDATION_ERROR",
                    "message": f"Invalid input: {str(e)}",
                    "error_id": error_id
                }
            )

        # Handle unexpected server-side errors
        except Exception as e:
            logger.error(
                "Unexpected server error",
                exc_info=True,
                error_type=str(type(e).__name__),
                error_message=str(e),
                **request_context
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "error_id": error_id
                }
            )

def add_error_handler_middleware(app):
    """Register the error handler middleware in the FastAPI app."""
    app.add_middleware(ErrorHandlerMiddleware)