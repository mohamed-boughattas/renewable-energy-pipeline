from unittest.mock import MagicMock, patch

from renewable_energy_tracker.app.query import DbConnection, get_conn


def test_db_connection_pool_initialization() -> None:
    """Verify DbConnection._get_pool returns a non-None pool.

    Uses mock to avoid requiring a live PostgreSQL instance.
    """
    with patch("renewable_energy_tracker.app.query.DbConnection._get_pool") as mock_get_pool:
        mock_pool = MagicMock()
        mock_get_pool.return_value = mock_pool

        pool = DbConnection._get_pool()
        assert pool is not None


def test_db_connection_close_pool() -> None:
    """Verify DbConnection.close_pool resets _pool to None."""
    with patch.object(DbConnection, "_pool", MagicMock()):
        DbConnection.close_pool()
        assert DbConnection._pool is None


def test_db_connection_release_connection() -> None:
    """Verify DbConnection.release_connection returns conn to the pool."""
    mock_pool = MagicMock()
    mock_conn = MagicMock()

    with patch.object(DbConnection, "_pool", mock_pool):
        DbConnection.release_connection(mock_conn)
        mock_pool.putconn.assert_called_once_with(mock_conn)


def test_db_connection_release_connection_no_pool() -> None:
    """Verify release_connection does nothing when _pool is None."""
    with patch.object(DbConnection, "_pool", None):
        DbConnection.release_connection(MagicMock())


def test_get_conn() -> None:
    """Verify get_conn delegates to DbConnection.get_connection."""
    with patch.object(DbConnection, "get_connection") as mock_get_conn:
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn

        conn = get_conn()
        assert conn is mock_conn
        mock_get_conn.assert_called_once()
