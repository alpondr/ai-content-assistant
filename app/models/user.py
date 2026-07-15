"""SQLAlchemy model for the "users" table."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # we never store the raw password, only its bcrypt hash
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # one user -> many request logs. "back_populates" links it to
    # RequestLog.user so we can go both directions (user.request_logs / log.user).
    request_logs: Mapped[list["RequestLog"]] = relationship(
        "RequestLog", back_populates="user", cascade="all, delete-orphan"
    )
