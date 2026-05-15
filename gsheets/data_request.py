import time

import gspread
import pandas as pd
from requests.exceptions import ConnectionError, ChunkedEncodingError, Timeout

from general_config import config


GSHEETS_RETRIES = 3
GSHEETS_BACKOFF_SECONDS = 2
TRANSIENT_ERRORS = (ConnectionError, ChunkedEncodingError, Timeout)


class Gsheet:
    def __init__(self):
        self.json_path = config.GOOGLE_CREDENTIALS_PATH
        self.table_id = config.SPREADSHEET_ID
        self.gc = gspread.service_account(self.json_path)

    def _reconnect(self):
        self.gc = gspread.service_account(self.json_path)

    def get_data(self, sheet_number: int):
        last_err = None
        for attempt in range(1, GSHEETS_RETRIES + 1):
            try:
                table = self.gc.open_by_key(self.table_id).get_worksheet(sheet_number)
                return pd.DataFrame(table.get_all_records())
            except TRANSIENT_ERRORS as e:
                last_err = e
                print(
                    f"gsheets transient error (attempt {attempt}/{GSHEETS_RETRIES}): {e}"
                )
                if attempt < GSHEETS_RETRIES:
                    time.sleep(GSHEETS_BACKOFF_SECONDS * attempt)
                    self._reconnect()
            except ValueError as ve:
                print(f"ValueError: {ve}")
                return pd.DataFrame()
        print(f"gsheets gave up after {GSHEETS_RETRIES} attempts: {last_err}")
        return None


gsheet = Gsheet()
