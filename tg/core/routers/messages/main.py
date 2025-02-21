from aiogram import Router
from aiogram import types

router = Router(name=__name__)


@router.message()
async def any_message(message: types.Message):
    await message.answer(
        "Hello! I'm LandX bot.\n"
        "Send the command /help to get a list of all commands."
    )
