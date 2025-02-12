from aiogram import types
from tg.utils.find_report import get_latest_file_by_date
from tg.config import general_config as config
from commands_list import commands as c


async def start_command(message: types.Message):
    await message.answer(
        "Hello! I'm LandX bot.\n"
        "Send the command /help to get a list of all commands."
    )


async def help_command(message: types.Message):
    help_text = "Here are the available commands:\n\n"
    for command, description in c.items():
        help_text += f"{command}: {description}\n"
    await message.answer(help_text, parse_mode=None)


async def report_command(message: types.Message):
    report_path = get_latest_file_by_date()
    if report_path is None:
        report_content = "No reports found for today - please try again later."
    else:
        with open(f"{config.report_folder}/{report_path}", "r") as file:
            report_content = file.read()
    await message.answer(report_content)
