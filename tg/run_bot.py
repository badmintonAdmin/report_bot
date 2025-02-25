import asyncio

from tg.core.lndx_bot import LndxBot
import logging


async def main():
    bot = LndxBot()
    logging.basicConfig(level=logging.INFO)
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
