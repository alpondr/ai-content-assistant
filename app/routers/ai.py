"""
The 3 AI feature endpoints. Each one:
1. requires a logged-in user (get_current_user)
2. calls the matching function in the service layer
3. saves what happened to RequestLog - success or failure alike, so the
   history (Step 9) and the daily rate limit (Step 8) always reflect what
   actually happened
4. if the LLM call failed, returns a clean 503 instead of leaking a
   stack trace or crashing the process
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.database.session import get_db
from app.models.request_log import RequestLog, RequestType
from app.models.user import User
from app.schemas.ai import (
    QARequest,
    QAResponse,
    SentimentRequest,
    SentimentResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from app.services.llm_service import (
    LLMServiceError,
    analyze_sentiment,
    answer_question,
    summarize_text,
)

router = APIRouter(prefix="/ai", tags=["ai"])

LLM_UNAVAILABLE_DETAIL = "AI service is temporarily unavailable. Please try again later."

# all 3 AI endpoints draw from the same daily bucket per user: same limit
# string + same "scope" means slowapi counts them together, not separately.
DAILY_LIMIT = f"{settings.daily_request_limit}/day"
AI_SCOPE = "ai_daily_quota"


def _log_request(db: Session, user_id: int, request_type: RequestType, input_text: str, output_text: str | None) -> None:
    log = RequestLog(
        user_id=user_id,
        request_type=request_type,
        input_text=input_text,
        output_text=output_text,
    )
    db.add(log)
    db.commit()


@router.post("/summarize", response_model=SummarizeResponse)
@limiter.shared_limit(DAILY_LIMIT, scope=AI_SCOPE)
def summarize(
    request: Request,
    payload: SummarizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        summary = summarize_text(payload.text)
    except LLMServiceError:
        _log_request(db, current_user.id, RequestType.SUMMARIZE, payload.text, None)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=LLM_UNAVAILABLE_DETAIL)

    _log_request(db, current_user.id, RequestType.SUMMARIZE, payload.text, summary)
    return SummarizeResponse(summary=summary)


@router.post("/qa", response_model=QAResponse)
@limiter.shared_limit(DAILY_LIMIT, scope=AI_SCOPE)
def question_answer(
    request: Request,
    payload: QARequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # RequestLog only has one input_text column, so we combine context +
    # question into one readable string instead of adding a new DB column.
    combined_input = f"Context: {payload.context}\nQuestion: {payload.question}"

    try:
        answer = answer_question(payload.context, payload.question)
    except LLMServiceError:
        _log_request(db, current_user.id, RequestType.QA, combined_input, None)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=LLM_UNAVAILABLE_DETAIL)

    _log_request(db, current_user.id, RequestType.QA, combined_input, answer)
    return QAResponse(answer=answer)


@router.post("/sentiment", response_model=SentimentResponse)
@limiter.shared_limit(DAILY_LIMIT, scope=AI_SCOPE)
def sentiment(
    request: Request,
    payload: SentimentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = analyze_sentiment(payload.text)
    except LLMServiceError:
        _log_request(db, current_user.id, RequestType.SENTIMENT, payload.text, None)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=LLM_UNAVAILABLE_DETAIL)

    _log_request(db, current_user.id, RequestType.SENTIMENT, payload.text, result)
    return SentimentResponse(sentiment=result)
