# Renewable Energy Production Tracker

A data pipeline and dashboard that tracks renewable energy production across European countries using Ember Climate API data.

## Tech Stack

| Tool | Purpose |
|------|---------|
| **uv** | Package management & build |
| **just** | Task runner |
| **ruff** | Linting & formatting |
| **ty** | Type checking |
| **dlt** | Data ingestion (incremental, schema evolution) |
| **DuckDB** | OLAP database (local `.duckdb` file) |
| **dbt-duckdb** | SQL transformations (staging → marts) |
| **Soda** | Data quality monitoring |
| **polars** | DataFrame manipulation |
| **Shiny for Python** | Interactive dashboard |

## Architecture

```
Ember Climate API (JSON)
        │
        ▼
    ┌─────────┐
    │   dlt    │  incremental upsert
    │ pipeline │  schema inference
    └────┬────┘
         │
         ▼
   raw_monthly_* (DuckDB main schema)
         │
         ▼
    ┌─────────┐
    │   dbt    │  staging/ → cleaned views
    │          │  marts/    → aggregated tables
    └────┬────┘
         │
    ┌────┴────┐
    ▼         ▼
 Shiny      Soda
 Dashboard  Quality
```

**Data flow:** Ember API → dlt → DuckDB → dbt staging/marts → Shiny reads marts → Soda verifies contracts

## Prerequisites

- **Python 3.12+**
- **uv** — [install guide](https://docs.astral.sh/uv/getting-started/installation/)
- **just** — `brew install just` or [just.systems/man](https://just.systems/man/)
- **Ember API key** — free token from [Ember Climate](https://ember-climate.org/data/)

## Quick Start

```bash
# 1. Clone and enter directory
git clone <repo-url>
cd renewable_energy_tracker

# 2. Copy environment config and set your API key
cp .env.example .env
# Then edit .env and add your EMBER_API_KEY

# 3. Install dependencies
just setup

# 4. Verify code quality
just check

# 5. Ingest data from Ember API
just ingest

# 6. Run dbt transformations
just dbt-full

# 7. Launch the Shiny dashboard
just dashboard
```

## Usage

All commands go through `just`. Run `just --list` to see everything.

| Command | What it does |
|---------|-------------|
| `just setup` | Copy `.env.example` → `.env` + `uv sync --all-groups` |
| `just lint` | Run ruff |
| `just lint-fix` | Auto-fix ruff violations |
| `just typecheck` | Run ty |
| `just test` | Unit tests |
| `just test-cov` | Unit tests with HTML coverage report |
| `just check` | Lint → typecheck → test |
| `just ingest` | Fetch Ember data via dlt pipeline |
| `just dbt-deps` / `just dbt-seed` / `just dbt-run` / `just dbt-test` / `just dbt-full` | dbt lifecycle |
| `just soda-all` | Soda quality checks |
| `just dashboard` | Start Shiny app |
| `just all` | Full end-to-end pipeline |

## Project Structure

```
renewable-energy-tracker/
├── justfile                          # Task runner recipes
├── pyproject.toml                    # uv project config + dependencies
├── .env.example                      # Environment variables template
├── AGENTS.md                         # Agent instructions
├── .github/
│   └── workflows/ci.yml             # CI: lint → typecheck → test → dbt
├── soda/                            # Soda data quality contracts
├── src/
│   └── renewable_energy_tracker/   # Python package
│       ├── config.py                # Pydantic Settings
│       ├── pipeline.py              # dlt ingestion source/resource
│       ├── models/                  # Pydantic + Pandera schemas
│       └── app/                    # Shiny dashboard + components
├── dbt/                             # dbt project
│   ├── packages.yml                 # dbt-expectations dependency
│   ├── seeds/                      # Reference data (CSV)
│   ├── macros/                     # Jinja macros
│   ├── models/
│   │   ├── staging/               # Cleaned views
│   │   └── marts/                # Aggregated tables
│   └── tests/
└── tests/
    ├── conftest.py                # Fixtures + mock_settings (autouse)
    └── test_*.py                 # Unit tests
```

## Data Source

[Ember Climate API](https://api.ember-climate.org/) provides free access to global electricity data via a REST API.

- **Endpoint used:** Electricity data by category (generation, capacity, demand, emissions, carbon_intensity)
- **Response format:** JSON
- **Authentication:** Bearer token (free registration required)
- **Coverage:** Multiple countries across solar, wind, hydro, biomass, nuclear, and fossil sources

## License

MIT