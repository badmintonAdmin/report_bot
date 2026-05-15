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


LOANS_DAYS_THRESHOLD = 5


def short_addr(addr: str) -> str:
    if not isinstance(addr, str) or len(addr) < 10:
        return str(addr)
    return f"{addr[:6]}…{addr[-4:]}"


def get_lcg_loans() -> List[str]:
    loans = contract_data.get_lcg_loans()
    if loans is None:
        return [m.hbold("Error to get LCG loans data"), "=" * 32]
    if not loans:
        return [m.hbold("No loan payments due"), "=" * 32]

    rows = []
    for loan in loans:
        unpaid = loan.get("unpaid_periods", 0)
        if loan["next_interest_ts"] > 0 and (loan["interest_due"] > 0 or unpaid > 0):
            rows.append(
                {
                    "id": loan["id"],
                    "borrower": loan["borrower"],
                    "kind": "Interest",
                    "amount_usdc": loan["interest_due"] / 1e6,
                    "due_ts": loan["next_interest_ts"],
                    "unpaid_periods": unpaid,
                }
            )
        if loan["maturity_ts"] > 0 and loan["principal_debt"] > 0:
            rows.append(
                {
                    "id": loan["id"],
                    "borrower": loan["borrower"],
                    "kind": "Principal",
                    "amount_usdc": loan["principal_debt"] / 1e6,
                    "due_ts": loan["maturity_ts"],
                    "unpaid_periods": 0,
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        return [m.hbold("No loan payments due"), "=" * 32]

    df["due_date"] = pd.to_datetime(df["due_ts"], unit="s", utc=True)
    deadline = pd.Timestamp.now(tz=timezone.utc) + timedelta(days=LOANS_DAYS_THRESHOLD)
    df = df[df["due_date"] <= deadline].copy()

    if df.empty:
        return [m.hbold("No loan payments due"), "=" * 32]

    now = pd.Timestamp.now(tz=timezone.utc).normalize()
    result = [m.hbold("==LANDX CREDIT GATEWAY==")]
    for _, row in df.iterrows():
        days_left = (row["due_date"] - now).days
        overdue_flag = (
            f" | OVERDUE: {row['unpaid_periods']} period(s)"
            if row["unpaid_periods"] and row["unpaid_periods"] > 0
            else ""
        )
        result.append(
            f"{row['id']}: {short_addr(row['borrower'])} | "
            f"{row['kind']} due: ${row['amount_usdc']:,.2f} | "
            f"DAYS: {days_left}{overdue_flag}"
        )
        result.append("=" * 32)

    return result


def get_lcg_data():
    return 1


get_epoch()
