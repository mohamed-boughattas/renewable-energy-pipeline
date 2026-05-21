# AGENTS.md

## Setup

```bash
cp .env.example .env && just setup
```

`.dlt/` is gitignored — create these files manually before `just ingest`:

**`.dlt/config.toml`** (pipeline settings):
```
pipeline_name = "ember_energy"
dataset = "main"

[normalize]
newline_clearing = "during-load"
```

**`.dlt/secrets.toml`** (credentials):
```
destination.duckdb.credentials = "data/renewable_energy.duckdb"

sources.ember_source.api_key = "${EMBER_API_KEY}"
```

`data/` directory must exist before ingest — DuckDB creates the file but not the parent directory.

## Commands

`just <recipe>` is the only interface. Run `just --list` to see all recipes.

| Recipe | Action |
|--------|--------|
| `check` | lint → typecheck → test (CI order) |
| `lint` / `lint-fix` | ruff check / fix |
| `typecheck` | ty check (src/ only) |
| `test` | pytest unit tests (ignores `tests/integration/`) |
| `test-all` | pytest all tests including integration |
| `test-cov` | unit tests with coverage |
| `setup` | copy .env + uv sync |
| `ingest` | dlt pipeline (Ember → DuckDB); clears `.dlt/pipelines/` |
| `dbt-deps` / `dbt-seed` / `dbt-run` / `dbt-test` / `dbt-full` | dbt lifecycle |
| `soda-all` | Soda contract verify |
| `dashboard` | Shiny app |
| `all` | ingest → dbt-full → soda-all → dashboard |

CI runs `pytest -v` (no `--ignore`), so integration tests run in CI.

## Architecture

```
Ember API → dlt (raw_monthly_*) → dbt staging/ → dbt marts/ → Shiny
                                                        ↘ Soda contracts
```

| Subsystem | Location | Notes |
|-----------|----------|-------|
| dlt ingestion | `pipeline.py` | 5 resources: generation, capacity, demand, emissions, carbon_intensity |
| dbt staging | `dbt/models/staging/` | Views; `{{ source('raw', ...) }}` |
| dbt marts | `dbt/models/marts/` | Tables; `mart_` prefix |
| Shiny dashboard | `src/.../app/` | Direct `duckdb.connect(read_only=True)` — no pool |
| Soda contracts | `soda/contracts/` | Uses `soda/ds_config.yml` |

**Raw table names:** `raw_monthly_generation`, `raw_monthly_capacity`, `raw_monthly_demand`, `raw_monthly_emissions`, `raw_monthly_carbon_intensity`

## Testing

- `conftest.py` has an **autouse fixture** (`mock_settings_env`) that patches `get_settings()` with a mock — tests never instantiate real `Settings()` and don't need `EMBER_API_KEY`
- To add a test that needs a real DuckDB, provide duckdb_path explicitly and ensure the file exists

## dbt specifics

- Run from `dbt/` via `cd dbt && uv run dbt ... --profiles-dir .`
- **`dbt-duckdb` is in `[project.dependencies]`**, not dev — required at runtime
- profiles.yml: `path: "../data/renewable_energy.duckdb"` (relative to `dbt/`)
- `dbt_project.yml` vars: `dbt_date:time_zone: "UTC"` (required by `metaplane/dbt_expectations` freshness tests)
- Seeds: `{{ ref('countries') }}` and `{{ ref('energy_sources') }}` — land in `main_seed` schema
- `metaplane/dbt_expectations` (not `calogica`)
- `co2_avoided` macro uses `grid_avg_emission_factor` var (default 0.45) from `dbt_project.yml`

## Gotchas

- **Ember uses 3-letter ISO codes** (DEU, FRA, ESP) — seeds and staging models use these. Staging models JOIN on `country_code = countries.code`, so 2-letter codes silently produce empty results
- **`ingest` clears `.dlt/pipelines/`** to prevent stale incremental state from skipping new rows
- **`just setup` uses `;` not `&&`** — `uv sync` runs even if `.env` already existed
- `ty` stub-less deps handled via `[tool.ty.analysis] replace-imports-with-any` (dlt, shiny, duckdb, pandera)
- `Settings()` raises `pydantic.ValidationError` if `EMBER_API_KEY` is missing; guarded with `# ty: ignore[missing-argument]`
- DuckDB SQL: `ROUND(double, int)` fails — cast first: `ROUND(value::numeric, 2)`
