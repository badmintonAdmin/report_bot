from aiogram import Router, types
from aiogram.enums import ChatAction
from aiogram.filters import Command

from gsheets.template import all_format
from local_db.requests import get_report
from tg.core.access import IsAllowed
from report.data.request_contract import get_aave_data

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

    await message.answer(text)
    await processing_message.delete()


@router.message(Command("lcg"), IsAllowed())
async def top_up(message: types.Message):
    processing_message = await message.answer(
        "⏳ Processing your request, please wait..."
    )

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    text = "Coming soon..."
    await message.answer(text)
    await processing_message.delete()


@router.message(Command("aave"), IsAllowed())
async def top_up(message: types.Message):
    processing_message = await message.answer(
        "⏳ Processing your request, please wait..."
    )
    data = get_aave_data()
    row = data.iloc[0]
    str_line = (
        f"📊 <b>AAVE information:</b>\n"
        f"💰 Supply: ${row['supply']:,.2f}\n"
        f"💸 Borrowed: ${row['borrowed']:,.2f}\n"
        f"⚖️ Net: ${row['net']:,.2f}\n"
        f"🛡️ Health Factor: {row['hf']:,.2f}"
    )
    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await message.answer(str_line)
    await processing_message.delete()
