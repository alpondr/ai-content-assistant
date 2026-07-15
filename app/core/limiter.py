"""
Rate limiting setup, using slowapi (a wrapper around the "limits" library).

The requirement is: each USER gets a shared daily quota across all 3 AI
endpoints (not one quota per endpoint, and not limited by IP address).

slowapi identifies "who is asking" through a key_func that receives the raw
Request. It runs before FastAPI's own dependency injection resolves our
get_current_user, so we can't reuse that dependency here - instead we
decode the JWT ourselves, just to get an identity string to count against.
This is a bit of duplicated logic with get_current_user, but the two serve
different purposes: get_current_user *authenticates* (401 if invalid),
this only *identifies* (falls back to IP if there's no valid token, but
those requests get rejected with 401 before they could do anything anyway).
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.security import decode_access_token


def get_user_identifier(request: Request) -> str:
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1]
        email = decode_access_token(token)
        if email:
            return email
    return get_remote_address(request)


limiter = Limiter(key_func=get_user_identifier)
