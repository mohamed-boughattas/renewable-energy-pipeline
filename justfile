set dotenv-path := ".env"
set dotenv-required := false

# ── Default: list recipes ──
@_default:
    @just --list

# Initialize development environment
setup:
    test -f .env || cp .env.example .env; uv sync --all-groups

# Check code style with ruff
lint:
    uv run ruff check src/ tests/

# Auto-fix ruff violations
lint-fix:
    uv run ruff check --fix src/ tests/

# Run static type checking with ty
typecheck:
    uv run ty check src/

# Run unit tests (skip integration)
test:
    uv run pytest -v --ignore=tests/integration/

# Run all tests including integration
test-all:
    uv run pytest -v

# Lint, typecheck, and test
check: lint typecheck test

# Run tests with coverage report
test-cov:
    uv run pytest --cov=src/ --cov-report=term-missing --cov-report=html --ignore=tests/integration/

# Start PostgreSQL and Kestra
db-up:
    docker compose up -d

# Stop Docker containers
db-down:
    docker compose down

# Destroy and recreate containers
db-reset:
    docker compose down -v && docker compose up -d

# Fetch ENTSO-E data via dlt pipeline
ingest:
    uv run python -m renewable_energy_tracker.pipeline

# Install dbt package dependencies
dbt-deps:
    cd dbt && uv run dbt deps

# Load reference data (countries, sources, factors)
dbt-seed:
    cd dbt && uv run dbt seed --profiles-dir . --target dev

# Execute dbt transformations
dbt-run:
    cd dbt && uv run dbt run --profiles-dir . --target dev

# Run dbt data tests
dbt-test:
    cd dbt && uv run dbt test --profiles-dir . --target dev

# Full dbt lifecycle
dbt-full: dbt-deps dbt-seed dbt-run dbt-test

# Start Shiny dashboard
dashboard:
    uv run shiny run src/renewable_energy_tracker/app/app.py

# Scan raw table for quality issues
soda-raw:
    uv run soda scan -d ret_postgres -c soda/configuration.yml soda/checks_raw.yml

# Scan gold models for quality issues
soda-gold:
    uv run soda scan -d ret_postgres -c soda/configuration.yml soda/checks_gold.yml

# Run all Soda quality checks
soda-all: soda-raw soda-gold

# Run everything end-to-end
all: db-up ingest dbt-full soda-all dashboard
