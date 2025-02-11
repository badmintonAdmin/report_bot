from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import os
from .find_report import get_latest_file_by_date
from dotenv import load_dotenv

load_dotenv()


class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TOKEN")
        self.log = "../report_logs"
        self.application = Application.builder().token(self.token).build()

    async def start(self, update: Update, context: CallbackContext) -> None:
        await update.message.reply_text(
            "Hello, I am LandX report bot! "
            "To receive the report, please use the command /get_report"
        )

    async def get_chat_id(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.message.chat_id
        await update.message.reply_text(f"Chat ID: {chat_id}")

    async def get_report(self, update: Update, context: CallbackContext) -> None:
        report_path = get_latest_file_by_date(self.log)
        if report_path is None:
            report_content = "No reports found for today - please try again later."
        else:
            with open(f"{self.log}/{report_path}", "r") as file:
                report_content = file.read()
        await update.message.reply_text(report_content, parse_mode="Markdown")

    async def send_message(self, chat_id: str, text: str) -> None:
        await self.application.bot.send_message(
            chat_id=chat_id, text=text, parse_mode="Markdown"
        )

    def run(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("get_report", self.get_report))
        self.application.add_handler(CommandHandler("get_chatid", self.get_chat_id))
        self.application.run_polling()


tgbot = TelegramBot()
