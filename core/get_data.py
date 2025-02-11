from db import database
from core.data.response import *
from core.data.request_contract import *


def get_all_data():
    big_arr = []
    cash_out = []
    sql_queries = [
        "main.sql",
        "lndx_pools_balance.sql",
        "holders_counts.sql",
        "arb_wallets_cTokens.sql",
        "private_balance.sql",
        "prices_cTokens.sql",
    ]
    db_data = {
        query.replace(".sql", ""): database.execute_query(query)
        for query in sql_queries
    }
    database.close_connection()

    xTokens_data = get_xTokens_info()
    cTokens_data = get_cTokens_info()
    claimable = all_contract_data(xTokens_data, cTokens_data, db_data["prices_cTokens"])
    exchange_data = exchange_balance(db_data["arb_wallets_cTokens"], claimable)

    big_arr.append(all_tokens_to_usd(db_data["main"]))
    big_arr.append(all_liquid_tokens_to_usd(db_data["main"]))
    big_arr.append(lndx_amount(db_data["main"], db_data["lndx_pools_balance"]))
    big_arr.append(amount_usd(db_data["main"]))
    big_arr.append(amount_eth(db_data["main"]))
    big_arr.append(amount_btc(db_data["main"]))
    big_arr.append(xTokens_change(db_data["main"]))
    big_arr.append(lndx_holders(db_data["holders_counts"]))
    big_arr.append(xToken_holders(db_data["holders_counts"]))
    big_arr.append(exchange_data)
    cash_out.append(private_sold(db_data["private_balance"]))

    return big_arr, cash_out
