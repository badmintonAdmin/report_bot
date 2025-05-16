from aiogram.types import BotCommand


async def set_bot_commands(bot):
    bot_commands = [
        BotCommand(command="start", description="Start bot"),
        BotCommand(command="help", description="Get all available commands"),
        BotCommand(command="aave", description="Get info from AAVE"),
    ]
    await bot.set_my_commands(bot_commands)
