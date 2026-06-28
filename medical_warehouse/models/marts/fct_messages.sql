SELECT
    m.message_id,
    dc.channel_key,
    dd.date_key,
    m.message_text,
    m.message_length,
    m.views,
    m.forwards,
    m.has_image_flag
FROM stg_telegram_messages m
LEFT JOIN dim_channels dc ON m.channel_name = dc.channel_name
LEFT JOIN dim_dates dd ON CAST(m.message_date AS DATE) = dd.full_date