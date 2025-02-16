from aiogram.types import BotCommand
from tg.core.commands_list import commands


async def set_bot_commands(bot):
    bot_commands = [
        BotCommand(command=cmd, description=desc)
        for cmd, desc in commands.items()
        if not desc.startswith("=")
    ]
    await bot.set_my_commands(bot_commands)
