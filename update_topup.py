from gsheets.template import all_format
from tg.core.lndx_bot import LndxBot
import asyncio
from general_config import config


async def get_topup():
    bot = LndxBot()
    report = all_format()
    try:
        await bot.send_message(chat_id=config.OWNER_ID, text=report)
    finally:
        await bot.bot.session.close()


if __name__ == "__main__":
    asyncio.run(get_topup())
