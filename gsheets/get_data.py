from gsheets.data_request import gsheet
from general_config import config
import pandas as pd
from datetime import timedelta
from aiogram.utils import markdown as m


def get_policies():
    df = gsheet.get_data(int(config.POLICIES))
    if df.empty:
        return ["The file with pools data is empty"]
    filtered_df = filtered(df, 3)
    if filtered_df.empty:
        text = [m.hbold("No policies to top up"), "=" * 32]
        return text
    gen_content = [m.hbold("==Top Up Policies==")]
    now = pd.Timestamp.now().normalize()
    for i, row in filtered_df.iterrows():
        gen_content.append(
            f"{row['NO']}: (ID {row['id']}) | {row['name']} | DAYS: {(row['date'] - now).days}"
        )
        gen_content.append("=" * 32)

    return gen_content


def get_pools():
    df = gsheet.get_data(int(config.POOLS))
    if df.empty:
        text = [m.hbold("The file with pools data is empty"), "=" * 32]
        return text
    filtered_df = filtered(df, 5)
    if filtered_df.empty:
        text = [m.hbold("No pools to top up"), "=" * 32]
        return text
    gen_content = [m.hbold("==Top Up Pools==")]
    now = pd.Timestamp.now().normalize()
    for i, row in filtered_df.iterrows():
        gen_content.append(
            f"{row['NO']}: {row['name']} | DAYS: {(row['date'] - now).days}"
        )
        gen_content.append("=" * 32)

    return gen_content


def get_loans():
    df = gsheet.get_data(int(config.LOANS))
    if df.empty:
        return [m.hbold("The file with loans data is empty")]
    filtered_df = filtered(df, 5)
    if filtered_df.empty:
        text = [m.hbold("No loan payments due"), "=" * 32]
        return text
    gen_content = [m.hbold("==LANDX CREDIT GATEWAY==")]
    now = pd.Timestamp.now().normalize()
    for i, row in filtered_df.iterrows():
        gen_content.append(
            f"{row['NO']}:{row['name']} | Total due: {row['total']} | DAYS: {(row['date'] - now).days}"
        )
        gen_content.append("=" * 32)

    return gen_content


# def get_epoch():
#     df = gsheet.get_data(int(config.EPOCH))
#     if df.empty:
#         text = [m.hbold("The file with epoch data is empty"), "=" * 32]
#         return text
#     filtered_df = filtered(df, 3)
#     if filtered_df.empty:
#         text = [m.hbold("No epochs to top up"), "=" * 32]
#         return text
#     gen_content = [m.hbold("=== Top UP epochs ==")]
#     now = pd.Timestamp.now().normalize()
#     for i, row in filtered_df.iterrows():
#         gen_content.append(
#             f"Epoch: {row['Epoch']} | Chain: {row['Chain']} | DAYS: {(row['date'] - now).days}"
#         )
#         gen_content.append("=" * 32)
#     return gen_content


def filtered(df: pd.DataFrame, days: int):
    df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    df["done"] = df["done"].str.strip().str.upper() == "TRUE"
    start_date = pd.Timestamp.now() + timedelta(days=days)
    filtered_df = df[(df["date"] <= start_date) & (df["done"] == False)]
    return filtered_df
