from dagster import op, job, schedule, Definitions, RunRequest
from datetime import datetime
import os
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(PROJECT_ROOT, "venv", "Scripts", "python.exe")
DBT_PROJECT_DIR = os.path.join(PROJECT_ROOT, "medical_warehouse")

def run_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, cwd=cwd or PROJECT_ROOT, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

@op
def scrape_telegram_data():
    print("Running scraper...")
    cmd = f'"{VENV_PYTHON}" src/scraper.py'
    stdout, stderr, rc = run_command(cmd)
    if rc != 0:
        raise Exception(f"Scraper failed: {stderr}")
    print(stdout)
    return True

@op
def load_raw_to_postgres(scrape_success):
    if not scrape_success:
        raise Exception("Scraper failed")
    print("Loading raw data...")
    cmd = f'"{VENV_PYTHON}" src/load_raw_data.py'
    stdout, stderr, rc = run_command(cmd)
    if rc != 0:
        raise Exception(f"Load failed: {stderr}")
    print(stdout)
    return True

@op
def run_dbt_transformations(load_success):
    if not load_success:
        raise Exception("Load failed")
    print("Running dbt...")
    cmd = f'"{VENV_PYTHON}" -m dbt run --project-dir {DBT_PROJECT_DIR}'
    stdout, stderr, rc = run_command(cmd, cwd=DBT_PROJECT_DIR)
    if rc != 0:
        raise Exception(f"dbt failed: {stderr}")
    print(stdout)
    return True

@op
def run_yolo_enrichment(dbt_success):
    if not dbt_success:
        raise Exception("dbt failed")
    print("Running YOLO...")
    cmd = f'"{VENV_PYTHON}" src/yolo_detect.py'
    stdout, stderr, rc = run_command(cmd)
    if rc != 0:
        raise Exception(f"YOLO failed: {stderr}")
    print(stdout)
    return True

@op
def load_yolo_to_postgres(yolo_success):
    if not yolo_success:
        raise Exception("YOLO failed")
    print("Loading YOLO results...")
    cmd = f'"{VENV_PYTHON}" src/load_yolo_results.py'
    stdout, stderr, rc = run_command(cmd)
    if rc != 0:
        raise Exception(f"YOLO load failed: {stderr}")
    print(stdout)
    return True

@job
def medical_warehouse_pipeline():
    scrape = scrape_telegram_data()
    load = load_raw_to_postgres(scrape)
    dbt = run_dbt_transformations(load)
    yolo = run_yolo_enrichment(dbt)
    load_yolo_to_postgres(yolo)

@schedule(
    job=medical_warehouse_pipeline,
    cron_schedule="0 6 * * *",
    execution_timezone="UTC",
)
def daily_pipeline_schedule():
    return RunRequest(
        run_key=f"daily_run_{datetime.now().strftime('%Y-%m-%d')}",
        tags={"source": "schedule", "trigger": "daily"},
    )

defs = Definitions(
    jobs=[medical_warehouse_pipeline],
    schedules=[daily_pipeline_schedule],
) 