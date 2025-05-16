from db import database
import report.data.response as res
import report.data.request_contract as con
from report.data.response import lcg_data


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
        "staked.sql",
    ]
    db_data = {
        query.replace(".sql", ""): database.execute_query(query)
        for query in sql_queries
    }
    database.close_connection()

    lcg_data = con.get_lcg_info()
    lcg = res.lcg_data(lcg_data)
    aave = res.aave_data(con.get_aave_data())

    xTokens_data = con.get_xTokens_info()
    cTokens_data = con.get_cTokens_info()
    claimable = res.all_contract_data(
        xTokens_data, cTokens_data, db_data["prices_cTokens"]
    )
    exchange_data = res.exchange_balance(db_data["arb_wallets_cTokens"], claimable)

    big_arr.append(res.all_tokens_to_usd(db_data["main"]))
    big_arr.append(res.all_liquid_tokens_to_usd(db_data["main"]))
    big_arr.append(aave)
    big_arr.append(res.lndx_amount(db_data["main"], db_data["lndx_pools_balance"]))
    big_arr.append(res.amount_usd(db_data["main"]))
    big_arr.append(res.amount_eth(db_data["main"]))
    big_arr.append(res.amount_btc(db_data["main"]))
    big_arr.append(res.xTokens_change(db_data["main"]))
    big_arr.append(res.lndx_holders(db_data["holders_counts"]))
    big_arr.append(res.xToken_holders(db_data["holders_counts"]))
    big_arr.append(exchange_data)
    big_arr.append(lcg)
    big_arr.append(res.invest_balance(db_data["staked"]))
    cash_out.append(res.private_sold(db_data["private_balance"]))

    return big_arr, cash_out
