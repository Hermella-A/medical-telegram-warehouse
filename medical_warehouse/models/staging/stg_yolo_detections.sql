SELECT
    message_id,
    channel_name,
    image_path,
    detected_class,
    class_name,
    confidence,
    image_category
FROM raw.yolo_detections
WHERE detected_class != -1  -- exclude rows with no detections