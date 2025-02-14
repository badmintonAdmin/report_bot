from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models.command import CommandModel
from models.report import ReportModel
from general_config import config


engine = create_async_engine(config.DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_command():
    async with AsyncSessionLocal() as session:
        await session.commit()


async def create_report():
    async with AsyncSessionLocal() as session:
        await session.commit()
