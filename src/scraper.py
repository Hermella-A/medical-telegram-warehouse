"""
Telegram scraper for medical business channels.
Extracts messages, metadata, and downloads images.
"""
import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv

# Load environment variables
load_dotenv('C:/Users/Dataencoder/Desktop/medical-telegram-warehouse/.env')

API_ID = int(os.getenv('34522112'))
API_HASH = os.getenv('ba8f982ab8aed17346c0e7811150db14')
PHONE = os.getenv('+251961045238')

# Configuration
CHANNELS = [
    '@CheMed123',
    '@Lobelia4cosmetics',
    '@Tikvahpharm',
    # Add more from et.tgstat.com/medicine
]
DATA_DIR = Path('data/raw/telegram_messages')
IMAGES_DIR = Path('data/raw/images')
LOG_DIR = Path('logs')

# Create directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def scrape_channel(client, channel_name, days_back=30):
    """Scrape messages from a single channel."""
    try:
        entity = await client.get_entity(channel_name)
        logger.info(f"Scraping channel: {channel_name}")

        date_limit = datetime.now() - timedelta(days=days_back)
        messages = []
        image_paths = []

        async for message in client.iter_messages(entity, offset_date=date_limit):
            # Extract basic fields
            msg_data = {
                'message_id': message.id,
                'channel_name': channel_name,
                'message_date': message.date.isoformat(),
                'message_text': message.text or '',
                'views': message.views,
                'forwards': message.forwards,
                'has_media': bool(message.media)
            }

            # Download image if present
            image_path = None
            if message.media and isinstance(message.media, MessageMediaPhoto):
                try:
                    # Create channel-specific image folder
                    channel_img_dir = IMAGES_DIR / channel_name
                    channel_img_dir.mkdir(parents=True, exist_ok=True)
                    img_filename = f"{message.id}.jpg"
                    img_path = channel_img_dir / img_filename
                    await client.download_media(message.media, file=img_path)
                    image_path = str(img_path.relative_to(Path.cwd()))
                    logger.info(f"Downloaded image: {image_path}")
                except Exception as e:
                    logger.error(f"Error downloading image for msg {message.id}: {e}")

            msg_data['image_path'] = image_path
            messages.append(msg_data)

        # Save messages to JSON file (partitioned by date)
        if messages:
            date_str = datetime.now().strftime('%Y-%m-%d')
            date_dir = DATA_DIR / date_str
            date_dir.mkdir(parents=True, exist_ok=True)
            out_file = date_dir / f"{channel_name}.json"
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(messages)} messages to {out_file}")
        else:
            logger.info(f"No messages found for {channel_name}")

    except Exception as e:
        logger.error(f"Failed to scrape {channel_name}: {e}")

async def main():
    """Main async entry point."""
    client = TelegramClient('session', API_ID, API_HASH)
    await client.start(phone=PHONE)

    # Scrape each channel
    for channel in CHANNELS:
        await scrape_channel(client, channel, days_back=7)  # Adjust days as needed

    await client.disconnect()
    logger.info("Scraping completed.")

if __name__ == '__main__':
    asyncio.run(main()) 

from telethon.errors import FloodWaitError

async def scrape_with_retry(client, channel, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await scrape_channel(client, channel)
        except FloodWaitError as e:
            wait = e.seconds
            print(f"Flood wait {wait}s for {channel}, retry {attempt+1}/{max_retries}")
            await asyncio.sleep(wait)
        except Exception as e:
            print(f"Error scraping {channel}: {e}")
            await asyncio.sleep(2 ** attempt)  # exponential backoff
    raise Exception(f"Failed to scrape {channel} after {max_retries} attempts")