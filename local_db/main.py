from local_db.models.command import CommandModel
from local_db.ldb import ldb
from sqlalchemy import select


async def get_command():
    async with ldb.get_session() as session:
        result = await session.scalar(select(CommandModel))
        print(result)
        return result


async def get_report():
    async with ldb.get_session() as session:
        await session.commit()
