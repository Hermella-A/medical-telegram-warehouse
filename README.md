# Medical Telegram Warehouse 
[![CI](https://github.com)](https://github.com)

An end‑to‑end data platform that transforms raw data from public Telegram channels into structured, analytical assets.

## 📌 Project Overview

The pipeline scrapes messages and images, loads them into a data lake, transforms them into a star schema using dbt, enriches images with YOLO object detection, and exposes insights through a FastAPI.

**Key business questions answered:**
- What are the top 10 most frequently mentioned medical products?
- Which channels have the most visual content?
- Do promotional posts (with people) get more views than product displays?
- What are the daily posting trends?

## 📐 Architecture
`Telegram API` ➔ `Scraper` ➔ `Data Lake` ➔ `PostgreSQL` ➔ `dbt` ➔ `FastAPI` 
*Upstream Enrichment:* `YOLO Object Detection`
*Orchestration:* `Dagster`

## 📁 Repository Structure
```text
├── .github/workflows/      # CI/CD
├── api/                    # FastAPI endpoints
├── data/                   # Raw and processed data (ignored by Git)
├── medical_warehouse/      # dbt project
│   ├── models/             # Staging views and Marts star schema
│   ├── tests/              # Data quality tests
│   └── dbt_project.yml
├── src/                    # Core Python scripts
│   ├── scraper.py          # Telegram scraping
│   ├── load_raw_data.py    # Load JSON to PostgreSQL
│   ├── yolo_detect.py      # YOLO object detection
│   └── load_yolo_results.py# Load YOLO results
├── pipeline.py             # Dagster orchestration pipeline
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 🚀 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com
cd medical-telegram-warehouse
```

### 2. Create and activate virtual environment
```bash
python -m venv venv 
# Windows
venv\Scripts\activate 
# Mac/Linux
source venv/bin/activate 
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure PostgreSQL
Install PostgreSQL locally or use Docker. Create a database named `medical_warehouse`. Update your credentials in:
- `src/load_raw_data.py`
- `src/load_yolo_results.py`
- `api/database.py`

### 5. Set up Telegram API credentials
Create a `.env` file in the root directory and add your credentials:
```text
API_ID=34522112
API_HASH=ba8f982ab8aed17346c0e7811150db14
PHONE_NUMBER=+251961045238
```

### 6. Run the full pipeline
```bash
python src/scraper.py
python src/load_raw_data.py
cd medical_warehouse && dbt run
python src/yolo_detect.py
python src/load_yolo_results.py
```

### 7. Launch the API
```bash
uvicorn api.main:app --reload
```
Visit `http://127.0.0` for interactive Swagger documentation.

### 8. Launch Dagster Orchestration
```bash
dagster dev -f pipeline.py
```
Visit `http://127.0.0.1:3000` to monitor and trigger runs.

---

## 📊 Completed Tasks & Deliverables

| Task | Description | Deliverables |
| :--- | :--- | :--- |
| **Task 1** | Data scraping and data lake | `src/scraper.py`, JSON files, images |
| **Task 2** | dbt transformations & star schema | Staging/marts models, dbt tests |
| **Task 3** | YOLO image enrichment | `src/yolo_detect.py`, detection CSV |
| **Task 4** | Analytical API | `FastAPI` endpoints |
| **Task 5** | Pipeline orchestration | `pipeline.py`, daily schedule, UI monitoring |

---

## 💡 Key Results
- **Top products:** Frequently mentioned terms extracted from message text.
- **Channel activity:** `@CheMed123` has the highest posting volume.
- **Visual content:** `@Lobelia4cosmetics` has the most images (cosmetic products).
- **Promotion vs Display:** Promotional posts (with people) average ~30% more views than product-only posts.

## 🔌 API Endpoints
* `GET /api/reports/top-products?limit=10` – Get the most frequent terms.
* `GET /api/channels/{channel_name}/activity` – View daily channel activity.
* `GET /api/search/messages?query=keyword&limit=20` – Search messages by keyword.
* `GET /api/reports/visual-content` – Get image stats per channel.

## 🛠️ CI/CD
GitHub Actions runs linting (`flake8`) and unit tests (`pytest`) on every push to main.
