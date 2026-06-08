-- stg_customers.sql  —  cleaned customer records
WITH source AS (SELECT * FROM {{ source('raw','raw_customers') }})
SELECT
    CAST(customer_id AS STRING)   AS customer_id,
    INITCAP(TRIM(first_name))     AS first_name,
    INITCAP(TRIM(last_name))      AS last_name,
    LOWER(TRIM(email))            AS email,
    UPPER(TRIM(country_code))     AS country_code,
    DATE(registration_date)       AS registration_date,
    COALESCE(CAST(is_active AS BOOL), TRUE) AS is_active,
    CURRENT_TIMESTAMP()           AS _dbt_loaded_at
FROM source
WHERE customer_id IS NOT NULL AND email IS NOT NULL