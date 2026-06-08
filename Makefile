.PHONY: install install-dev lint format test run-api docker-up clean

install:
	pip install -r requirements.txt

install-dev: install
	pip install pytest pytest-cov black isort flake8 httpx

lint:
	flake8 src/ api/ dags/ tests/ --max-line-length=100 --ignore=E501,W503
	black --check --line-length 100 src/ api/ dags/ tests/

format:
	black --line-length 100 src/ api/ dags/ tests/
	isort src/ api/ dags/ tests/

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

run-api:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

docker-up:
	docker compose -f docker/docker-compose.yml up --build -d

docker-down:
	docker compose -f docker/docker-compose.yml down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/ dist/
