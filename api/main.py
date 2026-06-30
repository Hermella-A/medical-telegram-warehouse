from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from . import database, schemas

app = FastAPI(
    title="Medical Telegram Warehouse API",
    description="Analytical API for medical Telegram channel data",
    version="1.0"
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"message": "Medical Telegram Warehouse API. See /docs for documentation."}

# Endpoint 1: Top products (keyword frequency)
@app.get("/api/reports/top-products", response_model=List[schemas.TopProductResponse])
async def top_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Returns the most frequently mentioned terms/products across all channels.
    Extracts words from message_text and counts frequency (excluding common stopwords).
    """
    # Simple stopword list (extend as needed)
    stopwords = {'the', 'a', 'an', 'of', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'in', 'and', 'or', 'but', 'not', 'is', 'it', 'this', 'that', 'these', 'those', 'are', 'were', 'was', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'etc', 'etc.', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'our', 'their'}

    # SQL to extract words and count frequency
    # This uses regexp_split_to_table to split message_text into words
    sql = text("""
        WITH words AS (
            SELECT lower(regexp_split_to_table(message_text, '\s+')) AS word
            FROM fct_messages
            WHERE message_text IS NOT NULL AND message_text != ''
        )
        SELECT word, COUNT(*) AS frequency
        FROM words
        WHERE word ~ '^[a-z]{3,}$'  -- at least 3 letters
          AND word NOT IN :stopwords
        GROUP BY word
        ORDER BY frequency DESC
        LIMIT :limit
    """)
    result = db.execute(sql, {"stopwords": tuple(stopwords), "limit": limit})
    rows = result.fetchall()
    return [{"term": row[0], "frequency": row[1]} for row in rows]

# Endpoint 2: Channel activity
@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivityResponse])
async def channel_activity(
    channel_name: str,
    db: Session = Depends(get_db)
):
    """
    Returns daily posting activity for a specific channel.
    """
    sql = text("""
        SELECT dd.full_date AS date, COUNT(*) AS message_count, AVG(m.views) AS avg_views
        FROM fct_messages m
        JOIN dim_channels dc ON m.channel_key = dc.channel_key
        JOIN dim_dates dd ON m.date_key = dd.date_key
        WHERE dc.channel_name = :channel_name
        GROUP BY dd.full_date
        ORDER BY dd.full_date
    """)
    result = db.execute(sql, {"channel_name": channel_name})
    rows = result.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found or no data.")
    return [{"date": row[0], "message_count": row[1], "avg_views": row[2]} for row in rows]

# Endpoint 3: Message search
@app.get("/api/search/messages", response_model=List[schemas.MessageSearchResponse])
async def search_messages(
    query: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search for messages containing a specific keyword (case-insensitive).
    """
    sql = text("""
        SELECT
            m.message_id,
            dc.channel_name,
            dd.full_date AS message_date,
            m.message_text,
            m.views,
            m.forwards
        FROM fct_messages m
        JOIN dim_channels dc ON m.channel_key = dc.channel_key
        JOIN dim_dates dd ON m.date_key = dd.date_key
        WHERE lower(m.message_text) LIKE lower(:query)
        ORDER BY dd.full_date DESC
        LIMIT :limit
    """)
    result = db.execute(sql, {"query": f"%{query}%", "limit": limit})
    rows = result.fetchall()
    return [
        {
            "message_id": row[0],
            "channel_name": row[1],
            "message_date": row[2],
            "message_text": row[3],
            "views": row[4],
            "forwards": row[5]
        }
        for row in rows
    ]

# Endpoint 4: Visual content stats
@app.get("/api/reports/visual-content", response_model=List[schemas.VisualContentStatsResponse])
async def visual_content_stats(
    db: Session = Depends(get_db)
):
    """
    Returns statistics about image usage across channels.
    """
    sql = text("""
        SELECT
            dc.channel_name,
            COUNT(DISTINCT id.image_path) AS total_images,
            SUM(CASE WHEN id.image_category = 'promotional' THEN 1 ELSE 0 END) AS promotional,
            SUM(CASE WHEN id.image_category = 'product_display' THEN 1 ELSE 0 END) AS product_display,
            SUM(CASE WHEN id.image_category = 'lifestyle' THEN 1 ELSE 0 END) AS lifestyle,
            SUM(CASE WHEN id.image_category = 'other' THEN 1 ELSE 0 END) AS other
        FROM fct_image_detections id
        JOIN dim_channels dc ON id.channel_key = dc.channel_key
        GROUP BY dc.channel_name
        ORDER BY total_images DESC
    """)
    result = db.execute(sql)
    rows = result.fetchall()
    return [
        {
            "channel_name": row[0],
            "total_images": row[1],
            "promotional": row[2],
            "product_display": row[3],
            "lifestyle": row[4],
            "other": row[5]
        }
        for row in rows
    ]