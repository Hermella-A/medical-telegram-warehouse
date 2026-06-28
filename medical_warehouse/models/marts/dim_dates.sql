WITH date_spine AS (
    SELECT DISTINCT CAST(message_date AS DATE) AS date_day
    FROM {{ ref('stg_telegram_messages') }}
)

SELECT
    CAST(TO_CHAR(date_day, 'YYYYMMDD') AS INTEGER) AS date_key,
    date_day AS full_date,
    EXTRACT(DAY FROM date_day) AS day_of_month,
    EXTRACT(DOW FROM date_day) AS day_of_week,
    TO_CHAR(date_day, 'Day') AS day_name,
    EXTRACT(WEEK FROM date_day) AS week_of_year,
    EXTRACT(MONTH FROM date_day) AS month,
    TO_CHAR(date_day, 'Month') AS month_name,
    EXTRACT(QUARTER FROM date_day) AS quarter,
    EXTRACT(YEAR FROM date_day) AS year,
    CASE WHEN EXTRACT(DOW FROM date_day) IN (0,6) THEN 1 ELSE 0 END AS is_weekend
FROM date_spine