"""Lets a logged-in user list their own past AI requests, with pagination."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.request_log import RequestLog
from app.models.user import User
from app.schemas.request_log import PaginatedRequestLogs, RequestLogOut

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=PaginatedRequestLogs)
def list_my_requests(
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page (max 50)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # only ever query the current user's own logs - never let one user see
    # another user's history
    base_query = (
        db.query(RequestLog)
        .filter(RequestLog.user_id == current_user.id)
        .order_by(RequestLog.created_at.desc())
    )

    total = base_query.count()
    logs = base_query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedRequestLogs(
        total=total,
        page=page,
        page_size=page_size,
        items=[RequestLogOut.model_validate(log) for log in logs],
    )
