-- ============================================================
--  KPI Calculations
-- ============================================================


-- TOT MONEY EARNED

SELECT ROUND(SUM(amount)::numeric, 2)  AS tot_earned FROM transaction_facts WHERE money_in = True

--TOT MONEY SPENT

SELECT ROUND(SUM(amount)::numeric, 2)  AS tot_spent FROM transaction_facts WHERE money_in = False

-- TOT MONEY INVESTED

SELECT  ROUND(SUM(amount)::numeric, 2) AS invested FROM transaction_facts WHERE category_id = 'bcl_cat_s&p50013'
	
-- TOT MONEY SAVED: IMPORTANT invested money are recored as money out but it's not money spent.

WITH money_in AS(
    SELECT
        ROUND(SUM(amount)::numeric, 2) AS tot_earned 
    FROM transaction_facts 
    WHERE money_in = True 
),
money_out AS(
    SELECT
        money_in,
        ROUND(SUM(amount)::numeric, 2) AS tot_spent 
    FROM transaction_facts 
    WHERE money_in = False
	GROUP BY money_in
),
balances AS(
    SELECT
        money_in,
        money_out,
        ROUND(SUM(amount)::numeric, 2) AS invested 
    FROM transaction_facts 
    WHERE category_id = 'bcl_cat_s&p50013'
	GROUP BY money_in,money_out
)
SELECT (money_in::int + invested::int) - (money_out::int - invested::int) AS tot_saved 
FROM balances;
 



