WITH
category_private AS (
    SELECT id
    FROM wallet_categories
    WHERE name = 'Private Holders'
),
private_wallets AS (
    SELECT *
    FROM wallets
    WHERE category_id IN (SELECT * FROM category_private)
),

private_holders_balance AS (
    SELECT
        DATE_TRUNC('day', b.date) AS date,
        b.asset AS tokens,
        w.address,
        COALESCE(SUM(b.balance), 0) AS balance
    FROM wallet_balances b
    INNER JOIN private_wallets w
    ON b.wallet_id = w.id
    WHERE b.asset IN ('LNDX', 'veLNDX')
    AND network = 'eth'
    GROUP BY 1, 2, 3
),
starts_date as (
    SELECT
        min(date) as star_date
    FROM private_holders_balance
    LIMIT 1
),
date_series AS (
    SELECT generate_series(
        (SELECT * FROM starts_date),
        NOW(),
        INTERVAL '1 day'
    )::date AS date
),
all_dates_and_addresses AS (
    SELECT
        d.date,
        w.address,
        a.tokens
    FROM date_series d
    CROSS JOIN (SELECT DISTINCT address FROM private_wallets) w
    CROSS JOIN (SELECT DISTINCT tokens FROM private_holders_balance) a
),

full_balance_data AS (
    SELECT
        d.date,
        d.address,
        d.tokens AS tokens,
        COALESCE(b.balance, 0) AS balance
    FROM all_dates_and_addresses d
    LEFT JOIN private_holders_balance b
    ON d.date = b.date AND d.address = b.address AND d.tokens = b.tokens
),

previous_balances AS (
    SELECT
        date,
        address,
        tokens,
        balance,
        LAG(balance) OVER (PARTITION BY address, tokens ORDER BY date) AS previous_balance
    FROM full_balance_data
)
,velndx_balance AS (
    SELECT
        date,
        address,
        tokens,
        balance AS veLNDX,
        COALESCE(balance - previous_balance, 0) AS diff_veLNDX,
        CASE
            WHEN COALESCE(balance - previous_balance, 0) < 0 THEN COALESCE(ABS((balance - previous_balance) * 2), 0)
            ELSE 0
        END AS claimed_lndx
    FROM previous_balances
    WHERE tokens = 'veLNDX'
)

,lndx_balance AS (
    SELECT
        date,
        address,
        tokens,
        balance AS LNDX
    FROM previous_balances
    WHERE tokens = 'LNDX'
)

,agg_data_all_tokens AS (
    SELECT
        v.date,
        v.address,
        v.veLNDX,
        v.diff_veLNDX,
        COALESCE(l.LNDX, 0) AS LNDX,
        v.claimed_lndx
    FROM velndx_balance v
    LEFT JOIN lndx_balance l
    ON v.date = l.date AND v.address = l.address
)

,calc_diff_lndx AS (
    SELECT *,
        COALESCE(LNDX - LAG(LNDX) OVER (PARTITION BY address ORDER BY date), 0) AS diff_lndx
    FROM agg_data_all_tokens
)

,sold_lndx_tokens AS (
    SELECT
        date,
        address,
        veLNDX,
        diff_veLNDX,
        claimed_lndx,
        LNDX,
        diff_lndx,
        CASE
            WHEN claimed_lndx > 0 AND diff_lndx != 0 AND diff_veLNDX < 0 THEN (diff_lndx - claimed_lndx)
            WHEN claimed_lndx > 0 AND diff_lndx = 0 THEN (LNDX - claimed_lndx)
            ELSE diff_lndx
        END AS sold_lndx
    FROM calc_diff_lndx
)

SELECT *
FROM sold_lndx_tokens
WHERE DATE_TRUNC('day', date) >= NOW() - INTERVAL '1 day'
ORDER BY date DESC;
