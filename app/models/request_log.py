"""SQLAlchemy model for the "request_logs" table.

Every time a user calls one of the AI endpoints (summarize, Q&A, sentiment),
we store one row here: who asked, what type of request, the input, the
output, and when. This is what powers the "list my past requests" feature
and lets us count how many requests a user made today (for rate limiting).
"""

import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.session import Base


class RequestType(str, enum.Enum):
    """The 3 AI features our API offers. Used in code, stored as plain text in DB."""

    SUMMARIZE = "summarize"
    QA = "qa"
    SENTIMENT = "sentiment"


class RequestLog(Base):
    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    # stored as a normal string column (not a native Postgres ENUM type) so
    # adding a 4th request type later never needs a DB migration for the enum itself.
    request_type: Mapped[str] = mapped_column(String, nullable=False)

    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="request_logs")
