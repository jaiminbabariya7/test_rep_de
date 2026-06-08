-- int_order_items.sql  —  orders joined with customer data
WITH orders AS (SELECT * FROM {{ ref('stg_orders') }}),
customers AS (SELECT * FROM {{ ref('stg_customers') }})
SELECT
    o.order_id, o.customer_id, o.order_date, o.order_status,
    o.order_amount_usd, o.item_count,
    c.email, c.country_code, c.registration_date AS customer_since,
    DATE_DIFF(o.order_date, c.registration_date, DAY) AS days_since_registration,
    ROUND(o.order_amount_usd / NULLIF(o.item_count,0), 2) AS avg_item_value_usd
FROM orders o LEFT JOIN customers c USING (customer_id)