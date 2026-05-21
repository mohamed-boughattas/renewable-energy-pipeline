# AGENTS.md

## Setup

- `cp .env.example .env` then `just setup` (idempotent — `test -f .env || cp` then `uv sync --all-groups`)
- Create `.dlt/config.toml` before `just ingest` — see README Quick Start for template. `.dlt/` is gitignored.

## Commands

Primary interface is `just <recipe>`. All recipes:

| Recipe | Action |
|--------|--------|
| `lint` / `lint-fix` | ruff check / fix |
| `typecheck` | ty check (src/ only) |
| `test` / `test-all` | pytest (unit / all) |
| `test-cov` | pytest with coverage (unit, no integration) |
| `check` | lint → typecheck → test |
| `setup` | Copy .env, uv sync |
| `ingest` | dlt pipeline (Ember API → DuckDB) |
| `dbt-deps` / `dbt-seed` / `dbt-run` / `dbt-test` / `dbt-full` | dbt lifecycle |
| `soda-all` | Soda contract verification |
| `dashboard` | Shiny for Python |
| `all` | Full pipeline: ingest → dbt-full → soda-all → dashboard |

## Architecture

| Subsystem | Location | Role |
|-----------|----------|------|
| **dlt Ingestion** | `src/.../pipeline.py` | Ember Climate API → DuckDB `main` schema (incremental, upsert) |
| **Soda** | `soda/` | Data quality contracts (freshness, schema, metrics) |
| **dbt** | `dbt/` | SQL transforms: staging → marts (views → tables) |
| **Dashboard** | `src/.../app/` | Shiny for Python (direct DuckDB reads) |

**Data flow:** Ember API → dlt (`raw_monthly_*`) → dbt staging/marts → Shiny reads marts → Soda verifies contracts

## dbt specifics

- Run from `dbt/` via `cd dbt && uv run dbt ... --profiles-dir .` (profiles.yml is in `dbt/`, not `~/.dbt/`)
- **Requires `dbt-duckdb` adapter** in the venv — `dbt-core` alone is insufficient for `uv run dbt`
- Naming: `mart_` prefix (marts), `stg_` (staging), sources from `raw.*`
- `dbt-deps` works without Docker; fetches packages from internet

## dlt ingestion (`pipeline.py`)

- `@dlt.source` with multiple `@dlt.resource` for each category (generation, capacity, demand, emissions, carbon_intensity)
- `write_disposition="merge"`, `strategy="upsert"` on `(country_code, series_name, year, month)`
- HTTP via `dlt.sources.helpers.requests` (auto-retry with exponential backoff)
- API key resolved via `dlt.secrets.value` (reads from environment)
- Lands in DuckDB via `destination="duckdb"` with `dataset_name="main"`
- `pipelines_dir=".dlt/pipelines"` for local pipeline state

## Soda

- Config: `soda/ds_config.yml` — DuckDB data source
- Run via `uv run soda contract verify --contract soda/contracts/ --data-source soda/ds_config.yml`
- Uses contract files in `soda/contracts/` for schema and freshness guarantees

## Tests

- `tests/conftest.py`: `autouse=True` mock patches `get_settings()` — no `.env` needed for unit tests
- No integration tests requiring Docker

## Gotchas

- `ty` stub-less deps handled via `[tool.ty.analysis] replace-imports-with-any` (dlt, shiny, duckdb, pandera)
- `Settings()` raises `pydantic.ValidationError` if `EMBER_API_KEY` missing; guarded with `# ty: ignore[missing-argument]`
- `just setup` uses `;` not `&&` so `uv sync` runs regardless of whether `.env` already exists
- Dashboard components use `duckdb.connect(path, read_only=True)` directly — no connection pooling needed for DuckDB