# Renewable Energy Production Tracker

A data pipeline and dashboard that tracks renewable energy production across 6 European countries using ENTSO-E Transparency Platform data.

## Tech Stack

| Tool | Purpose |
|------|---------|
| **uv** | Package management & build |
| **just** | Task runner |
| **ruff** | Linting & formatting |
| **ty** | Type checking |
| **dlt** | Data ingestion (incremental, schema evolution) |
| **lxml** | XML parsing for ENTSO-E API responses |
| **Soda** | Data quality monitoring |
| **pandas** | DataFrame validation & dashboard data |
| **Pydantic** | Settings & record-level validation |
| **Pandera** | DataFrame-level validation |
| **Kestra** | Orchestration |
| **PostgreSQL** | Data storage |
| **dbt** | SQL transformations (medallion: bronze → silver → gold) |
| **Shiny for Python** | Interactive dashboard |
| **Great Tables** | Publication-quality tables |

## Architecture

```
ENTSO-E API (XML)
       │
       ▼
   ┌─────────┐
   │   dlt    │  incremental upsert
   │ pipeline │  schema inference
   └────┬────┘
        │
        ▼
  raw.raw_daily_production (PostgreSQL)
        │
        ▼
   ┌─────────┐
   │   dbt    │  bronze/  → source definitions (view)
   │(medallion)│  silver/  → cleaned + enriched (view)
   │          │  gold/    → aggregated marts (table)
   └────┬────┘
        │
   ┌────┴────┐
   ▼         ▼
Shiny      Soda
Dashboard  Quality
(+ Great   Checks
 Tables)
```

**Countries tracked:** Germany (DE), France (FR), Spain (ES), Denmark (DK), Norway (NO), Netherlands (NL)

**Data flow:** ENTSO-E XML → dlt (`raw.raw_daily_production`) → dbt bronze/silver/gold → Shiny reads gold models → Soda monitors quality

## Prerequisites

- **Python 3.12+**
- **uv** — [install guide](https://docs.astral.sh/uv/getting-started/installation/)
- **just** — `brew install just` or [just.systems/man](https://just.systems/man/)
- **Docker** & Docker Compose
- **ENTSO-E API key** — free token from the [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd renewable_energy_tracker

# 2. Copy environment config and set your API key
cp .env.example .env
#   Then edit .env and add your ENTSOE_API_KEY

# 3. Create dlt pipeline config
mkdir -p .dlt && cat > .dlt/config.toml << 'EOF'
pipeline_name = "entsoe_energy"

[normalize]
  newline_clearing = "during-load"
EOF
cat > .dlt/secrets.toml << 'EOF'
[destination.postgres.credentials]
host = "${POSTGRES_HOST}"
port = "${POSTGRES_PORT}"
username = "${POSTGRES_USER}"
password = "${POSTGRES_PASSWORD}"
database = "${POSTGRES_DB}"

[sources.entsoe_source]
api_key = "${ENTSOE_API_KEY}"
EOF

# 4. Start PostgreSQL + Kestra (requires Docker daemon running)
just db-up

# 5. Verify code quality early (no Docker needed)
just check

# 6. Fetch ENTSO-E data via dlt pipeline (requires Docker)
just ingest

# 7. Run dbt (requires Docker; may need `uv add --dev dbt-postgres` locally if adapter missing)
just dbt-full

# 8. Launch the Shiny dashboard
just dashboard
```

> **Note:** Several steps (`db-up`, `ingest`, `dbt-*`, `soda-*`) require the Docker daemon running. On first run `just db-up` pulls ~3.5GB of images (PostgreSQL 16 + Kestra).

> **dlt env var interpolation:** `.dlt/secrets.toml` uses `${VAR}` syntax which dlt resolves via `EnvironProvider`. just's `set dotenv-path` does not reliably export these to subprocesses — set the variables explicitly or export them from your shell.

## Usage

All commands go through `just`. Run `just --list` to see everything.

| Command | What it does |
|---------|-------------|
| `just setup` | Copy `.env.example` → `.env` + `uv sync --all-groups` |
| `just lint` | Run ruff |
| `just lint-fix` | Auto-fix ruff violations |
| `just typecheck` | Run ty |
| `just test` | Unit tests (skip integration) |
| `just test-all` | All tests including integration |
| `just test-cov` | Unit tests with HTML coverage report |
| `just check` | Lint → typecheck → test |
| `just db-up` / `just db-down` | Start/stop Docker containers |
| `just db-reset` | Destroy and recreate containers |
| `just ingest` | Fetch ENTSO-E data via dlt |
| `just dbt-deps` / `just dbt-seed` / `just dbt-run` / `just dbt-test` / `just dbt-full` | dbt lifecycle |
| `just soda-raw` / `just soda-gold` / `just soda-all` | Soda quality checks |
| `just dashboard` | Start Shiny app |
| `just all` | Full end-to-end pipeline |

## Project Structure

```
renewable-energy-tracker/
├── justfile                          # Task runner recipes
├── pyproject.toml                    # uv project config + dependencies
├── docker-compose.yml                # PostgreSQL 16 + Kestra
├── .env.example                      # Environment variables template
├── AGENTS.md                         # Agent instructions (just recipes, gotchas, architecture)
├── .dlt/                            # dlt pipeline config (gitignored; secrets.toml uses ${VAR} interpolation)
├── .github/
│   └── workflows/ci.yml             # CI: lint → typecheck → test → dbt → soda
├── soda/                            # Soda data quality checks
│   ├── configuration.yml
│   ├── checks_raw.yml
│   └── checks_gold.yml
├── sql/
│   └── schema.sql                   # Raw tables + indexes
├── src/
│   └── renewable_energy_tracker/     # Python package (src layout)
│       ├── config.py                # Pydantic Settings
│       ├── pipeline.py              # dlt ingestion source/resource
│       ├── models/                  # Pydantic + Pandera schemas
│       └── app/                    # Shiny dashboard + components
├── dbt/                             # dbt project (medallion architecture)
│   ├── packages.yml                 # dbt-expectations dependency (calogica → metaplane migration pending)
│   ├── seeds/                      # Reference data (CSV)
│   ├── macros/                     # Jinja macros (co2_avoided)
│   ├── models/
│   │   ├── bronze/                # Source definitions
│   │   ├── silver/                # Cleaned + enriched
│   │   └── gold/                  # Aggregated marts
│   └── tests/
├── kestra/
│   └── flows/                      # Scheduled + backfill flows
└── tests/
    ├── conftest.py                  # Fixtures + mock_settings (autouse)
    ├── integration/                 # Docker-based integration tests
    └── unit tests
├── htmlcov/                         # Coverage HTML report (gitignored)
└── .coverage                       # Coverage data (gitignored)
```

## Data Source

[ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) provides free access to European power system data via a REST API.

- **Endpoint used:** Actual Generation per Production Type (documentType A73)
- **Response format:** XML
- **Authentication:** Security token (free registration required)
- **Coverage:** 6 European countries across solar, wind, hydro, biomass, nuclear, and fossil sources

## License

MIT
