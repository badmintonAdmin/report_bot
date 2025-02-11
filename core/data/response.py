import pandas as pd


def all_tokens_to_usd(data: pd.DataFrame) -> list:
    if data.empty:
        return ["All tokens: NOT DATA"]

    all_token_usd = (
        data.groupby("date")[["total_balance_usd", "abs_diff_usd"]].sum().iloc[0]
    )

    token_usd_str = f"{all_token_usd['total_balance_usd']:,.2f}"
    diff_token_usd = all_token_usd["abs_diff_usd"]
    diff_token_usd_str = f"{abs(diff_token_usd):,.2f}"

    diff_sign = "-$" if diff_token_usd < 0 else "+$"
    final_all_token_usd = (
        f"ALL TOKENS {diff_sign}{diff_token_usd_str} | ${token_usd_str}"
    )

    return [final_all_token_usd]


def all_liquid_tokens_to_usd(data: pd.DataFrame) -> list:

    if data.empty:
        return ["LIQUID ASSETS: NOT DATA"]
    values_to_remove = [
        "LNDX",
        "xBasket",
        "xBASKET",
        "xCORN",
        "xRICE",
        "xSOY",
        "xWHEAT",
        "wLNDX",
        "ETHG",
    ]
    all_liquid_tokens = data[~data["tokens"].isin(values_to_remove)]

    all_liquid_tokens = all_liquid_tokens.groupby("date")[
        ["total_balance_usd", "abs_diff_usd"]
    ].sum()
    token_liq_usd = all_liquid_tokens["total_balance_usd"].iloc[0]
    diff_liq_usd = all_liquid_tokens["abs_diff_usd"].iloc[0]
    token__liq_usd_str = "{:,.2f}".format(token_liq_usd)
    diff_token_liq_usd_str = "{:,.2f}".format(abs(diff_liq_usd))

    balance_usdt = "" + token__liq_usd_str + ""
    diff_srt = "-$" if (diff_liq_usd < 0) else "+$"
    diff_balance = "LIQUID ASSETS " + diff_srt + diff_token_liq_usd_str + " | $"
    final_all_token_liq_usd = diff_balance + balance_usdt

    return [final_all_token_liq_usd]


def lndx_amount(main: pd.DataFrame, lp_pool: pd.DataFrame) -> list:

    if main.empty:
        return ["LNDX: NOT DATA"]
    # traders
    all_lndx = main.copy()
    all_lndx = all_lndx.query('tokens=="LNDX"')
    all_lndx_trades = all_lndx.groupby("tokens")[
        ["diff_amount", "diff_amount_usd", "abs_diff_usd"]
    ].sum()
    all_lndx__diff = all_lndx_trades["diff_amount"]
    # usd
    all_lndx_usd = all_lndx.groupby("tokens")[
        ["total_balance", "total_balance_usd"]
    ].sum()
    all_lndx_usd = all_lndx_usd["total_balance_usd"]

    # CEX USDT
    lndx_cex_usd = main.copy()
    lndx_cex_usd = lndx_cex_usd.query('main=="CEX" & tokens=="USDT"')
    total_cex = lndx_cex_usd["diff_amount"].sum()

    # LP USD
    lp_lndx = lp_pool
    lp_lndx_USDC = lp_lndx.query('asset=="USDC"')["diff"]

    # Total usd
    Total_usdc = total_cex + lp_lndx_USDC

    # LP ETH wETH
    lp_lndx = lp_pool
    lp_lndx_ETH = lp_lndx.query('asset=="ETH" | asset=="WETH"')["diff"].sum()

    # rep
    all_usdt_count = "{:,.2f}".format(float(abs(Total_usdc.iloc[0])))
    diff_eth_count = "{:,.2f}".format(float(abs(lp_lndx_ETH)))
    diff_lndx_count = "{:,.2f}".format(float(abs(all_lndx__diff.iloc[0])))
    all_usd_lndx = "{:,.2f}".format(float(abs(all_lndx_usd.iloc[0])))

    diff_lndx_count = (
        "+" + diff_lndx_count
        if float(all_lndx__diff.iloc[0]) > 0
        else "-" + diff_lndx_count
    )
    all_usdt_count = (
        "+$" + all_usdt_count
        if float(Total_usdc.iloc[0]) > 0
        else "-$" + all_usdt_count
    )
    diff_eth_count = (
        "+ETH " + diff_eth_count if float(lp_lndx_ETH) > 0 else "-ETH " + diff_eth_count
    )

    final_srt_report = f"LNDX {diff_lndx_count} | {all_usdt_count} | {diff_eth_count} (LNDX Balance = ${all_usd_lndx})"

    return [final_srt_report]


def amount_usd(main: pd.DataFrame) -> list:
    if main.empty:
        return ["USD: NOT DATA"]
    filtred_usdt = main.query('tokens=="USDT" | tokens=="USDC"')

    if filtred_usdt.empty:
        return ["USD: NOT DATA"]

    all_usdt = filtred_usdt.groupby("date")[["total_balance"]].sum()
    diff_usdt = filtred_usdt.groupby("date")[["diff_amount"]].sum()
    all_usdt = all_usdt["total_balance"].iloc[0]
    diff_usdt = diff_usdt["diff_amount"].iloc[0]
    all_usdt_number = "{:,.2f}".format(all_usdt)
    diff_usdt_number = "{:,.2f}".format(abs(diff_usdt))

    balance_usdt = "(Balance $" + all_usdt_number + ")"
    diff_srt = "-$" if (diff_usdt < 0) else "+$"
    diff_balance = "USD " + diff_srt + diff_usdt_number + " "
    final_usdc_str = diff_balance + balance_usdt

    return [final_usdc_str]


def amount_eth(main: pd.DataFrame) -> list:
    if main.empty:
        return ["ETH: NOT DATA"]
    filtred_eth = main.query('tokens=="WETH" | tokens=="ETH"')

    if filtred_eth.empty:
        return ["ETH: NOT DATA"]

    all_eth = filtred_eth.groupby("date")[["total_balance"]].sum()
    diff_eth = filtred_eth.groupby("date")[["diff_amount"]].sum()
    wbtc_eth = filtred_eth.groupby("date")[["total_balance_usd"]].sum()
    all_eth = all_eth["total_balance"].iloc[0]
    diff_eth = diff_eth["diff_amount"].iloc[0]
    eth_usd = wbtc_eth["total_balance_usd"].iloc[0]
    all_eth_number = "{:,.2f}".format(all_eth)
    diff_eth_number = "{:,.2f}".format(diff_eth)
    usdt_eth_number = "{:,.2f}".format(eth_usd)
    diff_srt = "" if (diff_eth < 0) else "+"

    final_str_eth = f"ETH {diff_srt}{diff_eth_number} (Balance {all_eth_number} ETH = ${usdt_eth_number})"

    return [final_str_eth]


def amount_btc(main: pd.DataFrame) -> list:
    if main.empty:
        return ["BTC: NOT DATA"]
    filtred_wbtc = main.query('tokens=="WBTC" | tokens=="BTC"')

    if filtred_wbtc.empty:
        return ["BTC: NOT DATA"]

    all_wbtc = filtred_wbtc.groupby("date")[["total_balance"]].sum()
    diff_wbtc = filtred_wbtc.groupby("date")[["diff_amount"]].sum()
    wbtc_usd = filtred_wbtc.groupby("date")[["total_balance_usd"]].sum()
    all_wbtc = all_wbtc["total_balance"].iloc[0]
    diff_wbtc = diff_wbtc["diff_amount"].iloc[0]
    wbtc_usd = wbtc_usd["total_balance_usd"].iloc[0]
    all_wbtc_number = "{:,.2f}".format(all_wbtc)
    diff_wbtc_number = "{:,.2f}".format(abs(diff_wbtc))
    usdt_wbtc_number = "{:,.2f}".format(abs(wbtc_usd))

    final_str_btc = (
        f"BTC {diff_wbtc_number} (Balance {all_wbtc_number} BTC = ${usdt_wbtc_number})"
    )

    return [final_str_btc]


def xTokens_change(main: pd.DataFrame) -> list:
    if main.empty:
        return ["xTokens: NOT DATA"]

    main["tokens"] = main["tokens"].str.lower()
    filtred_xtokens = main.query(
        'tokens in ["xwheat", "xsoy", "xcorn", "xrice", "xbasket"]'
    )
    if filtred_xtokens.empty:
        return ["xTokens: NOT DATA"]
    all_xtokens = filtred_xtokens.groupby(["date", "tokens"])[
        ["diff_amount", "diff_amount_usd"]
    ].sum()
    target_xtokens = all_xtokens.query(
        "`diff_amount_usd` > 1000 | `diff_amount_usd` < -1000"
    )
    if target_xtokens.empty:
        return ["No major sales of xTokens occurred."]
    arr_x_tokens = []
    for index, row in target_xtokens.iterrows():
        str_sng = "$" if row["diff_amount"] < 0 else "$"
        str_sng_1 = "-" if row["diff_amount"] < 0 else "+"
        str_diff = "{:,.2f}".format(abs(row["diff_amount"]))
        str_abs_diff_usd = "{:,.2f}".format(abs(row["diff_amount_usd"]))
        str_sng += str_abs_diff_usd
        recovery_str = index[1][0].lower() + index[1][1:].upper()
        str_xtokens = f"{recovery_str} {str_sng_1}{str_diff} | {str_sng}"
        arr_x_tokens.append(str_xtokens)

    return [arr_x_tokens]


def lndx_holders(holders: pd.DataFrame) -> list:
    if holders.empty:
        return ["HOLDERS: NOT DATA"]
    q_lndx_holders = holders.query('types_tokens =="lndx"')

    sing = "+" if (q_lndx_holders["diff"].iloc[-1] > 0) else ""
    count_change_holders_lndx = q_lndx_holders["diff"].iloc[-1]
    count_holders_lndx = q_lndx_holders["count"].iloc[-1]
    count_holders_lndx = "{:,.0f}".format(count_holders_lndx)
    count_change_holders_lndx = "{:,.0f}".format(count_change_holders_lndx)

    lndx_count_str = (
        f"LNDX HOLDERS {sing}{count_change_holders_lndx} | {count_holders_lndx}"
    )

    return [lndx_count_str]


def xToken_holders(holders: pd.DataFrame) -> list:
    if holders.empty:
        return ["NO DATA"]
    q_xToken_holders = holders.query('types_tokens =="xTokens"')

    sing = "+" if (q_xToken_holders["diff"].iloc[-1] > 0) else ""
    count_change_holders_x = q_xToken_holders["diff"].iloc[-1]
    count_holders_x = q_xToken_holders["count"].iloc[-1]
    count_holders_x = "{:,.0f}".format(count_holders_x)
    count_change_holders_x = "{:,.0f}".format(count_change_holders_x)

    x_count_str = f"xTOKEN HOLDERS {sing}{count_change_holders_x} | {count_holders_x}"

    return [x_count_str]


def all_contract_data(
    xTokens: pd.DataFrame, cTokens: pd.DataFrame, cPrice: pd.DataFrame
) -> list:
    cTokens_price = cPrice.rename(columns={"asset": "tokens"})
    cTokens_price["merge_tokens"] = cTokens_price["tokens"].str[1:]
    xTokens["merge_tokens"] = xTokens["tokens"].str[1:]
    cTokens["merge_tokens"] = cTokens["tokens"].str[1:]

    combined_data = pd.merge(xTokens, cTokens, on="merge_tokens")
    final_data = pd.merge(combined_data, cTokens_price, on="merge_tokens")

    final_data["no_sold"] = final_data["total_supply"] - final_data["balance"]
    final_data["all_token"] = final_data["no_sold"] + final_data["unclaimed"]
    final_data["CLAIMABLE"] = final_data["all_token"] * final_data["price"].apply(float)
    claimable = final_data["CLAIMABLE"].sum()

    return [claimable]


def exchange_balance(balance: pd.DataFrame, claimable: list[float]) -> list:
    if balance is None:
        return ["ARBITRUM EXCHANGE: not data"]

    balance_wallets = balance.query('asset=="USDC"')

    bw_amount = balance_wallets["balance"].iloc[-1]
    bw_amount = "{:,.0f}".format(bw_amount)
    claimable = "{:,.0f}".format(claimable[0])

    bw_amount_str = (
        f"cTOKEN ARBITRUM EXCHANGE BALANCE ${bw_amount} | CLAIMABLE ${claimable}"
    )

    return [bw_amount_str]


def private_sold(balance: pd.DataFrame) -> list:
    if balance is None:
        return ["CASH OUT: NOT DATA"]
    sold = balance.query("sold_lndx<0")
    if sold.empty:
        return ["No cash-out occurred"]
    total_sold = sold["sold_lndx"].sum()
    sold_wallet = sold["sold_lndx"].count()

    arr = [sold_wallet]
    sorted_sold = sold.sort_values(by="sold_lndx")
    for index, row in sorted_sold.iterrows():
        sold_lndx = "{:,.2f}".format(row["sold_lndx"])
        str_line = str(row["address"]) + " :sold LNDX: " + str(sold_lndx)
        arr.append(str_line)
    arr.append(str("{:,.2f}".format(total_sold)))

    return arr
