.PHONY: install install-dev lint test dbt-run dbt-test clean
install:
	pip install apache-airflow[google] dbt-bigquery
install-dev: install
	pip install pytest pytest-cov black flake8
lint:
	flake8 dags/ tests/ --max-line-length=100
test:
	pytest tests/ -v --cov=dags --cov-report=term-missing
dbt-run:
	dbt run --project-dir dbt_project --profiles-dir dbt_project
dbt-test:
	dbt test --project-dir dbt_project --profiles-dir dbt_project
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true