from gsheets.data_request import gsheet
from general_config import config
import pandas as pd
from datetime import timedelta


def get_policies():
    df = gsheet.get_data(int(config.POLICIES))

    print(df)


def get_loans():
    df = gsheet.get_data(int(config.LOANS))
    if df.empty:
        return ["The file with loans data is empty"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    df["done"] = df["done"].str.strip().str.upper() == "TRUE"
    start_date = pd.Timestamp.now() + timedelta(days=5)
    filtered_df = df[(df["date"] <= start_date) & (df["done"] == False)]
    if filtered_df.empty:
        return ["No loan payments due"]
    gen_content = ["*==LANDX CREDIT GATEWAY==*"]
    now = pd.Timestamp.now()
    for i, row in filtered_df.iterrows():
        gen_content.append(
            f"{row['NO']}:{row['name']} | Total due: {row['total']} | DAYS: {(row['date'] - now).days}"
        )
        gen_content.append("=" * 32)

    return gen_content


def get_epoch():
    df = gsheet.get_data(int(config.EPOCH))
    if df.empty:
        return ["The file with epoch data is empty"]
    df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce", dayfirst=True)
    df["Done"] = df["Done"].str.strip().str.upper() == "TRUE"
    start_date = pd.Timestamp.now() + timedelta(days=3)
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


content = get_loans()
print(content)
