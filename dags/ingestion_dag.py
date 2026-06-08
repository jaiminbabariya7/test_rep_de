"""Airflow DAG: Daily data ingestion — API → GCS → BigQuery."""
from __future__ import annotations
from datetime import timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago
import logging, requests

logger = logging.getLogger(__name__)
GCS_BUCKET = "de-reference-raw"
BQ_PROJECT = "{{ var.value.gcp_project_id }}"

DEFAULT_ARGS = {
    "owner": "jaimin.babariya",
    "depends_on_past": False,
    "start_date": days_ago(1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
}

def extract_to_gcs(execution_date: str, **kwargs) -> str:
    """Extract API data and upload Parquet to GCS.
    
    Args:
        execution_date: Airflow execution date (YYYY-MM-DD).
    Returns:
        GCS URI of uploaded file.
    """
    import io, pandas as pd
    from google.cloud.storage import Client as GCSClient
    logger.info("Extracting for %s", execution_date)
    resp = requests.get(f"https://api.example.com/orders?date={execution_date}", timeout=30)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json().get("data", []))
    df["_extracted_at"] = __import__("datetime").datetime.utcnow().isoformat()
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    gcs_key = f"ingestion/orders/{execution_date}/orders.parquet"
    GCSClient().bucket(GCS_BUCKET).blob(gcs_key).upload_from_file(buf)
    uri = f"gs://{GCS_BUCKET}/{gcs_key}"
    logger.info("Uploaded %d records to %s", len(df), uri)
    return uri

with DAG("ingestion_dag", default_args=DEFAULT_ARGS,
         description="Daily: API → GCS → BigQuery",
         schedule_interval="0 6 * * *", catchup=False,
         max_active_runs=1, tags=["ingestion","gcs","bigquery"]) as dag:
    start = EmptyOperator(task_id="start")
    extract = PythonOperator(task_id="extract_to_gcs", python_callable=extract_to_gcs,
                             op_kwargs={"execution_date": "{{ ds }}"})
    load_bq = GCSToBigQueryOperator(task_id="load_to_bigquery",
        bucket=GCS_BUCKET, source_objects=["ingestion/orders/{{ ds }}/orders.parquet"],
        destination_project_dataset_table=f"{BQ_PROJECT}.staging.raw_orders",
        source_format="PARQUET", write_disposition="WRITE_APPEND",
        create_disposition="CREATE_IF_NEEDED")
    trigger_dbt = TriggerDagRunOperator(task_id="trigger_dbt", trigger_dag_id="dbt_run_dag",
                                        wait_for_completion=True, poke_interval=30)
    end = EmptyOperator(task_id="end")
    start >> extract >> load_bq >> trigger_dbt >> end
