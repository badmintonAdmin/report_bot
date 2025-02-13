from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from general_config import config


class BaseBot(Bot):
    def __init__(self):
        token = config.TOKEN
        self.log = "../../report_logs"
        default_properties = DefaultBotProperties(parse_mode="Markdown")
        super().__init__(token=token, default=default_properties)


basebot = BaseBot()
