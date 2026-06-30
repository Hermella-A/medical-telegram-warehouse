"""
Load raw Telegram JSON data into PostgreSQL raw schema with retries and error handling.
"""
import os
import json
import time
import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import OperationalError
from datetime import datetime

DB_CONFIG = {
    "dbname": "medical_warehouse",
    "user": "postgres",
    "password": "postgres",  # change to your password
    "host": "localhost",
    "port": "5432"
}

def get_connection(retries=3, delay=2):
    for attempt in range(retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            return conn
        except OperationalError as e:
            print(f"Connection attempt {attempt+1} failed: {e}")
            time.sleep(delay * (attempt + 1))
    raise Exception("Could not connect to PostgreSQL after multiple retries.")

def load_file(filepath):
    """Load a single JSON file with error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            messages = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Skipping {filepath} – invalid JSON: {e}")
        return []
    return messages


def get_db_connection(max_retries=3):
    for attempt in range(max_retries):
        try:
            return psycopg2.connect(...)
        except OperationalError as e:
            print(f"DB connection failed (attempt {attempt+1}): {e}")
            time.sleep(2 ** attempt)
    raise Exception("Could not connect to PostgreSQL after multiple attempts.")


def main():
    conn = get_connection()
    cur = conn.cursor()

    # Create raw schema and table if not exists
    cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            message_id BIGINT PRIMARY KEY,
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

    json_dir = "data/raw/telegram_messages"
    total_loaded = 0

    for root, dirs, files in os.walk(json_dir):
        for file in files:
            if not file.endswith('.json'):
                continue
            filepath = os.path.join(root, file)
            messages = load_file(filepath)
            if not messages:
                continue

            rows = []
            for msg in messages:
                rows.append((
                    msg.get('message_id'),
                    msg.get('channel_name'),
                    msg.get('message_date'),
                    msg.get('message_text', ''),
                    msg.get('views'),
                    msg.get('forwards'),
                    msg.get('has_media', False),
                    msg.get('image_path'),
                    json.dumps(msg)
                ))

            # Insert with ON CONFLICT to avoid duplicates
            insert_sql = """
                INSERT INTO raw.telegram_messages 
                (message_id, channel_name, message_date, message_text, views, forwards, has_media, image_path, raw_json)
                VALUES %s
                ON CONFLICT (message_id) DO NOTHING
            """
            try:
                execute_values(cur, insert_sql, rows)
                conn.commit()
                print(f"Loaded {len(rows)} messages from {filepath}")
                total_loaded += len(rows)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
                conn.rollback()

    cur.close()
    conn.close()
    print(f"Total messages loaded: {total_loaded}")

if __name__ == "__main__":
    main() 