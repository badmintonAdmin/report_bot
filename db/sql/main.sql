WITH
aggregated_prices AS (
  SELECT
    pt.asset,
    pt.date,
    AVG(pt.price) as avg_price
  FROM prices pt
  WHERE asset = 'LNDX'
  GROUP BY pt.asset, pt.date
),
cex_balances_aggregated AS (
  SELECT
    DATE_TRUNC('day', b.date) as date,
    'CEX' as main,
    ce.name as type_category,
    b.asset as tokens,
    AVG(pt.avg_price) as price,
    SUM(b.total_balance) as total_balance
  FROM cex_account_balances b
  LEFT JOIN cex_accounts ac
    ON b.account_id = ac.id
  LEFT JOIN cex ce
    ON ac.cex_id = ce.id
  LEFT JOIN aggregated_prices pt
    ON b.asset = pt.asset AND b.date::date = pt.date::date
  GROUP BY 1, 2, 3, 4
),
cex_balances_lagged AS (
  SELECT
    b.*,
    LAG(b.total_balance) OVER (PARTITION BY b.type_category, b.tokens ORDER BY b.date) as prev_total_balance,
    LAG(b.date) OVER (PARTITION BY b.type_category, b.tokens ORDER BY b.date) as prev_date
  FROM cex_balances_aggregated b
),
cex_balances AS (
  SELECT
    b.date,
    b.main,
    b.type_category,
    b.tokens,
    CASE
      WHEN tokens = 'USDT' THEN 1
      ELSE b.price
    END as price,
    b.total_balance,
    CASE
      WHEN b.prev_date IS NULL OR b.prev_date != b.date - INTERVAL '1 day'
      THEN b.total_balance
      ELSE b.total_balance - b.prev_total_balance
    END as diff_amount
  FROM cex_balances_lagged b
),
pre_final_cex_data AS (
  SELECT
    date,
    main,
    type_category,
    tokens,
    price,
    total_balance,
    diff_amount,
    total_balance * price as total_balance_usd,
    diff_amount * price as diff_amount_usd
  FROM cex_balances
),
final_cex_data AS (
  SELECT
    date,
    main,
    type_category,
    tokens,
    price,
    total_balance,
    diff_amount,
    total_balance_usd,
    diff_amount_usd,
    COALESCE((total_balance_usd) - LAG(total_balance_usd) OVER (PARTITION BY type_category, tokens ORDER BY date), 0) as abs_diff_usd
  FROM pre_final_cex_data
),
-- MM DEX
mm_Wallets_FD AS (
  SELECT
    w.id,
    CASE
      WHEN ct.name IN ('Cashout Soft Profit', 'Buyout/Cashout') THEN 'MM dex'
      ELSE ct.name
    END as ct_name
  FROM wallets w
  LEFT JOIN wallet_categories ct
    ON w.category_id = ct.id
  WHERE ct.name in('MM dex', 'Cashout Soft Profit', 'Buyout/Cashout', 'Treasury', 'Treasury Investments')
),
mm_balance_wallets AS (
  SELECT
    DATE_TRUNC('day',  b.date) as date,
    s.ct_name as main,
    b.network as type_category,
    b.asset as tokens,
    AVG(b.price) as price,
    SUM(b.balance) as total_balance
  FROM wallet_balances b
  INNER JOIN mm_Wallets_FD s
    ON b.wallet_id = s.id
  WHERE b.price <> 0
  GROUP BY 1, 2, 3, 4
),
mm_balance_wallets_lagged AS (
  SELECT
    b.*,
    LAG(b.total_balance) OVER (PARTITION BY b.main, b.type_category, b.tokens ORDER BY b.date) as prev_total_balance,
    LAG(b.date) OVER (PARTITION BY b.main, b.type_category, b.tokens ORDER BY b.date) as prev_date
  FROM mm_balance_wallets b
),
dex_balances as (
    SELECT
    b.*,
    CASE
      WHEN b.prev_date IS NULL OR b.prev_date != b.date - INTERVAL '1 day'
      THEN b.total_balance
      ELSE b.total_balance - b.prev_total_balance
    END as diff_amount
    FROM mm_balance_wallets_lagged b
),
final_mm_balance_dex AS (
  SELECT
    date,
    main,
    type_category,
    tokens,
    price,
    total_balance,
    diff_amount,
    (total_balance * price) as total_balance_usd,
    (diff_amount * price) as diff_amount_usd,
    (total_balance * price) - LAG(total_balance * price) OVER (PARTITION BY main, type_category, tokens ORDER BY DATE_TRUNC('day', date)) as abs_diff_usd
  FROM dex_balances
),
-- Pools lq
protocols_lp AS (
  SELECT *
  FROM protocols
  WHERE name = 'Uniswap V3'
),
lp_positions AS (
  SELECT
    DATE_TRUNC('day', pt.date) as date,
    'DEX Funds' as main,
    lp.network as type_category,
    pa.asset as tokens,
    AVG(pa.price) as price,
    SUM(pa.amount) as total_balance,
    SUM(pa.amount) - COALESCE(LAG(SUM(pa.amount)) OVER (PARTITION BY lp.network, pa.asset ORDER BY DATE_TRUNC('day', pt.date)), 0) as diff_amount
  FROM protocol_portfolio_items pt
  INNER JOIN protocols_lp lp
    ON pt.protocol_id = lp.id
  LEFT JOIN portfolio_supply_assets pa
    ON pa.portfolio_id = pt.id
  GROUP BY 1, 2, 3, 4
),
final_lp AS (
  SELECT
    date,
    main,
    type_category,
    tokens,
    price,
    total_balance,
    diff_amount,
    (total_balance * price) as total_balance_usd,
    (diff_amount * price) as diff_amount_usd,
    (total_balance * price) - LAG(total_balance * price) OVER (PARTITION BY type_category, tokens ORDER BY date) as abs_diff_usd
  FROM lp_positions
),
-- Investment
invest_wallet AS (
  SELECT
    wt.id
  FROM wallet_categories ct
  JOIN wallets wt
    ON wt.category_id = ct.id
  WHERE ct.name = 'Treasury Investments'
),
investment_aggregated AS (
  SELECT
    DATE_TRUNC('day', pi.date) as date,
    'Treasury Investments' as main,
    pi.protocol_id as type_category,
    pt.asset as tokens,
    AVG(pt.price) as price,
    SUM(pt.amount) as total_balance
  FROM protocol_portfolio_items pi
  LEFT JOIN portfolio_supply_assets pt
    ON pi.id = pt.portfolio_id
  WHERE wallet_id IN (SELECT id FROM invest_wallet)
  GROUP BY 1, 2, 3, 4
),
investment_lagged AS (
  SELECT
    i.*,
    LAG(i.total_balance) OVER (PARTITION BY i.type_category, i.tokens ORDER BY i.date) as prev_total_balance,
    LAG(i.date) OVER (PARTITION BY i.type_category, i.tokens ORDER BY i.date) as prev_date
  FROM investment_aggregated i
),
investment AS (
  SELECT
    date,
    main,
    type_category,
    tokens,
    price,
    total_balance,
    CASE
      WHEN prev_date IS NULL OR prev_date != date - INTERVAL '1 day'
      THEN total_balance
      ELSE total_balance - prev_total_balance
    END as diff_amount
  FROM investment_lagged
),
final_invest AS (
  SELECT
    date,
    main,
    type_category,
    tokens,
    price,
    total_balance,
    diff_amount,
    (total_balance * price) as total_balance_usd,
    (diff_amount * price) as diff_amount_usd,
    COALESCE((total_balance * price) - LAG(total_balance * price) OVER (PARTITION BY type_category, tokens ORDER BY date), 0) as abs_diff_usd
  FROM investment
),
Final_all AS (
  SELECT * FROM final_cex_data
  UNION ALL
  SELECT * FROM final_mm_balance_dex
  UNION ALL
  SELECT * FROM final_lp
  UNION ALL
  SELECT * FROM final_invest
)


SELECT *
FROM Final_all
WHERE price > 0
AND  date = DATE_TRUNC('day',NOW())
and Tokens NOT IN ('ETHG')
ORDER BY date, main, type_category;
