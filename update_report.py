import random
import string
from datetime import datetime
from core.run import get_remote_report
from tg.core.lndx_bot import LndxBot
import asyncio
from general_config import config
from local_db.requests import add_report


async def save_report_to_log():
    report = get_remote_report()
    bot = LndxBot()

    today = datetime.today()
    await add_report(report, today)
    try:
        await bot.send_message(chat_id=config.OWNER_ID, text=report)
    finally:
        await bot.bot.session.close()


if __name__ == "__main__":
    asyncio.run(save_report_to_log())
