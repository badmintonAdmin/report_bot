import random
import string
from datetime import datetime
from core.run import get_report
from tg.core.lndx_bot import LndxBot
import asyncio
from general_config import config
from local_db.requests import add_report


def generate_random_string(length=5):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


async def save_report_to_log():
    report = get_report()
    bot = LndxBot()

    today = datetime.today()
    await add_report(report, today)

    try:
        await bot.send_message(chat_id=config.OWNER_ID, text=report)
    finally:
        await bot.bot.session.close()


if __name__ == "__main__":
    asyncio.run(save_report_to_log())
