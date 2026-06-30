SELECT
    y.message_id,
    dc.channel_key,
    dd.date_key,
    y.image_path,
    y.detected_class,
    y.class_name,
    y.confidence,
    y.image_category,
    m.views,
    m.forwards
FROM stg_yolo_detections y
LEFT JOIN stg_telegram_messages m ON y.message_id = m.message_id
LEFT JOIN dim_channels dc ON y.channel_name = dc.channel_name
LEFT JOIN dim_dates dd ON m.message_date::DATE = dd.full_date