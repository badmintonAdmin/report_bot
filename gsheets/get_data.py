from gsheets.data_request import gsheet
from general_config import config
import pandas as pd
from datetime import timedelta


def get_policies():
    df = gsheet.get_data(int(config.POLICIES))
    if df.empty:
        return ["The file with pools data is empty"]
    filtered_df = filtered(df, 3)
    if filtered_df.empty:
        return ["No pools to top up"]
    gen_content = ["*==Top Up Policies==*"]
    now = pd.Timestamp.now()
    for i, row in filtered_df.iterrows():
        gen_content.append(
            f"{row['NO']}: (ID {row['id']}) | {row['name']} | DAYS: {(row['date'] - now).days}"
        )
        gen_content.append("=" * 32)

    return gen_content


def get_pools():
    df = gsheet.get_data(int(config.POOLS))
    if df.empty:
        return ["The file with pools data is empty"]
    filtered_df = filtered(df, 5)
    if filtered_df.empty:
        return ["No pools to top up"]
    gen_content = ["*==Top Up Pools==*"]
    now = pd.Timestamp.now()
    for i, row in filtered_df.iterrows():
        gen_content.append(
            f"{row['NO']}: {row['name']} | DAYS: {(row['date'] - now).days}"
        )
        gen_content.append("=" * 32)

    return gen_content


def get_loans():
    df = gsheet.get_data(int(config.LOANS))
    if df.empty:
        return ["The file with loans data is empty"]
    filtered_df = filtered(df, 5)
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
    filtered_df = filtered(df, 3)
    if filtered_df.empty:
        return ["No epochs to top up"]
    gen_content = ["*=== Top UP epochs ==*"]
    now = pd.Timestamp.now()
    for i, row in filtered_df.iterrows():
        gen_content.append(
            f"Epoch: {row['Epoch']} | Chain: {row['Chain']} | DAYS: {(row['date'] - now).days}"
        )
        gen_content.append("=" * 32)
    return gen_content


def filtered(df: pd.DataFrame, days: int):
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    df["done"] = df["done"].str.strip().str.upper() == "TRUE"
    start_date = pd.Timestamp.now() + timedelta(days=days)
    filtered_df = df[(df["date"] <= start_date) & (df["done"] == False)]
    return filtered_df
