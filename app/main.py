from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.exception import EngageFatalException, EngageNonFatalException
from app.api.schemas.common_schemas import CommonResponse
from app.config.logger import get_logger
from app.config.config import CORS_ORIGINS, CORS_METHODS, CORS_HEADERS
from app.infra.db.postgres.postgres_config import get_db
from app.api.routes import analyze
# Import models to ensure they are registered with SQLAlchemy
from app.infra.db.postgres.models import code_analysis
import logging

APP_TITLE = "CodeShield AI Backend"
app = FastAPI(title=APP_TITLE, version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# Include API routes
app.include_router(analyze.router, prefix="/api/v1")
# Also include direct route for frontend compatibility (without /api/v1 prefix)
from app.api.routes.analyze import analyze_code
from app.api.schemas.analyze_schemas import AnalyzeResponse, AnalyzeRequest
from fastapi import Depends
from sqlalchemy.orm import Session

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code_direct(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Direct analyze endpoint for frontend compatibility."""
    return await analyze_code(request, db)

logger = get_logger(__name__)

@app.get("/")
async def root():
    return {
        "message": APP_TITLE,
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "analyze": "/analyze (or /api/v1/analyze)",
            "history": "/api/v1/analyze/history",
            "get_analysis": "/api/v1/analyze/{analysis_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint that verifies database connection"""
    health_status = {
        "status": "healthy",
        "service": APP_TITLE,
        "database": "unknown"
    }
    
    # Check database connection
    try:
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
        db.close()
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status

@app.exception_handler(EngageFatalException)
async def fatal_exception_handler(request, exc: EngageFatalException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=CommonResponse[dict](
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=exc.detail,
            message_id="0",
            data={}
        ).model_dump()
    )

@app.exception_handler(EngageNonFatalException)
async def non_fatal_exception_handler(request, exc: EngageNonFatalException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=CommonResponse[dict](
            code=status.HTTP_400_BAD_REQUEST,
            message=exc.detail,
            message_id="0",
            data={}
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle FastAPI request validation errors by converting them to our custom format.
    """
    logger = get_logger(__name__)
    first_error = exc.errors()[0]
    location_parts = [str(loc) for loc in first_error["loc"]]

    if location_parts[0] == "body":
        location_parts.pop(0)

    location = ".".join(location_parts)
    message = f"{location}: {first_error['msg']}"

    logger.error(f"Request validation error: {message}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=CommonResponse[dict](
            code=status.HTTP_400_BAD_REQUEST,
            message=message,
            message_id="0",
            data={}
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """
    Handle all other exceptions.
    """
    logger = get_logger(__name__)
    error_message = str(exc)
    logger.error(f"Unexpected error: {error_message}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=CommonResponse[dict](
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"An unexpected error occurred: {error_message}",
            message_id="0",
            data={}
        ).model_dump()
    )


