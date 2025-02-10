from http.client import responses

from db import database
from core.data.response import *
from core.data.request_contract import *


main = database.execute_query('main.sql')
LP_pools = database.execute_query('lndx_pools_balance.sql')
holders = database.execute_query('holders_counts.sql')
usd_cTokens_exchange = database.execute_query('arb_wallets_cTokens.sql')

#Get data from contract and calculate claimable
cTokens_price = database.execute_query('prices_cTokens.sql')
xTokens_data = get_xTokens_info()
cTokens_data = get_cTokens_info()
claimable = all_contract_data(xTokens_data,cTokens_data,cTokens_price)

exchange_data = exchange_balance(usd_cTokens_exchange,claimable)

lndx = all_tokens_to_usd(main)
liq = all_liquid_tokens_to_usd(main)
lndx_change = lndx_amount(main,LP_pools)
USD = amount_usd(main)
eth = amount_eth(main)
btc = amount_btc(main)
xTokens = xTokens_change(main)
lndx_hold = lndx_holders(holders)
x_hold = xToken_holders(holders)

print(lndx)
print(liq)
print(lndx_change)
print(USD)
print(eth)
print(btc)
print(xTokens)
print(lndx_hold)
print(x_hold)
print(exchange_data)