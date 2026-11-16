-- ============================================================
--  KPI Calculations
-- ============================================================


--TOT MONEY EARNED: IMPORTANT removed all top ups from barclays

WITH balances AS(
	SELECT 
    SUM(amount) FILTER (
        WHERE money_in = True
          AND category_id NOT IN ('monzo_cat_transferin29', 'wise_transferin34')
    )::int AS tot_income,

    SUM(amount) FILTER (
   		 WHERE category_id = 'bcl_cat_s&p50013'
    )::int AS invested

FROM transaction_facts
)
SELECT tot_income + invested AS tot_earned FROM balances

--TOT MONEY SPENT: IMPORTANT monzo and wise transactions are omitted since their balances comes from bank transfers from barclays

WITH balances AS(
	SELECT 
    SUM(amount) FILTER (
        WHERE money_in = False
		AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%'])
		)::int AS tot_expenses,

    SUM(amount) FILTER (
   		 WHERE category_id = 'bcl_cat_s&p50013'
    )::int AS invested

FROM transaction_facts
)
SELECT tot_expenses - invested AS tot_spent FROM balances

-- TOT MONEY INVESTED

SELECT  ROUND(SUM(amount)::numeric, 2) AS invested FROM transaction_facts WHERE category_id = 'bcl_cat_s&p50013'
	
-- TOT MONEY SAVED: IMPORTANT invested money are recored as money out but it's not money spent.

WITH balances AS(
	SELECT 
    SUM(amount) FILTER (
        WHERE money_in = True
          AND category_id NOT IN ('monzo_cat_transferin29', 'wise_transferin34')
    )::int AS tot_income,

	  SUM(amount) FILTER (
        WHERE money_in = False
		AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%'])
		)::int AS tot_expenses,

    SUM(amount) FILTER (
   		 WHERE category_id = 'bcl_cat_s&p50013'
    )::int AS invested

FROM transaction_facts
)
SELECT (tot_income + invested) - (tot_expenses - invested) AS money_saved FROM balances



