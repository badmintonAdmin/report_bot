from contracts import contract_data
from report.config_data import config_data
import pandas as pd


def get_xTokens_info():
    xTokens = config_data.xTokens
    arr = []
    for name in xTokens:
        amount = contract_data.get_xtokens_data(xTokens[name])
        arr.append({"tokens": name, "unclaimed": amount / 1e6})

    df = pd.DataFrame(arr)
    return df


def get_cTokens_info():
    cTokens = config_data.cTokens
    arr = []
    for name in cTokens:
        info = contract_data.get_ctokens_data(cTokens[name])
        arr.append(
            {
                "tokens": name,
                "balance": info["balance"] / 1e6,
                "total_supply": info["count"] / 1e6,
            }
        )

    df = pd.DataFrame(arr)
    return df


def get_lcg_info():

    borrow_data = contract_data.get_total_borrowed()
    staked = contract_data.get_total_staked()
    available = contract_data.get_available()

    borrowed = borrow_data["total_borrowed"] / 1e6
    staked = staked["total_staked"] / 1e6
    available = available["balance"] / 1e6
    avg_apr = borrow_data["borrow_apr"] / 100
    apr = borrowed * avg_apr / staked - 0.5
    arr = []
    arr.append(
        {
            "borrowed": borrowed,
            "staked": staked,
            "available": available,
            "apr": apr,
        }
    )

    df = pd.DataFrame(arr)
    return df


def get_aave_data():
    data = contract_data.get_aave_data()
    df = pd.DataFrame(data)
    return df
