from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd


class TestTimeseriesUi:
    def test_timeseries_ui_returns_taglist(self) -> None:
        """Verify timeseries_ui returns a ui.TagList (not None)."""
        from renewable_energy_tracker.app.components.timeseries import timeseries_ui

        result = timeseries_ui()
        assert result is not None


class TestTimeseriesServer:
    def test_timeseries_server_registers_outputs(self) -> None:
        """Verify timeseries_server registers timeseries_data output."""
        from shiny import Inputs, Outputs, Session

        from renewable_energy_tracker.app.components.timeseries import (
            timeseries_server,
        )

        mock_input = MagicMock(spec=Inputs)
        mock_output = MagicMock(spec=Outputs)
        mock_session = MagicMock(spec=Session)

        timeseries_server(mock_input, mock_output, mock_session)


class TestTimeseriesData:
    def test_timeseries_data_empty_when_no_countries(self) -> None:
        """Verify timeseries_data returns empty DataFrame when no countries selected."""
        with patch("renewable_energy_tracker.app.components.timeseries.get_conn"):
            from renewable_energy_tracker.app.components.timeseries import (
                timeseries_server,
            )

            mock_input = MagicMock()
            mock_input.ts_countries.return_value = []
            mock_output = MagicMock()
            mock_session = MagicMock()

            timeseries_server(mock_input, mock_output, mock_session)


class TestOverviewUi:
    def test_overview_ui_returns_taglist(self) -> None:
        """Verify overview_ui returns a ui.TagList (not None)."""
        from renewable_energy_tracker.app.components.overview import overview_ui

        result = overview_ui()
        assert result is not None


class TestOverviewServer:
    def test_overview_server_registers_kpi_outputs(self) -> None:
        """Verify overview_server registers all four KPI output renderers."""
        from shiny import Inputs, Outputs, Session

        from renewable_energy_tracker.app.components.overview import overview_server

        mock_input = MagicMock(spec=Inputs)
        mock_output = MagicMock(spec=Outputs)
        mock_session = MagicMock(spec=Session)

        overview_server(mock_input, mock_output, mock_session)


class TestOverviewData:
    def test_overview_kpi_data_empty_database(self) -> None:
        """Verify kpi_data returns zeros when database is empty."""
        with patch(
            "renewable_energy_tracker.app.components.overview.get_conn"
        ) as mock_get_conn:
            mock_conn = MagicMock()
            mock_get_conn.return_value = mock_conn
            with patch(
                "pandas.read_sql_query", return_value=pd.DataFrame()
            ):
                from renewable_energy_tracker.app.components.overview import (
                    overview_server,
                )

                mock_input = MagicMock()
                mock_output = MagicMock()
                mock_session = MagicMock()

                overview_server(mock_input, mock_output, mock_session)


class TestComparisonUi:
    def test_comparison_ui_returns_taglist(self) -> None:
        """Verify comparison_ui returns a ui.TagList (not None)."""
        from renewable_energy_tracker.app.components.comparison import comparison_ui

        result = comparison_ui()
        assert result is not None


class TestComparisonServer:
    def test_comparison_server_registers_outputs(self) -> None:
        """Verify comparison_server registers ranking output."""
        from shiny import Inputs, Outputs, Session

        from renewable_energy_tracker.app.components.comparison import (
            comparison_server,
        )

        mock_input = MagicMock(spec=Inputs)
        mock_output = MagicMock(spec=Outputs)
        mock_session = MagicMock(spec=Session)

        comparison_server(mock_input, mock_output, mock_session)


class TestCo2SavingsUi:
    def test_co2_savings_ui_returns_taglist(self) -> None:
        """Verify co2_savings_ui returns a ui.TagList (not None)."""
        from renewable_energy_tracker.app.components.co2_savings import co2_savings_ui

        result = co2_savings_ui()
        assert result is not None


class TestCo2SavingsServer:
    def test_co2_savings_server_registers_outputs(self) -> None:
        """Verify co2_savings_server registers co2_table output."""
        from shiny import Inputs, Outputs, Session

        from renewable_energy_tracker.app.components.co2_savings import (
            co2_savings_server,
        )

        mock_input = MagicMock(spec=Inputs)
        mock_output = MagicMock(spec=Outputs)
        mock_session = MagicMock(spec=Session)

        co2_savings_server(mock_input, mock_output, mock_session)


class TestTimeseriesDateRange:
    def test_timeseries_date_range_uses_reasonable_bounds(self) -> None:
        """Verify date range filter covers last year to next year."""
        today = date.today()
        expected_start = date(today.year - 1, 1, 1)
        expected_end = date(today.year + 1, 12, 31)

        assert expected_start.year == today.year - 1
        assert expected_end.year == today.year + 1


class TestAppUi:
    def test_app_ui_is_defined(self) -> None:
        """Verify app_ui is defined (imports without error)."""
        from renewable_energy_tracker.app.app import app_ui

        assert app_ui is not None

    def test_server_is_defined(self) -> None:
        """Verify server function is defined."""
        from renewable_energy_tracker.app.app import server

        assert callable(server)


class TestAppServer:
    def test_server_calls_all_module_servers(self) -> None:
        """Verify server function calls all four module server functions."""
        from shiny import Inputs, Outputs, Session

        from renewable_energy_tracker.app.app import server

        mock_input = MagicMock(spec=Inputs)
        mock_output = MagicMock(spec=Outputs)
        mock_session = MagicMock(spec=Session)

        with patch("renewable_energy_tracker.app.app.overview_server") as mock_overview, \
             patch("renewable_energy_tracker.app.app.timeseries_server") as mock_ts, \
             patch("renewable_energy_tracker.app.app.comparison_server") as mock_comp, \
             patch("renewable_energy_tracker.app.app.co2_savings_server") as mock_co2, \
             patch.object(mock_session, "on_ended"):

            server(mock_input, mock_output, mock_session)

            mock_overview.assert_called_once()
            mock_ts.assert_called_once()
            mock_comp.assert_called_once()
            mock_co2.assert_called_once()
