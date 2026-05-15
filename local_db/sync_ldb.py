from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from general_config import config


_sync_url = str(config.DATABASE_URL).replace("+aiosqlite", "")
_engine = create_engine(_sync_url)
_SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False)


@contextmanager
def sync_session():
    session = _SessionFactory()
    try:
        yield session
    finally:
        session.close()
