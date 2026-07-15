"""
Shared FastAPI dependencies.

get_current_user is used by every protected endpoint (AI features, history).
It reads the "Authorization: Bearer <token>" header automatically (that's
what OAuth2PasswordBearer does), decodes it, and loads the matching user
from the database. If anything is wrong, it raises 401 before the endpoint
code even runs.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User

# tokenUrl just tells the /docs page where to get a token from; FastAPI
# itself only cares about reading the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_error

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_error

    return user
