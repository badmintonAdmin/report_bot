from gsheets.data_request import gsheet
from general_config import config
import pandas as pd
from datetime import timedelta


def get_policies():
    df = gsheet.get_data(int(config.POLICIES))
    print(df)


def get_epoch():
    df = gsheet.get_data(int(config.EPOCH))
    if df.empty:
        return ["The file with epoch data is empty"]
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
    df["Done"] = df["Done"].str.strip().str.upper() == "TRUE"
    start_date = pd.Timestamp.now() + timedelta(days=7)
    filtered_df = df[(df["Start Date"] <= start_date) & (df["Done"] == False)]
    if filtered_df.empty:
        return ["No epochs to top up"]
    gen_content = ["*=== Top UP epochs ==*"]
    now = pd.Timestamp.now()
    for i, row in filtered_df.iterrows():
        gen_content.append(
            f"Epoch: {row['Epoch']} | Chain: {row['Chain']} | DAYS: {(row['Start Date'] - now).days}"
        )
        gen_content.append("=" * 32)
    return gen_content


content = get_epoch()
print(content)
