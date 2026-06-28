WITH channel_agg AS (
    SELECT
        channel_name,
        MIN(message_date) AS first_post_date,
        MAX(message_date) AS last_post_date,
        COUNT(*) AS total_posts,
        AVG(views) AS avg_views
    FROM stg_telegram_messages
    GROUP BY channel_name
)

SELECT
    ROW_NUMBER() OVER (ORDER BY channel_name) AS channel_key,
    channel_name,
    CASE
        WHEN LOWER(channel_name) LIKE '%pharma%' OR LOWER(channel_name) LIKE '%med%' THEN 'Pharmaceutical'
        WHEN LOWER(channel_name) LIKE '%cosmetic%' OR LOWER(channel_name) LIKE '%lobelia%' THEN 'Cosmetics'
        ELSE 'Medical'
    END AS channel_type,
    first_post_date,
    last_post_date,
    total_posts,
    avg_views
FROM channel_agg