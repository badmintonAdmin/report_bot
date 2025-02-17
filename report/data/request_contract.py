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
