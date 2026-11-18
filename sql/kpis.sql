-- ============================================================
--  KPI Calculations
-- ============================================================


-- 1. TOT MONEY EARNED: IMPORTANT removed all top ups from barclays

WITH balances AS(
	SELECT 
    SUM(amount) FILTER (
        WHERE money_in = True
          AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%','%wise_transferin34%'])
    )::int AS tot_income,

    SUM(amount) FILTER (
   		 WHERE category_id = 'bcl_cat_s&p50013'
    )::int AS invested

FROM transaction_facts
)
SELECT tot_income + invested AS tot_earned FROM balances

-- 2. TOT MONEY SPENT: IMPORTANT monzo and wise transactions are omitted since their balances comes from bank transfers from barclays

WITH balances AS(
	SELECT 
    SUM(amount) FILTER (
        WHERE money_in = False
		AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%','%wise_transferin34%'])
		)::int AS tot_expenses,

    SUM(amount) FILTER (
   		 WHERE category_id = 'bcl_cat_s&p50013'
    )::int AS invested

FROM transaction_facts
)
SELECT tot_expenses - invested AS tot_spent FROM balances

-- 3. TOT MONEY INVESTED

SELECT  ROUND(SUM(amount)::numeric, 2) AS invested FROM transaction_facts WHERE category_id = 'bcl_cat_s&p50013'
	
-- 4. TOT MONEY SAVED: IMPORTANT invested money are recored as money out but it's not money spent.

WITH balances AS(
	SELECT 
    SUM(amount) FILTER (
        WHERE money_in = True
          AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%','%wise_transferin34%'])
    )::int AS tot_income,

	  SUM(amount) FILTER (
        WHERE money_in = False
		AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%','%wise_transferin34%'])
		)::int AS tot_expenses,

    SUM(amount) FILTER (
   		 WHERE category_id = 'bcl_cat_s&p50013'
    )::int AS invested

FROM transaction_facts
)
SELECT (tot_income + invested) - (tot_expenses - invested) AS money_saved FROM balances
 
-- 5.  MONEY EARNED FOR EACH MONTH

SELECT 
    month_payment_period,
    SUM(amount) FILTER(
		WHERE money_in = True
		AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%','%wise_transferin34%'])
	)::numeric AS tot_earned
FROM transaction_facts 
GROUP BY month_payment_period
ORDER BY tot_earned DESC

-- 6. MONEY SPENT FOR EACH MONTH

SELECT 
    month_payment_period,
    SUM(amount) FILTER(
		WHERE money_in = False
		AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%','%wise_transferin34%'])
	)::numeric AS tot_spent
FROM transaction_facts 
GROUP BY month_payment_period
ORDER BY tot_spent DESC


-- 7. MONEY SAVED FOR EACH MONTH AND PERCENTAGES

WITH monthly_balances AS (
    SELECT 
    month_payment_period,
	 SUM(amount) FILTER(
		WHERE money_in = True
		AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%','%wise_transferin34%'])
	)::INT AS tot_earned,
    SUM(amount) FILTER(
		WHERE money_in = False
		AND category_id NOT LIKE ALL (ARRAY['%monzo_cat%', '%wise_cat%','%wise_transferin34%'])
	)::INT AS tot_spent
    FROM transaction_facts 
    GROUP BY month_payment_period
    ORDER BY tot_spent DESC
)

SELECT 
    month_payment_period,
    tot_earned,
    tot_spent,
    tot_earned - tot_spent AS tot_saved,
	 ROUND(
        100.0 * (tot_earned - tot_spent)
        / tot_earned,
        2
    ) AS tot_saved_percentage
FROM monthly_balances
ORDER BY tot_saved DESC


-- 8. MONTHLY AMOUNT SPENT PER CATEGORY
    
SELECT
month_payment_period,
category_id,
SUM(amount)::numeric AS tot_amount
FROM transaction_facts
WHERE money_in = False
GROUP BY month_payment_period,category_id
ORDER BY month_payment_period

-- 9. AVERAGE I SPENT ON FOOD,BILLS AND RENT PER MONTH

SELECT
	month_payment_period,
	SUM(amount) FILTER(
		WHERE money_in = False
		AND category_id LIKE ANY(ARRAY['%electricity%','%rent%','%tax%',
		'%food%','%water%'
		]))::numeric AS tot_spent
	FROM transaction_facts
	GROUP BY month_payment_period
	ORDER BY tot_spent



