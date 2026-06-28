WITH source AS (
    SELECT
        message_id,
        channel_name,
        message_date,
        message_text,
        views,
        forwards,
        has_media,
        image_path
    FROM raw.telegram_messages
    WHERE message_text IS NOT NULL AND LENGTH(message_text) > 0
)

SELECT
    message_id,
    channel_name,
    message_date,
    message_text,
    LENGTH(message_text) AS message_length,
    views,
    forwards,
    has_media,
    image_path,
    CASE 
        WHEN has_media IN ('true', 't', 'True', 'TRUE', '1', 'yes', 'y') THEN 1
        ELSE 0
    END AS has_image_flag
FROM source