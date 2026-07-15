"""
This module sets up the SQLAlchemy "engine" (the thing that actually talks to
PostgreSQL) and a session factory (SessionLocal) that creates one DB session
per request.

Base is the parent class every ORM model (User, RequestLog, ...) inherits
from. SQLAlchemy uses it to know which Python classes map to which tables.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# engine = the connection pool to PostgreSQL. Created once, reused everywhere.
engine = create_engine(settings.database_url)

# SessionLocal is a "factory": calling SessionLocal() gives us a new DB session.
# autocommit=False / autoflush=False = we control exactly when data is written.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency. For every request that needs the DB, FastAPI calls
    this function, injects the returned session into the endpoint, and
    (thanks to the try/finally) closes it again once the request is done.
    This way we never "leak" open DB connections.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
