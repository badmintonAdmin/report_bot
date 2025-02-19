from aiogram import types
from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, Command
from aiogram.utils.chat_action import ChatActionSender

from tg.core.commands_list import commands as c
from tg.query.get_data import where_tokens
from tg.utils.format_message import format_where_tokens
from tg.utils.filter_data import apply_amount_filter
from tg.core.access import IsAllowed
from gsheets.template import all_format
from local_db.requests import get_report

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


@router.message(Command("where_tokens"), IsAllowed())
async def get_tokens(message: types.Message):
    await message.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.TYPING
    )
    choice_tokens = message.text.split()[1:]
    if not choice_tokens:
        text = "⚠️ You did not specify any tokens. Use:\n\n```\n/where_tokens xBasket,USDC,USDT\n```"
        await message.answer(text, parse_mode="Markdown")
        return
    processing_message = await message.answer(
        "⏳ Processing your request, please wait..."
    )
    await message.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.TYPING
    )
    tokens = choice_tokens[0].split(",")
    tokens = [token.lower().strip() for token in tokens]
    params = {"tokens": tuple(tokens)}

    where_clause = where_tokens(params)

    if where_clause is None or where_clause.empty:
        text = f'The selected tokens "{", ".join(choice_tokens)}" were not found or the database has not been updated yet.'
    else:
        where_clause = where_clause.sort_values(
            by=["token", "amount"], ascending=[True, False]
        ).reset_index(drop=True)

        if len(choice_tokens) > 1:
            where_clause = apply_amount_filter(where_clause, choice_tokens[1])

        text = (
            format_where_tokens(where_clause)
            if not where_clause.empty
            else f'The selected tokens "{", ".join(choice_tokens)}" were not found.'
        )

    await send_long_message(message, text)
    await processing_message.delete()


async def send_long_message(message: types.Message, text: str, chunk_size=4000):
    paragraphs = text.split("\n")
    buffer = ""
    for paragraph in paragraphs:
        if len(buffer) + len(paragraph) + 1 < chunk_size:
            buffer += paragraph + "\n"
        else:
            await message.answer(buffer.strip(), parse_mode="Markdown")
            buffer = paragraph + "\n"

    if buffer.strip():
        await message.answer(buffer.strip(), parse_mode="Markdown")


@router.message(Command("get_topup"), IsAllowed())
async def top_up(message: types.Message):
    processing_message = await message.answer(
        "⏳ Processing your request, please wait..."
    )

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    text = all_format()

    await message.answer(text, parse_mode="Markdown")
    await processing_message.delete()
