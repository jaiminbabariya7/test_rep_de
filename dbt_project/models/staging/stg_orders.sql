-- stg_orders.sql  —  cleaned, typed order records
WITH source AS (SELECT * FROM {{ source('raw','raw_orders') }})
SELECT
    CAST(order_id AS STRING)       AS order_id,
    CAST(customer_id AS STRING)    AS customer_id,
    DATE(order_date)               AS order_date,
    UPPER(TRIM(status))            AS order_status,
    ROUND(CAST(amount AS NUMERIC),2) AS order_amount_usd,
    CAST(item_count AS INT64)      AS item_count,
    CURRENT_TIMESTAMP()            AS _dbt_loaded_at
FROM source
WHERE order_id IS NOT NULL AND customer_id IS NOT NULL AND amount > 0