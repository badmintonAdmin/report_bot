from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Union

import pandas as pd
from aiogram.utils import markdown as m

from contracts.contract_data import contract_data


DAYS_THRESHOLD = 4


def get_epoch() -> Union[List[str], None]:
    arb_epoch = contract_data.get_epoch("arb")
    eth_epoch = contract_data.get_epoch("eth")
    if not arb_epoch or not eth_epoch:
        return [m.hbold("Error to get epoch data"), "=" * 32]

    epochs = {
        "arb": arb_epoch,
        "eth": eth_epoch,
    }

    rows = []
    for chain, info in epochs.items():
        epoch_number, start_ts, end_ts = info["epoch"]
        next_epoch = info["next_epoch"][0]
        start_date = datetime.fromtimestamp(start_ts, tz=timezone.utc)
        end_date = datetime.fromtimestamp(end_ts, tz=timezone.utc)
        rows.append(
            {
                "Chain": chain.upper(),
                "Epoch": epoch_number,
                "StartDate": start_date,
                "EndDate": end_date,
                "done": True if next_epoch > 0 else False,
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return [m.hbold("The file with epoch data is empty"), "=" * 32]

    filtered_df = filter_epochs(df, DAYS_THRESHOLD)

    if filtered_df.empty:
        return [m.hbold("No epochs to top up"), "=" * 32]

    return format_epoch_rows(filtered_df)


def filter_epochs(df: pd.DataFrame, days: int) -> pd.DataFrame:
    df["EndDate"] = pd.to_datetime(df["EndDate"], errors="coerce")
    deadline = pd.Timestamp.now(tz=timezone.utc) + timedelta(days=days)
    return df[(df["EndDate"] <= deadline) & (df["done"] == False)].copy()


def format_epoch_rows(df: pd.DataFrame) -> List[str]:
    result = [m.hbold("=== Top UP epochs ===")]
    now = pd.Timestamp.now(tz=timezone.utc).normalize()

    for _, row in df.iterrows():
        days_left = (row["EndDate"] - now).days
        result.append(
            f"Epoch: {row['Epoch']} | Chain: {row['Chain']} | DAYS: {days_left}"
        )
        result.append("=" * 32)

    return result


def get_lcg_data():
    return 1


get_epoch()
