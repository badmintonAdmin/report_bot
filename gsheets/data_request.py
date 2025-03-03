import gspread
import pandas as pd
from general_config import config


class Gsheet:
    def __init__(self):
        self.json_path = config.GOOGLE_CREDENTIALS_PATH
        self.table_id = config.SPREADSHEET_ID
        self.gc = gspread.service_account(self.json_path)

    def get_data(self, sheet_number: int):
        try:
            table = self.gc.open_by_key(self.table_id).get_worksheet(sheet_number)
            data = pd.DataFrame(table.get_all_records())
            return data

        except ValueError as ve:
            print(f"ValueError: {ve}")


gsheet = Gsheet()
