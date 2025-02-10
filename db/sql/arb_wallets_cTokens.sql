SELECT *
FROM wallet_balances
WHERE wallet_id = 54
AND DATE_TRUNC('day', date) = DATE_TRUNC('day', NOW())