from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from local_db.models.command import CommandModel
from general_config import config
from sqlalchemy import select


engine = create_async_engine(
    config.DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_command():
    async with AsyncSessionLocal() as session:
        commands = await session.scalar(select(CommandModel))
        print(commands)
        return commands


async def get_report():
    async with AsyncSessionLocal() as session:
        await session.commit()
