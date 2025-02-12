from datetime import datetime
import os
from ..config import general_config


def get_latest_file_by_date():
    folder = general_config.report_folder
    today = datetime.today().strftime("%Y_%m_%d")
    files = os.listdir(folder)
    today_files = [f for f in files if f.startswith(today) and f.endswith(".txt")]

    if not today_files:
        return None
    latest_file = max(
        today_files, key=lambda f: os.path.getmtime(os.path.join(folder, f))
    )
    return latest_file
