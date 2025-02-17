from local_db.models.command import CommandModel
from local_db.models.report import ReportModel
from local_db.models.topup import TopupModel
from local_db.ldb import ldb
from sqlalchemy import select, desc


async def get_command():
    async with ldb.get_session() as session:
        result = await session.scalars(select(CommandModel))
        print(result)
        return result


async def get_report():
    async with ldb.get_session() as session:
        result = await session.execute(
            select(ReportModel.report).order_by(desc(ReportModel.date)).limit(1)
        )
        report = result.scalar()
        return report if report else None


async def add_report(report, date):
    async with ldb.get_session() as session:
        session.add(ReportModel(date_report=date, report=report))
        await session.commit()


async def add_topup(data: str):
    async with ldb.get_session() as session:
        session.add(TopupModel(topup=data))
        await session.commit()
