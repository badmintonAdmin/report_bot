WITH prices_cTokens as (
    SELECT *
    FROM prices
    where asset like 'c%'
)

SELECT * FROM prices_cTokens
    WHERE DATE_TRUNC('day', date) = DATE_TRUNC('day', NOW())
    and network = 'eth'
ORDER BY date DESC;