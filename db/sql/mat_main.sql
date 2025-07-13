 WITH aggregated_prices AS (
         SELECT pt.asset,
            pt.date,
            avg(pt.price) AS avg_price
           FROM prices pt
          WHERE ((pt.asset)::text = 'LNDX'::text)
          GROUP BY pt.asset, pt.date
        ), cex_balances_aggregated AS (
         SELECT date_trunc('day'::text, b.date) AS date,
            'CEX'::text AS main,
            ce.name AS type_category,
            b.asset AS tokens,
            avg(pt.avg_price) AS price,
            sum(b.total_balance) AS total_balance
           FROM (((cex_account_balances b
             LEFT JOIN cex_accounts ac ON ((b.account_id = ac.id)))
             LEFT JOIN cex ce ON ((ac.cex_id = ce.id)))
             LEFT JOIN aggregated_prices pt ON ((((b.asset)::text = (pt.asset)::text) AND ((b.date)::date = (pt.date)::date))))
          GROUP BY (date_trunc('day'::text, b.date)), 'CEX'::text, ce.name, b.asset
        ), cex_balances_lagged AS (
         SELECT b.date,
            b.main,
            b.type_category,
            b.tokens,
            b.price,
            b.total_balance,
            lag(b.total_balance) OVER (PARTITION BY b.type_category, b.tokens ORDER BY b.date) AS prev_total_balance,
            lag(b.date) OVER (PARTITION BY b.type_category, b.tokens ORDER BY b.date) AS prev_date
           FROM cex_balances_aggregated b
        ), cex_balances AS (
         SELECT b.date,
            b.main,
            b.type_category,
            b.tokens,
                CASE
                    WHEN ((b.tokens)::text = 'USDT'::text) THEN (1)::numeric
                    ELSE b.price
                END AS price,
            b.total_balance,
                CASE
                    WHEN ((b.prev_date IS NULL) OR (b.prev_date <> (b.date - '1 day'::interval))) THEN b.total_balance
                    ELSE (b.total_balance - b.prev_total_balance)
                END AS diff_amount
           FROM cex_balances_lagged b
        ), pre_final_cex_data AS (
         SELECT cex_balances.date,
            cex_balances.main,
            cex_balances.type_category,
            cex_balances.tokens,
            cex_balances.price,
            cex_balances.total_balance,
            cex_balances.diff_amount,
            (cex_balances.total_balance * cex_balances.price) AS total_balance_usd,
            (cex_balances.diff_amount * cex_balances.price) AS diff_amount_usd
           FROM cex_balances
        ), final_cex_data AS (
         SELECT pre_final_cex_data.date,
            pre_final_cex_data.main,
            pre_final_cex_data.type_category,
            pre_final_cex_data.tokens,
            pre_final_cex_data.price,
            pre_final_cex_data.total_balance,
            pre_final_cex_data.diff_amount,
            pre_final_cex_data.total_balance_usd,
            pre_final_cex_data.diff_amount_usd,
            COALESCE((pre_final_cex_data.total_balance_usd - lag(pre_final_cex_data.total_balance_usd) OVER (PARTITION BY pre_final_cex_data.type_category, pre_final_cex_data.tokens ORDER BY pre_final_cex_data.date)), (0)::numeric) AS abs_diff_usd
           FROM pre_final_cex_data
        ), mm_wallets_fd AS (
         SELECT w.id,
                CASE
                    WHEN ((ct.name)::text = ANY ((ARRAY['Cashout Soft Profit'::character varying, 'Buyout/Cashout'::character varying])::text[])) THEN 'MM dex'::character varying
                    ELSE ct.name
                END AS ct_name
           FROM (wallets w
             LEFT JOIN wallet_categories ct ON ((w.category_id = ct.id)))
          WHERE ((ct.name)::text = ANY ((ARRAY['MM dex'::character varying, 'Cashout Soft Profit'::character varying, 'Buyout/Cashout'::character varying, 'Treasury'::character varying, 'Treasury Investments'::character varying])::text[]))
        ), mm_balance_wallets AS (
         SELECT date_trunc('day'::text, b.date) AS date,
            s.ct_name AS main,
            b.network AS type_category,
            b.asset AS tokens,
            avg(b.price) AS price,
            sum(b.balance) AS total_balance
           FROM (wallet_balances b
             JOIN mm_wallets_fd s ON ((b.wallet_id = s.id)))
          GROUP BY (date_trunc('day'::text, b.date)), s.ct_name, b.network, b.asset
        ), mm_balance_wallets_lagged AS (
         SELECT b.date,
            b.main,
            b.type_category,
            b.tokens,
            b.price,
            b.total_balance,
            lag(b.total_balance) OVER (PARTITION BY b.main, b.type_category, b.tokens ORDER BY b.date) AS prev_total_balance,
            lag(b.date) OVER (PARTITION BY b.main, b.type_category, b.tokens ORDER BY b.date) AS prev_date
           FROM mm_balance_wallets b
        ), dex_balances AS (
         SELECT b.date,
            b.main,
            b.type_category,
            b.tokens,
            b.price,
            b.total_balance,
            b.prev_total_balance,
            b.prev_date,
                CASE
                    WHEN ((b.prev_date IS NULL) OR (b.prev_date <> (b.date - '1 day'::interval))) THEN b.total_balance
                    ELSE (b.total_balance - b.prev_total_balance)
                END AS diff_amount
           FROM mm_balance_wallets_lagged b
        ), final_mm_balance_dex AS (
         SELECT dex_balances.date,
            dex_balances.main,
            dex_balances.type_category,
            dex_balances.tokens,
            dex_balances.price,
            dex_balances.total_balance,
            dex_balances.diff_amount,
            (dex_balances.total_balance * dex_balances.price) AS total_balance_usd,
            (dex_balances.diff_amount * dex_balances.price) AS diff_amount_usd,
            ((dex_balances.total_balance * dex_balances.price) - lag((dex_balances.total_balance * dex_balances.price)) OVER (PARTITION BY dex_balances.main, dex_balances.type_category, dex_balances.tokens ORDER BY (date_trunc('day'::text, dex_balances.date)))) AS abs_diff_usd
           FROM dex_balances
        ), protocols_lp AS (
         SELECT protocols.id,
            protocols.network,
            protocols.name,
            protocols.logo
           FROM public.protocols
          WHERE ((protocols.name)::text = 'Uniswap V3'::text)
        ), lp_positions AS (
         SELECT date_trunc('day'::text, pt.date) AS date,
            'DEX Funds'::text AS main,
            lp.network AS type_category,
            pa.asset AS tokens,
            avg(pa.price) AS price,
            sum(pa.amount) AS total_balance,
            (sum(pa.amount) - COALESCE(lag(sum(pa.amount)) OVER (PARTITION BY lp.network, pa.asset ORDER BY (date_trunc('day'::text, pt.date))), (0)::numeric)) AS diff_amount
           FROM ((protocol_portfolio_items pt
             JOIN protocols_lp lp ON (((pt.protocol_id)::text = (lp.id)::text)))
             LEFT JOIN portfolio_supply_assets pa ON ((pa.portfolio_id = pt.id)))
          GROUP BY (date_trunc('day'::text, pt.date)), 'DEX Funds'::text, lp.network, pa.asset
        ), final_lp AS (
         SELECT lp_positions.date,
            lp_positions.main,
            lp_positions.type_category,
            lp_positions.tokens,
            lp_positions.price,
            lp_positions.total_balance,
            lp_positions.diff_amount,
            (lp_positions.total_balance * lp_positions.price) AS total_balance_usd,
            (lp_positions.diff_amount * lp_positions.price) AS diff_amount_usd,
            ((lp_positions.total_balance * lp_positions.price) - lag((lp_positions.total_balance * lp_positions.price)) OVER (PARTITION BY lp_positions.type_category, lp_positions.tokens ORDER BY lp_positions.date)) AS abs_diff_usd
           FROM lp_positions
        ), invest_wallet AS (
         SELECT wt.id
           FROM (wallet_categories ct
             JOIN wallets wt ON ((wt.category_id = ct.id)))
          WHERE ((ct.name)::text = 'Treasury Investments'::text)
        ), investment_aggregated AS (
         SELECT date_trunc('day'::text, pi.date) AS date,
            'Treasury Investments'::text AS main,
            pi.protocol_id AS type_category,
            pt.asset AS tokens,
            avg(pt.price) AS price,
            sum(pt.amount) AS total_balance
           FROM (protocol_portfolio_items pi
             LEFT JOIN portfolio_supply_assets pt ON ((pi.id = pt.portfolio_id)))
          WHERE (pi.wallet_id IN ( SELECT invest_wallet.id
                   FROM invest_wallet))
          GROUP BY (date_trunc('day'::text, pi.date)), 'Treasury Investments'::text, pi.protocol_id, pt.asset
        ), investment_lagged AS (
         SELECT i.date,
            i.main,
            i.type_category,
            i.tokens,
            i.price,
            i.total_balance,
            lag(i.total_balance) OVER (PARTITION BY i.type_category, i.tokens ORDER BY i.date) AS prev_total_balance,
            lag(i.date) OVER (PARTITION BY i.type_category, i.tokens ORDER BY i.date) AS prev_date
           FROM investment_aggregated i
        ), investment AS (
         SELECT investment_lagged.date,
            investment_lagged.main,
            investment_lagged.type_category,
            investment_lagged.tokens,
            investment_lagged.price,
            investment_lagged.total_balance,
                CASE
                    WHEN ((investment_lagged.prev_date IS NULL) OR (investment_lagged.prev_date <> (investment_lagged.date - '1 day'::interval))) THEN investment_lagged.total_balance
                    ELSE (investment_lagged.total_balance - investment_lagged.prev_total_balance)
                END AS diff_amount
           FROM investment_lagged
        ), final_invest AS (
         SELECT investment.date,
            investment.main,
            investment.type_category,
            investment.tokens,
            investment.price,
            investment.total_balance,
            investment.diff_amount,
            (investment.total_balance * investment.price) AS total_balance_usd,
            (investment.diff_amount * investment.price) AS diff_amount_usd,
            COALESCE(((investment.total_balance * investment.price) - lag((investment.total_balance * investment.price)) OVER (PARTITION BY investment.type_category, investment.tokens ORDER BY investment.date)), (0)::numeric) AS abs_diff_usd
           FROM investment
        ), our_wallets AS (
         SELECT w.id AS w_id,
            w.address,
            w.memo,
            c.id,
            c.name
           FROM (wallets w
             LEFT JOIN wallet_categories c ON ((w.category_id = c.id)))
          WHERE ((c.name)::text = ANY ((ARRAY['Treasury'::character varying, 'Treasury Investments'::character varying, 'Credit Gateway Liqudity'::character varying])::text[]))
        ), protocols AS (
         SELECT protocols.id,
            protocols.name AS p_name
           FROM public.protocols
          WHERE ((protocols.id)::text <> ALL ((ARRAY['arb_uniswap3'::character varying, 'uniswap3'::character varying])::text[]))
        ), protocols_items AS (
         SELECT protocol_portfolio_items.id,
            protocol_portfolio_items.name,
            protocol_portfolio_items.protocol_id,
            protocol_portfolio_items.wallet_id,
            protocol_portfolio_items.date
           FROM protocol_portfolio_items
          WHERE ((protocol_portfolio_items.protocol_id)::text IN ( SELECT protocols.id
                   FROM protocols))
        ), portfolio_assets AS (
         SELECT d.id AS p_id,
            p.id AS pos_id,
            p.date,
            p.name AS p_name,
            p.protocol_id,
            d.asset,
            d.amount,
            d.price,
            (d.amount * d.price) AS amount_usd,
            w.address,
            w.name AS wallet_category,
            w.memo
           FROM ((portfolio_supply_assets d
             LEFT JOIN protocols_items p ON ((p.id = d.portfolio_id)))
             LEFT JOIN our_wallets w ON ((p.wallet_id = w.w_id)))
          WHERE ((p.id IS NOT NULL) AND (w.address IS NOT NULL))
        ), agg_position AS (
         SELECT date_trunc('day'::text, portfolio_assets.date) AS date,
            'Treasury Investments'::text AS main,
            'Investments Protocols'::text AS type_category,
            portfolio_assets.asset AS tokens,
            avg(portfolio_assets.price) AS price,
            sum(portfolio_assets.amount) AS total_balance,
            sum(portfolio_assets.amount_usd) AS total_balance_usd
           FROM portfolio_assets
          WHERE ((portfolio_assets.p_name)::text <> 'Vesting'::text)
          GROUP BY (date_trunc('day'::text, portfolio_assets.date)), 'Treasury Investments'::text, 'Investments Protocols'::text, portfolio_assets.asset
        ), final_protocol_investments AS (
         SELECT agg_position.date,
            agg_position.main,
            agg_position.type_category,
            agg_position.tokens,
            agg_position.price,
            agg_position.total_balance,
            COALESCE((agg_position.total_balance - lag(agg_position.total_balance) OVER (PARTITION BY agg_position.tokens ORDER BY agg_position.date)), (0)::numeric) AS diff_amount,
            agg_position.total_balance_usd,
            COALESCE((agg_position.total_balance_usd - lag(agg_position.total_balance_usd) OVER (PARTITION BY agg_position.tokens ORDER BY agg_position.date)), (0)::numeric) AS diff_amount_usd,
            COALESCE(((agg_position.total_balance * agg_position.price) - lag((agg_position.total_balance * agg_position.price)) OVER (PARTITION BY agg_position.tokens ORDER BY agg_position.date)), (0)::numeric) AS abs_diff_usd
           FROM agg_position
        ), final_all AS (
         SELECT final_cex_data.date,
            final_cex_data.main,
            final_cex_data.type_category,
            final_cex_data.tokens,
            final_cex_data.price,
            final_cex_data.total_balance,
            final_cex_data.diff_amount,
            final_cex_data.total_balance_usd,
            final_cex_data.diff_amount_usd,
            final_cex_data.abs_diff_usd
           FROM final_cex_data
        UNION ALL
         SELECT final_mm_balance_dex.date,
            final_mm_balance_dex.main,
            final_mm_balance_dex.type_category,
            final_mm_balance_dex.tokens,
            final_mm_balance_dex.price,
            final_mm_balance_dex.total_balance,
            final_mm_balance_dex.diff_amount,
            final_mm_balance_dex.total_balance_usd,
            final_mm_balance_dex.diff_amount_usd,
            final_mm_balance_dex.abs_diff_usd
           FROM final_mm_balance_dex
        UNION ALL
         SELECT final_lp.date,
            final_lp.main,
            final_lp.type_category,
            final_lp.tokens,
            final_lp.price,
            final_lp.total_balance,
            final_lp.diff_amount,
            final_lp.total_balance_usd,
            final_lp.diff_amount_usd,
            final_lp.abs_diff_usd
           FROM final_lp
        UNION ALL
         SELECT final_invest.date,
            final_invest.main,
            final_invest.type_category,
            final_invest.tokens,
            final_invest.price,
            final_invest.total_balance,
            final_invest.diff_amount,
            final_invest.total_balance_usd,
            final_invest.diff_amount_usd,
            final_invest.abs_diff_usd
           FROM final_invest
        UNION ALL
         SELECT final_protocol_investments.date,
            final_protocol_investments.main,
            final_protocol_investments.type_category,
            final_protocol_investments.tokens,
            final_protocol_investments.price,
            final_protocol_investments.total_balance,
            final_protocol_investments.diff_amount,
            final_protocol_investments.total_balance_usd,
            final_protocol_investments.diff_amount_usd,
            final_protocol_investments.abs_diff_usd
           FROM final_protocol_investments
        )
 SELECT final_all.date,
    final_all.main,
    final_all.type_category,
    final_all.tokens,
    final_all.price,
    final_all.total_balance,
    final_all.diff_amount,
    final_all.total_balance_usd,
    final_all.diff_amount_usd,
    final_all.abs_diff_usd
   FROM final_all
  WHERE ((final_all.price > (0)::numeric) AND ((final_all.tokens)::text <> 'ETHG'::text))
  ORDER BY final_all.date, final_all.main, final_all.type_category;