"""
YOLO object detection on Telegram images.
Scans downloaded images, runs YOLOv8, categorises images, and saves results to CSV.
"""
import os
import cv2
import pandas as pd
from ultralytics import YOLO
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
IMAGES_DIR = Path("data/raw/images")
OUTPUT_CSV = "data/processed/yolo_detections.csv"
MODEL_NAME = "yolov8n.pt"  # nano model for speed

# Load YOLO model
model = YOLO(MODEL_NAME)
print(f"Loaded YOLO model: {MODEL_NAME}")

# Classification logic
def classify_image(detections):
    """
    Categorise image based on detected objects.
    Returns: 'promotional', 'product_display', 'lifestyle', or 'other'
    """
    has_person = any(det['class'] == 0 for det in detections)      # person = class 0
    has_bottle = any(det['class'] in (39, 40) for det in detections) # bottle = 39, wine glass = 40
    has_container = any(det['class'] in (24, 25, 26, 27, 28) for det in detections) # backpacks, etc.

    if has_person and (has_bottle or has_container):
        return 'promotional'      # person holding/showing a product
    elif has_bottle or has_container:
        return 'product_display'  # product only
    elif has_person:
        return 'lifestyle'        # person only
    else:
        return 'other'

def process_image(image_path):
    """Run YOLO on a single image and return detections and category."""
    try:
        results = model(image_path, verbose=False)
        detections = []
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    detections.append({'class': cls, 'confidence': conf})
        category = classify_image(detections)
        return detections, category
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return [], 'error'

def main():
    # Gather all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        image_files.extend(IMAGES_DIR.rglob(ext))

    print(f"Found {len(image_files)} images to process.")

    results_list = []
    for img_path in image_files:
        # Extract message_id from filename (assuming format: {message_id}.jpg)
        # The path is like data/raw/images/channel_name/message_id.jpg
        channel_name = img_path.parent.name
        message_id = img_path.stem  # filename without extension

        detections, category = process_image(img_path)

        # Store results
        for det in detections:
            results_list.append({
                'message_id': int(message_id) if message_id.isdigit() else message_id,
                'channel_name': channel_name,
                'image_path': str(img_path),
                'detected_class': det['class'],
                'class_name': model.names[det['class']],
                'confidence': det['confidence'],
                'image_category': category
            })

        # Also add a row with category even if no detections
        if not detections:
            results_list.append({
                'message_id': int(message_id) if message_id.isdigit() else message_id,
                'channel_name': channel_name,
                'image_path': str(img_path),
                'detected_class': -1,
                'class_name': 'none',
                'confidence': 0.0,
                'image_category': category
            })

        print(f"Processed {img_path} → category: {category}")

    # Save results to CSV
    df = pd.DataFrame(results_list)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Saved {len(df)} records to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()  