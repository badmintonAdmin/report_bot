import os
from aiogram.types import Message
from aiogram.filters import BaseFilter
from dotenv import load_dotenv

load_dotenv()

OWNER_ID = int(os.getenv("OWNER_ID"))
ALLOWED_GROUP_ID = int(os.getenv("ALLOWED_GROUP_ID"))


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
