"""
Entry point of the application.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.routers import ai, auth

app = FastAPI(
    title="AI Content Assistant API",
    description="A learning project: FastAPI + PostgreSQL + Gemini powered content assistant.",
    version="0.1.0",
)

app.include_router(auth.router)
app.include_router(ai.router)


@app.get("/health")
def health_check():
    """Simple endpoint to check that the server is alive."""
    return {"status": "ok"}
