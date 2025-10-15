from airflow import DAG
from airflow.operators.python import PythonOperator
import json
import logging
from datetime import datetime
import pandas as pd
import sqlalchemy

log = logging.getLogger(__name__)


def start_pipline():
    log.info("pipline started!")


def extract_data(**context):
    try:
        file_path = "/opt/airflow/logs/sample_logs.jsonl"
        log.info(f"Reading data from {file_path}")

        with open(file_path, "r") as file:
            data = [json.loads(line.strip()) for line in file if line.strip()]

        log.info(f"Data extracted successfully! Total records: {len(data)}")
        context["ti"].xcom_push(key="data", value=data)
    except FileNotFoundError as e:
        log.error(f"File not found: {e}")
        raise
    except Exception as e:
        log.exception(f"Error extracting data: {e}")
        raise


def process_data(**context):
    data = context["ti"].xcom_pull(key="data", task_ids="extract")

    if not data:
        log.error("No data received from extract task!")
        raise ValueError("No data to process")

    log.info(f"Processing {len(data)} records")
    df = pd.DataFrame(data)

    log.info(f"DataFrame columns: {df.columns.tolist()}")
    log.info(f"DataFrame shape: {df.shape}")

    df = df[df["sensor_id"] > 0]
    df = df.dropna()

    df = df[(df["temperature"] <= 100) & (df["temperature"] >= -25)]
    context["ti"].xcom_push(key="cleaned_data", value=df.to_dict(orient="records"))


def create_table():
    """Create MySQL table if it doesn't exist"""
    engine = sqlalchemy.create_engine(
        "mysql+pymysql://airflow:airflow@mysql/airflow_db"
    )

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sensor_readings(
        id INT AUTO_INCREMENT PRIMARY KEY,
        sensor_id INT,
        timestamp VARCHAR(255),
        temperature FLOAT,
        humidity FLOAT,
        INDEX idx_timestamp (timestamp),
        INDEX idx_sensor_id (sensor_id)
    )
    """

    with engine.begin() as conn:
        conn.execute(sqlalchemy.text(create_table_sql))

    log.info("Table created successfully!")


def load_data(**context):
    df = pd.DataFrame(context["ti"].xcom_pull(key="cleaned_data", task_ids="transform"))

    if df.empty:
        log.warning("No data to load!")
        return

    log.info(f"Loading {len(df)} records to database")

    engine = sqlalchemy.create_engine(
        "mysql+pymysql://airflow:airflow@mysql/airflow_db"
    )

    # Calculate averages per sensor
    avg_df = df.groupby("sensor_id", as_index=False)[["temperature", "humidity"]].mean()
    avg_df.rename(
        columns={"temperature": "avg_temperature", "humidity": "avg_humidity"},
        inplace=True,
    )

    # Load aggregated data (replace existing)
    avg_df.to_sql("sensor_avg", con=engine, if_exists="replace", index=False)
    log.info(f"Loaded {len(avg_df)} average records to sensor_avg table")

    # Load detailed data (replace to avoid duplicates)
    df.to_sql("sensor_readings", con=engine, if_exists="replace", index=False)
    log.info(f"Loaded {len(df)} records to sensor_readings table")


with DAG(
    dag_id="etl_dag",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:
    start = PythonOperator(task_id="start", python_callable=start_pipline)

    extract = PythonOperator(task_id="extract", python_callable=extract_data)

    transform = PythonOperator(task_id="transform", python_callable=process_data)

    create_table_task = PythonOperator(
        task_id="create_mysql_table", python_callable=create_table
    )

    load2 = PythonOperator(task_id="load_data", python_callable=load_data)

    start >> extract >> transform >> create_table_task >> load2
