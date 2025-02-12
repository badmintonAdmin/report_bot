from aiogram import Dispatcher, F
from base_bot import basebot
from aiogram.filters import CommandStart, Command
from handlers import start_command, help_command, report_command


class LndxBot:
    def __init__(self):
        self.bot = basebot
        self.dp = Dispatcher()

    def register_handlers(self):
        self.dp.message.register(start_command, CommandStart())
        self.dp.message.register(help_command, Command("help"))
        self.dp.message.register(report_command, Command("get_report"))

    async def run(self):
        self.register_handlers()
        print("Bot running....")
        await self.dp.start_polling(self.bot)
