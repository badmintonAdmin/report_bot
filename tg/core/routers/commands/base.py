from aiogram import Router, types
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, Command

from tg.core.access import IsAllowed
from tg.core.commands_list import commands as c
from apis.coingecko.main import get_token_price
from aiogram.utils import markdown as m

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "Hello! I'm LandX bot.\n"
        "Send the command /help to get a list of all commands."
    )


@router.message(Command("help"), IsAllowed())
async def help_command(message: types.Message):
    help_text = "Here are the available commands:\n\n"
    for command, description in c.items():
        help_text += f"{command}: {description}\n"
    await message.answer(help_text, parse_mode=None)


@router.message(Command("lndx_price"), IsAllowed())
async def get_price_command(message: types.Message):
    await message.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.TYPING
    )
    price = get_token_price("landx-governance-token")
    text = f"Current LNDX price: {m.hbold(f'${price}')} from coingecko"
    await message.answer(text)
