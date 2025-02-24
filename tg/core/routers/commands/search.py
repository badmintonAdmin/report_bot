from aiogram import Router, types
from aiogram.enums import ChatAction
from aiogram.filters import Command

from tg.core.access import IsAllowed
from tg.query.get_data import where_tokens
from tg.utils.filter_data import apply_amount_filter
from tg.utils.format_message import format_where_tokens
from aiogram.utils.markdown import hpre

router = Router()


@router.message(Command("where_tokens"), IsAllowed())
async def get_tokens(message: types.Message):
    await message.bot.send_chat_action(
        chat_id=message.chat.id, action=ChatAction.TYPING
    )
    choice_tokens = message.text.split()[1:]
    if not choice_tokens:
        text = f"""⚠️ You did not specify any tokens. Use:
        {hpre("/where_tokens xBasket,USDC,USDT >5")}"""
        await message.answer(text)
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
            await message.answer(buffer.strip())
            buffer = paragraph + "\n"

    if buffer.strip():
        await message.answer(buffer.strip())
