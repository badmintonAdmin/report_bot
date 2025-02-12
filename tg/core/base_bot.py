from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
import os
from dotenv import load_dotenv

load_dotenv()


class BaseBot(Bot):
    def __init__(self):
        token = os.getenv("TOKEN")
        self.log = "../../report_logs"
        default_properties = DefaultBotProperties(parse_mode="Markdown")
        super().__init__(token=token, default=default_properties)


basebot = BaseBot()
