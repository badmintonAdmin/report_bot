import asyncio
from tg.core.lndx_bot import LndxBot


async def main():
    bot = LndxBot()
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
