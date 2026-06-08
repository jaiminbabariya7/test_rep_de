-- dim_customers.sql  —  customer dimension with LTV segments
WITH customers AS (SELECT * FROM {{ ref('stg_customers') }}),
orders AS (SELECT * FROM {{ ref('fct_orders') }}),
summary AS (SELECT customer_id, COUNT(*) AS total_orders, SUM(order_amount_usd) AS ltv_usd,
    MIN(order_date) AS first_order, MAX(order_date) AS last_order
    FROM orders GROUP BY customer_id)
SELECT c.*, COALESCE(s.total_orders,0) AS total_orders,
    COALESCE(s.ltv_usd,0) AS lifetime_value_usd, s.first_order, s.last_order,
    CASE WHEN s.ltv_usd>=1000 THEN 'platinum' WHEN s.ltv_usd>=500 THEN 'gold'
         WHEN s.ltv_usd>=100 THEN 'silver' ELSE 'bronze' END AS customer_tier,
    CURRENT_TIMESTAMP() AS _dbt_updated_at
FROM customers c LEFT JOIN summary s USING (customer_id)