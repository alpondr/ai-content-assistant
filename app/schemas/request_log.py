"""Pydantic schema for reading back RequestLog rows (history endpoint, Step 9)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RequestLogOut(BaseModel):
    id: int
    request_type: str
    input_text: str
    output_text: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedRequestLogs(BaseModel):
    """Wraps a page of RequestLogOut items with the info needed to fetch other pages."""

    total: int
    page: int
    page_size: int
    items: list[RequestLogOut]
