import logging

import psycopg2
from psycopg2 import pool

logger = logging.getLogger(__name__)


class DbConnection:
    _pool: pool.ThreadedConnectionPool | None = None

    @classmethod
    def _get_pool(cls) -> pool.ThreadedConnectionPool:
        """Get or initialize the PostgreSQL connection pool.

        Returns:
            pool.ThreadedConnectionPool: The connection pool singleton.
        """
        if cls._pool is None:
            from renewable_energy_tracker.config import get_settings

            settings = get_settings()
            cls._pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=5,
                host=settings.postgres_host,
                port=settings.postgres_port,
                dbname=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password,
            )
            logger.info("Connection pool initialized")
        return cls._pool

    @classmethod
    def get_connection(cls) -> psycopg2.extensions.connection:
        """Acquire a connection from the pool.

        Returns:
            psycopg2.extensions.connection: A database connection.
        """
        return cls._get_pool().getconn()

    @classmethod
    def release_connection(cls, conn: psycopg2.extensions.connection) -> None:
        """Return a connection to the pool.

        Args:
            conn: The connection to release.
        """
        if cls._pool is not None:
            cls._pool.putconn(conn)

    @classmethod
    def close_pool(cls) -> None:
        """Close all connections in the pool and reset it."""
        if cls._pool is not None:
            cls._pool.closeall()
            cls._pool = None
            logger.info("Connection pool closed")


def get_conn() -> psycopg2.extensions.connection:
    """Shorthand for DbConnection.get_connection.

    Returns:
        psycopg2.extensions.connection: A database connection.
    """
    return DbConnection.get_connection()
