# AGENTS.md

## Setup

- `cp .env.example .env` then `just setup` (idempotent — `test -f .env || cp` then `uv sync --all-groups`)
- `just db-up` pulls Docker images on first run (PostgreSQL 16 ~450MB, Kestra ~3GB), then starts containers; schema loads from `sql/schema.sql` via init script
- Create `.dlt/config.toml` and `.dlt/secrets.toml` before `just ingest` — see README Quick Start for templates. `.dlt/` is gitignored.

## Commands

Primary interface is `just <recipe>`. All 22 recipes:

| Recipe | Action |
|--------|--------|
| `lint` / `lint-fix` | ruff check / fix |
| `typecheck` | ty check (src/ only) |
| `test` / `test-all` | pytest (unit / all) |
| `test-cov` | pytest with coverage (unit, no integration) |
| `check` | lint → typecheck → test |
| `setup` | Copy .env, uv sync |
| `db-up` / `db-down` / `db-reset` | Docker Compose lifecycle |
| `ingest` | dlt pipeline (ENTSO-E XML → `raw` schema) |
| `dbt-deps` / `dbt-seed` / `dbt-run` / `dbt-test` / `dbt-full` | dbt lifecycle |
| `soda-raw` / `soda-gold` / `soda-all` | Soda quality checks |
| `dashboard` | Shiny for Python |
| `all` | Full pipeline: db-up → ingest → dbt-full → soda-all → dashboard |

## Architecture

| Subsystem | Location | Role |
|-----------|----------|------|
| **dlt Ingestion** | `src/.../pipeline.py` | ENTSO-E XML → PostgreSQL `raw` schema (incremental, upsert) |
| **Soda Quality** | `soda/` | Data quality checks (freshness, schema, metrics) |
| **dbt** | `dbt/` | SQL transforms: bronze → silver → gold (views → tables) |
| **Dashboard** | `src/.../app/` | Shiny for Python (uses `DbConnection` thread-safe pool) |

**Data flow:** ENTSO-E XML → dlt (`raw.raw_daily_production`) → dbt bronze/silver/gold → Shiny reads gold models → Soda monitors quality

## dbt specifics

- Run from `dbt/` via `cd dbt && uv run dbt ... --profiles-dir .` (profiles.yml is in `dbt/`, not `~/.dbt/`)
- **Requires `dbt-postgres` adapter** in the venv — `dbt-core` alone is insufficient for `uv run dbt`. Add `dbt-postgres` to `[project.dependencies]`.
- Medallion: `bronze/` (source definitions, view) → `silver/` (cleaned views) → `gold/` (aggregated tables)
- Naming: `gld_` prefix (gold), `slv_` (silver), sources from `raw.raw_daily_production`
- `dbt-deps` works without Docker; fetches packages from internet
- `calogica/dbt_expectations` deprecated — update `packages.yml` to use `metaplane/dbt_expectations`
- Container names: `ret_postgres`, `ret_kestra`

## dlt ingestion (`pipeline.py`)

- `@dlt.source` / `@dlt.resource` with `write_disposition="merge"`, `strategy="upsert"` on `(country_code, source_code, production_date)`
- `dlt.sources.incremental` on `production_date`; cursor tracked in `_dlt_pipeline_state`
- HTTP via `dlt.sources.helpers.requests` (auto-retry 5x with exponential backoff)
- API key resolved via `dlt.secrets.value` (reads from `.dlt/secrets.toml`)
- Lands in `raw` dataset (PostgreSQL schema), not `public`
- **`.dlt/secrets.toml` uses `${POSTGRES_PORT}` env var syntax** — dlt resolves these from `os.environ` via `EnvironProvider`. Ensure POSTGRES_* and ENTSOE_API_KEY are actual shell env vars (just's `set dotenv-path` may not export them to subprocesses reliably). CI workflow sets them explicitly in `env:` block.

## Soda

- Config: `soda/configuration.yml` — uses `${POSTGRES_HOST}` env var syntax
- Run via `uv run soda scan -d ret_postgres ...` (soda-postgres is in `[dev]`)

## Tests

- `tests/conftest.py`: `autouse=True` mock patches `get_settings()` — no `.env` needed for unit tests
- Integration tests (`tests/integration/`) have their own `postgres_container` fixture that starts Docker via `docker compose up -d postgres`; requires running Docker daemon
- Integration test credentials are hardcoded (match docker-compose.yml defaults)

## Gotchas

- `ty` stub-less deps handled via `[tool.ty.analysis] replace-imports-with-any` (dlt, lxml, shiny, psycopg2, pandera)
- `Settings()` raises `pydantic.ValidationError` if `ENTSOE_API_KEY` missing; guarded with `# ty: ignore[missing-argument]` (no default, user must set the var)
- Pandera raises `SchemaError` (singular) from `pandera.errors`, not `SchemaErrors`
- `just setup` uses `;` not `&&` so `uv sync` runs regardless of whether `.env` already exists
- `dlt[postgres]` brings `psycopg2-binary` — postgres destination works without a separate driver install
