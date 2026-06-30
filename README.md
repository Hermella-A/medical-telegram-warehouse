# Medical Telegram Warehouse

[![CI](https://github.com/Hermella-A/medical-telegram-warehouse/actions/workflows/ci.yml/badge.svg)](https://github.com/Hermella-A/medical-telegram-warehouse/actions/workflows/ci.yml)

## Project Overview

This project builds an end‑to‑end data platform for Kara Solutions, transforming raw data from public Telegram channels (CheMed, Lobelia Cosmetics, Tikvah Pharma) into a structured, analytical asset. The pipeline scrapes messages and images, loads them into a data lake, transforms them into a star schema using dbt, enriches images with YOLO object detection, and exposes insights through a FastAPI.

**Key business questions answered:**
- What are the top 10 most frequently mentioned medical products?
- Which channels have the most visual content?
- Do promotional posts (with people) get more views than product displays?
- What are the daily posting trends?

## Architecture
Telegram API → Scraper → Data Lake (JSON + Images) → PostgreSQL (raw) → dbt (staging + marts) → FastAPI
↑ ↑
Dagster Orchestration YOLO Enrichment

## Repository Structure
├── .github/workflows/ # CI/CD
├── api/ # FastAPI endpoints (Task 4)
├── data/ # Raw and processed data (ignored by Git)
├── medical_warehouse/ # dbt project (Task 2)
│ ├── models/
│ │ ├── staging/ # Cleaned views
│ │ └── marts/ # Star schema (dim_channels, dim_dates, fct_messages, fct_image_detections)
│ ├── tests/ # Data quality tests
│ └── dbt_project.yml
├── src/
│ ├── scraper.py # Telegram scraping (Task 1)
│ ├── load_raw_data.py # Load JSON to PostgreSQL
│ ├── yolo_detect.py # YOLO object detection (Task 3)
│ └── load_yolo_results.py # Load YOLO results
├── pipeline.py # Dagster orchestration (Task 5)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md


## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Hermella-A/medical-telegram-warehouse.git
cd medical-telegram-warehouse

2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux

3. Install dependencies
pip install -r requirements.txt

4. Configure PostgreSQL
Install PostgreSQL locally (or use Docker).

Create a database: medical_warehouse.

Update credentials in src/load_raw_data.py, src/load_yolo_results.py, and api/database.py.

5. Set up Telegram API credentials
Create a .env file with:

API_ID=34522112
API_HASH=ba8f982ab8aed17346c0e7811150db14
PHONE_NUMBER=+251961045238 

6. Run the full pipeline
python src/scraper.py
python src/load_raw_data.py
cd medical_warehouse && dbt run
python src/yolo_detect.py
python src/load_yolo_results.py

7. Launch the API

uvicorn api.main:app --reload
Visit http://127.0.0.1:8000/docs for interactive Swagger documentation.

8. Launch Dagster orchestration

dagster dev -f pipeline.py
Visit http://127.0.0.1:3000 to monitor and trigger runs.

Completed Tasks
Task	Description	Deliverables
Task 1	Data scraping and data lake	src/scraper.py, JSON files, images
Task 2	dbt transformations and star schema	Staging/marts models, dbt tests, documentation
Task 3	YOLO image enrichment	src/yolo_detect.py, detection CSV, fct_image_detections
Task 4	Analytical API (FastAPI)	4 endpoints (/api/reports/top-products, /api/channels/{name}/activity, /api/search/messages, /api/reports/visual-content)
Task 5	Pipeline orchestration (Dagster)	pipeline.py, daily schedule, UI monitoring
Key Results
Top products: Frequently mentioned terms extracted from message text.

Channel activity: @CheMed123 has the highest posting volume.

Visual content: @Lobelia4cosmetics has the most images (cosmetic products).

Promotional vs product display: Promotional posts (with people) average ~30% more views than product-only posts.

API Endpoints
GET /api/reports/top-products?limit=10 – Most frequent terms.

GET /api/channels/{channel_name}/activity – Daily activity.

GET /api/search/messages?query=keyword&limit=20 – Search messages.

GET /api/reports/visual-content – Image stats per channel.

CI/CD
GitHub Actions runs linting (flake8) and unit tests (pytest) on every push to main.