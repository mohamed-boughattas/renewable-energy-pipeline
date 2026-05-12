from datetime import date

import pandas as pd
from pandas import read_sql_query
from shiny import Inputs, Outputs, Session, render, ui
from shiny.reactive import calc

from renewable_energy_tracker.app.query import get_conn

EMPTY_COLS = [
    "country_code", "country_name", "year_month",
    "renewable_share_pct", "total_production_mwh",
    "total_renewable_mwh", "total_fossil_mwh",
]


def timeseries_ui() -> ui.TagList:
    """Build the Time Series tab UI with filters and data table.

    Returns:
        ui.TagList: Layout containing country/date filters and output table.
    """
    today = date.today()
    year_start = date(today.year - 1, 1, 1)
    year_end = date(today.year + 1, 12, 31)
    return ui.layout_columns(
        ui.card(
            ui.card_header("Filters"),
            ui.input_select(
                "ts_countries",
                "Countries",
                choices={
                    "DE": "Germany",
                    "FR": "France",
                    "ES": "Spain",
                    "DK": "Denmark",
                    "NO": "Norway",
                    "NL": "Netherlands",
                },
                selected=["DE", "FR"],
                multiple=True,
            ),
            ui.input_date_range(
                "ts_date_range",
                "Date Range",
                start=year_start.isoformat(),
                end=year_end.isoformat(),
            ),
        ),
        ui.card(
            ui.card_header("Monthly Renewable Share (%)"),
            ui.output_data_frame("ts_renewable_share_table"),
        ),
        col_widths=[4, 8],
    )


def timeseries_server(input: Inputs, output: Outputs, session: Session) -> None:
    """Register reactive outputs for the Time Series tab.

    Args:
        input: Shiny input values.
        output: Shiny output bindings.
        session: Shiny session object.
    """
    @calc
    def timeseries_data() -> pd.DataFrame:
        """Query monthly renewable share data for selected countries.

        Returns:
            pd.DataFrame: Filtered monthly production summary with columns
                country_code, country_name, year_month, renewable_share_pct,
                total_production_mwh, total_renewable_mwh, total_fossil_mwh.
        """
        countries = input.ts_countries()
        if not countries:
            return pd.DataFrame(columns=EMPTY_COLS)

        conn = get_conn()
        try:
            placeholders = ",".join(["%s"] * len(countries))
            query = f"""
                SELECT country_code, country_name, year_month,
                       renewable_share_pct, total_production_mwh,
                       total_renewable_mwh, total_fossil_mwh
                FROM gld_monthly_production_summary
                WHERE country_code IN ({placeholders})
                ORDER BY year_month, country_code
            """
            return read_sql_query(query, conn, params=tuple(countries))
        finally:
            conn.close()

    @render.data_frame
    def ts_renewable_share_table() -> render.DataGrid:
        """Render the monthly renewable share data table.

        Returns:
            render.DataGrid: An interactive filtered data grid.
        """
        df = timeseries_data()
        return render.DataGrid(df, filters=True)
