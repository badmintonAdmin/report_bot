from aiogram import Dispatcher, F
from tg.core.base_bot import basebot
from tg.core.handlers import router


class LndxBot:
    def __init__(self):
        self.bot = basebot
        self.dp = Dispatcher()
        self.dp.include_router(router)

    async def send_message(self, chat_id: str, text: str) -> None:
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            print(f"Error sending message: {e}")

    async def run(self):
        print("Bot running....")
        await self.dp.start_polling(self.bot)
