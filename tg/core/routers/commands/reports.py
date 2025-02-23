from aiogram import Router, types
from aiogram.enums import ChatAction
from aiogram.filters import Command

from gsheets.template import all_format
from local_db.requests import get_report
from tg.core.access import IsAllowed

router = Router()


@router.message(Command("get_report"), IsAllowed())
async def report_command(message: types.Message):
    last_report = await get_report()
    if last_report is None:
        report_content = "No reports found for today - please try again later."
    else:
        report_content = last_report
    await message.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.TYPING
    )
    await message.answer(report_content)


@router.message(Command("get_topup"), IsAllowed())
async def top_up(message: types.Message):
    processing_message = await message.answer(
        "⏳ Processing your request, please wait..."
    )

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    text = all_format()

    await message.answer(text, parse_mode="Markdown")
    await processing_message.delete()
