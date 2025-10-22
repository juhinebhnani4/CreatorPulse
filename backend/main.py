"""
CreatorPulse FastAPI Backend - Main Application Entry Point.

This is a frontend-agnostic REST API that supports:
- Streamlit frontend (MVP)
- Next.js frontend (future)
- Mobile apps (future)
- Public API integrations

Architecture:
- Pure JSON responses
- JWT authentication
- CORS enabled
- API versioning (/api/v1/*)
- Consistent error handling
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import json

from backend.settings import settings
from backend.middleware.cors import setup_cors
from backend.middleware.rate_limiter import limiter
from backend.models.responses import APIResponse


# Custom JSONResponse that handles Unicode properly
class UnicodeJSONResponse(JSONResponse):
    """JSONResponse that properly handles Unicode characters (emojis, etc.)"""
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,  # Don't escape Unicode characters
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


# Create FastAPI app with custom response class
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Frontend-agnostic REST API for CreatorPulse AI Newsletter Generator",
    docs_url="/docs" if settings.debug else None,  # Disable docs in production
    redoc_url="/redoc" if settings.debug else None,
    default_response_class=UnicodeJSONResponse,  # Use Unicode-aware JSON responses
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup CORS
setup_cors(app)


# =============================================================================
# EXCEPTION HANDLERS (Consistent Error Responses)
# =============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with consistent format."""
    return UnicodeJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse.error_response(
            code="VALIDATION_ERROR",
            message="Invalid request data",
            details={"errors": exc.errors()}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    if settings.debug:
        # In debug mode, show full error
        return UnicodeJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponse.error_response(
                code="INTERNAL_ERROR",
                message=str(exc),
                details={"type": type(exc).__name__}
            ).model_dump()
        )
    else:
        # In production, hide error details
        return UnicodeJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponse.error_response(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred"
            ).model_dump()
        )


# =============================================================================
# ROOT ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information."""
    return APIResponse.success_response({
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": f"{settings.backend_url}/docs" if settings.debug else None,
        "api_v1": f"{settings.backend_url}{settings.api_v1_prefix}",
    })


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return APIResponse.success_response({
        "status": "healthy",
        "environment": settings.environment,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    })


# =============================================================================
# API v1 ROUTES
# =============================================================================

from backend.api.v1 import auth, workspaces, content, newsletters, subscribers, delivery, scheduler, style, trends, feedback, analytics
from backend.api import tracking
# from backend.api.v1 import jobs

app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])
app.include_router(workspaces.router, prefix=f"{settings.api_v1_prefix}/workspaces", tags=["Workspaces"])
app.include_router(content.router, prefix=f"{settings.api_v1_prefix}/content", tags=["Content"])
app.include_router(newsletters.router, prefix=f"{settings.api_v1_prefix}/newsletters", tags=["Newsletters"])
app.include_router(subscribers.router, prefix=f"{settings.api_v1_prefix}/subscribers", tags=["Subscribers"])
app.include_router(delivery.router, prefix=f"{settings.api_v1_prefix}/delivery", tags=["Delivery"])
app.include_router(scheduler.router, prefix=f"{settings.api_v1_prefix}/scheduler", tags=["Scheduler"])
app.include_router(style.router, prefix=f"{settings.api_v1_prefix}/style", tags=["Style Training"])
app.include_router(trends.router, prefix=f"{settings.api_v1_prefix}/trends", tags=["Trends Detection"])
app.include_router(feedback.router, prefix=f"{settings.api_v1_prefix}/feedback", tags=["Feedback & Learning"])
app.include_router(analytics.router, prefix=f"{settings.api_v1_prefix}/analytics", tags=["Analytics"])
app.include_router(tracking.router, prefix="/track", tags=["Tracking"])
# app.include_router(jobs.router, prefix=f"{settings.api_v1_prefix}/jobs", tags=["Jobs"])


# =============================================================================
# STARTUP & SHUTDOWN EVENTS
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print(f"[STARTUP] {settings.app_name} v{settings.app_version} starting...")
    print(f"[INFO] Environment: {settings.environment}")
    print(f"[INFO] Backend URL: {settings.backend_url}")
    print(f"[INFO] API v1: {settings.backend_url}{settings.api_v1_prefix}")
    if settings.debug:
        print(f"[INFO] Docs: {settings.backend_url}/docs")

    # Test Supabase connection
    if settings.supabase_url and settings.supabase_key:
        print(f"[OK] Supabase configured: {settings.supabase_url}")
    else:
        print("[WARN] Supabase not configured - set SUPABASE_URL and SUPABASE_KEY")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print(f"[SHUTDOWN] {settings.app_name} shutting down...")


# =============================================================================
# MAIN (for local development with uvicorn)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
