---
name: cohort-analysis
description: Perform customer cohort analysis from transaction data.
task_id: SIM-003
author: human-expert
authoring_time_minutes: 60
iterations: 4
---

# Skill: Customer Cohort Analysis

## Trigger Condition
When a task requires grouping customers by their first interaction date and tracking behavior over time.

## Strategy

### Step 1: Data Loading and Validation
- Read CSV with columns: customer_id, date, amount, category
- Parse dates to datetime; reject rows with invalid dates
- Ensure amount is numeric; flag negative amounts as refunds

### Step 2: Identify Cohorts
- For each customer, find their earliest transaction date
- Truncate to month: `first_purchase_month = min(dates).to_period('M')`
- Assign each customer to their cohort

### Step 3: Build Retention Matrix
- For each cohort month and each subsequent month, count unique active customers
- Retention rate = active_in_month_N / cohort_size
- Create a DataFrame with cohort months as rows, period offsets as columns

### Step 4: Output
- Save the cohort matrix as CSV with headers: cohort_month, period_0, period_1, ...
- Values should be retention percentages (0-100), rounded to 1 decimal

### Step 5: Edge Cases
- Customers with only one transaction appear in period_0 only
- Months with zero transactions should show 0% retention, not NaN
- Handle cohorts with very few customers (< 5) by flagging them

## Common Pitfalls
- Using transaction count instead of unique customer count for retention
- Timezone issues when truncating dates to months
- Not handling the case where a customer's first purchase is a refund
- Off-by-one errors in period offset calculation
