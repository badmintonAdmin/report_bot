from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


class BaseBot(Bot):
    def __init__(self, bot_token):
        default_properties = DefaultBotProperties(parse_mode="HTML")
        super().__init__(token=bot_token, default=default_properties)
