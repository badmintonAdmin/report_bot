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

    values_to_remove = {
        "LNDX",
        "xBasket",
        "xBASKET",
        "xCORN",
        "xRICE",
        "xSOY",
        "xWHEAT",
        "wLNDX",
        "ETHG",
    }
    filtered_data = data[~data["tokens"].isin(values_to_remove)]

    all_liquid_tokens = (
        filtered_data.groupby("date")[["total_balance_usd", "abs_diff_usd"]]
        .sum()
        .iloc[0]
    )

    diff_sign = "-$" if all_liquid_tokens["abs_diff_usd"] < 0 else "+$"

    final_all_token_liq_usd = (
        f"LIQUID ASSETS {diff_sign}{abs(all_liquid_tokens['abs_diff_usd']):,.2f} | "
        f"${all_liquid_tokens['total_balance_usd']:,.2f}"
    )

    return [final_all_token_liq_usd]


# Helper function to calculate totals and format
def format_amount(amount, symbol=""):
    return f"{symbol}{abs(amount):,.2f}"


def lndx_amount(main: pd.DataFrame, lp_pool: pd.DataFrame) -> list:
    if main.empty:
        return ["LNDX: NOT DATA"]

    # Traders (LNDX tokens)
    lndx_data = main.query('tokens=="LNDX"')
    all_lndx_trades = lndx_data.groupby("tokens")[
        ["diff_amount", "diff_amount_usd", "abs_diff_usd"]
    ].sum()
    all_lndx_diff = all_lndx_trades["diff_amount"]
    all_lndx_usd = lndx_data.groupby("tokens")[["total_balance_usd"]].sum()[
        "total_balance_usd"
    ]

    # CEX USDT
    cex_lndx = main.query('main=="CEX" & tokens=="USDT"')
    total_cex = cex_lndx["diff_amount"].sum()

    # LP USD
    lp_lndx_usdc = lp_pool.query('asset=="USDC"')["diff"].sum()

    # Total USD
    total_usdc = total_cex + lp_lndx_usdc

    # LP ETH (WETH or ETH)
    lp_lndx_eth = lp_pool.query('asset in ["ETH", "WETH"]')["diff"].sum()

    # Format output
    diff_lndx_count = format_amount(all_lndx_diff.iloc[0])
    all_usdt_count = format_amount(total_usdc, "$")
    diff_eth_count = format_amount(lp_lndx_eth, "ETH ")
    all_usd_lndx = format_amount(all_lndx_usd.iloc[0], "$")

    # Add signs for positive/negative differences
    diff_lndx_count = (
        f"+{diff_lndx_count}" if all_lndx_diff.iloc[0] > 0 else f"-{diff_lndx_count}"
    )
    all_usdt_count = f"+{all_usdt_count}" if total_usdc > 0 else f"-{all_usdt_count}"
    diff_eth_count = f"+{diff_eth_count}" if lp_lndx_eth > 0 else f"-{diff_eth_count}"

    final_report = f"LNDX {diff_lndx_count} | {all_usdt_count} | {diff_eth_count} (LNDX Balance = {all_usd_lndx})"

    return [final_report]


def amount_usd(main: pd.DataFrame) -> list:
    if main.empty:
        return ["USD: NOT DATA"]

    filtered_usdt = main[main["tokens"].isin(["USDT", "USDC"])]

    if filtered_usdt.empty:
        return ["USD: NOT DATA"]

    grouped = (
        filtered_usdt.groupby("date")[["total_balance", "diff_amount"]].sum().iloc[0]
    )

    diff_sign = "-$" if grouped["diff_amount"] < 0 else "+$"

    final_usdc_str = (
        f"USD {diff_sign}{abs(grouped['diff_amount']):,.2f} "
        f"(Balance ${grouped['total_balance']:,.2f})"
    )

    return [final_usdc_str]


def amount_eth(main: pd.DataFrame) -> list:
    if main.empty:
        return ["ETH: NOT DATA"]

    filtered_eth = main[main["tokens"].isin(["WETH", "ETH"])]

    if filtered_eth.empty:
        return ["ETH: NOT DATA"]

    grouped = (
        filtered_eth.groupby("date")[
            ["total_balance", "diff_amount", "total_balance_usd"]
        ]
        .sum()
        .iloc[0]
    )

    diff_sign = "" if grouped["diff_amount"] < 0 else "+"

    final_eth_str = (
        f"ETH {diff_sign}{grouped['diff_amount']:,.2f} "
        f"(Balance {grouped['total_balance']:,.2f} ETH = ${grouped['total_balance_usd']:,.2f})"
    )

    return [final_eth_str]


def amount_btc(main: pd.DataFrame) -> list:
    if main.empty:
        return ["BTC: NOT DATA"]

    filtered_wbtc = main[main["tokens"].isin(["WBTC", "BTC"])]

    if filtered_wbtc.empty:
        return ["BTC: NOT DATA"]

    grouped = (
        filtered_wbtc.groupby("date")[
            ["total_balance", "diff_amount", "total_balance_usd"]
        ]
        .sum()
        .iloc[0]
    )

    diff_sign = "-" if grouped["diff_amount"] < 0 else "+"

    final_str_btc = (
        f"BTC {diff_sign}{abs(grouped['diff_amount']):,.2f} "
        f"(Balance {grouped['total_balance']:,.2f} BTC = ${grouped['total_balance_usd']:,.2f})"
    )

    return [final_str_btc]


def xTokens_change(main: pd.DataFrame) -> list:
    if main.empty:
        return ["xTokens: NOT DATA"]

    main = main.copy()
    main["tokens"] = main["tokens"].str.lower()
    target_tokens = {"xwheat", "xsoy", "xcorn", "xrice", "xbasket"}
    filtered_xtokens = main[main["tokens"].isin(target_tokens)]

    if filtered_xtokens.empty:
        return ["xTokens: NOT DATA"]

    all_xtokens = filtered_xtokens.groupby(["date", "tokens"])[
        ["diff_amount", "diff_amount_usd"]
    ].sum()

    target_xtokens = all_xtokens[
        (all_xtokens["diff_amount_usd"] > 1000)
        | (all_xtokens["diff_amount_usd"] < -1000)
    ]

    if target_xtokens.empty:
        return ["No major sales of xTokens occurred."]

    arr_x_tokens = []
    for (date, token), row in target_xtokens.iterrows():
        sign = "-" if row["diff_amount"] < 0 else "+"
        sign_pool = "+" if row["diff_amount"] < 0 else "-"
        str_diff = f"{abs(row['diff_amount']):,.2f}"
        str_abs_diff_usd = f"{abs(row['diff_amount_usd']):,.2f}"
        token_name = "".join([token[0], token[1].upper(), token[2:]])

        str_xtokens = f"{token_name} {sign}{str_diff} | {sign_pool}${str_abs_diff_usd}"
        arr_x_tokens.append(str_xtokens)

    return [arr_x_tokens]


def lndx_holders(holders: pd.DataFrame) -> list:
    if holders.empty:
        return ["HOLDERS: NOT DATA"]

    q_lndx_holders = holders.query('types_tokens == "lndx"')

    if q_lndx_holders.empty:
        return ["HOLDERS: NOT DATA"]

    last_row = q_lndx_holders.iloc[-1]
    sing = "+" if last_row["diff"] > 0 else ""
    count_change_holders_lndx = "{:,.0f}".format(last_row["diff"])
    count_holders_lndx = "{:,.0f}".format(last_row["count"])

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
    if balance.empty:
        return ["CASH OUT: NOT DATA"]

    sold = balance.query("sold_lndx < 0")
    if sold.empty:
        return ["No cash-out occurred"]

    total_sold = sold["sold_lndx"].sum()
    sold_wallet = sold["sold_lndx"].count()

    arr = [sold_wallet]

    sorted_sold = sold.sort_values(by="sold_lndx")
    for index, row in sorted_sold.iterrows():
        sold_lndx = f"{row['sold_lndx']:,.2f}"
        str_line = f"{row['address']} :sold LNDX: {sold_lndx}"
        arr.append(str_line)
    arr.append(f"{total_sold:,.2f}")

    return arr
