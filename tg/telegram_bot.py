from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os
from dotenv import load_dotenv

load_dotenv()


class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TOKEN")
        self.application = Application.builder().token(self.token).build()

    async def start(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text("Hello, I am your bot!")

    async def send_message(self, chat_id: str, text: str) -> None:
        await self.application.bot.send_message(chat_id=chat_id, text=text)

    def run(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.run_polling()


tgbot = TelegramBot()
