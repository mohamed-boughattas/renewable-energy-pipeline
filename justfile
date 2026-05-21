set dotenv-path := ".env"
set dotenv-required := false

@_default:
    @just --list

setup:
    test -f .env || cp .env.example .env; uv sync --all-groups

lint:
    uv run ruff check src/ tests/

lint-fix:
    uv run ruff check --fix src/ tests/

typecheck:
    uv run ty check src/

test:
    uv run pytest -v --ignore=tests/integration/

test-all:
    uv run pytest -v

check: lint typecheck test

test-cov:
    uv run pytest --cov=src/ --cov-report=term-missing --cov-report=html --ignore=tests/integration/

ingest:
    rm -rf .dlt/pipelines
    uv run python -m renewable_energy_tracker.pipeline

dbt-deps:
    cd dbt && uv run dbt deps

dbt-seed:
    cd dbt && uv run dbt seed --profiles-dir .

dbt-run:
    cd dbt && uv run dbt run --profiles-dir .

dbt-test:
    cd dbt && uv run dbt test --profiles-dir .

dbt-full: dbt-deps dbt-seed dbt-run dbt-test

soda-all:
    uv run soda contract verify --contract soda/contracts/ --data-source soda/ds_config.yml

dashboard:
    uv run shiny run src/renewable_energy_tracker/app/app.py

all: ingest dbt-full soda-all dashboard
