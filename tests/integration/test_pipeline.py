import subprocess
import time
from collections.abc import Iterator

import psycopg2
import pytest

DOCKER_COMPOSE = ["docker", "compose", "-f", "docker-compose.yml"]


@pytest.fixture(scope="module")
def postgres_container() -> Iterator[None]:
    """Start a PostgreSQL container via Docker Compose for integration tests.

    Waits up to 30 seconds for the container to become ready.
    Tears down the container after the module completes.

    Yields:
        None: Signals that the container is ready.
    """
    subprocess.run(DOCKER_COMPOSE + ["up", "-d", "postgres"], check=True, capture_output=True)
    for _ in range(30):
        result = subprocess.run(
            DOCKER_COMPOSE
            + ["exec", "-T", "postgres", "pg_isready", "-U", "renewable"],
            capture_output=True,
        )
        if result.returncode == 0:
            break
        time.sleep(1)
    else:
        pytest.skip("PostgreSQL container did not become ready")

    yield

    subprocess.run(DOCKER_COMPOSE + ["down", "-v"], capture_output=True)


@pytest.fixture(scope="module")
def dbt_pipeline(postgres_container: None) -> Iterator[None]:
    """Run dbt seed, run, and test against the live PostgreSQL instance.

    Args:
        postgres_container: Ensures the database is running.

    Yields:
        None: Signals that all dbt commands completed successfully.
    """
    env = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "renewable_energy",
        "POSTGRES_USER": "renewable",
        "POSTGRES_PASSWORD": "renewable123",
    }
    for cmd in ["seed", "run", "test"]:
        subprocess.run(
            ["dbt", cmd, "--profiles-dir", "dbt", "--project-dir", "dbt"],
            env=env,
            check=True,
            capture_output=True,
        )


@pytest.fixture
def db_connection() -> Iterator[psycopg2.extensions.connection]:
    """Create a direct psycopg2 connection to the test PostgreSQL instance.

    Yields:
        psycopg2.extensions.connection: An active database connection.
    """
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="renewable_energy",
        user="renewable",
        password="renewable123",
    )
    yield conn
    conn.close()


def test_raw_daily_production_table(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Verify the raw_daily_production table has the expected columns.

    Args:
        db_connection: Fixture providing a live database connection.
    """
    with db_connection.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'raw_daily_production'
            ORDER BY ordinal_position
            """,
        )
        columns = {row[0]: row[1] for row in cur.fetchall()}

    assert "id" in columns
    assert "country_code" in columns
    assert "source_code" in columns
    assert "production_date" in columns
    assert "production_mwh" in columns


def test_gold_models_exist(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Verify all expected gold-layer tables exist and are non-empty.

    Args:
        db_connection: Fixture providing a live database connection.
    """
    gold_tables = [
        "gld_monthly_production_summary",
        "gld_country_renewable_ranking",
        "gld_co2_savings_by_country",
    ]
    with db_connection.cursor() as cur:
        for table in gold_tables:
            cur.execute(f"SELECT 1 FROM {table} LIMIT 1")
            assert cur.fetchone() is not None, f"{table} is empty or missing"


def test_gold_monthly_production_columns(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Verify gld_monthly_production_summary has the required columns.

    Args:
        db_connection: Fixture providing a live database connection.
    """
    with db_connection.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'gld_monthly_production_summary'
            ORDER BY ordinal_position
            """,
        )
        columns = [row[0] for row in cur.fetchall()]

    required = {"country_code", "year_month", "total_production_mwh", "renewable_share_pct"}
    assert required.issubset(columns), f"Missing columns: {required - set(columns)}"


def test_dbt_tests_pass(
    db_connection: psycopg2.extensions.connection,
) -> None:
    """Verify no dbt tests have failed.

    Args:
        db_connection: Fixture providing a live database connection.
    """
    with db_connection.cursor() as cur:
        cur.execute(
            """
            SELECT table_name, test_status
            FROM dbt_test_results
            WHERE test_status = 'fail'
            """,
        )
        failures = cur.fetchall()
    assert len(failures) == 0, f"dbt tests failed: {failures}"
