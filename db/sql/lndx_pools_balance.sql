WITH
lp_lndx as (
    SELECT
    id
    FROM protocols
    where name = 'Uniswap V3'
),
data_pools as (
    SELECT
    DATE_TRUNC('day',un.date) as date,
    lp.portfolio_id,
    lp.asset,
    lp.amount
    FROM portfolio_supply_assets lp
    LEFT JOIN protocol_portfolio_items un
    ON lp.portfolio_id = un.id
    LEFT JOIN lp_lndx fd
    ON fd.id = un.protocol_id

),
filtred_pools as (
    SELECT DISTINCT portfolio_id
    FROM data_pools
    WHERE asset = 'LNDX'
),
filtred_all_data as (
    SELECT
    p.*
    FROM data_pools p
    INNER JOIN filtred_pools fp
    ON p.portfolio_id = fp.portfolio_id
),
agg_data as (
	SELECT
	date,
	asset,
	sum(amount) as amount
	FROM filtred_all_data
	GROUP BY 1,2
),
add_diff_day as (
	SELECT
	*,
	amount - LAG(amount) OVER (PARTITION BY asset ORDER BY date ) as diff
	FROM agg_data
)
SELECT *
FROM add_diff_day
WHERE date = DATE_TRUNC('day',NOW())
ORDER BY date DESC;