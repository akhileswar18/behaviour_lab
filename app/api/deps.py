from sqlmodel import Session

from app.persistence.engine import get_engine


def get_session() -> Session:
    with Session(get_engine()) as session:
        yield session
