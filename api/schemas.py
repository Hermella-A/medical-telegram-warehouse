from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class TopProductResponse(BaseModel):
    term: str
    frequency: int

class ChannelActivityResponse(BaseModel):
    date: date
    message_count: int
    avg_views: Optional[float]

class MessageSearchResponse(BaseModel):
    message_id: int
    channel_name: str
    message_date: date
    message_text: str
    views: int
    forwards: int

class VisualContentStatsResponse(BaseModel):
    channel_name: str
    total_images: int
    promotional: int
    product_display: int
    lifestyle: int
    other: int