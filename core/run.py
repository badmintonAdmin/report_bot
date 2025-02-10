from http.client import responses

from db import database
from contracts import contract_data
from core.data.response import *

address_contracts_x = {
    'xCORN': '0x2D09268E7a8271b41CdD3019D97a4980D8110BfA',
    'xRICE': '0x2D8C8888FBFEa79f63dF39baFFf15E70CE4b66c5',
    'xWHEAT': '0xBa5630d57A8DdEf4EB97b5659c2cb9191dBB4Cab',
    'xSOY': '0xaab1f70478E734e972cDcC108c42A7c8915f5606'
}

address_contracts_c = {
    'cCORN': '0xd2a43A38b2A6EeC4aAfbca9b464Ac3259F2FC10a',
    'cRICE': '0x5C3f847A8521aD90869EAd3CaEe4d108a77003A7',
    'cWHEAT': '0x18aca6fda542cEabb99767d6F48e8134aAF7E6EF',
    'cSOY': '0xC87c971af5038AA9549516e0432766dE50E88c24'
}


main = database.execute_query('main.sql')
LP_pools = database.execute_query('lndx_pools_balance.sql')
holders = database.execute_query('holders_counts.sql')
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