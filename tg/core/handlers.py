from aiogram import types
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from tg.utils.find_report import get_latest_file_by_date
from tg.config import general_config as config
from tg.core.commands_list import commands as c
from tg.query.get_data import where_tokens
from tg.utils.format_message import format_where_tokens
from tg.utils.filter_data import apply_amount_filter

router = Router()


@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "Hello! I'm LandX bot.\n"
        "Send the command /help to get a list of all commands."
    )


@router.message(Command("help"))
async def help_command(message: types.Message):
    help_text = "Here are the available commands:\n\n"
    for command, description in c.items():
        help_text += f"{command}: {description}\n"
    await message.answer(help_text, parse_mode=None)


@router.message(Command("get_report"))
async def report_command(message: types.Message):
    report_path = get_latest_file_by_date()
    if report_path is None:
        report_content = "No reports found for today - please try again later."
    else:
        with open(f"{config.report_folder}/{report_path}", "r") as file:
            report_content = file.read()
    await message.answer(report_content)


@router.message(Command("where_tokens"))
async def get_tokens(message: types.Message):
    choice_tokens = message.text.split()[1:]
    if not choice_tokens:
        text = "⚠️ You did not specify any tokens. Use:\n\n```\n/where_tokens xBasket,USDC,USDT\n```"
        await message.answer(text, parse_mode="Markdown")
        return
    processing_message = await message.answer(
        "⏳ Processing your request, please wait..."
    )
    tokens = choice_tokens[0].split(",")
    tokens = [token.lower().strip() for token in tokens]
    params = {"tokens": tuple(tokens)}

    where_clause = where_tokens(params)
    if where_clause is None or where_clause.empty:
        text = f'The selected tokens "{", ".join(choice_tokens)}" were not found or the database has not been updated yet.'
        await message.answer(text)
        await processing_message.delete()
        return

    where_clause = where_clause.sort_values(
        by=["token", "amount"], ascending=[True, False]
    ).reset_index(drop=True)
    if len(choice_tokens) > 1:
        data = apply_amount_filter(where_clause, choice_tokens[1])
        if data.empty:
            await processing_message.delete()
            text = f'The selected tokens "{", ".join(choice_tokens)}" were not found.'
            await send_long_message(message, text)
            return
        else:
            text = format_where_tokens(data)
            await send_long_message(message, text)
            return

    text = format_where_tokens(where_clause)
    await send_long_message(message, text)
    await processing_message.delete()


async def send_long_message(message: types.Message, text: str, chunk_size=4000):
    for i in range(0, len(text), chunk_size):
        await message.answer(text[i : i + chunk_size], parse_mode="Markdown")
