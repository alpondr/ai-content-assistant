"""
Request/response schemas for the 3 AI features.
Each feature gets its own request and response shape so FastAPI can validate
input and document output clearly in the auto-generated /docs page.
"""

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=1, description="Long text that should be summarized")


class SummarizeResponse(BaseModel):
    summary: str


class QARequest(BaseModel):
    context: str = Field(min_length=1, description="Text the question is about")
    question: str = Field(min_length=1)


class QAResponse(BaseModel):
    answer: str


class SentimentRequest(BaseModel):
    text: str = Field(min_length=1)


class SentimentResponse(BaseModel):
    sentiment: str  # expected: "positive" | "negative" | "neutral"
