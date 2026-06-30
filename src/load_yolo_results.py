import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Database connection
conn = psycopg2.connect(
    dbname="medical_warehouse",
    user="postgres",
    password="password123",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Create table (drop if exists to start fresh)
cur.execute("DROP TABLE IF EXISTS raw.yolo_detections;")
cur.execute("""
    CREATE TABLE raw.yolo_detections (
        message_id BIGINT,
        channel_name TEXT,
        image_path TEXT,
        detected_class INTEGER,
        class_name TEXT,
        confidence FLOAT,
        image_category TEXT,
        loaded_at TIMESTAMP DEFAULT NOW()
    );
""")
conn.commit()

# Load CSV
df = pd.read_csv("data/processed/yolo_detections.csv")

# Insert without ON CONFLICT
insert_sql = """
    INSERT INTO raw.yolo_detections 
    (message_id, channel_name, image_path, detected_class, class_name, confidence, image_category)
    VALUES %s
"""

rows = [tuple(row) for row in df[['message_id', 'channel_name', 'image_path', 'detected_class', 'class_name', 'confidence', 'image_category']].values]
execute_values(cur, insert_sql, rows)
conn.commit()

cur.close()
conn.close()
print("✅ YOLO results loaded into PostgreSQL.")