WITH
-- Wallets treasury
our_wallets as (
    SELECT
        w.id as w_id,
        w.address,
        w.memo,
        c.*
    FROM wallets w
    LEFT JOIN wallet_categories c
    ON w.category_id = c.id
    WHERE c.name IN ('Treasury','Treasury Investments','Credit Gateway Liqudity')
),
-- All protocols
Protocols as (

    SELECT
        id,
        name as p_name
    FROM protocols
    WHERE id NOT IN ('arb_uniswap3','uniswap3')
),
Protocols_items as (
    SELECT *
    FROM protocol_portfolio_items
    WHERE protocol_id IN (SELECT id FROM Protocols)
),
portfolio_assets as (
    SELECT
        d.id as p_id,
        p.id as pos_id,
        p.date,
        p.name as p_name,
        p.protocol_id,
        d.asset,
        d.amount,
        d.price,
        d.amount * d.price as amount_usd,
        w.address,
        w.name as wallet_category,
        w.memo
    FROM portfolio_supply_assets d
    LEFT JOIN Protocols_items p
    ON p.id = d.portfolio_id
    LEFT JOIN our_wallets w
    ON p.wallet_id = w.w_id
    WHERE  p.id NOTNULL and w.address NOTNULL
),
agg_position as (
    SELECT
        DATE_TRUNC('day',date) as days,
        protocol_id as protocol,
        p_name as position_type,
        address,
        wallet_category,
        memo,
        asset,
        avg(price) as price,
        sum(amount) as amount,
        sum(amount_usd) as amount_usd
    FROM portfolio_assets
    GROUP BY 1,2,3,4,5,6,7

)
SELECT
    days,
    protocol,
    position_type,
    asset,
    amount,
    price,
    amount_usd,
    COALESCE(amount - LAG(amount) OVER(PARTITION BY protocol, position_type,asset, address ORDER BY days),0) as diff_amount,
    COALESCE(amount_usd - LAG(amount_usd) OVER(PARTITION BY protocol, position_type,asset, address ORDER BY days),0) as diff_amount_usd,
    address,
    wallet_category,
    memo

FROM agg_position
WHERE position_type <> 'Vesting' and days =  DATE_TRUNC('day',NOW())
ORDER BY days DESC;