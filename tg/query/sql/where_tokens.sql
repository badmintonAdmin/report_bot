WITH
category as (
	SELECT * 
    FROM wallet_categories
    WHERE name IN ('Treasury','Treasury Investments')
)
,wallets as (
	SELECT
        w.id, 
        w.address,
        w.memo,
        c.name as category 
    FROM category c
    LEFT JOIN wallets w
    ON w.category_id = c.id
),
all_balance as (
	SELECT 
        w.address,
        b.network as chain,
        b.asset as token,
        b.balance as amount,
        w.category,
        w.memo
    FROM wallets w
    LEFT JOIN wallet_balances b
    ON b.wallet_id = w.id
    WHERE DATE_TRUNC('day',b.date) = CURRENT_DATE
    AND b.price >0
)
SELECT * 
FROM all_balance
WHERE LOWER(token) IN %(tokens)s