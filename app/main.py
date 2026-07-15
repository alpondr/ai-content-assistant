"""
Entry point of the application.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.routers import ai, auth

app = FastAPI(
    title="AI Content Assistant API",
    description="A learning project: FastAPI + PostgreSQL + Gemini powered content assistant.",
    version="0.1.0",
)

# app.state.limiter is where slowapi's decorators (used in routers/ai.py)
# look up the Limiter instance at request time.
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": (
                f"You've reached your daily limit of {settings.daily_request_limit} "
                "AI requests. Please try again tomorrow."
            )
        },
    )


app.include_router(auth.router)
app.include_router(ai.router)


@app.get("/health")
def health_check():
    """Simple endpoint to check that the server is alive."""
    return {"status": "ok"}
