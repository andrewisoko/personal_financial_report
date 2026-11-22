# DAX measures on KPIs


 1. tot Earned

```
 tot_earned = 
CALCULATE(
    SUM(transaction_facts[amount]),
    transaction_facts[money_in] = TRUE(),
    CONTAINSSTRING(transaction_facts[category_id], "bcl")
)
+
CALCULATE(
    SUM(transaction_facts[amount]),
    transaction_facts[category_id] = "bcl_cat_s&p50013"
)

```

2. tot spent

```

tot_spent = 
CALCULATE(
    SUM(transaction_facts[amount]),
    transaction_facts[money_in] = FALSE(),
    CONTAINSSTRING(transaction_facts[category_id], "bcl")
)
-
CALCULATE(
    SUM(transaction_facts[amount]),
    transaction_facts[category_id] = "bcl_cat_s&p50013"
)

```

3. tot_saved

```
tot_saved = CALCULATE(
    transaction_facts[tot_earned] - transaction_facts[tot_spent])
```

4. average_spent

```
average_spent = CALCULATE(
    AVERAGE(transaction_facts[amount]))
```