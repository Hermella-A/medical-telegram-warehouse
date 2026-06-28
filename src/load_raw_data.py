"""
Load raw Telegram JSON data into PostgreSQL raw schema.
"""
import os
import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    dbname="medical_warehouse",
    user="postgres",
    password="password123",  
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Create raw schema if not exists
cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
cur.execute("""
    CREATE TABLE IF NOT EXISTS raw.telegram_messages (
        message_id BIGINT,
        channel_name TEXT,
        message_date TIMESTAMP,
        message_text TEXT,
        views INTEGER,
        forwards INTEGER,
        has_media BOOLEAN,
        image_path TEXT,
        raw_json JSONB,
        loaded_at TIMESTAMP DEFAULT NOW()
    );
""")
conn.commit()

# Path to JSON files
json_dir = "data/raw/telegram_messages"

# Process each JSON file
for root, dirs, files in os.walk(json_dir):
    for file in files:
        if file.endswith('.json'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            # Prepare data for bulk insert
            rows = []
            for msg in messages:
                # Extract fields
                rows.append((
                    msg.get('message_id'),
                    msg.get('channel_name'),
                    msg.get('message_date'),
                    msg.get('message_text', ''),
                    msg.get('views'),
                    msg.get('forwards'),
                    msg.get('has_media', False),
                    msg.get('image_path'),
                    json.dumps(msg)  # raw JSON
                ))
            
            # Bulk insert
            insert_sql = """
                INSERT INTO raw.telegram_messages 
                (message_id, channel_name, message_date, message_text, views, forwards, has_media, image_path, raw_json)
                VALUES %s
            """
            execute_values(cur, insert_sql, rows)
            conn.commit()
            print(f"Loaded {len(rows)} messages from {filepath}")

cur.close()
conn.close()
print("Data loading complete.") 