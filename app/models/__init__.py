"""
Import all models here so that:
1. `Base.metadata` knows about every table (needed for Alembic autogenerate).
2. Other modules can do `from app.models import User, RequestLog` directly.
"""

from app.models.user import User
from app.models.request_log import RequestLog

__all__ = ["User", "RequestLog"]
