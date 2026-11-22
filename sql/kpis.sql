-- ============================================================
--  KPI Calculations
-- ============================================================


-- 1. TOT MONEY EARNED: IMPORTANT removed all top ups from barclays

SELECT 
    SUM(amount) FILTER (
        WHERE money_in = True
        AND category_id LIKE '%bcl%'
    ) +
    SUM(amount) FILTER (
   		 WHERE category_id = 'bcl_cat_s&p50013'
    ) AS tot_earned

FROM transaction_facts


-- 2. TOT MONEY SPENT: IMPORTANT monzo and wise transactions are omitted since their balances comes from bank transfers from barclays
	SELECT 
    SUM(amount) FILTER (
        WHERE money_in = False
		AND category_id LIKE '%bcl%'
		)::numeric
		- 
		SUM(amount) FILTER (
   		WHERE category_id = 'bcl_cat_s&p50013'
    )::numeric AS tot_spent

FROM transaction_facts


-- 3. TOT MONEY INVESTED

SELECT  ROUND(SUM(amount)::numeric, 2) AS invested FROM transaction_facts WHERE category_id = 'bcl_cat_s&p50013'
	
-- 4. TOT MONEY SAVED: IMPORTANT invested money are recored as money out but it's not money spent.

WITH balances AS(
	SELECT 
    SUM(amount) FILTER (
        WHERE money_in = True
        AND category_id LIKE '%bcl%'
    )::int AS tot_income,

	  SUM(amount) FILTER (
        WHERE money_in = False
		AND category_id LIKE '%bcl%'
		)::int AS tot_expenses,

    SUM(amount) FILTER (
   		 WHERE category_id = 'bcl_cat_s&p50013'
    )::int AS invested

FROM transaction_facts
)
SELECT (tot_income + invested) - (tot_expenses - invested) AS tot_saved FROM balances
 
-- 5.  TOT MONEY EARNED FOR EACH MONTH

SELECT 
    month_payment_period,
    SUM(amount) FILTER(
		WHERE money_in = True
		AND category_id LIKE '%bcl%'

	)::numeric + SUM(amount) FILTER( WHERE category_id LIKE '%bcl_cat_s&p50013%')::numeric AS tot_earned
FROM transaction_facts 
GROUP BY month_payment_period
ORDER BY tot_earned DESC

-- 6. TOT MONEY SPENT FOR EACH MONTH

SELECT 
    month_payment_period,
    SUM(amount) FILTER(
		WHERE money_in = False
		AND category_id LIKE '%bcl%'
        AND category_id NOT LIKE '%bcl_cat_s&p50013%'
	)::numeric AS tot_spent
FROM transaction_facts 
GROUP BY month_payment_period
ORDER BY tot_spent DESC

-- 7. AVERAGE SPENT EACH MONTH

SELECT 
    month_payment_period,
    AVG(amount) FILTER(
		WHERE money_in = False
		AND category_id LIKE '%bcl%'
        AND category_id NOT LIKE '%bcl_cat_s&p50013%'
	)::int AS tot_spent
FROM transaction_facts 
GROUP BY month_payment_period
ORDER BY tot_spent DESC


-- 8. TOT MONEY SAVED FOR EACH MONTH AND PERCENTAGES

WITH monthly_balances AS (
    SELECT 
    month_payment_period,
	-- tot_earned + invested ---
	 SUM(amount) FILTER(
		WHERE money_in = True
		AND category_id LIKE '%bcl%'
	)::numeric + SUM(amount) FILTER (
   		WHERE category_id = 'bcl_cat_s&p50013') AS tot_earned,
	-------------------------------
    SUM(amount) FILTER(
		WHERE money_in = False
        AND category_id LIKE '%bcl%'
        AND category_id NOT LIKE '%bcl_cat_s&p50013%'
	)::numeric AS tot_spent
	
    FROM transaction_facts 
    GROUP BY month_payment_period
    ORDER BY tot_spent DESC
)

SELECT 
    month_payment_period,
    tot_earned,
    tot_spent,
    (tot_earned - tot_spent)::numeric AS tot_saved,
	 ROUND(
        100.0 * (tot_earned - tot_spent)::int
        / tot_earned::int,
        2
    ) AS tot_saved_percentage
FROM monthly_balances
ORDER BY tot_saved DESC


-- 9.TOT MONTHLY AMOUNT SPENT PER CATEGORY
    
SELECT
month_payment_period,
category_id,
SUM(amount)::numeric AS tot_amount
FROM transaction_facts
WHERE money_in = False
GROUP BY month_payment_period,category_id
ORDER BY month_payment_period


-- 10. TOTAL SPENT ON ESSENTIALS AND EXTRAS

SELECT
	month_payment_period,
	SUM(amount) FILTER(
		WHERE money_in = False
		AND category_id LIKE ANY(ARRAY['%electricity%','%rent%','%tax%',
		'%food%','%water%'
		]))::numeric AS tot_spent_essentials,
	SUM(amount) FILTER(
		WHERE money_in = False
		AND category_id NOT LIKE ALL(ARRAY['%electricity%','%rent%','%tax%',
		'%food%','%water%','%bcl_cat_monzotransferout19%',
		'%bcl_cat_wisetransferout20%','%bcl_cat_s&p50013%'
		]))::numeric AS tot_spent_extras
	FROM transaction_facts
	GROUP BY month_payment_period
	ORDER BY tot_spent_essentials


