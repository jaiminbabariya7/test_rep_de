"""Airflow DAG: dbt transformation pipeline — staging → intermediate → mart."""
from __future__ import annotations
from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

DBT = "dbt --project-dir /opt/airflow/dbt_project --profiles-dir /opt/airflow/dbt_project"

DEFAULT_ARGS = {"owner": "jaimin.babariya", "depends_on_past": False,
                "start_date": days_ago(1), "retries": 1,
                "retry_delay": timedelta(minutes=5)}

with DAG("dbt_run_dag", default_args=DEFAULT_ARGS,
         description="dbt: staging → intermediate → mart",
         schedule_interval=None, catchup=False,
         tags=["dbt","transform","bigquery"]) as dag:
    start        = EmptyOperator(task_id="start")
    run_staging  = BashOperator(task_id="dbt_run_staging",  bash_command=f"{DBT} run --select staging.*")
    test_staging = BashOperator(task_id="dbt_test_staging", bash_command=f"{DBT} test --select staging.*")
    run_int      = BashOperator(task_id="dbt_run_intermediate", bash_command=f"{DBT} run --select intermediate.*")
    run_mart     = BashOperator(task_id="dbt_run_mart",     bash_command=f"{DBT} run --select mart.*")
    test_mart    = BashOperator(task_id="dbt_test_mart",    bash_command=f"{DBT} test --select mart.*")
    end          = EmptyOperator(task_id="end")
    start >> run_staging >> test_staging >> run_int >> run_mart >> test_mart >> end
