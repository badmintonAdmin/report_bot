WITH
all_holders as (
    SELECT
    DATE_TRUNC('day',date) as date,
    asset,
    count(*) as count,
    count(*) - lAG(COUNT(*)) OVER (PARTITION BY asset ORDER BY DATE_TRUNC('day',date)) as diff
    FROM holders
    GROUP BY 1,2
),
calculate as (
    SELECT *,
    CASE
        WHEN asset = 'LNDX' THEN 'lndx'
        WHEN asset like 'x%' THEN 'xTokens'
        ELSE 'Other'
    END as types_tokens
    FROM all_holders
)

SELECT
date,
types_tokens,
sum(count) as count,
sum(diff) as diff
FROM calculate
WHERE date = DATE_TRUNC('day',NOW())
GROUP BY 1,2
ORDER BY date DESC;

