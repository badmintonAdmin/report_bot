from aiogram.types import Message
from aiogram.filters import BaseFilter
from general_config import config

OWNER_ID = int(config.OWNER_ID)
ALLOWED_GROUP_ID = int(config.ALLOWED_GROUP_ID)


class IsAllowed(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.chat.type == "private":
            if message.from_user.id == OWNER_ID:
                return True
            await message.answer("🚫 Only admin can send messages.")
            return False
        if message.chat.type in ["group", "supergroup"]:
            if message.chat.id == ALLOWED_GROUP_ID:
                return True
            await message.answer("🚫 Only admin can send messages.")
            return False
        await message.answer("🚫 Only admin can send messages.")
        return False
