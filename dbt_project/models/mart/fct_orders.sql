-- fct_orders.sql  —  order fact table with rolling KPIs
WITH base AS (SELECT * FROM {{ ref('int_order_items') }})
SELECT
    order_id, customer_id, order_date, order_status,
    order_amount_usd, item_count, avg_item_value_usd, country_code,
    SUM(order_amount_usd) OVER (PARTITION BY customer_id ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS customer_ltv_usd,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_number,
    order_status = 'COMPLETED' AS is_completed,
    CURRENT_TIMESTAMP() AS _dbt_updated_at
FROM base