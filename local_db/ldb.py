from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from general_config import config
from contextlib import asynccontextmanager


class LocalDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            engine = create_async_engine(
                config.DATABASE_URL,
                echo=True,
            )
            cls._instance.session_factory = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return cls._instance

    @asynccontextmanager
    async def get_session(self):
        session = self.session_factory()
        try:
            yield session
        finally:
            await session.close()


ldb = LocalDB()
