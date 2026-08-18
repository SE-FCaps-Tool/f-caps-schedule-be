from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from .config import get_settings


@lru_cache(maxsize=4)
def get_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True)


def get_db() -> Generator[Session, None, None]:
    with Session(get_engine(get_settings().database_url)) as session:
        yield session

