from datetime import datetime
import os


def get_latest_file_by_date(folder):
    today = datetime.today().strftime("%Y_%m_%d")
    files = os.listdir(folder)
    today_files = [f for f in files if f.startswith(today) and f.endswith(".txt")]

    if not today_files:
        return None
    latest_file = max(
        today_files, key=lambda f: os.path.getmtime(os.path.join(folder, f))
    )
    return latest_file
