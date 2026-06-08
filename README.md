# Data Engineering Reference Project

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-2.8-017CEE?logo=apacheairflow)
![dbt](https://img.shields.io/badge/dbt-1.7-FF694B?logo=dbt)
![BigQuery](https://img.shields.io/badge/BigQuery-Warehouse-4285F4?logo=googlebigquery)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

> Production-ready DE reference stack: Apache Airflow + dbt + BigQuery. Reusable DAG patterns, layered dbt models (staging → intermediate → mart), data quality tests, full dev workflow.

## Architecture
```
Raw Sources (GCS / API / Database)
        ↓
Apache Airflow  ←  orchestrates extract, load, and dbt runs
        ↓
dbt on BigQuery
  ├── staging/      ←  clean, rename, cast types
  ├── intermediate/ ←  joins, deduplication, business logic
  └── mart/         ←  fact & dimension tables for BI / ML
        ↓
BigQuery Mart → Dashboards · Analytics · Downstream ML
```

## Project Structure
```
├── dags/
│   ├── ingestion_dag.py       # Daily extract → GCS → BigQuery
│   └── dbt_run_dag.py         # Trigger dbt run after ingestion
├── dbt_project/
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/           stg_orders.sql, stg_customers.sql
│       ├── intermediate/      int_order_items.sql
│       └── mart/              fct_orders.sql, dim_customers.sql
├── tests/
│   └── test_dags.py
├── pyproject.toml
└── Makefile
```

## dbt Models

| Layer | Model | Description |
|---|---|---|
| staging | `stg_orders` | Cleaned, typed order records |
| staging | `stg_customers` | Cleaned customer records |
| intermediate | `int_order_items` | Orders joined with customers |
| mart | `fct_orders` | Order fact table with rolling KPIs |
| mart | `dim_customers` | Customer dimension with LTV tiers |

## Setup
```bash
git clone https://github.com/jaiminbabariya7/test_rep_de
cd test_rep_de && make install-dev
export GOOGLE_APPLICATION_CREDENTIALS=path/to/sa.json
export GCP_PROJECT_ID=your-project-id
make dbt-run    # run all dbt models
make dbt-test   # run data quality tests
make test       # run unit tests
```

## Skills Demonstrated
`Apache Airflow` · `dbt Core` · `BigQuery` · `Python` · `ELT` · `Data Modelling` · `Pipeline Orchestration` · `Data Quality Testing`
